from pathlib import Path

import dash
import pandas as pd
import plotly.graph_objects as go
from dash import Input, Output, callback, dcc, html, dash_table

from componentes import (
    cabecalho_pagina,
    card,
    conclusao,
    interpretacao,
)
import tema

dash.register_page(__name__, path="/modelos", name="Modelos", order=3)

BASE_DIR = Path(__file__).resolve().parents[1]
RESULTADOS_PATH = BASE_DIR / "data" / "resultados_modelos.csv"

# [BINÁRIO] Curta = até 14 dias | Prolongada = mais de 14 dias.
# Os resultados dos modelos clássicos vêm do arquivo data/resultados_modelos.csv,
# gerado pela última célula do notebook (seção 15). Os experimentos extras abaixo
# foram copiados das saídas do notebook binário (seções 10 a 14), arredondados.
NOMES_PT = {
    "Logistic Regression": "Regressão Logística",
    "Random Forest (regularizada)": "Random Forest regularizada",
}
ESTRATEGIA_PT = {
    "class_weight": "Pesos por classe",
}

EXPERIMENTOS_EXTRAS = [
    {"Experimento": "EXP-01", "Modelo": "RF Regressor", "Estratégia": "Prevê os dias e corta em 14",
     "Acurácia": 0.65, "F1 macro": 0.62, "F1 Prolongada": 0.51, "Recall Prolongada": 0.74},
    {"Experimento": "EXP-02", "Modelo": "XGBoost", "Estratégia": "Dados originais",
     "Acurácia": 0.79, "F1 macro": 0.64, "F1 Prolongada": 0.41, "Recall Prolongada": 0.30},
    {"Experimento": "EXP-03", "Modelo": "XGBoost", "Estratégia": "Pesos por classe",
     "Acurácia": 0.70, "F1 macro": 0.65, "F1 Prolongada": 0.52, "Recall Prolongada": 0.66},
    {"Experimento": "EXP-04", "Modelo": "XGBoost", "Estratégia": "Pesos + raça e pelagem",
     "Acurácia": 0.71, "F1 macro": 0.66, "F1 Prolongada": 0.54, "Recall Prolongada": 0.68},
]

METRICAS = ["Acurácia", "F1 macro", "F1 Prolongada", "Recall Prolongada"]


def carregar_resultados():
    """Lê a tabela exportada pelo notebook e padroniza nomes e colunas."""
    if not RESULTADOS_PATH.exists():
        return None
    try:
        df = pd.read_csv(RESULTADOS_PATH, encoding="utf-8-sig")
    except Exception:
        return None

    obrigatorias = {"Modelo", "Balanceamento", "Test Accuracy", "Test Macro F1",
                    "Test F1 Prolongada", "Test Recall Prolongada", "Train Macro F1"}
    if not obrigatorias.issubset(df.columns):
        return None

    linhas = []
    for _, r in df.iterrows():
        linhas.append({
            "Experimento": "Clássicos",
            "Modelo": NOMES_PT.get(r["Modelo"], r["Modelo"]),
            "Estratégia": ESTRATEGIA_PT.get(r["Balanceamento"], r["Balanceamento"]),
            "Acurácia": float(r["Test Accuracy"]),
            "F1 macro": float(r["Test Macro F1"]),
            "F1 Prolongada": float(r["Test F1 Prolongada"]),
            "Recall Prolongada": float(r["Test Recall Prolongada"]),
            "F1 macro treino": float(r["Train Macro F1"]),
        })
    return linhas


CLASSICOS = carregar_resultados()
RESULTADOS = (CLASSICOS or []) + EXPERIMENTOS_EXTRAS


def _rotulo(r):
    return f"{r['Experimento']} — {r['Modelo']}<br>{r['Estratégia']}"


def criar_grafico(metrica):
    validos = [r for r in RESULTADOS if r.get(metrica) is not None]
    fig = go.Figure(
        go.Bar(
            x=[r[metrica] for r in validos],
            y=[_rotulo(r) for r in validos],
            orientation="h",
            marker_color=tema.PRIMARIA,
            text=[f"{r[metrica]:.3f}" for r in validos],
            textposition="outside",
            cliponaxis=False,
            hovertemplate="%{y}<br>" + metrica + ": %{x:.3f}<extra></extra>",
        )
    )
    fig.update_layout(
        title=f"{metrica} no conjunto de teste",
        xaxis_title="Pontuação",
        yaxis_title="",
        xaxis=dict(range=[0, 1.0], tickformat=".0%", gridcolor=tema.LINHAS),
        yaxis=dict(autorange="reversed", automargin=True),
        showlegend=False,
        height=max(420, 48 * len(validos)),
        margin=dict(l=20, r=65, t=65, b=45),
    )
    return fig


