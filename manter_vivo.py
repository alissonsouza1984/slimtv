import time
import requests

def manter_site_vivo(url, intervalo_segundos=120):
    """Envia requisições periódicas para manter o site ativo"""
    while True:
        try:
            resposta = requests.get(url)
            print(f"[OK] {url} respondeu com {resposta.status_code}")
        except Exception as e:
            print(f"[ERRO] Falha ao acessar {url}: {e}")
        time.sleep(intervalo_segundos)

manter_site_vivo("https://confission.onrender.com", intervalo_segundos=120)

