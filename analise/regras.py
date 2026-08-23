"""Regras de risco aplicadas as leituras IoT. Cada regra que dispara soma
pontos ao score do equipamento."""

TEMPERATURA_ALTA_LIMITE = 35.0
UMIDADE_BAIXA_LIMITE = 30.0

PONTOS_TEMPERATURA_ALTA = 2
PONTOS_UMIDADE_BAIXA = 2
PONTOS_DADOS_INCOMPLETOS = 3
PONTOS_REPETICAO = 2


def verificar_temperatura_alta(leitura):
    """Regra: temperatura acima do limite -> +2."""
    temperatura = leitura.get("temperatura")
    return isinstance(temperatura, (int, float)) and temperatura > TEMPERATURA_ALTA_LIMITE


def verificar_umidade_baixa(leitura):
    """Regra: umidade abaixo do limite -> +2. Se a leitura nao tem o campo
    umidade, essa regra nao se aplica (isso cai na regra de dados
    incompletos, nao aqui)."""
    umidade = leitura.get("umidade")
    if umidade is None:
        return False
    return isinstance(umidade, (int, float)) and umidade < UMIDADE_BAIXA_LIMITE


def verificar_dados_incompletos(leitura):
    """Regra: campo obrigatorio ausente -> +3."""
    campos_esperados = ["equipamento", "temperatura", "umidade", "timestamp"]
    return any(campo not in leitura for campo in campos_esperados)


def detectar_repeticoes(leituras_equipamento):
    """Regra: leitura identica (mesma temperatura e umidade) repetida em
    sequencia para o mesmo equipamento -> +2 na leitura repetida.
    Recebe a lista de leituras JA ORDENADA por timestamp de um unico
    equipamento e devolve os indices das leituras que sao repeticao."""
    indices_repetidos = []
    for i in range(1, len(leituras_equipamento)):
        atual = leituras_equipamento[i]
        anterior = leituras_equipamento[i - 1]
        if (
            atual.get("temperatura") == anterior.get("temperatura")
            and atual.get("umidade") == anterior.get("umidade")
        ):
            indices_repetidos.append(i)
    return indices_repetidos


def avaliar_leitura(leitura, e_repeticao=False):
    """Aplica todas as regras numa leitura e devolve (pontos, motivos)."""
    pontos = 0
    motivos = []

    if verificar_temperatura_alta(leitura):
        pontos += PONTOS_TEMPERATURA_ALTA
        motivos.append(f"temperatura alta ({leitura.get('temperatura')} C) (+{PONTOS_TEMPERATURA_ALTA})")

    if verificar_umidade_baixa(leitura):
        pontos += PONTOS_UMIDADE_BAIXA
        motivos.append(f"umidade baixa ({leitura.get('umidade')}%) (+{PONTOS_UMIDADE_BAIXA})")

    if verificar_dados_incompletos(leitura):
        pontos += PONTOS_DADOS_INCOMPLETOS
        motivos.append(f"dados incompletos (+{PONTOS_DADOS_INCOMPLETOS})")

    if e_repeticao:
        pontos += PONTOS_REPETICAO
        motivos.append(f"leitura repetida (+{PONTOS_REPETICAO})")

    return pontos, motivos
