"""Países e indicadores do painel."""

# nome em português, código do FMI (DataMapper), código do BIS (ISO-2), grupo
PAISES = [
    ("EUA", "USA", "US", "Avançadas"),
    ("Zona do Euro", "EURO", "XM", "Avançadas"),
    ("Alemanha", "DEU", "DE", "Avançadas"),
    ("Reino Unido", "GBR", "GB", "Avançadas"),
    ("Japão", "JPN", "JP", "Avançadas"),
    ("Canadá", "CAN", "CA", "Avançadas"),
    ("Austrália", "AUS", "AU", "Avançadas"),
    ("Coreia do Sul", "KOR", "KR", "Avançadas"),
    ("China", "CHN", "CN", "Emergentes"),
    ("Índia", "IND", "IN", "Emergentes"),
    ("Brasil", "BRA", "BR", "Emergentes"),
    ("México", "MEX", "MX", "Emergentes"),
    ("Chile", "CHL", "CL", "Emergentes"),
    ("Argentina", "ARG", "AR", "Emergentes"),
]

NOME_POR_FMI = {fmi: nome for nome, fmi, _, _ in PAISES}
NOME_POR_BIS = {bis: nome for nome, _, bis, _ in PAISES}
GRUPO = {nome: grupo for nome, _, _, grupo in PAISES}
ORDEM = [nome for nome, *_ in PAISES]

# Indicadores anuais do World Economic Outlook (FMI), com projeções
INDICADORES_FMI = {
    "NGDP_RPCH": ("crescimento", "Crescimento do PIB real (%)"),
    "PCPIPCH": ("inflacao", "Inflação ao consumidor, média do ano (%)"),
    "LUR": ("desemprego", "Taxa de desemprego (%)"),
    "BCA_NGDPD": ("conta_corrente", "Saldo em conta corrente (% do PIB)"),
    "GGXCNL_NGDP": ("resultado_fiscal", "Resultado fiscal nominal (% do PIB)"),
    "GGXWDG_NGDP": ("divida", "Dívida bruta do governo (% do PIB)"),
    "PPPPC": ("pib_pc_ppc", "PIB per capita (US$ internacionais, PPC)"),
    "NGDPD": ("pib_usd", "PIB (US$ bilhões correntes)"),
}
ROTULO = {curto: rotulo for curto, rotulo in INDICADORES_FMI.values()}
ROTULO.update(
    {
        "juros": "Taxa básica de juros (% a.a.)",
        "inflacao_12m": "Inflação ao consumidor em 12 meses (%)",
        "juro_real": "Juro real ex-post (% a.a.)",
    }
)
