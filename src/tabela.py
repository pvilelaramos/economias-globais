"""Tabela comparativa, escrita dentro do README entre dois marcadores."""
from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd

from paises import ORDEM

INICIO = "<!-- TABELA:INICIO -->"
FIM = "<!-- TABELA:FIM -->"


def _f(v, casas: int = 1) -> str:
    if pd.isna(v):
        return "–"
    return f"{v:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def montar(anual: pd.DataFrame, mensal: pd.DataFrame, ano: int) -> str:
    a = anual[anual["ano"] == ano].set_index("pais")
    prox = anual[anual["ano"] == ano + 1].set_index("pais")
    ult = mensal.dropna(subset=["juros"]).groupby("pais").last()
    ult_cpi = mensal.dropna(subset=["inflacao_12m"]).groupby("pais").last()

    ref_juros = mensal.dropna(subset=["juros"])["data"].max()
    linhas = [
        f"| País | PIB {ano} | PIB {ano + 1} | Inflação {ano} | Desemprego | "
        f"Conta corrente | Resultado fiscal | Dívida bruta | Juros | Inflação 12m | Juro real |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for p in ORDEM:
        g = lambda df, c: df[c].get(p) if c in df.columns else None  # noqa: E731
        juros = g(ult, "juros")
        cpi = g(ult_cpi, "inflacao_12m")
        real = ((1 + juros / 100) / (1 + cpi / 100) - 1) * 100 if juros is not None and cpi is not None else None
        nome = f"**{p}**" if p == "Brasil" else p
        linhas.append(
            f"| {nome} | {_f(g(a, 'crescimento'))} | {_f(g(prox, 'crescimento'))} | "
            f"{_f(g(a, 'inflacao'))} | {_f(g(a, 'desemprego'))} | {_f(g(a, 'conta_corrente'))} | "
            f"{_f(g(a, 'resultado_fiscal'))} | {_f(g(a, 'divida'), 0)} | {_f(juros, 2)} | "
            f"{_f(cpi)} | {_f(real)} |"
        )
    nota = (
        f"\n*Valores em %. PIB (variação real), inflação (média do ano) e desemprego: FMI (WEO); "
        f"conta corrente, resultado fiscal e dívida em % do PIB. Juros e inflação 12m: BIS, "
        f"último dado disponível (juros até {ref_juros:%m/%Y}). Juro real = juros deflacionados "
        f"pela inflação em 12 meses. Atualizado em {date.today():%d/%m/%Y}.*"
    )
    return "\n".join(linhas) + "\n" + nota


def escrever_no_readme(readme: Path, tabela: str) -> None:
    texto = readme.read_text(encoding="utf-8")
    ini, fim = texto.index(INICIO) + len(INICIO), texto.index(FIM)
    readme.write_text(texto[:ini] + "\n" + tabela + "\n" + texto[fim:], encoding="utf-8")
