from natsort import natsorted
import requests
from flask import Flask, render_template, url_for, Response, send_file, request
from functools import lru_cache
import os
import re
import subprocess
from io import BytesIO
from weasyprint import HTML
from datetime import datetime

# === Função para manter o script vivo ===
def verificar_e_executar_manter_vivo():
    """
    Verifica se 'manter_vivo.py' está rodando. Se não, executa com nohup.
    """
    nome_script = "manter_vivo.py"
    processo_encontrado = False

    try:
        resultado = subprocess.run(['ps', 'aux'], stdout=subprocess.PIPE, text=True, check=True)
        for linha in resultado.stdout.splitlines():
            if nome_script in linha and 'python' in linha and not 'grep' in linha:
                print(f"✅ {nome_script} já está rodando.")
                processo_encontrado = True
                break

        if not processo_encontrado:
            if not os.path.isfile(nome_script):
                print(f"❌ Erro: {nome_script} não encontrado.")
                return

            with open('nohup.out', 'a') as log:
                subprocess.Popen(
                    ['nohup', 'python', nome_script],
                    stdout=log,
                    stderr=log,
                    stdin=subprocess.DEVNULL,
                    start_new_session=True
                )
            print(f"✅ {nome_script} iniciado com nohup.")
    except Exception as e:
        print(f"❌ Erro ao verificar/executar {nome_script}: {e}")

# Executa o extrator em segundo plano
process = subprocess.Popen(
    ["python3", "static/text/extrator_links.py"],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL
)
print("Extrator iniciado em segundo plano.")

app = Flask(__name__)

# Caminho para o arquivo de links
LINKS_FILE = os.path.join(app.static_folder, 'text', 'salmos_links.txt')

# === 1. Defina formatar_nome_salmo ANTES de carregar_salmos ===
def formatar_nome_salmo(filename):
    # Remove extensão
    nome = re.sub(r'\.(mp3|doc)$', '', filename, flags=re.IGNORECASE)
    # Remove '_playback'
    nome = re.sub(r'_playback$', '', nome, flags=re.IGNORECASE)
    # Normaliza múltiplos underscores
    nome = re.sub(r'_+', '_', nome).strip('_')

    # Casos especiais
    if 'dn_' in nome:
        return "Daniel 3"
    if 'isaias12' in nome or 'isaías12' in nome:
        return "Responsório de Isaías 12"
    if 'responsorio' in nome:
        return "Responsório"
    if 'vigilia' in nome or 'vigiliapascal' in nome:
        return "Vigília Pascal"

    # Padrão: salmo_X ou salmo_X_Y
    match = re.match(r'^salmo_(\d+)(?:_(\w+))?$', nome, re.IGNORECASE)
    if match:
        numero = match.group(1)
        sufixo = match.group(2) or ''
        if sufixo.isdigit():
            return f"Salmo {numero} — Versão {sufixo}"
        elif sufixo and re.match(r'^[a-d]$', sufixo, re.IGNORECASE):
            versao = ord(sufixo.lower()) - ord('a') + 1
            return f"Salmo {numero} — Versão {versao}"
        else:
            return f"Salmo {numero}"
    return nome.replace('_', ' ').title()

# === 2. Defina chave_ordenacao (opcional, pode ser inline) ===
def chave_ordenacao(salmo):
    nome = salmo['nome']

    # Ordem: Daniel 3 → Isaías 12 → Vigília Pascal → Salmos por número
    if 'Daniel 3' in nome:
        return (1, 0, 0)
    if 'Isaias12' in nome or 'Isaías 12' in nome or 'Responsório de Isaías 12' in nome:
        return (2, 0, 0)
    if 'Vigília Pascal' in nome:
        return (3, 0, 0)

    # Extrai número do salmo e versão
    match = re.match(r'Salmo (\d+)(?:[ _\-]?(.+))?', nome)
    if match:
        numero = int(match.group(1))
        sufixo = match.group(2) or '0'
        versao_match = re.search(r'(\d+)', sufixo)
        versao = int(versao_match.group(1)) if versao_match else 0
        return (10, numero, versao)

    return (99, nome.lower())

