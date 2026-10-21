
import dash
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


# Resultados iniciais e novos experimentos.
# None representa uma métrica que não foi informada.
RESULTADOS = [
    {
        "Experimento": "Inicial",
        "Modelo": "Random Forest",
        "Estratégia": "Sem SMOTE",
        "Acurácia": 0.773768,
        "F1 macro": 0.529654,
        "F1 ponderado": None,
    },
    {
        "Experimento": "Inicial",
        "Modelo": "Random Forest",
        "Estratégia": "Com SMOTE",
        "Acurácia": 0.749168,
        "F1 macro": 0.528638,
        "F1 ponderado": None,
    },
    {
        "Experimento": "Inicial",
        "Modelo": "Regressão Logística",
        "Estratégia": "Sem SMOTE",
        "Acurácia": 0.753248,
        "F1 macro": 0.286420,
        "F1 ponderado": None,
    },
    {
        "Experimento": "Inicial",
        "Modelo": "Regressão Logística",
        "Estratégia": "Com SMOTE",
        "Acurácia": 0.529338,
        "F1 macro": 0.388797,
        "F1 ponderado": None,
    },
    {
        "Experimento": "Inicial",
        "Modelo": "KNN",
        "Estratégia": "Sem SMOTE",
        "Acurácia": 0.746533,
        "F1 macro": 0.444413,
        "F1 ponderado": None,
    },
    {
        "Experimento": "Inicial",
        "Modelo": "KNN",
        "Estratégia": "Com SMOTE",
        "Acurácia": 0.577471,
        "F1 macro": 0.441384,
        "F1 ponderado": None,
    },
    {
        "Experimento": "EXP-01",
        "Modelo": "Regressão",
        "Estratégia": "Faixas revisadas",
        "Acurácia": 0.48,
        "F1 macro": 0.47,
        "F1 ponderado": 0.50,
    },
    {
        "Experimento": "EXP-02",
        "Modelo": "XGBoost",
        "Estratégia": "Dados originais",
        "Acurácia": 0.65,
        "F1 macro": 0.49,
        "F1 ponderado": 0.60,
    },
    {
        "Experimento": "EXP-03",
        "Modelo": "XGBoost",
        "Estratégia": "Pesos por classe",
        "Acurácia": 0.56,
        "F1 macro": 0.52,
        "F1 ponderado": 0.58,
    },
    {
        "Experimento": "EXP-04",
        "Modelo": "XGBoost",
        "Estratégia": "Pesos + novas características",
        "Acurácia": 0.57,
        "F1 macro": 0.53,
        "F1 ponderado": 0.59,
    },
]


def criar_grafico(metrica):
    resultados_validos = [
        r for r in RESULTADOS
        if r[metrica] is not None
    ]

    rotulos = [
        f"{r['Experimento']} — {r['Modelo']}<br>{r['Estratégia']}"
        for r in resultados_validos
    ]

    valores = [
        r[metrica] for r in resultados_validos
    ]

    fig = go.Figure(
        go.Bar(
            x=valores,
            y=rotulos,
            orientation="h",
            marker_color=tema.PRIMARIA,
            text=[f"{valor:.3f}" for valor in valores],
            textposition="outside",
            cliponaxis=False,
            hovertemplate=(
                "%{y}<br>"
                + metrica
                + ": %{x:.3f}<extra></extra>"
            ),
        )
    )

    fig.update_layout(
        title=f"{metrica} por experimento",
        xaxis_title="Pontuação",
        yaxis_title="",
        xaxis=dict(
            range=[0, 0.9],
            tickformat=".0%",
            gridcolor=tema.LINHAS,
        ),
        yaxis=dict(
            autorange="reversed",
            automargin=True,
        ),
        showlegend=False,
        height=650,
        margin=dict(l=20, r=65, t=65, b=45),
    )

    return fig


