"""Servidor HTTP que recebe as leituras IoT, valida antes de aceitar
(seguranca basica) e armazena num arquivo local (sem banco de dados)."""

import json
import os
import time

from flask import Flask, jsonify, request

DIR_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAMINHO_DADOS = os.path.join(DIR_BASE, "dados", "leituras.jsonl")

CAMPOS_OBRIGATORIOS = ["equipamento", "temperatura", "timestamp"]
TEMPERATURA_MIN, TEMPERATURA_MAX = -30.0, 80.0
UMIDADE_MIN, UMIDADE_MAX = 0.0, 100.0

app = Flask(__name__)


def validar_payload(dados):
    """Validacao basica de seguranca: rejeita payload sem os campos
    obrigatorios ou com valores fora de faixa fisicamente plausivel.
    Retorna (valido, motivo)."""
    if not isinstance(dados, dict):
        return False, "payload nao e um objeto JSON"

    for campo in CAMPOS_OBRIGATORIOS:
        if campo not in dados:
            return False, f"campo obrigatorio ausente: {campo}"

    temperatura = dados.get("temperatura")
    if not isinstance(temperatura, (int, float)):
        return False, "temperatura precisa ser numerica"
    if not (TEMPERATURA_MIN <= temperatura <= TEMPERATURA_MAX):
        return False, "temperatura fora da faixa plausivel"

    if "umidade" in dados:
        umidade = dados["umidade"]
        if not isinstance(umidade, (int, float)):
            return False, "umidade precisa ser numerica"
        if not (UMIDADE_MIN <= umidade <= UMIDADE_MAX):
            return False, "umidade fora da faixa plausivel"

    return True, "ok"


@app.route("/dados", methods=["POST"])
def receber_dados():
    corpo = request.get_json(silent=True)
    valido, motivo = validar_payload(corpo)

    if not valido:
        return jsonify({"status": "rejeitado", "motivo": motivo}), 400

    registro = dict(corpo)
    registro["recebido_em"] = time.time()

    os.makedirs(os.path.dirname(CAMINHO_DADOS), exist_ok=True)
    with open(CAMINHO_DADOS, "a", encoding="utf-8") as arquivo:
        arquivo.write(json.dumps(registro, ensure_ascii=False) + "\n")

    return jsonify({"status": "recebido"}), 201


@app.route("/dados", methods=["GET"])
def listar_dados():
    if not os.path.exists(CAMINHO_DADOS):
        return jsonify([])

    registros = []
    with open(CAMINHO_DADOS, "r", encoding="utf-8") as arquivo:
        for linha in arquivo:
            linha = linha.strip()
            if linha:
                registros.append(json.loads(linha))

    return jsonify(registros)


@app.route("/saude", methods=["GET"])
def saude():
    return jsonify({"status": "online"})


def limpar_dados_armazenados():
    """Apaga o arquivo de dados, pra comecar uma rodada nova do zero."""
    if os.path.exists(CAMINHO_DADOS):
        os.remove(CAMINHO_DADOS)
