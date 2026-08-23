"""Ponto de entrada: sobe o servidor, gera e envia leituras IoT, roda a
analise de risco e mostra o resultado. Fluxo completo: IoT -> Servidor ->
Dados -> Analise -> Resultado."""

import argparse
import json
import logging
import os
import threading
import time

from iot.gerador import gerar_leituras
from iot.cliente import enviar_leituras
from servidor.app import app, CAMINHO_DADOS, limpar_dados_armazenados
from analise.motor import analisar_leituras
from saida.relatorio import exibir_resumo, exportar_csv, exportar_json

DIR_BASE = os.path.dirname(os.path.abspath(__file__))
DIR_SAIDA = os.path.join(DIR_BASE, "output")
HOST, PORTA = "127.0.0.1", 5055
URL_SERVIDOR = f"http://{HOST}:{PORTA}/dados"


def subir_servidor_em_thread():
    logging.getLogger("werkzeug").setLevel(logging.ERROR)
    thread = threading.Thread(
        target=lambda: app.run(host=HOST, port=PORTA, debug=False, use_reloader=False),
        daemon=True,
    )
    thread.start()
    time.sleep(1)  # espera o servidor subir
    return thread


def ler_dados_armazenados():
    if not os.path.exists(CAMINHO_DADOS):
        return []
    leituras = []
    with open(CAMINHO_DADOS, "r", encoding="utf-8") as arquivo:
        for linha in arquivo:
            linha = linha.strip()
            if linha:
                leituras.append(json.loads(linha))
    return leituras


def main():
    parser = argparse.ArgumentParser(description="Sistema de risco IoT - Cognitive Cybersecurity")
    parser.add_argument("--quantidade", type=int, default=20, help="Quantidade de leituras normais a gerar")
    parser.add_argument("--sem-problemas", action="store_true", help="Nao injeta leituras problematicas de proposito")
    parser.add_argument("--manter-dados", action="store_true", help="Nao limpa os dados de rodadas anteriores")
    argumentos = parser.parse_args()

    if not argumentos.manter_dados:
        limpar_dados_armazenados()

    print("[SISTEMA] Subindo servidor...")
    subir_servidor_em_thread()

    print("[IOT] Gerando leituras dos sensores...")
    leituras = gerar_leituras(
        quantidade=argumentos.quantidade,
        incluir_problemas=not argumentos.sem_problemas,
    )

    print(f"[IOT] Enviando {len(leituras)} leitura(s) para o servidor...")
    aceitas, rejeitadas = enviar_leituras(leituras, URL_SERVIDOR)
    print(f"[SERVIDOR] {aceitas} aceita(s), {rejeitadas} rejeitada(s) na validacao.")

    print("[ANALISE] Lendo dados armazenados e calculando risco...")
    dados_armazenados = ler_dados_armazenados()
    resultados = analisar_leituras(dados_armazenados)

    print()
    exibir_resumo(resultados)

    caminho_json = exportar_json(resultados, os.path.join(DIR_SAIDA, "resultado_risco.json"))
    caminho_csv = exportar_csv(resultados, os.path.join(DIR_SAIDA, "resultado_risco.csv"))

    print()
    print("=== ARQUIVOS GERADOS ===")
    print(caminho_json)
    print(caminho_csv)


if __name__ == "__main__":
    main()
