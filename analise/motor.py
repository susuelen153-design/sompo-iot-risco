"""Motor de risco: agrupa as leituras por equipamento, aplica as regras e
calcula o score final de cada um."""

from analise.regras import avaliar_leitura, detectar_repeticoes
from analise.seguranca import dados_invalidos, leitura_suspeita

FAIXAS_CLASSIFICACAO = [
    (0, 2, "BAIXO"),
    (3, 5, "MEDIO"),
    (6, float("inf"), "ALTO"),
]


def classificar_score(score):
    """Classifica o score total: 0-2 Baixo, 3-5 Medio, 6+ Alto."""
    for minimo, maximo, rotulo in FAIXAS_CLASSIFICACAO:
        if minimo <= score <= maximo:
            return rotulo
    return "INDEFINIDO"


def agrupar_por_equipamento(leituras):
    """Agrupa as leituras por equipamento, ordenadas por timestamp
    (necessario pra detectar repeticao em sequencia)."""
    grupos = {}
    for leitura in leituras:
        equipamento_id = leitura.get("equipamento", "desconhecido")
        grupos.setdefault(equipamento_id, []).append(leitura)

    for equipamento_id in grupos:
        grupos[equipamento_id].sort(key=lambda l: l.get("timestamp") or 0)

    return grupos


def analisar_equipamento(equipamento_id, leituras_equipamento):
    """Aplica as regras a todas as leituras de um equipamento e devolve o
    resultado consolidado (score total, classificacao, motivos, alertas de
    seguranca)."""
    indices_repetidos = set(detectar_repeticoes(leituras_equipamento))

    score_total = 0
    motivos_totais = []
    alertas_seguranca = []

    for i, leitura in enumerate(leituras_equipamento):
        pontos, motivos = avaliar_leitura(leitura, e_repeticao=(i in indices_repetidos))
        score_total += pontos
        motivos_totais.extend(motivos)

        alertas_seguranca.extend(dados_invalidos(leitura))
        alertas_seguranca.extend(leitura_suspeita(leitura))

    return {
        "equipamento": equipamento_id,
        "leituras_analisadas": len(leituras_equipamento),
        "score": score_total,
        "nivel": classificar_score(score_total),
        "motivos": motivos_totais,
        "alertas_seguranca": sorted(set(alertas_seguranca)),
    }


def analisar_leituras(leituras):
    """Ponto de entrada do motor: recebe a lista bruta de leituras
    armazenadas e devolve uma lista de resultados, um por equipamento."""
    grupos = agrupar_por_equipamento(leituras)
    return [analisar_equipamento(eq_id, lts) for eq_id, lts in grupos.items()]
