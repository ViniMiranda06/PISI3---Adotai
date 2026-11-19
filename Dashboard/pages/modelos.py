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
from leitura import existe_tabela, ler_tabela

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
    if not existe_tabela(RESULTADOS_PATH):
        return None
    try:
        df = ler_tabela(RESULTADOS_PATH)  # .parquet ou .csv
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

# [JUSTIÇA] Auditoria de desempenho por subgrupos do modelo final (Random Forest regularizada,
# limiar 0,51, 15.935 animais de teste). Valores da saída da célula 7.4.1 do notebook (EDA);
# recall e precisão de cada grupo calculados a partir das contagens da própria auditoria
# (N real Prolongada e falsos negativos) e arredondados para 3 casas.
# Cada linha: (grupo, N, N real Prolongada, recall, precisão, falsos negativos, observação).
_OBS_POUCOS = "Poucos casos Prolongada: leitura frágil"
JUSTICA_ESPECIE = [
    ("Bird", 84, 18, "0.722", "0.929", 5, _OBS_POUCOS),
    ("Cat", 5933, 2004, "0.806", "0.511", 388, ""),
    ("Dog", 9022, 1845, "0.445", "0.369", 1024, ""),
    ("Other", 896, 60, "0.617", "0.487", 23, _OBS_POUCOS),
]
JUSTICA_SEXO = [
    ("Intact Female", 4794, 1418, "0.669", "0.517", 470, ""),
    ("Intact Male", 5001, 1443, "0.667", "0.471", 480, ""),
    ("Neutered Male", 2531, 531, "0.514", "0.345", 258, ""),
    ("Spayed Female", 2241, 509, "0.593", "0.374", 207, ""),
    ("Unknown", 1368, 26, "0.038", "1.000", 25, _OBS_POUCOS),
]
JUSTICA_IDADE = [
    ("Filhote (< 1 ano)", 6666, 1835, "0.793", "0.546", 379, ""),
    ("Adulto (1 a < 7 anos)", 7824, 1767, "0.477", "0.355", 925, ""),
    ("Idoso (>= 7 anos)", 1445, 325, "0.582", "0.429", 136, ""),
]
# Diferença de recall (maior - menor) entre os grupos de cada dimensão, da célula 7.4.1.
JUSTICA_DIFERENCAS = [
    ("Espécie", "Dog (0.445)", "Cat (0.806)", "0.361"),
    ("Sexo", "Unknown (0.038)", "Intact Female (0.669)", "0.630"),
    ("Faixa etária", "Adulto (0.477)", "Filhote (0.793)", "0.317"),
]
COLUNAS_JUSTICA = ["Grupo", "N", "N Prolongada", "Recall Prolongada",
                   "Precisão Prolongada", "Falsos negativos", "Observação"]

_ESTILO_TABELA = dict(
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
        "minWidth": "90px",
    },
)


def _milhar(v):
    return f"{v:,}".replace(",", ".")


def _tabela_justica(linhas):
    """Tabela compacta de um subgrupo, com o mesmo estilo da tabela de resultados."""
    return dash_table.DataTable(
        data=[
            {"Grupo": g, "N": _milhar(n), "N Prolongada": _milhar(npro),
             "Recall Prolongada": rec, "Precisão Prolongada": prec,
             "Falsos negativos": _milhar(fn), "Observação": obs}
            for g, n, npro, rec, prec, fn, obs in linhas
        ],
        columns=[{"name": c, "id": c} for c in COLUNAS_JUSTICA],
        **_ESTILO_TABELA,
    )


