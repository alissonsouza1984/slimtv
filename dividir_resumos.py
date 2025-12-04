import os
import re

# Caminho da pasta onde os arquivos .txt estão
AUDIO_DIR = "static/audio/catequese"

# Mapeamento exato entre o título da aula e o nome do arquivo
ARQUIVOS_POR_TITULO = {
    "1 - Por que estamos neste mundo?": "1 - Por que estamos neste mundo?.txt",
    "10 - As coisas visíveis e invisíveis": "10 - As coisas visíveis e invisíveis.txt",
    "11 - Mal, uma invenção angélica": "11 - Mal, uma invenção angélica.txt",
    "12 - A promessa do Salvador": "12 - A promessa do Salvador.txt",
    "13 - E o Verbo se fez carne": "13 - E o Verbo se fez carne.txt",
    "14 - O mistério da Santíssima Trindade": "14 - O mistério da Santíssima Trindade.txt",
    "15 - O mistério de Jesus Cristo": "15 - O mistério de Jesus Cristo.txt",
    "16 - Uma só pessoa em duas naturezas": "16 - Uma só pessoa em duas naturezas.txt",
    "17 - A visão beatífica de Jesus Cristo": "17 - A visão beatífica de Jesus Cristo.txt",
    "18 - Cristo, sacerdote e vítima": "18 - Cristo, sacerdote e vítima.txt",
    "19 - A nossa incorporação a Cristo": "19 - A nossa incorporação a Cristo.txt",
    "2 - Como Deus quer que sejamos felizes?": "2 - Como Deus quer que sejamos felizes?.txt",
    "20 - As dores de Cristo durante a paixão": "20 - As dores de Cristo durante a paixão.txt",
    "21 - A justiça da redenção": "21 - A justiça da redenção.txt",
    "22 - A humanidade ressuscitada de Cristo": "22 - A humanidade ressuscitada de Cristo.txt",
    "23 - O que significa a ascensão de Cristo?": "23 - O que significa a ascensão de Cristo?.txt",
    "24 - Por que Jesus nos enviou o Espírito Santo?": "24 - Por que Jesus nos enviou o Espírito Santo?.txt",
    "25 - O que é a graça atual?": "25 - O que é a graça atual?.txt",
    "26 - O que é a graça santificante?": "26 - O que é a graça santificante?.txt",
    "27 - Creio na Santa Igreja Católica": "27 - Creio na Santa Igreja Católica.txt",
    "28 - Há salvação fora da Igreja": "28 - Há salvação fora da Igreja.txt",
    "29 - Qual é a única Igreja de Cristo": "29 - Qual é a única Igreja de Cristo.txt",
    "3 - O Deus que se revela": "3 - O Deus que se revela.txt",
    "30 - O que é a comunhão dos santos?": "30 - O que é a comunhão dos santos?.txt",
    "31 - O que é a remissão dos pecados?": "31 - O que é a remissão dos pecados?.txt",
    "32 - Depois da morte vem o juízo": "32 - Depois da morte vem o juízo.txt",
    "33 - Céu, inferno e purgatório": "33 - Céu, inferno e purgatório.txt",
    "34 - Que virá a julgar os vivos e os mortos": "34 - Que virá a julgar os vivos e os mortos.txt",
    "4 - Não há Cristo sem Igreja": "4 - Não há Cristo sem Igreja.txt",
    "5 - Como nasce a virtude da fé?": "5 - Como nasce a virtude da fé?.txt",
    "6 - Como saber onde está a verdadeira fé?": "6 - Como saber onde está a verdadeira fé?.txt",
    "7 - O magistério da Igreja e os dogmas da fé": "7 - O magistério da Igreja e os dogmas da fé.txt",
    "8 - Deus existe?": "8 - Deus existe?.txt",
    "9 - O que significa criar?": "9 - O que significa criar?.txt"
}

def dividir_resumos():
    arquivo_entrada = "todos_resumos_corrigidos.txt"

    if not os.path.exists(arquivo_entrada):
        print(f"❌ Erro: Arquivo '{arquivo_entrada}' não encontrado.")
        return

    with open(arquivo_entrada, "r", encoding="utf-8") as f:
        conteudo = f.read()

    # Padrão para capturar cada bloco: --- AULA: Título da Aula ---
    padrao = re.compile(
        r"---\s*AULA:\s*(.+?)\s*---\s*\n+((?:[^-]|-(?!--))+?)(?=\n*--- AULA:|$)",
        re.DOTALL
    )

    matches = padrao.findall(conteudo)

    if not matches:
        print("❌ Nenhum bloco encontrado. Verifique o formato do arquivo.")
        return

    print(f"✅ Encontradas {len(matches)} aulas. Iniciando restauração...\n")

    for titulo, texto in matches:
        titulo = titulo.strip()
        texto = texto.strip()

        # Extrai apenas o número e o início do título para busca (ex: "1 - Por que estamos...")
        chave_busca = re.match(r'^\d+', titulo)
        if not chave_busca:
            print(f"⚠️  Título inválido (sem número): '{titulo}'")
            continue

        numero = chave_busca.group()
        candidatos = [k for k in ARQUIVOS_POR_TITULO.keys() if k.startswith(numero + " - ")]

        if not candidatos:
            print(f"❌ Nenhum arquivo encontrado para o número '{numero}' (título: '{titulo}')")
            continue

        # Usa o mapeamento exato
        if titulo in ARQUIVOS_POR_TITULO:
            nome_arquivo = ARQUIVOS_POR_TITULO[titulo]
            caminho = os.path.join(AUDIO_DIR, nome_arquivo)
            try:
                with open(caminho, "w", encoding="utf-8") as f:
                    f.write(texto)
                print(f"✅ Atualizado: '{nome_arquivo}'")
            except Exception as e:
                print(f"❌ Erro ao salvar '{nome_arquivo}': {e}")
        else:
            print(f"❌ Título não encontrado no mapeamento exato: '{titulo}'")
            print(f"   Possíveis: {candidatos}")

    print("\n🎉 Todos os resumos foram restaurados corretamente nos arquivos originais!")

if __name__ == "__main__":
    dividir_resumos()
