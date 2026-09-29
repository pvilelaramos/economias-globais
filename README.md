# Economias globais

Painel comparativo das principais economias do mundo: **crescimento, inflação,
juros, desemprego, contas externas e contas públicas**, com dados do FMI e do
BIS e atualização automática todo mês.

🌐 **Painel interativo: [pvilelaramos.github.io/economias-globais](https://pvilelaramos.github.io/economias-globais/)**

## Visão geral

<!-- TABELA:INICIO -->
| País | PIB 2026 | PIB 2027 | Inflação 2026 | Desemprego | Conta corrente | Resultado fiscal | Dívida bruta | Juros | Inflação 12m | Juro real |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| EUA | 1,7 | 2,0 | 2,5 | 4,2 | -3,2 | -5,5 | 124 | 3,62 | 3,4 | 0,2 |
| Zona do Euro | 1,2 | 1,3 | 1,9 | 6,3 | 2,1 | -3,4 | 90 | 2,25 | 3,2 | -1,0 |
| Alemanha | 0,9 | 1,5 | 1,9 | 3,2 | 5,0 | -3,5 | 67 | 2,25 | 2,9 | -0,6 |
| Reino Unido | 1,4 | 1,5 | 2,2 | 4,4 | -3,7 | -3,7 | 105 | 3,75 | 3,1 | 0,6 |
| Japão | 0,6 | 0,6 | 1,7 | 2,6 | 3,3 | -3,1 | 234 | 1,00 | 1,9 | -0,9 |
| Canadá | 1,6 | 1,7 | 2,1 | 6,5 | -0,3 | -1,6 | 111 | 2,25 | 3,0 | -0,8 |
| Austrália | 2,1 | 2,3 | 3,5 | 4,5 | -3,4 | -1,6 | 51 | 4,35 | 3,9 | 0,4 |
| Coreia do Sul | 1,4 | 2,1 | 1,8 | 3,0 | 3,6 | -0,5 | 56 | 2,75 | 2,8 | -0,0 |
| China | 4,0 | 4,2 | 0,6 | 5,1 | 1,7 | -8,5 | 102 | 3,00 | 0,8 | 2,2 |
| Índia | 6,3 | 6,5 | 4,1 | 4,9 | -1,4 | -7,2 | 80 | 5,25 | 4,4 | 0,8 |
| **Brasil** | 2,0 | 2,2 | 4,3 | 7,3 | -2,2 | -7,7 | 96 | 14,00 | 4,2 | 9,4 |
| México | 1,4 | 2,1 | 3,2 | 3,8 | -1,1 | -3,3 | 61 | 6,50 | 3,3 | 3,1 |
| Chile | 2,2 | 2,3 | 3,2 | 8,1 | -2,4 | -1,1 | 43 | 4,50 | 4,1 | 0,4 |
| Argentina | 4,5 | 4,0 | 14,5 | 6,0 | -0,3 | 1,4 | 68 | 29,00 | 33,7 | -3,5 |

*Valores em %. PIB (variação real), inflação (média do ano) e desemprego: FMI (WEO); conta corrente, resultado fiscal e dívida em % do PIB. Juros e inflação 12m: BIS, último dado disponível (juros até 08/2026). Juro real = juros deflacionados pela inflação em 12 meses. Atualizado em 29/09/2026.*
<!-- TABELA:FIM -->

![Juros e inflação](figures/juros_inflacao.png)

<p>
  <img src="figures/crescimento.png" width="48%" alt="Crescimento do PIB">
  <img src="figures/fiscal.png" width="48%" alt="Dívida e resultado fiscal">
</p>

## Países

**Avançadas:** EUA, Zona do Euro, Alemanha, Reino Unido, Japão, Canadá, Austrália, Coreia do Sul
**Emergentes:** China, Índia, Brasil, México, Chile, Argentina

## Dados

| Indicador | Frequência | Fonte |
|---|---|---|
| Crescimento do PIB real, inflação média, desemprego | Anual, com projeções | FMI, *World Economic Outlook* (API DataMapper) |
| Conta corrente, resultado fiscal e dívida bruta (% do PIB) | Anual, com projeções | FMI, *World Economic Outlook* |
| PIB em US$ e PIB per capita em PPC | Anual, com projeções | FMI, *World Economic Outlook* |
| Taxa básica de juros | Mensal | BIS, *Central bank policy rates* |
| Inflação ao consumidor em 12 meses | Mensal | BIS, *Consumer prices* |

O FMI revisa as projeções duas vezes por ano (abril e outubro), e os dados
mensais do BIS chegam com defasagem de algumas semanas.

## Como rodar

```bash
pip install -r requirements.txt
python src/atualizar.py            # baixa tudo e atualiza gráficos, tabela e site
python src/atualizar.py --offline  # reusa os CSVs de data/processado
python -m pytest tests/
```

O GitHub Actions ([`.github/workflows/atualizar.yml`](.github/workflows/atualizar.yml))
roda o pipeline no dia 10 de cada mês.

## Estrutura

```
├── src/
│   ├── paises.py         # países e indicadores
│   ├── coleta.py         # APIs do FMI e do BIS
│   ├── graficos.py       # figuras do README
│   ├── tabela.py         # tabela comparativa
│   ├── exportar_site.py  # dados da página interativa
│   └── atualizar.py      # roda tudo
├── docs/                 # página interativa (GitHub Pages)
├── data/processado/
├── figures/
└── tests/
```

## Próximos passos

- Curvas de juros (10 anos) e taxas de câmbio
- Expectativas de inflação e metas dos bancos centrais
- Termos de troca e preços de commodities para os exportadores (Brasil, Chile, Austrália)

---

Pedro Vilela Ramos · Economia (IE/UFRJ)