def criar_grafico_overfitting():
    """F1 macro no treino x no teste: quanto maior a distância, mais o modelo decorou o treino."""
    if not CLASSICOS:
        return go.Figure()
    rotulos = [_rotulo(r) for r in CLASSICOS]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=rotulos, x=[r["F1 macro treino"] for r in CLASSICOS], orientation="h",
        name="Treino", marker_color=tema.SECUNDARIA,
        hovertemplate="%{y}<br>Treino: %{x:.3f}<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        y=rotulos, x=[r["F1 macro"] for r in CLASSICOS], orientation="h",
        name="Teste", marker_color=tema.PRIMARIA,
        hovertemplate="%{y}<br>Teste: %{x:.3f}<extra></extra>",
    ))
    fig.update_layout(
        title="F1 macro: treino x teste (diferença grande = overfitting)",
        barmode="group",
        xaxis=dict(range=[0, 1.0], tickformat=".0%", gridcolor=tema.LINHAS),
        yaxis=dict(autorange="reversed", automargin=True),
        height=max(420, 60 * len(CLASSICOS)),
        margin=dict(l=20, r=30, t=65, b=45),
        legend=dict(orientation="h", y=1.08, x=0),
    )
    return fig


def _fmt(v, casas=3):
    return f"{v:.{casas}f}" if v is not None else "—"


tabela = dash_table.DataTable(
    data=[
        {
            "Experimento": r["Experimento"],
            "Modelo": r["Modelo"],
            "Estratégia": r["Estratégia"],
            "Acurácia": _fmt(r.get("Acurácia")),
            "F1 macro": _fmt(r.get("F1 macro")),
            "F1 Prolongada": _fmt(r.get("F1 Prolongada")),
            "Recall Prolongada": _fmt(r.get("Recall Prolongada")),
            "F1 macro treino": _fmt(r.get("F1 macro treino")),
        }
        for r in RESULTADOS
    ],
    columns=[{"name": c, "id": c} for c in
             ["Experimento", "Modelo", "Estratégia", "Acurácia", "F1 macro",
              "F1 Prolongada", "Recall Prolongada", "F1 macro treino"]],
    sort_action="native",
    filter_action="native",
    page_size=15,
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
        "minWidth": "100px",
    },
)

aviso_csv = (
    []
    if CLASSICOS
    else [html.Div(
        "Resultados dos modelos clássicos não encontrados. Rode o notebook até a seção 15 "
        "e copie resultados_modelos.csv para a pasta Dashboard/data.",
        className="a-fazer",
    )]
)

