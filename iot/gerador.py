"""Gerador de leituras IoT simuladas (sensores de temperatura/umidade em
equipamentos rurais). Gera leituras normais e algumas propositalmente
problemáticas (temperatura alta, umidade baixa, dados incompletos,
repetição), pra exercitar o motor de risco."""

import random
import time

EQUIPAMENTOS = ["trator_01", "trator_02", "colheitadeira_01", "sensor_02", "sensor_03"]


def _leitura_normal(equipamento_id):
    return {
        "equipamento": equipamento_id,
        "temperatura": round(random.uniform(18.0, 32.0), 1),
        "umidade": round(random.uniform(35.0, 70.0), 1),
        "timestamp": time.time(),
    }


def _leitura_temperatura_alta(equipamento_id):
    leitura = _leitura_normal(equipamento_id)
    leitura["temperatura"] = round(random.uniform(38.0, 48.0), 1)
    return leitura


def _leitura_umidade_baixa(equipamento_id):
    leitura = _leitura_normal(equipamento_id)
    leitura["umidade"] = round(random.uniform(5.0, 24.0), 1)
    return leitura


def _leitura_incompleta(equipamento_id):
    leitura = _leitura_normal(equipamento_id)
    leitura.pop("umidade")
    return leitura


def gerar_leituras(quantidade=20, incluir_problemas=True):
    """Gera uma lista de leituras IoT. Se incluir_problemas=True, mistura
    leituras normais com leituras que disparam as regras de risco
    (temperatura alta, umidade baixa, dados incompletos e repetição)."""
    leituras = []

    for _ in range(quantidade):
        equipamento_id = random.choice(EQUIPAMENTOS)
        leituras.append(_leitura_normal(equipamento_id))

    if incluir_problemas:
        leituras.append(_leitura_temperatura_alta("trator_01"))
        leituras.append(_leitura_umidade_baixa("trator_01"))
        leituras.append(_leitura_incompleta("sensor_02"))

        # repeticao proposital: mesma leitura enviada duas vezes em seguida
        leitura_repetida = _leitura_normal("colheitadeira_01")
        leituras.append(leitura_repetida)
        leituras.append(dict(leitura_repetida))

    random.shuffle(leituras)
    return leituras