# === 3. Agora defina carregar_salmos ===
def carregar_salmos():
    if not os.path.exists(LINKS_FILE):
        return []

    with open(LINKS_FILE, 'r', encoding='utf-8') as f:
        linhas = [linha.strip() for linha in f if linha.strip()]

    mp3_urls = []
    doc_urls = []
    secao = None

    for linha in linhas:
        if linha.startswith('## Links MP3:'):
            secao = 'mp3'
            continue
        elif linha.startswith('## Links DOC (Cifras):'):
            secao = 'doc'
            continue
        if secao == 'mp3' and linha.endswith('.mp3'):
            mp3_urls.append(linha)
        elif secao == 'doc' and linha.endswith('.doc'):
            doc_urls.append(linha)

    mp3_dict = {url.split('/')[-1]: url for url in mp3_urls}
    doc_dict = {url.split('/')[-1].replace('.doc', '.mp3'): url for url in doc_urls}

    salmos = []
    for filename, mp3_url in mp3_dict.items():
        doc_url = doc_dict.get(filename, "#")
        nome = filename.rsplit('.', 1)[0]  # mantém nome original
        salmos.append({
            'filename': filename,
            'nome': nome,
            'mp3_url': mp3_url,
            'doc_url': doc_url
        })

    # Ordena por nome (opcional)
    return sorted(salmos, key=lambda x: x['nome'])

# === 4. Carregue os salmos (depois de tudo definido) ===
SALMOS = carregar_salmos()

# === 5. Rotas do Flask ===
@app.route('/salmos')
def pagina_salmos():
    return render_template('salmos.html', salmos=SALMOS, ano=2025)

# 🔊 Rota: Stream do áudio (sem expor URL)
@app.route('/play/<path:filename>')
def play_salmo(filename):
    from urllib.parse import unquote
    filename = unquote(filename)
    salmo = next((s for s in SALMOS if s['filename'] == filename), None)
    if not salmo:
        return "Salmos não encontrado", 404
    def generate():
        with requests.get(salmo['mp3_url'], stream=True) as r:
            r.raise_for_status()
            for chunk in r.iter_content(1024):
                yield chunk
    return Response(generate(), mimetype="audio/mpeg")

# ⬇️ Rota: Download anônimo (via wget em memória)
@app.route('/download/mp3/<path:filename>')
def download_mp3(filename):
    from urllib.parse import unquote
    filename = unquote(filename)
    salmo = next((s for s in SALMOS if s['filename'] == filename), None)
    if not salmo:
        return "Salmos não encontrado", 404


    def generate():
        process = subprocess.Popen(
            ['wget', '-q', '-O-', salmo['mp3_url']],
            stdout=subprocess.PIPE
        )
        for chunk in iter(lambda: process.stdout.read(1024), b""):
            yield chunk
        process.wait()

    return Response(
        generate(),
        mimetype='audio/mpeg',
        headers={'Content-Disposition': f'attachment; filename="{filename}"'}
    )


@app.route('/download/doc/<path:filename>')
def download_doc(filename):
    from urllib.parse import unquote
    filename = unquote(filename)
    doc_filename = filename.replace('.mp3', '.doc')
    salmo = next((s for s in SALMOS if s['filename'].replace('.mp3', '.doc') == doc_filename), None)
    if not salmo or salmo['doc_url'] == "#":
        return "Cifra não disponível", 404

    def generate():
        with requests.get(salmo['doc_url'], stream=True) as r:
            r.raise_for_status()
            for chunk in r.iter_content(chunk_size=1024):
                yield chunk

    return Response(
        generate(),
        mimetype='application/vnd.ms-word',
        headers={'Content-Disposition': f'attachment; filename="{doc_filename}"'}
    )


