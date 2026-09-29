"""Testes dos leitores com respostas no formato das APIs do FMI e do BIS.

Rodar com:  python -m pytest tests/
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import coleta  # noqa: E402
import tabela  # noqa: E402


def test_ler_fmi():
    resposta = {
        "values": {
            "NGDP_RPCH": {
                "BRA": {"2024": 3.4, "2025": 2.3},
                "USA": {"2025": 1.9},
                "WEOWORLD": {"2025": 3.0},  # agregado fora da lista: ignorado
            }
        },
        "api": {"version": "1"},
    }
    df = coleta.ler_fmi(resposta, "NGDP_RPCH")
    assert set(df["pais"]) == {"Brasil", "EUA"}
    assert df.loc[(df.pais == "Brasil") & (df.ano == 2025), "valor"].item() == 2.3


def test_ler_bis():
    csv = (
        "FREQ,REF_AREA,TIME_PERIOD,OBS_VALUE\n"
        "M,BR,2025-01,12.25\n"
        "M,BR,2025-02,13.25\n"
        "M,XM,2025-02,2.9\n"
        "M,ZZ,2025-02,1.0\n"
    )
    df = coleta.ler_bis(csv)
    assert set(df["pais"]) == {"Brasil", "Zona do Euro"}
    assert df[df.pais == "Brasil"]["valor"].tolist() == [12.25, 13.25]


def test_tabela_no_readme(tmp_path):
    readme = tmp_path / "README.md"
    readme.write_text(f"antes\n{tabela.INICIO}\nvelho\n{tabela.FIM}\ndepois\n", encoding="utf-8")
    anual = pd.DataFrame({"pais": ["Brasil", "Brasil"], "ano": [2026, 2027], "crescimento": [2.0, 2.2]})
    mensal = pd.DataFrame({"pais": ["Brasil"], "data": pd.to_datetime(["2026-08-01"]),
                           "juros": [14.0], "inflacao_12m": [4.5]})
    tabela.escrever_no_readme(readme, tabela.montar(anual, mensal, 2026))
    texto = readme.read_text(encoding="utf-8")
    assert "velho" not in texto and "antes" in texto and "depois" in texto
    assert "| **Brasil** | 2,0 | 2,2 |" in texto


def test_ler_dbnomics():
    resposta = {"series": {"docs": [
        {"series_code": "BRA.NGDP_RPCH.pcent_change", "period": ["2025", "2026"], "value": [2.3, "NA"]},
        {"series_code": "163.GGXWDG_NGDP.pcent_gdp", "period": ["2025"], "value": [88.0]},
        {"series_code": "BRA.XXXX.units", "period": ["2025"], "value": [1.0]},
    ]}}
    df = coleta.ler_dbnomics(resposta)
    assert len(df) == 2
    assert df[df.pais == "Zona do Euro"]["indicador"].item() == "divida"
