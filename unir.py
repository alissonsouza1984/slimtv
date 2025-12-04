import re

# Caminho da pasta onde os .txt serão salvos
AUDIO_DIR = "static/audio/catequese"

def dividir_resumos(arquivo_corrigido):
    with open(arquivo_corrigido, "r", encoding="utf-8") as f:
        conteudo = f.read()

    # Expressão regular para capturar cada bloco de aula
    padrao = re.compile(r"---\s*AULA:\s*([^\\]+)\s*---\s*\n+((?:[^=]|=(?!=))+?)(?=\n*=*\n*--- AULA:|$)", re.DOTALL)

    matches = padrao.findall(conteudo)

    if not matches:
        print("❌ Nenhum bloco de aula encontrado no arquivo. Verifique o formato.")
        return

    for base_name, texto in matches:
        # Limpa espaços
        base_name = base_name.strip()
        texto = texto.strip()

        # Nome do arquivo original
        filename = f"{base_name}.txt"
        caminho = os.path.join(AUDIO_DIR, filename)

        try:
            with open(caminho, "w", encoding="utf-8") as f:
                f.write(texto)
            print(f"✅ {filename} atualizado com sucesso!")
        except Exception as e:
            print(f"❌ Erro ao salvar {filename}: {e}")

    print("\n✅ Todos os resumos foram restaurados nos arquivos originais!")

if __name__ == "__main__":
    dividir_resumos("todos_resumos_corrigidos.txt")