pecados = {
    "1. Amar a Deus sobre todas as coisas": [
        "Negligenciei minha oração diária",
        "Tive dúvidas sobre a fé e critiquei os ensinamentos da Igreja",
        "Senti desânimo espiritual e me revoltei contra Deus",
        "Frequentei cultos ou práticas supersticiosas (ex: cartomantes, horóscopos)",
        "Busquei minha própria glória em vez da vontade de Deus",
        "Fui orgulhoso, vaidoso ou apegado a elogios",
        "Apeguei-me excessivamente ao dinheiro e aos bens materiais",
        "Fui impaciente e pouco tolerante com os outros",
        "Fui indiferente diante do sofrimento alheio",
        "Faltou-me empatia e amor ao próximo",
        "Levei outros ao pecado com meus conselhos, atitudes ou exemplos",
        "Ignorei oportunidades de praticar caridade"
    ],
    "2. Não tomar o nome de Deus em vão": [
        "Usei o nome de Deus ou dos santos de forma desrespeitosa",
        "Ridicularizei símbolos da fé ou religiosos",
        "Fiz promessas sem intenção de cumprir",
        "Fiz juramentos falsos ou desnecessários",
        "Permiti ou ri quando outros zombaram da fé",
        "Usei expressões religiosas com banalidade ou em vão"
    ],
    "3. Guardar domingos e festas de guarda": [
        "Faltei à missa dominical ou em dias santos sem necessidade grave",
        "Cheguei intencionalmente atrasado à missa ou saí antes da bênção final",
        "Comunguei estando em pecado mortal",
        "Deixei de me confessar ao menos uma vez ao ano",
        "Não jejuei ou não fiz abstinência quando mandado pela Igreja",
        "Negligenciei a ajuda material à Igreja",
        "Fui à missa por obrigação, sem esforço de viver a fé no dia a dia"
    ],
    "4. Honrar pai e mãe": [
        "Desobedeci e faltei com respeito aos meus pais ou superiores",
        "Negligenciei os cuidados com meus pais idosos ou doentes",
        "Maltratei meu cônjuge com palavras ou atitudes",
        "Dei mau exemplo aos meus filhos",
        "Permiti influências negativas sobre meus filhos (TV, internet, amizades)",
        "Fui negligente na formação religiosa dos meus filhos",
        "Deixei de corrigir meus filhos por comodismo",
        "Fui ingrato com meus pais ou avós"
    ],
    "5. Não matar": [
        "Alimentei ódio, rancor, inimizade ou desejo de vingança",
        "Recusei-me a perdoar",
        "Desejei a morte ou o mal a alguém (ou a mim mesmo)",
        "Apoiei ou pratiquei aborto, eutanásia ou outras práticas semelhantes",
        "Fui descuidado com minha saúde (excesso de comida, drogas, bebida, sedentarismo)",
        "Assumi riscos desnecessários à minha vida (direção imprudente, vícios)",
        "Dei escândalo ou mau exemplo",
        "Proferi palavrões ou palavras agressivas contra os outros",
        "Feri emocionalmente alguém com minhas palavras ou atitudes",
        "Fui violento, mesmo verbalmente, com pessoas próximas"
    ],
    "6. Não pecar contra a castidade": [
        "Consenti em pensamentos ou desejos impuros",
        "Me masturbei, assisti pornografia ou tive relações sexuais fora do casamento",
        "Fui infiel emocionalmente ou fisicamente",
        "Tive liberdades excessivas no namoro",
        "Usei roupas provocativas com má intenção",
        "Participei de conversas ou fiz piadas imorais",
        "Consumi conteúdo sexualizado (TV, filmes, redes sociais)",
        "Mantive amizades que me levaram ao pecado",
        "Fiz comentários maliciosos sobre o corpo de outras pessoas",
        "Alimentei fantasias sexuais intencionalmente"
    ],
    "7. Não roubar": [
        "Roubei ou fui desonesto em contratos ou negócios",
        "Me apropriei de bens ou dinheiro indevidamente",
        "Deixei de pagar dívidas justas ou salários devidos",
        "Desperdicei tempo no trabalho ou trabalhei com negligência",
        "Fui viciado em jogos de azar",
        "Vivi acima dos meus meios",
        "Fui injusto ao cobrar ou receber valores excessivos",
        "Usei benefícios ou ajudas indevidamente"
    ],
    "8. Não levantar falso testemunho": [
        "Menti habitualmente, mesmo sem prejudicar diretamente",
        "Caluniei, difamei ou exagerei defeitos dos outros",
        "Ouvi ou espalhei boatos",
        "Julguei mal ou condenei injustamente alguém",
        "Causei divisão entre pessoas por fofoca",
        "Não reparei a má reputação causada por mim",
        "Fui hipócrita ou dissimulado para parecer melhor"
    ],
    "9. Não desejar a mulher do próximo": [
        "Alimentei desejos impuros por pessoas casadas ou consagradas",
        "Tive fantasias ou intenções de infidelidade",
        "Assediei verbal ou fisicamente",
        "Flertei com pessoas comprometidas",
        "Tive curiosidade indevida sobre a intimidade de outras pessoas",
        "Usei o olhar de maneira impura ou desrespeitosa"
    ],
    "10. Não cobiçar as coisas alheias": [
        "Invejei os bens, o sucesso ou os talentos dos outros",
        "Desejei tomar ou imitar aquilo que pertence a outros",
        "Fiquei descontente com a minha vida por causa de comparações",
        "Fui ambicioso em excesso, sem gratidão pelo que tenho",
        "Desejei viver a vida dos outros em vez de valorizar a minha"
    ],
    "Mandamentos da Igreja": [
        "Faltei à Missa em festas de guarda",
        "Não me confessei ao menos uma vez por ano",
        "Não comunguei na Páscoa",
        "Comunguei em pecado grave",
        "Não guardei jejum e abstinência nos tempos prescritos",
        "Não ajudei a Igreja materialmente",
        "Desprezei os sacramentos por comodismo ou frieza espiritual"
    ],
    "Pecados relacionados ao casamento e à família": [
        "Fui negligente com meu cônjuge (no diálogo, carinho ou atenção)",
        "Fui violento física ou verbalmente dentro do lar",
        "Desrespeitei meu cônjuge",
        "Guardei mágoas e não perdoei no matrimônio",
        "Priorizei trabalho ou lazer em detrimento da família",
        "Recusei-me a ter filhos sem justa causa",
        "Não dei testemunho cristão dentro do lar",
        "Fui indiferente à vida familiar ou às necessidades dos meus",
        "Usei palavras ofensivas ou humilhantes com meus familiares"
    ],
    "Pecados espirituais e morais": [
        "Fui preguiçoso espiritualmente (não busquei crescer na fé)",
        "Me desinteressei pelas coisas de Deus",
        "Fui indiferente no zelo apostólico (não evangelizei, nem ajudei outros na fé)",
        "Fui conivente com o pecado, meu ou alheio",
        "Busquei o sucesso pessoal acima da vontade divina",
        "Agi por egoísmo, pensando apenas em mim",
        "Fui omisso diante de injustiças ou sofrimentos ao meu redor"
    ],
        "Pecados veniais (faltas leves que enfraquecem minha alma, mas não rompem a amizade com Deus)": [
        "Falei palavras impacientes, com leve irritação ou impolidez",
        "Fui negligente em atos de caridade com os mais próximos",
        "Fiz piadas ou comentários inapropriados, sem intenção grave",
        "Julguei os outros interiormente, mesmo sem espalhar críticas",
        "Tive distrações voluntárias durante a oração, sem esforço para me recolher",
        "Faltei com pequenas responsabilidades no trabalho ou estudo por descuido",
        "Deixei de ajudar alguém por comodismo, ainda que pudesse fazê-lo",
        "Busquei meu conforto ou prazer em coisas pequenas, sem moderação",
        "Fui impaciente com pessoas mais lentas ou com ideias diferentes das minhas",
        "Usei meu tempo de forma egoísta, deixando de servir mais ao próximo"
    ],

    "Pecados capitais (raízes do pecado que geram muitas outras faltas)": [
        "Cedi à soberba, agindo com orgulho ou querendo ser superior aos outros",
        "Fui avarento, apegado ao dinheiro ou a bens materiais, sem generosidade",
        "Entreguei-me à luxúria, buscando prazeres impuros nos pensamentos, olhares ou ações",
        "Fui invejoso, entristecendo-me com o bem ou sucesso alheio",
        "Alimentei a gula, comendo ou bebendo além do necessário por puro prazer",
        "Fui irado, permitindo que a raiva dominasse minhas palavras ou atitudes",
        "Fui preguiçoso, negligente no cumprimento dos meus deveres espirituais ou materiais"
    ]

}


