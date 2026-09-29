"""Roda o painel de ponta a ponta.

Uso:
    python src/atualizar.py            # baixa os dados (FMI e BIS)
    python src/atualizar.py --offline  # usa os CSVs de data/processado
"""
from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

import pandas as pd

import coleta
import graficos
from exportar_site import exportar
import tabela

RAIZ = Path(__file__).resolve().parents[1]
ANUAL = RAIZ / "data" / "processado" / "fmi_anual.csv"
MENSAL = RAIZ / "data" / "processado" / "bis_mensal.csv"


def carregar(offline: bool) -> tuple[pd.DataFrame, pd.DataFrame]:
    ANUAL.parent.mkdir(parents=True, exist_ok=True)
    if not offline:
        for nome, func, arq in (("BIS", coleta.baixar_mensal, MENSAL), ("FMI", coleta.baixar_fmi, ANUAL)):
            try:
                func().to_csv(arq, index=False, float_format="%.4f")
            except Exception as erro:  # noqa: BLE001
                if not arq.exists():
                    raise
                print(f"AVISO: coleta do {nome} falhou ({erro}); usando a última base salva.", flush=True)
    anual = pd.read_csv(ANUAL)
    mensal = pd.read_csv(MENSAL, parse_dates=["data"])
    return anual, mensal


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--offline", action="store_true")
    args = p.parse_args()
    anual, mensal = carregar(args.offline)
    ano = date.today().year

    fig = RAIZ / "figures"
    fig.mkdir(exist_ok=True)
    graficos.juros_inflacao(mensal, fig / "juros_inflacao.png")
    graficos.crescimento(anual, ano, fig / "crescimento.png")
    graficos.fiscal(anual, ano, fig / "fiscal.png")

    tabela.escrever_no_readme(RAIZ / "README.md", tabela.montar(anual, mensal, ano))

    exportar(anual, mensal, ano, RAIZ / "docs" / "dados.json")
    print(f"Pronto: {anual['pais'].nunique()} países (FMI), {mensal['pais'].nunique()} países (BIS).")


if __name__ == "__main__":
    main()
