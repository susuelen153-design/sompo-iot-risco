"""Verificacoes de seguranca sobre os dados armazenados: identifica dados
invalidos e leituras suspeitas, alem do que ja e barrado no servidor."""

import time

TEMPERATURA_MIN, TEMPERATURA_MAX = -30.0, 80.0
UMIDADE_MIN, UMIDADE_MAX = 0.0, 100.0
ATRASO_SUSPEITO_SEGUNDOS = 3600  # mais de 1h entre a leitura e o recebimento


def dados_invalidos(leitura):
    """Confere de novo, na camada de analise, os limites fisicos dos
    valores (defesa em profundidade: mesmo que algo passe pelo servidor,
    a analise nao usa um dado impossivel para calcular risco)."""
    motivos = []

    temperatura = leitura.get("temperatura")
    if temperatura is not None and not (TEMPERATURA_MIN <= temperatura <= TEMPERATURA_MAX):
        motivos.append("temperatura fora da faixa fisica plausivel")

    umidade = leitura.get("umidade")
    if umidade is not None and not (UMIDADE_MIN <= umidade <= UMIDADE_MAX):
        motivos.append("umidade fora da faixa fisica plausivel")

    return motivos


def leitura_suspeita(leitura):
    """Sinaliza leituras que nao sao necessariamente invalidas, mas tem
    caracteristicas suspeitas: timestamp no futuro, ou atraso grande entre
    a hora da leitura no dispositivo e a hora em que o servidor recebeu
    (indicio de replay de um dado antigo ou relogio do sensor adulterado)."""
    motivos = []
    agora = time.time()

    timestamp = leitura.get("timestamp")
    recebido_em = leitura.get("recebido_em")

    if isinstance(timestamp, (int, float)) and timestamp > agora + 60:
        motivos.append("timestamp no futuro")

    if isinstance(timestamp, (int, float)) and isinstance(recebido_em, (int, float)):
        atraso = recebido_em - timestamp
        if atraso > ATRASO_SUSPEITO_SEGUNDOS:
            motivos.append("atraso grande entre leitura e recebimento (possivel replay)")

    return motivos