# ✅ Rota principal
@app.route("/", methods=["GET", "POST"])
def index():
    resultado = {}
    html_conteudo = ""
    if request.method == "POST":
        for mandamento, lista in pecados.items():
            indices = request.form.getlist(mandamento)
            selecionados = [lista[int(i)] for i in indices if i.isdigit() and int(i) < len(lista)]
            if selecionados:
                resultado[mandamento] = selecionados

        custom = request.form.get("custom", "").strip()
        if custom:
            resultado.setdefault("Outros pecados digitados", []).append(custom)

        html_conteudo = render_template("pdf_template.html", resultado=resultado)

    return render_template("index.html", pecados=pecados, resultado=resultado, html_conteudo=html_conteudo)

# ✅ Rota de download do PDF
@app.route("/download", methods=["POST"])
def download():
    html_renderizado = request.form.get("html_conteudo", "")
    if not html_renderizado:
        return "Conteúdo vazio para gerar PDF", 400

    pdf_io = BytesIO()
    html = HTML(string=html_renderizado, base_url=request.base_url)
    html.write_pdf(target=pdf_io)
    pdf_io.seek(0)

    return Response(pdf_io.read(),
                    mimetype="application/pdf",
                    headers={"Content-Disposition": "attachment;filename=meus_pecados.pdf"})