layout = html.Div(
    [
        cabecalho_pagina(
            "Dá para prever se um animal vai ficar mais de 14 dias?",
            "Comparação dos modelos para as classes Curta (até 14 dias) "
            "e Prolongada (mais de 14 dias).",
        ),

        *aviso_csv,

        card(
            "Comparação das métricas",
            html.Div(
                [
                    html.Label("Métrica exibida no gráfico"),
                    dcc.Dropdown(
                        id="modelos-metrica",
                        options=[{"label": m, "value": m} for m in METRICAS],
                        value="F1 macro",
                        clearable=False,
                        style={"color": "#222"},
                    ),
                    dcc.Graph(id="modelos-grafico", figure=criar_grafico("F1 macro")),
                ]
            ),
        ),

        card("Resultados detalhados", tabela),

        interpretacao(
            "Cerca de 75% dos animais saem em até 14 dias, então um modelo que sempre "
            "responde 'Curta' já acerta 75% — por isso a acurácia sozinha engana. "
            "O F1 macro dá o mesmo peso às duas classes, e o F1 e o recall da classe "
            "Prolongada mostram o quanto o modelo encontra os animais que vão ficar mais "
            "tempo, que são os que o abrigo precisa priorizar."
        ),

        card(
            "Treino x teste",
            html.Div(
                [
                    dcc.Graph(figure=criar_grafico_overfitting()),
                    html.P(
                        "A Random Forest sem limite de profundidade quase decora o treino e "
                        "perde desempenho no teste. A versão regularizada (profundidade e "
                        "tamanho mínimo das folhas limitados) aproxima as duas barras, o "
                        "que indica um modelo que generaliza melhor para animais novos."
                    ),
                ]
            ),
        ),

        card(
            "Modelo final",
            html.Div(
                [
                    html.P(
                        "O modelo usado na página 'Teste agora' é a Random Forest regularizada "
                        "com pesos por classe (100 árvores, profundidade máxima 20 e pelo menos "
                        "5 animais por folha). O limiar de decisão de 0,51 foi escolhido por "
                        "validação cruzada só no treino, para maximizar o F1 da classe Prolongada."
                    ),
                    html.P(
                        "No conjunto de teste (15.935 animais): acurácia de 0,722, F1 macro de "
                        "0,666, ROC-AUC de 0,775 e, na classe Prolongada, recall de 0,63 e "
                        "precisão de 0,45. Ou seja, o modelo encontra cerca de 6 em cada 10 "
                        "animais que vão passar de 14 dias, mas, de cada 10 animais que ele "
                        "marca como Prolongada, só 4 a 5 realmente passam. Ele serve para "
                        "priorizar atenção, não como certeza."
                    ),
                ]
            ),
        ),

        card(
            "3 classes x 2 classes",
            html.Div(
                [
                    html.P(
                        "Para checar se juntar Média e Longa melhorou a previsão, o notebook "
                        "treinou o modelo antigo de 3 classes no mesmo treino, juntou as "
                        "previsões Média + Longa e comparou com o modelo de 2 classes na mesma "
                        "pergunta (o animal passa de 14 dias?). O ROC-AUC ficou praticamente "
                        "igual: 0,769 com 3 classes e 0,767 com 2 classes."
                    ),
                    html.P(
                        "A capacidade de separar os animais é a mesma. O ganho da mudança está "
                        "na clareza: uma pergunta direta e útil para o abrigo, com métricas mais "
                        "fáceis de interpretar."
                    ),
                ]
            ),
        ),

        card(
            "Outros experimentos",
            html.Div(
                [
                    html.H4("EXP-01 — Regressão"),
                    html.P(
                        "Em vez de classificar, um Random Forest Regressor prevê o número "
                        "de dias, e a previsão é cortada em 14 dias. Ele encontra bem os "
                        "animais de permanência prolongada (recall de 0,74), mas erra muitos "
                        "da classe Curta."
                    ),
                    html.H4("EXP-02 — XGBoost de referência"),
                    html.P(
                        "Sem balanceamento, o XGBoost tem a maior acurácia (0,79), mas "
                        "reconhece só 30% dos animais de permanência prolongada."
                    ),
                    html.H4("EXP-03 — Pesos por classe"),
                    html.P(
                        "Dar mais peso à classe Prolongada troca um pouco de acurácia por "
                        "um recall bem maior na classe Prolongada (0,66)."
                    ),
                    html.H4("EXP-04 — Engenharia de características"),
                    html.P(
                        "Foram adicionadas is_mix (raça mista/SRD), is_black_or_dark "
                        "(pelagem escura, para investigar o Black Dog Syndrome) e "
                        "simplified_breed (dez raças mais comuns). O ganho foi pequeno "
                        "(F1 macro de 0,65 para 0,66). Essas variáveis são hipóteses a "
                        "investigar, não evidência de que raça ou pelagem causem a "
                        "permanência."
                    ),
                ]
            ),
        ),

        conclusao(
            "Com as classes Curta e Prolongada, os melhores modelos ficam com F1 macro em torno "
            "de 0,65 a 0,68 e conseguem identificar boa parte dos animais que vão passar "
            "de 14 dias. Ainda assim, o desempenho tem um limite: só com os dados de "
            "entrada não dá para saber tudo o que decide uma adoção, como divulgação, "
            "feiras e o interesse dos visitantes."
        ),
    ]
)


@callback(
    Output("modelos-grafico", "figure"),
    Input("modelos-metrica", "value"),
)
def atualizar_grafico(metrica):
    return criar_grafico(metrica)
