
import dash
import plotly.graph_objects as go
from dash import dcc, html, dash_table

from componentes import (
    cabecalho_pagina,
    card,
    conclusao,
    interpretacao,
)
import tema

dash.register_page(__name__, path="/modelos", name="Modelos", order=3)

# Resultados dos seis experimentos registrados no notebook PISI3_EDA.ipynb.
RESULTADOS = [
    {"Modelo": "Random Forest", "Balanceamento": "Sem SMOTE",
     "Acurácia": 0.773768, "F1 macro": 0.529654},
    {"Modelo": "Random Forest", "Balanceamento": "Com SMOTE",
     "Acurácia": 0.748792, "F1 macro": 0.527575},
    {"Modelo": "Regressão Logística", "Balanceamento": "Sem SMOTE",
     "Acurácia": 0.753248, "F1 macro": 0.286420},
    {"Modelo": "Regressão Logística", "Balanceamento": "Com SMOTE",
     "Acurácia": 0.529338, "F1 macro": 0.388797},
    {"Modelo": "KNN", "Balanceamento": "Sem SMOTE",
     "Acurácia": 0.746533, "F1 macro": 0.444413},
    {"Modelo": "KNN", "Balanceamento": "Com SMOTE",
     "Acurácia": 0.577471, "F1 macro": 0.441384},
]

# Gráfico comparativo: as duas métricas usam a mesma escala, de 0 a 1.
fig = go.Figure()

for metrica, cor in [
    ("Acurácia", tema.PRIMARIA),
    ("F1 macro", tema.SECUNDARIA),
]:
    fig.add_trace(
        go.Bar(
            name=metrica,
            x=[
                f"{r['Modelo']}<br>{r['Balanceamento']}"
                for r in RESULTADOS
            ],
            y=[r[metrica] for r in RESULTADOS],
            marker_color=cor,
            text=[f"{r[metrica]:.3f}" for r in RESULTADOS],
            textposition="outside",
            cliponaxis=False,
        )
    )

fig.update_layout(
    barmode="group",
    title="Acurácia e F1 macro por modelo",
    xaxis_title="Modelo e balanceamento",
    yaxis_title="Pontuação",
    yaxis=dict(range=[0, 0.9], tickformat=".0%"),
    legend_title="Métrica",
    margin=dict(b=100, t=70),
)

# Tabela com os valores completos.
tabela = dash_table.DataTable(
    data=[
        {
            **r,
            "Acurácia": f"{r['Acurácia']:.6f}",
            "F1 macro": f"{r['F1 macro']:.6f}",
        }
        for r in RESULTADOS
    ],
    columns=[
        {"name": "Modelo", "id": "Modelo"},
        {"name": "Balanceamento", "id": "Balanceamento"},
        {"name": "Acurácia", "id": "Acurácia"},
        {"name": "F1 macro", "id": "F1 macro"},
    ],
    sort_action="native",
    style_table={"overflowX": "auto"},
    style_header={
        "backgroundColor": tema.FUNDO,
        "color": tema.TEXTO,
        "fontWeight": "bold",
        "border": f"1px solid {tema.LINHAS}",
    },
    style_cell={
        "backgroundColor": tema.CARTAO,
        "color": tema.TEXTO,
        "padding": "10px",
        "textAlign": "left",
        "border": f"1px solid {tema.LINHAS}",
        "whiteSpace": "normal",
        "height": "auto",
    },
)

layout = html.Div(
    [
        cabecalho_pagina(
            "Dá para prever a permanência de um animal?",
            "Comparação entre Random Forest, Regressão Logística e KNN, "
            "com e sem SMOTE.",
        ),
        card("Comparação das métricas", dcc.Graph(figure=fig)),
        card("Resultados detalhados", tabela),
        interpretacao(
            "A acurácia mede a proporção total de previsões corretas, "
            "enquanto o F1 macro resume o desempenho entre as classes. "
            "Por isso, o F1 macro ajuda a comparar os modelos quando "
            "o desempenho entre classes pode ser desigual."
        ),
        conclusao(
            "A Random Forest apresentou o maior F1 macro nos dois cenários. "
            "O efeito do SMOTE variou entre os modelos: a Regressão Logística "
            "melhorou no F1 macro, enquanto a Random Forest e o KNN tiveram "
            "pequenas reduções nessa métrica."
        ),
    ]
)