# ✅ Rota de orações
@app.route("/oracoes")
def oracoes():
    oracoes_lista = [
        {
            "id": 1,
            "titulo": "Ato de Contrição",
            "texto": (
                "Meu Deus, arrependo-me de todo o coração de Vos ter ofendido, "
                "porque sois infinitamente bom e digno de ser amado sobre todas as coisas. "
                "Proponho firmemente, com o auxílio da vossa graça, emendar-me e evitar as ocasiões de pecado. "
                "Senhor, pela paixão de Jesus Cristo, tende piedade de mim. Amém."
            ),
            "descricao": "Expressa arrependimento sincero e desejo de mudança."
        },
        {
            "id": 2,
            "titulo": "Oração do Arrependimento",
            "texto": (
                "Meu Jesus, por serdes tão bom, e por me amardes tanto, vos agradeço por me terdes esperado até agora e não terdes permitido que eu morresse em pecado. "
                "Peço-vos, por vossa paixão e morte na cruz, perdoai-me todos os meus pecados e fazei-me verdadeiramente penitente..."
            ),
            "descricao": "Para momentos de reflexão e conversão interior."
        },
        {
            "id": 3,
            "titulo": "Confissão Geral",
            "texto": (
                "Senhor meu Deus, reconheço diante de Vós que pequei muitas vezes por pensamentos, palavras, atos e omissões. "
                "Arrependo-me sinceramente de todas as minhas faltas e ofensas, especialmente daquelas que mais feriram o vosso amor. "
                "Com humildade, suplico a vossa misericórdia e, como o filho pródigo, digo: Pai, pequei contra o Céu e contra Vós. "
                "Não sou digno de ser chamado vosso filho. Tende piedade de mim, Senhor. Amém."
            ),
            "descricao": "Ideal para preparação antes da confissão sacramental."
        },
        {
            "id": 4,
            "titulo": "Miserere Mei Deus",
            "texto": (
                "Tende piedade de mim, ó Deus, segundo a vossa misericórdia; "
                "segundo a grandeza da vossa compaixão, apagai a minha culpa. "
                "Lavai-me totalmente da minha iniquidade, e purificai-me do meu pecado. "
                "Criai em mim, ó Deus, um coração puro e renovai em meu peito um espírito firme."
            ),
            "descricao": "Um dos salmos penitenciais mais conhecidos da tradição cristã."
        },
        {
            "id": 5,
            "titulo": "Do Profundo",
            "texto": (
                "Das profundezas clamo a Vós, Senhor. Senhor, escutai a minha voz! "
                "Estejam atentos os vossos ouvidos às súplicas da minha prece. "
                "Se levardes em conta nossas faltas, Senhor, quem poderá subsistir? "
                "Mas em Vós se encontra o perdão, e por isso Vos teme com reverência."
            ),
            "descricao": "Uma poderosa expressão de esperança na misericórdia divina."
        },
        {
            "id": 6,
            "titulo": "Salmo 6",
            "texto": (
                "Senhor, não me repreendais em vossa ira, nem me castigueis no vosso furor. "
                "Tende piedade de mim, Senhor, pois desfaleço; curai-me, Senhor, pois meus ossos tremem. "
                "A minha alma está profundamente perturbada... Salvai-me por causa da vossa misericórdia!"
            ),
            "descricao": "Suplica o perdão e a cura espiritual e física."
        },
        {
            "id": 7,
            "titulo": "Oração à Virgem Maria",
            "texto": (
                "Ó Maria Santíssima, Mãe de Deus e minha Mãe, refugio-me sob a vossa proteção maternal. "
                "Vós que sois a Medianeira de todas as graças, intercedei por mim junto a vosso Filho Jesus. "
                "Alcançai-me a graça do verdadeiro arrependimento, uma boa confissão e a perseverança no bem. "
                "Acompanhai-me em todos os momentos da vida, sobretudo na hora da morte. Amém."
            ),
            "descricao": "Peça a intercessão de Nossa Senhora após o exame de consciência."
        }
    ]
    return render_template("oracoes.html", oracoes=oracoes_lista)


