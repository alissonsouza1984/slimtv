import os
import re


DOCUMENTACAO = "DOCUMENTACAO_PROJETO.md"

def extrair_titulo_arquivo(linha):
    match = re.match(r"### ARQUIVO: (.+)", linha)
    if match:
        return match.group(1).strip()
    return None

def gerar_documentacao(txt_compilado):
    with open(txt_compilado, "r", encoding="utf-8") as f:
        linhas = f.readlines()

    documentacao = []
    atual_arquivo = None
    conteudo_buffer = []

    for linha in linhas:
        titulo = extrair_titulo_arquivo(linha)
        if titulo:
            if atual_arquivo:
                resumo = resumir_conteudo_arquivo(atual_arquivo, conteudo_buffer)
                documentacao.append(resumo)
                conteudo_buffer = []
            atual_arquivo = titulo
        elif atual_arquivo:
            conteudo_buffer.append(linha)

    # Último arquivo
    if atual_arquivo:
        resumo = resumir_conteudo_arquivo(atual_arquivo, conteudo_buffer)
        documentacao.append(resumo)

    # Salva a documentação final
    with open(DOCUMENTACAO, "w", encoding="utf-8") as f_out:
        f_out.write("# 📦 Documentação Técnica do Projeto\n\n")
        f_out.write("Este documento descreve todos os arquivos, módulos, recursos estáticos e estrutura lógica do projeto para fins de manutenção, melhorias ou suporte automatizado.\n\n")
        for bloco in documentacao:
            f_out.write(bloco)
            f_out.write("\n\n")

    print(f"✅ Documentação gerada: {DOCUMENTACAO}")

def resumir_conteudo_arquivo(nome_arquivo, linhas):
    resumo = f"## 📄 {nome_arquivo}\n"
    if nome_arquivo.endswith(".py"):
        resumo += "**Tipo:** Script Python\n\n"
        funcoes = [l for l in linhas if l.strip().startswith("def ")]
        rotas = [l for l in linhas if "@app.route" in l]
        if funcoes:
            resumo += f"**Funções definidas:** {len(funcoes)}\n\n"
            for func in funcoes:
                resumo += f"- {func.strip()}\n"
        if rotas:
            resumo += f"\n**Rotas Flask detectadas:**\n"
            for rota in rotas:
                resumo += f"- {rota.strip()}\n"

    elif nome_arquivo.endswith(".html"):
        resumo += "**Tipo:** Template HTML (Jinja2)\n"
        titulos = [l for l in linhas if "<title>" in l or "<h1>" in l]
        if titulos:
            resumo += "\n**Títulos encontrados:**\n"
            for t in titulos:
                resumo += f"- {t.strip()}\n"

    elif nome_arquivo.endswith(".css"):
        resumo += "**Tipo:** Folha de Estilo CSS\n"
        resumo += f"**Classes definidas:** {sum(1 for l in linhas if l.strip().startswith('.'))}\n"

    elif nome_arquivo.endswith(".mp3") or nome_arquivo.endswith(".jpg") or nome_arquivo.endswith(".png"):
        resumo += "**Tipo:** Arquivo de mídia (binário)\n"

    elif nome_arquivo == "Dockerfile":
        resumo += "**Tipo:** Dockerfile (imagem de container)\n"
        for l in linhas:
            if "FROM " in l or "RUN " in l or "CMD " in l:
                resumo += f"- {l.strip()}\n"

    elif nome_arquivo == "README.md":
        resumo += "**Tipo:** Arquivo de documentação\n"

    elif nome_arquivo == "requirements.txt":
        resumo += "**Tipo:** Dependências Python\n"
        deps = [l.strip() for l in linhas if l.strip()]
        resumo += "\n**Pacotes:**\n"
        for d in deps:
            resumo += f"- {d}\n"

    elif nome_arquivo.endswith(".txt"):
        resumo += "**Tipo:** Arquivo texto com dados ou links\n"
        linhas_validas = [l.strip() for l in linhas if l.strip() and not l.startswith("#")]
        resumo += f"**Total de linhas úteis:** {len(linhas_validas)}\n"

    else:
        resumo += "**Tipo:** Outro arquivo\n"

    return resumo

# Executar com base no arquivo já gerado anteriormente
gerar_documentacao("projeto_compilado.txt")