tabela = dash_table.DataTable(
    data=[
        {
            **r,
            "Acurácia": (
                f"{r['Acurácia']:.6f}"
                if r["Acurácia"] is not None else "—"
            ),
            "F1 macro": (
                f"{r['F1 macro']:.6f}"
                if r["F1 macro"] is not None else "—"
            ),
            "F1 ponderado": (
                f"{r['F1 ponderado']:.3f}"
                if r["F1 ponderado"] is not None else "—"
            ),
        }
        for r in RESULTADOS
    ],
    columns=[
        {"name": "Experimento", "id": "Experimento"},
        {"name": "Modelo", "id": "Modelo"},
        {"name": "Estratégia", "id": "Estratégia"},
        {"name": "Acurácia", "id": "Acurácia"},
        {"name": "F1 macro", "id": "F1 macro"},
        {"name": "F1 ponderado", "id": "F1 ponderado"},
    ],
    sort_action="native",
    filter_action="native",
    page_size=10,
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


layout = html.Div(
    [
        cabecalho_pagina(
            "Dá para prever a permanência de um animal?",
            "Comparação dos modelos iniciais e dos experimentos "
            "com novas estratégias de treinamento e características.",
        ),

        card(
            "Comparação das métricas",
            html.Div(
                [
                    html.Label("Métrica exibida no gráfico"),
                    dcc.Dropdown(
                        id="modelos-metrica",
                        options=[
                            {"label": "Acurácia", "value": "Acurácia"},
                            {"label": "F1 macro", "value": "F1 macro"},
                            {
                                "label": "F1 ponderado",
                                "value": "F1 ponderado",
                            },
                        ],
                        value="F1 macro",
                        clearable=False,
                        style={"color": "#222"},
                    ),
                    dcc.Graph(
                        id="modelos-grafico",
                        figure=criar_grafico("F1 macro"),
                    ),
                ]
            ),
        ),

        card("Resultados detalhados", tabela),

        interpretacao(
            "A acurácia mede a proporção total de previsões corretas. "
            "O F1 macro calcula a média do F1 entre as classes, atribuindo "
            "o mesmo peso a cada uma. O F1 ponderado considera a frequência "
            "das classes. Por isso, as métricas complementam-se na análise "
            "do desempenho. Os resultados dos novos experimentos foram "
            "informados com arredondamento; métricas não disponíveis "
            "não são apresentadas no gráfico."
        ),

        card(
            "Evolução dos experimentos",
            html.Div(
                [
                    html.H4("EXP-01 — Revisão das faixas"),
                    html.P(
                        "Inicialmente, a permanência era classificada como "
                        "curta (até 30 dias), média (de 31 a 45 dias) e longa "
                        "(acima de 45 dias). As faixas foram alteradas para "
                        "curta (até 7 dias), média (de 8 a 30 dias) e longa "
                        "(acima de 30 dias). A mudança buscou investigar se "
                        "a distribuição das amostras nas classes média e "
                        "longa dificultava o aprendizado por haver menos "
                        "amostras nessas categorias. Mesmo com a nova divisão "
                        "e o teste de regressão, os resultados permaneceram "
                        "limitados: acurácia de aproximadamente 0,48, "
                        "F1 macro de 0,47 e F1 ponderado de 0,50."
                    ),

                    html.H4("EXP-02 — XGBoost de referência"),
                    html.P(
                        "O XGBoost aplicado aos dados originais obteve "
                        "acurácia de 0,65, F1 macro de 0,49 e F1 ponderado "
                        "de 0,60. O recall foi de 0,92 para a classe Curta, "
                        "0,25 para Longa e 0,24 para Média, mostrando "
                        "diferenças no reconhecimento das classes."
                    ),

                    html.H4("EXP-03 — Pesos por classe"),
                    html.P(
                        "A aplicação de pesos por classe resultou em "
                        "acurácia de 0,56, F1 macro de 0,52 e F1 ponderado "
                        "de 0,58. Embora a acurácia tenha diminuído em "
                        "relação ao EXP-02, o F1 macro aumentou, indicando "
                        "uma distribuição mais equilibrada do desempenho "
                        "entre as classes."
                    ),

                    html.H4("EXP-04 — Engenharia de características"),
                    html.P(
                        "Além dos pesos por classe, foram adicionadas "
                        "características motivadas por pesquisas sobre "
                        "fatores externos potencialmente relacionados à "
                        "adoção de animais. A variável is_mix identifica "
                        "animais de raça mista/SRD, considerando a hipótese "
                        "de que características raciais possam estar "
                        "associadas ao interesse dos adotantes. A variável "
                        "is_black_or_dark identifica pelagem preta ou "
                        "escura e permite investigar o chamado Black Dog "
                        "Syndrome, fenômeno associado à percepção de que "
                        "animais de pelagem escura podem enfrentar "
                        "dificuldades adicionais de adoção. Por fim, "
                        "simplified_breed agrupa as dez raças mais comuns, "
                        "representando de forma simplificada possíveis "
                        "diferenças entre raças."
                    ),

                    html.P(
                        "Essas variáveis representam hipóteses a investigar, "
                        "não evidências de que raça ou pelagem causem "
                        "determinado tempo de permanência. O EXP-04 obteve "
                        "acurácia de 0,57, F1 macro de 0,53 e F1 ponderado "
                        "de 0,59. Esses resultados não isolam a contribuição "
                        "individual de cada nova característica."
                    ),
                ]
            ),
        ),

        conclusao(
            "Os resultados demonstram que prever com precisão o tempo de "
            "permanência dos animais é um problema desafiador. A alteração "
            "das faixas de permanência, a escolha de diferentes modelos, "
            "o uso de pesos por classe e a inclusão de características "
            "adicionais produziram desempenhos distintos, mas não "
            "eliminaram essa dificuldade. Nos experimentos iniciais, "
            "a Random Forest apresentou F1 macro próximo de 0,53; nos "
            "novos experimentos, os valores de F1 macro variaram de "
            "0,47 a 0,53. Como os resultados novos estão arredondados "
            "e a equivalência dos procedimentos de avaliação precisa "
            "ser confirmada, esses valores não permitem afirmar uma "
            "melhoria geral e conclusiva entre todos os modelos."
        ),
    ]
)


@callback(
    Output("modelos-grafico", "figure"),
    Input("modelos-metrica", "value"),
)
def atualizar_grafico(metrica):
    return criar_grafico(metrica)