@app.route("/liturgia")
def liturgia():
    import re
    from datetime import datetime
    import requests

    data_param = request.args.get("data")

    FALLBACK_LITURGIA = {
        "data": "16/07/2025",
        "liturgia": "Bem-aventurada Virgem Maria do Monte Carmelo, Festa",
        "cor": "Branco",
        "antifonas": {
            "entrada": "Todos vós que a Deus temeis, vinde escutar..."
        },
        "oracoes": {
            "coleta": "Senhor, nós vos pedimos: venha em nosso auxílio...",
            "oferendas": "Acolhei, Senhor, as orações e oferendas dos vossos fiéis...",
            "comunhao": "Senhor, vós nos fizestes participantes dos frutos da redenção eterna..."
        },
        "leituras": {
            "primeiraLeitura": [{
                "referencia": "Zc 2, 14-17",
                "titulo": "Leitura da Profecia de Zacarias",
                "texto": "Rejubila, alegra-te, cidade de Sião..."
            }],
            "segundaLeitura": [{
                "referencia": "Gl 4, 4-7",
                "titulo": "Leitura da Carta de São Paulo aos Gálatas",
                "texto": "Quando se completou o tempo previsto, Deus enviou o seu Filho..."
            }],
            "salmo": [{
                "referencia": "Lc 1, 46-55",
                "refrao": "O Poderoso fez por mim maravilhas, e Santo é o seu nome.",
                "texto": "A minh’alma engrandece ao Senhor..."
            }],
            "evangelho": [{
                "referencia": "Mt 12, 46-50",
                "titulo": "Proclamação do Evangelho de Jesus Cristo ✠ segundo Mateus",
                "texto": "Enquanto Jesus estava falando às multidões..."
            }]
        }
    }

    try:
        if data_param:
            data_obj = datetime.strptime(data_param, "%Y-%m-%d")
        else:
            data_obj = datetime.today()

        dia = f"{data_obj.day:02d}"
        mes = f"{data_obj.month:02d}"
        ano = f"{data_obj.year}"
        url = f"https://liturgia.up.railway.app/v2/?dia={dia}&mes={mes}&ano={ano}"
    except Exception as e:
        print(f"[ERRO] Falha ao processar data. Usando fallback. Detalhe: {e}")
        url = None

    try:
        if url:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            dados_api = response.json()
        else:
            raise Exception("URL inválida")
    except Exception as e:
        print(f"[AVISO] API falhou: {e}. Usando fallback.")
        dados_api = FALLBACK_LITURGIA

    # Leituras
    leituras = dados_api.get("leituras", {})

    primeira_leitura = ""
    primeira_leitura_lista = leituras.get("primeiraLeitura", [])
    if primeira_leitura_lista:
        pl = primeira_leitura_lista[0]
        primeira_leitura = f"<strong>{pl.get('referencia','')}</strong> – {pl.get('titulo','')}<br>{pl.get('texto','')}"

    segunda_leitura = ""
    segunda_leitura_lista = leituras.get("segundaLeitura", [])
    if segunda_leitura_lista:
        sl = segunda_leitura_lista[0]
        segunda_leitura = f"<strong>{sl.get('referencia','')}</strong> – {sl.get('titulo','')}<br>{sl.get('texto','')}"

    salmo_obj = leituras.get("salmo", [{}])[0]
    salmo_referencia = salmo_obj.get("referencia", "")
    salmo_refrao = salmo_obj.get("refrao", "")
    salmo_texto = salmo_obj.get("texto", "")

    evangelho = ""
    evangelho_lista = leituras.get("evangelho", [])
    if evangelho_lista:
        ev = evangelho_lista[0]
        evangelho = f"<strong>{ev.get('referencia','')}</strong> – {ev.get('titulo','')}<br>{ev.get('texto','')}"

    # Orações
    oracoes = dados_api.get("oracoes", {})
    coleta = oracoes.get("coleta", "")
    oferendas = oracoes.get("oferendas", "")
    comunhao = oracoes.get("comunhao", "")

    # Antífonas
    antifonas = dados_api.get("antifonas", {})
    antifona_entrada = antifonas.get("entrada", "")
    antifona_comunhao = antifonas.get("comunhao", "")

    # Informações gerais
    data_exibicao = dados_api.get("data", data_param or datetime.today().strftime("%d/%m/%Y"))
    titulo = dados_api.get("liturgia", "Liturgia do Dia")
    cor = dados_api.get("cor", "Cor não informada")

    # Selecionar salmos do dia para áudio (usando padrão parecido com antes)
    salmos_do_dia = []
    import re

    if salmo_referencia:
        numero_match = re.search(r'\b(\d+)\b', salmo_referencia)
        numero = numero_match.group(1) if numero_match else None

        if numero:
            for s in SALMOS:
                if f"salmo_{numero}" in s['filename'].lower():
                    salmos_do_dia.append(s)
        if "Dn 3" in salmo_referencia:
            for s in SALMOS:
                if "dn_3.mp3" == s['filename'].lower():
                    salmos_do_dia.append(s)
                    break
        if "Is 12" in salmo_referencia:
            for s in SALMOS:
                if "isaias12.mp3" == s['filename'].lower():
                    salmos_do_dia.append(s)
                    break
    salmos_do_dia.sort(key=lambda x: x['filename'])

    return render_template(
        "liturgia.html",
        titulo=titulo,
        cor=cor,
        data=data_exibicao,
        oracao_dia=coleta,
        oferendas=oferendas,
        comunhao=comunhao,
        antifona_entrada=antifona_entrada,
        antifona_comunhao=antifona_comunhao,
        primeira_leitura=primeira_leitura,
        segunda_leitura=segunda_leitura,
        salmo={
            "referencia": salmo_referencia,
            "refrao": salmo_refrao,
            "texto": salmo_texto
        },
        evangelho=evangelho,
        salmos_do_dia=salmos_do_dia,
        api_falhou=(dados_api == FALLBACK_LITURGIA),
        formatar_nome_salmo=formatar_nome_salmo,
    )



