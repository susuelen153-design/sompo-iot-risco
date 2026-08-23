# Sistema de Risco IoT - Cognitive Cybersecurity

Disciplina: Cibersegurança Cognitiva - Challenge Sprint 3
Professor: Gilberto Vieira Branco

## O que é

Sistema completo de risco para dados IoT: gera leituras de sensores
(temperatura e umidade), envia para um servidor HTTP, valida e armazena
os dados, analisa aplicando regras de risco e mostra um resumo claro por
equipamento.

Fluxo: **IoT → Servidor → Dados → Análise → Resultado**

## Sobre o código das Sprints 1 e 2

O enunciado pede pra reaproveitar o código das Sprints 1 e 2 dessa
disciplina. Não tínhamos esse código disponível, então este projeto foi
construído do zero implementando o mesmo fluxo (geração de dados IoT,
envio para servidor, armazenamento, análise e alertas) que as Sprints 1 e
2 provavelmente já cobriam, agora integrado num sistema único.

## Estrutura do projeto

```
sompo-iot-risco/
├── main.py                # orquestra tudo: sobe servidor, gera+envia dados, analisa, mostra resultado
├── iot/
│   ├── gerador.py          # gera leituras simuladas (normais e com problemas propositais)
│   └── cliente.py           # envia as leituras pro servidor via HTTP POST
├── servidor/
│   └── app.py                # servidor Flask: valida e armazena as leituras (arquivo local, sem banco de dados)
├── analise/
│   ├── regras.py              # regras de risco (temperatura, umidade, dados incompletos, repetição)
│   ├── seguranca.py            # identificação de dados inválidos/suspeitos
│   └── motor.py                 # agrupa por equipamento, calcula score e classifica
├── saida/
│   └── relatorio.py               # resumo no console e exportação JSON/CSV
├── dados/                          # "banco" simples em arquivo (gerado em runtime)
└── output/                         # resultados exportados (gerado em runtime)
```

## Como rodar

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt

python main.py
```

Isso sobe o servidor local, gera 20 leituras simuladas (com alguns
problemas propositais misturados), envia tudo pro servidor, roda a
análise e mostra o resultado.

### Opções

```bash
# Gerar uma quantidade diferente de leituras normais
python main.py --quantidade 40

# Rodar sem injetar leituras problemáticas de propósito
python main.py --sem-problemas

# Manter os dados de uma rodada anterior em vez de limpar
python main.py --manter-dados
```

## Como gerar dados

Os dados são gerados automaticamente pelo `main.py` (via
`iot/gerador.py`), simulando sensores de temperatura e umidade em 5
equipamentos. Para garantir que o sistema seja testável, o gerador sempre
inclui, além das leituras normais: uma leitura de temperatura alta, uma
de umidade baixa, uma com dado incompleto e uma repetição proposital
(a menos que `--sem-problemas` seja usado).

## Como ver o resultado

O resumo aparece direto no console ao final da execução:

```
=== RESULTADO ===
trator_01 -> MEDIO (4)
sensor_02 -> MEDIO (3)
colheitadeira_01 -> BAIXO (2)
```

Os resultados completos também são exportados em
`output/resultado_risco.json` e `output/resultado_risco.csv`.

## Como funciona o score

Cada regra que dispara numa leitura soma pontos ao score do equipamento:

| Regra | Pontos |
|---|---|
| Temperatura acima de 35°C | +2 |
| Umidade abaixo de 30% | +2 |
| Dado incompleto (campo obrigatório ausente) | +3 |
| Leitura repetida em sequência (mesma temperatura e umidade) | +2 |

Classificação final:

| Score | Nível |
|---|---|
| 0-2 | BAIXO |
| 3-5 | MEDIO |
| 6+ | ALTO |

## Segurança

Ver o documento do projeto para a explicação completa. Resumo:

- **Dados inválidos** são barrados no próprio servidor (`servidor/app.py`),
  antes de serem armazenados: campos obrigatórios ausentes ou valores
  fora de uma faixa fisicamente plausível são rejeitados com HTTP 400.
- **Dados suspeitos** (mas não necessariamente inválidos) são sinalizados
  na análise (`analise/seguranca.py`): timestamp no futuro, ou atraso
  grande entre o horário da leitura e o horário em que o servidor
  recebeu, o que pode indicar replay de um dado antigo.
- Melhorias de segurança recomendadas para produção (não implementadas
  neste MVP acadêmico) também estão documentadas.