def _tabela_diferencas_justica():
    cols = ["Dimensão", "Menor recall", "Maior recall", "Diferença de recall"]
    return dash_table.DataTable(
        data=[dict(zip(cols, linha)) for linha in JUSTICA_DIFERENCAS],
        columns=[{"name": c, "id": c} for c in cols],
        **_ESTILO_TABELA,
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
            "Justiça",
            html.Div(
                [
                    html.P(
                        "Esta auditoria compara o desempenho do modelo final entre grupos de "
                        "animais definidos por espécie, sexo e idade, no mesmo conjunto de teste "
                        "(15.935 animais) e com o mesmo limiar de 0,51. Ela mostra se o modelo "
                        "encontra os animais de permanência prolongada com a mesma facilidade em "
                        "todos os grupos. O modelo não foi alterado nem retreinado para isso."
                    ),
                    html.P(
                        "A previsão usa características conhecidas na entrada do animal: espécie, "
                        "sexo, idade, condição de entrada, tipo de entrada e informações de data "
                        "e hora. O modelo usa class_weight='balanced' para lidar com a diferença "
                        "de frequência entre Curta e Prolongada. Isso trata a distribuição das "
                        "classes, mas não garante desempenho equivalente entre grupos de animais."
                    ),
                    html.P(
                        "Como ler as tabelas: N é o total de animais do grupo; N Prolongada é "
                        "quantos realmente passaram de 14 dias; o recall é a parte desses animais "
                        "que o modelo encontrou; a precisão é a parte das previsões 'Prolongada' "
                        "que estava certa; falsos negativos são animais Prolongada que o modelo "
                        "marcou como Curta."
                    ),

                    html.H4("Por espécie"),
                    _tabela_justica(JUSTICA_ESPECIE),

                    html.H4("Por sexo"),
                    html.P(
                        "As categorias são as da base de dados: Intact = não castrado, Neutered "
                        "Male = macho castrado, Spayed Female = fêmea castrada e Unknown = sexo "
                        "não informado.",
                        style={"color": tema.TEXTO_SEC},
                    ),
                    _tabela_justica(JUSTICA_SEXO),

                    html.H4("Por faixa etária"),
                    _tabela_justica(JUSTICA_IDADE),

                    html.H4("Diferenças de recall entre grupos"),
                    _tabela_diferencas_justica(),
                    html.P(
                        "A diferença é descritiva: o maior recall menos o menor recall entre os "
                        "grupos de cada dimensão.",
                        style={"color": tema.TEXTO_SEC},
                    ),

                    interpretacao(
                        "O modelo não acerta igualmente em todos os grupos. Por espécie, ele "
                        "encontra 0,806 dos gatos de permanência prolongada, mas só 0,445 dos "
                        "cães, e os cães concentram 1.024 dos 1.440 falsos negativos do teste. "
                        "Por idade, o recall é maior nos filhotes (0,793) e menor nos adultos "
                        "(0,477). Por sexo, a maior diferença (0,630) vem do grupo Unknown, que "
                        "tem só 26 animais Prolongada e recall de 0,038; entre os demais grupos "
                        "o recall vai de 0,514 (Neutered Male) a 0,669 (Intact Female)."
                    ),
                    html.P(
                        "Atenção às amostras pequenas: Bird (18 animais Prolongada), Other (60) "
                        "e Unknown em sexo (26) têm poucos casos da classe Prolongada, e seus "
                        "valores mudam muito com poucos animais. A marcação 'leitura frágil' é um "
                        "alerta deste card (menos de 100 animais Prolongada), não um teste "
                        "estatístico; o critério de amostra limitada do notebook não marcou "
                        "nenhum grupo. Por isso, comparações que envolvem esses grupos não são "
                        "confiáveis."
                    ),
                    html.P(
                        "Limitações: são comparações de desempenho em um único conjunto de "
                        "teste, sem teste estatístico. Elas mostram diferenças, mas não explicam "
                        "a causa (por exemplo, diferenças reais na duração das estadias entre os "
                        "grupos) nem provam discriminação. Também não provam que o modelo seja "
                        "livre de viés."
                    ),

                    html.H4("Atributos do modelo"),
                    html.P(
                        "O modelo final usa nove variáveis: animal_type (espécie), "
                        "age_upon_intake_(days) (idade em dias), sex_upon_intake (sexo), "
                        "intake_condition, intake_type, intake_month, intake_year, "
                        "intake_weekday e intake_hour. Espécie, sexo e idade fazem parte das "
                        "entradas; por isso a auditoria verifica diferenças de desempenho entre "
                        "esses grupos mesmo sendo atributos do modelo."
                    ),
                    html.P(
                        "As variáveis is_mix, is_black_or_dark e simplified_breed (raça e "
                        "pelagem) não fazem parte do modelo final publicado. A ausência delas "
                        "não comprova, por si só, a ausência de vieses indiretos."
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