@app.route("/terco")
def terco():
    mistérios = {
        "Gozosos": [
            "1. A Anunciação do Anjo a Maria",
            "2. A Visitação de Maria a Isabel",
            "3. O Nascimento de Jesus em Belém",
            "4. A Apresentação do Menino Jesus no Templo",
            "5. O Encontro do Menino Jesus no Templo"
        ],
        "Dolorosos": [
            "1. Jesus agoniza no Horto",
            "2. Jesus é açoitado",
            "3. Jesus é coroado de espinhos",
            "4. Jesus carrega a Cruz",
            "5. Jesus é crucificado"
        ],
        "Gloriosos": [
            "1. Ressurreição de Jesus",
            "2. Ascensão de Jesus",
            "3. Descida do Espírito Santo",
            "4. Assunção de Maria",
            "5. Coroação de Maria"
        ],
        "Luminosos": [
            "1. Batismo de Jesus no Jordão",
            "2. Auto-revelação de Jesus em Caná",
            "3. Anúncio do Reino de Deus",
            "4. Transfiguração de Jesus",
            "5. Instituição da Eucaristia"
        ]
    }

    oracoes = {
        "Sinal da Cruz": "Em nome do Pai, e do Filho e do Espírito Santo. Amém.",
        "Oferecimento": "Divino Jesus, nós vos oferecemos este terço que vamos rezar, meditando nos mistérios da nossa redenção. Concedei-nos, pela intercessão da Virgem Maria, Mãe de Deus e nossa Mãe, as virtudes que nos são necessárias para bem rezá-lo e a graça de ganharmos as indulgências desta santa devoção.",
        "Oração do Anjo": "O Anjo do Senhor anunciou a Maria. E ela concebeu do Espírito Santo. Ave Maria... Eis aqui a serva do Senhor. Faça-se em mim segundo a Vossa palavra. Ave Maria... E o Verbo de Deus se fez carne. E habitou entre nós. Ave Maria... Rogai por nós, Santa Mãe de Deus. Para que sejamos dignos das promessas de Cristo.",
        "Credo": "Creio em Deus Pai todo-poderoso, criador do céu e da terra... (completo)",
        "Mistérios": {
            "Segunda": "Gozosos",
            "Terça": "Dolorosos",
            "Quarta": "Gloriosos",
            "Quinta": "Luminosos",
            "Sexta": "Dolorosos",
            "Sábado": "Gozosos",
            "Domingo": "Gloriosos"
        },
        "Final": {
            "Salve": "Salve, Rainha, Mãe de misericórdia, vida, doçura e esperança nossa, salve! A vós bradamos, os degredados filhos de Eva...",
            "Ladainha": "Senhor, tende piedade de nós... Cristo, tende piedade de nós... Senhor, tende piedade de nós..."
        }
    }

    return render_template("terco.html", mistérios=mistérios, oracoes=oracoes)


