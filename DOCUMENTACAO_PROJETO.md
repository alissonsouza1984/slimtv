# 📦 Documentação Técnica do Projeto

Este documento descreve todos os arquivos, módulos, recursos estáticos e estrutura lógica do projeto para fins de manutenção, melhorias ou suporte automatizado.

## 📄 app.py
**Tipo:** Script Python

**Funções definidas:** 18

- def formatar_nome_salmo(filename):
- def chave_ordenacao(salmo):
- def carregar_salmos():
- def pagina_salmos():
- def play_salmo(filename):
- def generate():
- def download_mp3(filename):
- def generate():
- def download_doc(filename):
- def generate():
- def index():
- def download():
- def oracoes():
- def liturgia():
- def extrair_texto(obj):
- def corresponde(filename_lower, padrao):
- def terco():
- def utility_processor():

**Rotas Flask detectadas:**
- @app.route('/salmos')
- @app.route('/play/<path:filename>')
- @app.route('/download/mp3/<path:filename>')
- @app.route('/download/doc/<path:filename>')
- @app.route("/", methods=["GET", "POST"])
- @app.route("/download", methods=["POST"])
- @app.route("/oracoes")
- @app.route("/liturgia")
- @app.route("/terco")


## 📄 compilar_projeto.py
**Tipo:** Script Python

**Funções definidas:** 1

- def adicionar_arquivos_de_pasta(pasta, extensoes=None):


## 📄 Dockerfile
**Tipo:** Dockerfile (imagem de container)
- FROM python:3.11-slim
- RUN apt-get update && apt-get install -y --no-install-recommends \
- RUN pip install --no-cache-dir -r requirements.txt
- CMD ["sh", "-c", "python static/text/extrator_links.py && gunicorn --bind 0.0.0.0:10000 app:app"]


## 📄 README.md
**Tipo:** Arquivo de documentação


## 📄 render.yaml
**Tipo:** Outro arquivo


## 📄 requirements.txt
**Tipo:** Dependências Python

**Pacotes:**
- ################################################################################
- Flask==2.3.3
- WeasyPrint==53.0
- gunicorn
- requests
- beautifulsoup4==4.12.3
- lxml==5.2.1
- ################################################################################


## 📄 static/audio/miserere_mei_deus.mp3
**Tipo:** Arquivo de mídia (binário)


## 📄 static/audio/baixar/baixar-mp3.py
**Tipo:** Script Python

**Funções definidas:** 1

- def baixar_mp3(link):


## 📄 static/audio/terco/dor.mp3
**Tipo:** Arquivo de mídia (binário)


## 📄 static/audio/terco/lum.mp3
**Tipo:** Arquivo de mídia (binário)


## 📄 static/audio/terco/goz.mp3
**Tipo:** Arquivo de mídia (binário)


## 📄 static/audio/terco/glo.mp3
**Tipo:** Arquivo de mídia (binário)


## 📄 static/css/style.css
**Tipo:** Folha de Estilo CSS
**Classes definidas:** 24


## 📄 static/img/cristo_pantocrator.jpg
**Tipo:** Arquivo de mídia (binário)


## 📄 static/img/terco/espirito_santo.png
**Tipo:** Arquivo de mídia (binário)


## 📄 static/img/terco/anunciacao.png
**Tipo:** Arquivo de mídia (binário)


## 📄 static/img/terco/horto.png
**Tipo:** Arquivo de mídia (binário)


## 📄 static/img/terco/nascimento.png
**Tipo:** Arquivo de mídia (binário)


## 📄 static/img/terco/acoites.png
**Tipo:** Arquivo de mídia (binário)


## 📄 static/img/terco/espinhos.png
**Tipo:** Arquivo de mídia (binário)


## 📄 static/img/terco/reino.png
**Tipo:** Arquivo de mídia (binário)


## 📄 static/img/terco/crucificacao.png
**Tipo:** Arquivo de mídia (binário)


## 📄 static/img/terco/visitacao.png
**Tipo:** Arquivo de mídia (binário)


## 📄 static/img/terco/apresentacao.png
**Tipo:** Arquivo de mídia (binário)


## 📄 static/img/terco/bodas.png
**Tipo:** Arquivo de mídia (binário)


## 📄 static/img/terco/ascensao.png
**Tipo:** Arquivo de mídia (binário)


## 📄 static/img/terco/eucaristia.png
**Tipo:** Arquivo de mídia (binário)


## 📄 static/img/terco/cruz.png
**Tipo:** Arquivo de mídia (binário)


## 📄 static/img/terco/assuncao.png
**Tipo:** Arquivo de mídia (binário)


## 📄 static/img/terco/transfiguracao.png
**Tipo:** Arquivo de mídia (binário)


## 📄 static/img/terco/coroacao.png
**Tipo:** Arquivo de mídia (binário)


## 📄 static/img/terco/templo.png
**Tipo:** Arquivo de mídia (binário)


## 📄 static/img/terco/batismo.png
**Tipo:** Arquivo de mídia (binário)


## 📄 static/img/terco/ressurreicao.png
**Tipo:** Arquivo de mídia (binário)


## 📄 static/text/salmo_22_10_playback.mp3
**Tipo:** Arquivo de mídia (binário)


## 📄 static/text/salmos_links.txt
**Tipo:** Arquivo texto com dados ou links
**Total de linhas úteis:** 345


## 📄 static/text/extrator_links.py
**Tipo:** Script Python

**Funções definidas:** 1

- def gerar_lista_links():


## 📄 templates/pdf_template.html
**Tipo:** Template HTML (Jinja2)

**Títulos encontrados:**
- <h1>Exame de Consciência</h1>


## 📄 templates/terco.html
**Tipo:** Template HTML (Jinja2)

**Títulos encontrados:**
- <title>Santo Rosário – Guia Completo</title>


## 📄 templates/salmos.html
**Tipo:** Template HTML (Jinja2)

**Títulos encontrados:**
- <title>Salmos e Cifras Sacras</title>
- <h1>🎵 Salmos e Cifras Sacras</h1>


## 📄 templates/backup.html
**Tipo:** Template HTML (Jinja2)

**Títulos encontrados:**
- <title>Meditações Teológicas dos Mistérios do Rosário</title>


## 📄 templates/liturgia.html
**Tipo:** Template HTML (Jinja2)

**Títulos encontrados:**
- <title>{{ titulo }}</title>


## 📄 templates/index.html
**Tipo:** Template HTML (Jinja2)

**Títulos encontrados:**
- <title>Exame de Consciência</title>
- <h1>Exame de Consciência</h1>`;


## 📄 templates/oracoes.html
**Tipo:** Template HTML (Jinja2)

**Títulos encontrados:**
- <title>Orações Católicas</title>


