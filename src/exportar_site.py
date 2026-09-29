"""Exporta os dados para a página interativa (docs/dados.json)."""
from __future__ import annotations

import json
import math
from datetime import date
from pathlib import Path

import pandas as pd

from paises import GRUPO, INDICADORES_FMI, ORDEM, ROTULO


def _limpa(v):
    return None if v is None or (isinstance(v, float) and math.isnan(v)) else round(float(v), 3)


def exportar(anual: pd.DataFrame, mensal: pd.DataFrame, ano_atual: int, destino: Path) -> None:
    dados = {
        "atualizado": date.today().isoformat(),
        "ano_atual": ano_atual,
        "paises": [{"nome": p, "grupo": GRUPO[p]} for p in ORDEM],
        "rotulos": ROTULO,
        "anual": {},
        "mensal": {},
    }
    for curto, _ in INDICADORES_FMI.values():
        if curto not in anual.columns:
            continue
        bloco = {}
        for pais, g in anual[["pais", "ano", curto]].dropna().groupby("pais"):
            bloco[pais] = [[int(a), _limpa(v)] for a, v in zip(g["ano"], g[curto])]
        dados["anual"][curto] = bloco
    for serie in ("juros", "inflacao_12m", "juro_real"):
        bloco = {}
        for pais, g in mensal[["pais", "data", serie]].dropna().groupby("pais"):
            bloco[pais] = [[d.strftime("%Y-%m"), _limpa(v)] for d, v in zip(g["data"], g[serie])]
        dados["mensal"][serie] = bloco
    destino.write_text(json.dumps(dados, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
