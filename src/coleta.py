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
# DBnomics espelha o WEO do FMI; é a reserva quando a API do FMI recusa o acesso
URL_DBNOMICS = "https://api.db.nomics.world/v22/series/IMF/{dataset}/{mascara}"
# No WEO, a Zona do Euro está no conjunto de agregados (código 163)
CODIGO_ZONA_EURO_WEO = "163"


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


def ler_dbnomics(json_: dict) -> pd.DataFrame:
    """Lê séries do WEO no DBnomics e devolve (pais, ano, indicador curto, valor)."""
    linhas = []
    for doc in json_.get("series", {}).get("docs", []):
        pais_cod, indicador = doc["series_code"].split(".")[:2]
        if pais_cod == CODIGO_ZONA_EURO_WEO:
            pais_cod = "EURO"
        if pais_cod not in NOME_POR_FMI or indicador not in INDICADORES_FMI:
            continue
        for periodo, valor in zip(doc["period"], doc["value"]):
            try:
                v = float(valor)
            except (TypeError, ValueError):
                continue
            linhas.append((NOME_POR_FMI[pais_cod], int(str(periodo)[:4]),
                           INDICADORES_FMI[indicador][0], v))
    return pd.DataFrame(linhas, columns=["pais", "ano", "indicador", "valor"])


def _fmi_datamapper() -> pd.DataFrame:
    codigos = "/".join(fmi for _, fmi, _, _ in PAISES)
    partes = []
    for indicador, (curto, _) in INDICADORES_FMI.items():
        print(f"FMI {indicador}...", flush=True)
        df = ler_fmi(_get(URL_FMI.format(indicador=indicador, paises=codigos),
                          tentativas=2).json(), indicador)
        partes.append(df.assign(indicador=curto))
    return pd.concat(partes, ignore_index=True)


def _fmi_dbnomics() -> pd.DataFrame:
    assuntos = "+".join(INDICADORES_FMI)
    paises = "+".join(fmi for _, fmi, _, _ in PAISES if fmi != "EURO")
    params = {"observations": 1, "limit": 1000, "format": "json"}
    print("DBnomics WEO (países)...", flush=True)
    partes = [ler_dbnomics(_get(URL_DBNOMICS.format(
        dataset="WEO:latest", mascara=f"{paises}.{assuntos}."), params).json())]
    try:
        print("DBnomics WEO (Zona do Euro)...", flush=True)
        partes.append(ler_dbnomics(_get(URL_DBNOMICS.format(
            dataset="WEOAGG:latest", mascara=f"{CODIGO_ZONA_EURO_WEO}.{assuntos}."), params).json()))
    except Exception as erro:  # noqa: BLE001
        print(f"  Zona do Euro indisponível no DBnomics: {erro}", flush=True)
    return pd.concat(partes, ignore_index=True)


def baixar_fmi() -> pd.DataFrame:
    """Tabela anual larga: uma linha por país-ano, uma coluna por indicador."""
    try:
        longo = _fmi_datamapper()
    except Exception as erro:  # noqa: BLE001
        print(f"API do FMI indisponível ({str(erro)[:100]}); usando DBnomics.", flush=True)
        longo = _fmi_dbnomics()
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
    # A Alemanha não tem juros próprios: usa a taxa do BCE (Zona do Euro)
    bce = juros[juros["pais"] == "Zona do Euro"].assign(pais="Alemanha")
    juros = pd.concat([juros[juros["pais"] != "Alemanha"], bce], ignore_index=True)
    print("BIS inflação ao consumidor...", flush=True)
    cpi = baixar_bis("WS_LONG_CPI", ".771").rename(columns={"valor": "inflacao_12m"})
    base = juros.merge(cpi, on=["pais", "data"], how="outer").sort_values(["pais", "data"])
    base["juro_real"] = ((1 + base["juros"] / 100) / (1 + base["inflacao_12m"] / 100) - 1) * 100
    return base.reset_index(drop=True)
