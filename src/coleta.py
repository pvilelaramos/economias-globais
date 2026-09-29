"""Coleta de dados: FMI (World Economic Outlook) e BIS (juros e inflação mensais)."""
from __future__ import annotations

import io
import time

import pandas as pd
import requests

from paises import INDICADORES_FMI, NOME_POR_BIS, NOME_POR_FMI, PAISES

CABECALHOS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0 Safari/537.36",
}
URL_FMI = "https://www.imf.org/external/datamapper/api/v1/{indicador}/{paises}"
URL_BIS = "https://stats.bis.org/api/v1/data/{fluxo}/{chave}/all"


def _get(url: str, params: dict | None = None, tentativas: int = 6) -> requests.Response:
    for i in range(tentativas):
        try:
            r = requests.get(url, params=params, headers=CABECALHOS, timeout=90)
            r.raise_for_status()
            if r.text.lstrip().startswith("<"):
                raise ValueError("resposta em HTML/XML em vez de dados")
            return r
        except (requests.RequestException, ValueError) as erro:
            print(f"  tentativa {i + 1}/{tentativas} falhou: {str(erro)[:150]}", flush=True)
            if i == tentativas - 1:
                raise
            time.sleep(10 * (i + 1))
    raise RuntimeError("inalcançável")


# ------------------------------------------------------------------ FMI
def ler_fmi(json_: dict, indicador: str) -> pd.DataFrame:
    """Transforma a resposta do DataMapper em formato longo (país, ano, valor)."""
    linhas = []
    for codigo, serie in json_.get("values", {}).get(indicador, {}).items():
        if codigo not in NOME_POR_FMI:
            continue
        for ano, valor in serie.items():
            if valor is not None:
                linhas.append((NOME_POR_FMI[codigo], int(ano), float(valor)))
    return pd.DataFrame(linhas, columns=["pais", "ano", "valor"])


def baixar_fmi() -> pd.DataFrame:
    """Tabela anual larga: uma linha por país-ano, uma coluna por indicador."""
    codigos = "/".join(fmi for _, fmi, _, _ in PAISES)
    partes = []
    for indicador, (curto, _) in INDICADORES_FMI.items():
        print(f"FMI {indicador}...", flush=True)
        df = ler_fmi(_get(URL_FMI.format(indicador=indicador, paises=codigos)).json(), indicador)
        partes.append(df.assign(indicador=curto))
    longo = pd.concat(partes, ignore_index=True)
    return longo.pivot_table(index=["pais", "ano"], columns="indicador", values="valor").reset_index()


# ------------------------------------------------------------------ BIS
def ler_bis(texto_csv: str) -> pd.DataFrame:
    """Lê o CSV do BIS e devolve (pais, data, valor)."""
    df = pd.read_csv(io.StringIO(texto_csv))
    col = {c.upper(): c for c in df.columns}
    out = pd.DataFrame(
        {
            "pais": df[col["REF_AREA"]].map(NOME_POR_BIS),
            "data": pd.to_datetime(df[col["TIME_PERIOD"]].astype(str)),
            "valor": pd.to_numeric(df[col["OBS_VALUE"]], errors="coerce"),
        }
    )
    return out.dropna()


def baixar_bis(fluxo: str, sufixo: str = "") -> pd.DataFrame:
    areas = "+".join(bis for _, _, bis, _ in PAISES)
    chave = f"M.{areas}{sufixo}"
    r = _get(URL_BIS.format(fluxo=fluxo, chave=chave), {"format": "csv", "startPeriod": "2000-01"})
    return ler_bis(r.text)


def baixar_mensal() -> pd.DataFrame:
    """Juros de política (WS_CBPOL) e inflação em 12 meses (WS_LONG_CPI, unidade 771)."""
    print("BIS juros de política...", flush=True)
    juros = baixar_bis("WS_CBPOL").rename(columns={"valor": "juros"})
    print("BIS inflação ao consumidor...", flush=True)
    cpi = baixar_bis("WS_LONG_CPI", ".771").rename(columns={"valor": "inflacao_12m"})
    base = juros.merge(cpi, on=["pais", "data"], how="outer").sort_values(["pais", "data"])
    base["juro_real"] = ((1 + base["juros"] / 100) / (1 + base["inflacao_12m"] / 100) - 1) * 100
    return base.reset_index(drop=True)
