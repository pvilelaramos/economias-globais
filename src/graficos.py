"""Gráficos estáticos para o README."""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from paises import ORDEM

AZUL, LARANJA = "#2a78d6", "#eb6834"
CINZA = "#b9b7ae"
TEXTO, TEXTO_2, GRADE, SUPERFICIE = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
DESTAQUE = "Brasil"

plt.rcParams.update(
    {
        "figure.facecolor": SUPERFICIE,
        "axes.facecolor": SUPERFICIE,
        "axes.edgecolor": GRADE,
        "axes.titlecolor": TEXTO,
        "axes.titleweight": "bold",
        "axes.titlelocation": "left",
        "axes.grid": True,
        "axes.grid.axis": "y",
        "grid.color": GRADE,
        "grid.linewidth": 0.8,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.spines.left": False,
        "xtick.color": TEXTO_2,
        "ytick.color": TEXTO_2,
        "font.size": 10,
        "legend.frameon": False,
        "lines.linewidth": 1.8,
    }
)

FONTE = "Elaboração: Pedro Vilela Ramos."


def juros_inflacao(mensal: pd.DataFrame, destino: Path, inicio: str = "2015-01") -> None:
    """Pequenos múltiplos: juros de política e inflação em 12 meses por país."""
    d = mensal[mensal["data"] >= inicio]
    paises = [p for p in ORDEM if p in set(d["pais"])]
    ncol = 4
    nlin = -(-len(paises) // ncol)
    fig, eixos = plt.subplots(nlin, ncol, figsize=(15, 3.1 * nlin), constrained_layout=True)
    eixos = eixos.ravel()
    for ax, pais in zip(eixos, paises):
        s = d[d["pais"] == pais].set_index("data")
        ax.plot(s.index, s["inflacao_12m"], color=LARANJA, label="Inflação 12 meses")
        ax.plot(s.index, s["juros"], color=AZUL, label="Taxa básica de juros")
        ax.axhline(0, color=TEXTO_2, lw=0.8)
        ax.set_title(pais, fontsize=11)
        ax.tick_params(labelsize=8)
        ultimos = {c: s[c].dropna() for c in ("juros", "inflacao_12m")}
        ultimos = {c: v for c, v in ultimos.items() if len(v)}
        # Afasta os rótulos quando os dois últimos valores estão próximos
        desloc = {c: 0 for c in ultimos}
        if len(ultimos) == 2:
            j, i = ultimos["juros"].iloc[-1], ultimos["inflacao_12m"].iloc[-1]
            faixa = max(s[["juros", "inflacao_12m"]].max().max() - s[["juros", "inflacao_12m"]].min().min(), 1e-9)
            if abs(j - i) / faixa < 0.08:
                desloc = {"juros": 6 if j >= i else -6, "inflacao_12m": -6 if j >= i else 6}
        for col, v in ultimos.items():
            ax.annotate(f"{v.iloc[-1]:.1f}", (v.index[-1], v.iloc[-1]), xytext=(4, desloc[col]),
                        textcoords="offset points", fontsize=8, color=TEXTO, va="center")
    for ax in eixos[len(paises):]:
        ax.set_visible(False)
    alcas, rotulos = eixos[0].get_legend_handles_labels()
    fig.legend(alcas, rotulos, loc="upper right", ncols=2, fontsize=10)
    fig.suptitle("Juros e inflação nas principais economias (%)", x=0.01, ha="left",
                 fontsize=15, fontweight="bold", color=TEXTO)
    fig.text(0.01, -0.01, f"Fonte: BIS. Escalas diferentes por país. {FONTE}",
             fontsize=8, color=TEXTO_2)
    fig.savefig(destino, dpi=130, bbox_inches="tight")
    plt.close(fig)


def crescimento(anual: pd.DataFrame, ano: int, destino: Path) -> None:
    """Barras horizontais do crescimento do PIB no ano, com o Brasil em destaque."""
    d = anual[anual["ano"] == ano][["pais", "crescimento"]].dropna()
    d = d.sort_values("crescimento")
    cores = [AZUL if p == DESTAQUE else CINZA for p in d["pais"]]
    fig, ax = plt.subplots(figsize=(8, 0.42 * len(d) + 1.4), constrained_layout=True)
    ax.barh(d["pais"], d["crescimento"], color=cores, height=0.7)
    ax.axvline(0, color=TEXTO_2, lw=1)
    ax.grid(axis="y", visible=False)
    ax.grid(axis="x", visible=True)
    for y, v in enumerate(d["crescimento"]):
        ax.annotate(f"{v:.1f}", (v, y), xytext=(4 if v >= 0 else -4, 0), textcoords="offset points",
                    ha="left" if v >= 0 else "right", va="center", fontsize=9, color=TEXTO)
    ax.set_title(f"Crescimento do PIB real em {ano} (%)", fontsize=13)
    ax.tick_params(axis="y", length=0)
    fig.text(0.01, -0.02, f"Fonte: FMI, World Economic Outlook (estimativas e projeções). {FONTE}",
             fontsize=8, color=TEXTO_2)
    fig.savefig(destino, dpi=130, bbox_inches="tight")
    plt.close(fig)


def fiscal(anual: pd.DataFrame, ano: int, destino: Path) -> None:
    """Dispersão: dívida bruta x resultado fiscal."""
    d = anual[anual["ano"] == ano][["pais", "divida", "resultado_fiscal"]].dropna()
    fig, ax = plt.subplots(figsize=(9, 6), constrained_layout=True)
    ax.grid(axis="x", visible=True)
    for _, r in d.iterrows():
        cor = AZUL if r["pais"] == DESTAQUE else CINZA
        ax.scatter(r["divida"], r["resultado_fiscal"], s=70, color=cor,
                   edgecolor=SUPERFICIE, linewidth=2, zorder=3)
        ax.annotate(r["pais"], (r["divida"], r["resultado_fiscal"]), xytext=(6, 4),
                    textcoords="offset points", fontsize=9, color=TEXTO)
    ax.axhline(0, color=TEXTO_2, lw=1)
    ax.set_xlabel("Dívida bruta do governo (% do PIB)", color=TEXTO_2)
    ax.set_ylabel("Resultado fiscal nominal (% do PIB)", color=TEXTO_2)
    ax.set_title(f"Dívida e resultado fiscal em {ano}", fontsize=13)
    fig.text(0.01, -0.02, f"Fonte: FMI, World Economic Outlook. {FONTE}", fontsize=8, color=TEXTO_2)
    fig.savefig(destino, dpi=130, bbox_inches="tight")
    plt.close(fig)