# ✅ Execução da aplicação
@app.context_processor
def utility_processor():
    return dict(formatar_nome_salmo=formatar_nome_salmo)


# -----------------------
# Função inserida: listar_palestras
# -----------------------


def listar_palestras(static_folder):
    """Lê os áudios e resumos da pasta static/audio/catequese e retorna uma lista de palestras ordenadas naturalmente."""
    audio_dir = os.path.join(static_folder, "audio", "catequese")
    palestras = []

    if not os.path.exists(audio_dir):
        return palestras

    def natural_sort_key(filename):
        name = os.path.splitext(filename)[0]
        # Extrai sequências de números e converte para int, mantendo ordem natural
        return [int(s) if s.isdigit() else s.lower() for s in re.split(r'(\d+)', name)]

    try:
        files = sorted(
            [f for f in os.listdir(audio_dir) if f.lower().endswith(".mp3")],
            key=natural_sort_key
        )
    except Exception as e:
        print(f"Erro ao listar arquivos: {e}")
        return palestras

    for filename in files:
        base_name = os.path.splitext(filename)[0]
        resumo_path = os.path.join(audio_dir, base_name + ".txt")

        resumo = ""
        if os.path.exists(resumo_path):
            try:
                with open(resumo_path, "r", encoding="utf-8") as f:
                    resumo = f.read().strip()
            except Exception as e:
                print(f"Erro ao ler resumo {resumo_path}: {e}")

        palestras.append({
            "id": base_name,
            "titulo": f"Aula {base_name}" if base_name.isdigit() else f"Aula {base_name}",
            "nome": base_name.replace("_", " ").title(),
            "filename": filename,
            "resumo": resumo
        })

    return palestras

@app.route('/catequese')
def catequese():
    """Rota para exibir as palestras de catequese."""
    palestras = listar_palestras(app.static_folder)
    ano = datetime.now().year
    return render_template('catequese.html', palestras=palestras, ano=ano)


if __name__ == "__main__":
    verificar_e_executar_manter_vivo()
    app.run(host="0.0.0.0", port=5000, debug=True)

