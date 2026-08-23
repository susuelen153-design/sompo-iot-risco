"""Geracao de saida organizada: resumo no console e exportacao JSON/CSV."""

import csv
import json
import os


def exibir_resumo(resultados):
    print("=== RESULTADO ===")
    for r in sorted(resultados, key=lambda x: x["score"], reverse=True):
        print(f"{r['equipamento']} -> {r['nivel']} ({r['score']})")

    print()
    print("=== ALERTAS DE SEGURANCA ===")
    algum_alerta = False
    for r in resultados:
        if r["alertas_seguranca"]:
            algum_alerta = True
            for alerta in r["alertas_seguranca"]:
                print(f"[{r['equipamento']}] {alerta}")
    if not algum_alerta:
        print("Nenhum dado invalido ou suspeito identificado nesta rodada.")

    print()
    print("=== DISTRIBUICAO POR NIVEL DE RISCO ===")
    contagem = {"BAIXO": 0, "MEDIO": 0, "ALTO": 0}
    for r in resultados:
        contagem[r["nivel"]] = contagem.get(r["nivel"], 0) + 1
    for nivel, quantidade in contagem.items():
        print(f"{nivel}: {quantidade}")


def exportar_json(resultados, caminho):
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as arquivo:
        json.dump(resultados, arquivo, ensure_ascii=False, indent=2)
    return caminho


def exportar_csv(resultados, caminho):
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, "w", newline="", encoding="utf-8") as arquivo:
        campos = ["equipamento", "leituras_analisadas", "score", "nivel"]
        escritor = csv.DictWriter(arquivo, fieldnames=campos, extrasaction="ignore")
        escritor.writeheader()
        for r in resultados:
            escritor.writerow(r)
    return caminho
