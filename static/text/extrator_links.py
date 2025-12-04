# static/text/extrator_links.py

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os

# URL do site
URL = 'http://www.portaldamusicacatolica.com.br/salmoonline_antigos.asp'

# Caminho absoluto para salvar o arquivo
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), 'salmos_links.txt')

# Headers realistas
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Referer': 'http://www.google.com/',
    'DNT': '1',
}

def gerar_lista_links():
    print(f"[INFO] Acessando: {URL}")
    try:
        response = requests.get(URL, headers=HEADERS, timeout=15, allow_redirects=True)
        response.raise_for_status()
        print(f"[INFO] Status: {response.status_code}")
    except requests.RequestException as e:
        print(f"[ERRO] Falha ao acessar o site: {e}")
        return

    try:
        soup = BeautifulSoup(response.content, 'html.parser')
    except Exception as e:
        print(f"[ERRO] Falha ao analisar o HTML: {e}")
        return

    # Extração de links MP3 e DOC
    mp3_links = []
    doc_links = []

    for a in soup.find_all('a', href=True):
        href = a['href'].strip()
        if not href:
            continue
        full_url = urljoin(URL, href)
        if full_url.lower().endswith('.mp3'):
            mp3_links.append(full_url)
        elif full_url.lower().endswith('.doc'):
            doc_links.append(full_url)

    # Remover duplicatas
    mp3_links = list(dict.fromkeys(mp3_links))
    doc_links = list(dict.fromkeys(doc_links))

    # Salvar no arquivo
    try:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write(f'# Foram encontrados {len(mp3_links)} links MP3 e {len(doc_links)} links DOC\n\n')
            f.write('## Links MP3:\n')
            for link in mp3_links:
                f.write(link + '\n')
            f.write('\n## Links DOC (Cifras):\n')
            for link in doc_links:
                f.write(link + '\n')

        print(f"[SUCESSO] Arquivo '{OUTPUT_FILE}' gerado com {len(mp3_links)} MP3 e {len(doc_links)} DOC.")
    except Exception as e:
        print(f"[ERRO] Falha ao salvar o arquivo: {e}")

if __name__ == "__main__":
    gerar_lista_links()