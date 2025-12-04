import os
import re

# Caminho da pasta onde estão os .txt
AUDIO_DIR = "static/audio/catequese"

def natural_sort_key(text):
    return [int(s) if s.isdigit() else s.lower() for s in re.split(r'(\d+)', text)]

def unir_resumos():
    # Listar todos os .txt
    txt_files = [f for f in os.listdir(AUDIO_DIR) if f.lower().endswith(".txt")]
    txt_files = sorted(txt_files, key=natural_sort_key)

    output_file = "todos_resumos.txt"

    with open(output_file, "w", encoding="utf-8") as outfile:
        for filename in txt_files:
            base_name = os.path.splitext(filename)[0]
            txt_path = os.path.join(AUDIO_DIR, filename)

            # Adiciona cabeçalho
            outfile.write(f"--- AULA: {base_name} ---\n\n")

            # Lê e escreve o conteúdo
            try:
                with open(txt_path, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    outfile.write(content)
            except Exception as e:
                outfile.write(f"[Erro ao ler o arquivo: {e}]")

            outfile.write("\n\n" + "="*60 + "\n\n")

    print(f"✅ Todos os resumos foram unidos em '{output_file}' na ordem correta!")

if __name__ == "__main__":
    unir_resumos()
