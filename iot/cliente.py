"""Cliente IoT: envia as leituras geradas pro servidor via HTTP POST,
simulando dispositivos reais enviando dados pela rede."""

import requests


def enviar_leituras(leituras, url_servidor):
    """Envia cada leitura pro endpoint do servidor. Devolve quantas foram
    aceitas e quantas foram rejeitadas (dado invalido detectado no servidor)."""
    aceitas = 0
    rejeitadas = 0

    for leitura in leituras:
        try:
            resposta = requests.post(url_servidor, json=leitura, timeout=5)
            if resposta.status_code == 201:
                aceitas += 1
            else:
                rejeitadas += 1
        except requests.exceptions.RequestException as erro:
            print(f"[CLIENTE] Falha ao enviar leitura de {leitura.get('equipamento', '?')}: {erro}")
            rejeitadas += 1

    return aceitas, rejeitadas
