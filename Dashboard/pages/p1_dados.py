"""
Página 1 — Os dados (três gráficos independentes).
Registra-se como página do dash usando dash.register_page.
"""

import dash
from dash import html, dcc, Input, Output
import plotly.express as px
import pandas as pd

from componentes import cabecalho_pagina, card, interpretacao, legenda_leitura
from data import dados

# Registrar a página para dash.pages
dash.register_page(__name__, path="/p1", name="P1: Os dados", order=2)

layout = html.Div(
    [
        cabecalho_pagina(
            "Como os dados estão distribuídos?",
            subtitulo="Três gráficos independentes: Espécie, Tipo de Entrada e Permanência.",
        ),
        html.Div(
            [
                # Linha com 3 cartões (em telas pequenas cada um pode ir para nova linha via CSS)
                html.Div(
                    [
                        card(
                            "Espécies",
                            dcc.Loading(dcc.Graph(id="g-especies"), type="circle"),
                        ),
                        card(
                            "Tipo de Entrada",
                            dcc.Loading(dcc.Graph(id="g-intake-type"), type="circle"),
                        ),
                        card(
                            "Permanência (categoria)",
                            dcc.Loading(dcc.Graph(id="g-permanencia"), type="circle"),
                        ),
                    ],
                    className="linha-cards",
                ),
                legenda_leitura(
                    "Cada gráfico mostra contagens por categoria. Permanência foi categorizada em Curta (<30d), Média (30-180d) e Longa (>180d)."
                ),
                interpretacao(
                    "Os três gráficos ajudam a entender volume por espécie, como os animais entram no abrigo e quanto tempo permanecem em categorias amplas."
                ),
            ],
            className="coluna-principal",
        ),
    ],
    className="pagina",
)


# CALLBACKS: cada gráfico é independente e usa as funções do módulo data.dados
@dash.callback(Output("g-especies", "figure"), Input("g-especies", "id"))
def grafico_especies(_):
    try:
        df = dados.carregar_dados()
    except FileNotFoundError as e:
        fig = px.bar(x=[], y=[])
        fig.update_layout(title_text=str(e))
        return fig

    s = df.get("species")
    if s is None:
        fig = px.bar(x=[], y=[])
        fig.update_layout(title_text="Coluna 'species' não encontrada no dataset.")
        return fig

    counts = s.dropna().astype(str).value_counts().sort_index()
    fig = px.bar(x=counts.index, y=counts.values, labels={"x": "Espécie", "y": "Contagem"}, title="Distribuição por Espécie")
    fig.update_layout(template="adotai")
    return fig


@dash.callback(Output("g-intake-type", "figure"), Input("g-intake-type", "id"))
def grafico_intake(_):
    try:
        df = dados.carregar_dados()
    except FileNotFoundError as e:
        fig = px.bar(x=[], y=[])
        fig.update_layout(title_text=str(e))
        return fig

    s = None
    for cand in ["intake_type", "intake"]:
        if cand in df.columns:
            s = df[cand]
            break
    if s is None:
        fig = px.bar(x=[], y=[])
        fig.update_layout(title_text="Coluna de 'intake_type'/'intake' não encontrada no dataset.")
        return fig

    counts = s.dropna().astype(str).value_counts().sort_index()
    fig = px.bar(x=counts.index, y=counts.values, labels={"x": "Tipo de Entrada", "y": "Contagem"}, title="Distribuição por Tipo de Entrada")
    fig.update_layout(template="adotai")
    return fig


@dash.callback(Output("g-permanencia", "figure"), Input("g-permanencia", "id"))
def grafico_permanencia(_):
    try:
        df = dados.carregar_dados()
    except FileNotFoundError as e:
        fig = px.bar(x=[], y=[])
        fig.update_layout(title_text=str(e))
        return fig

    df = dados.preparar_permanencia(df)
    if "permanencia_cat" not in df.columns:
        fig = px.bar(x=[], y=[])
        fig.update_layout(title_text="Não foi possível calcular a permanência. Verifique colunas de datas ou dias no CSV.")
        return fig

    counts = df["permanencia_cat"].dropna().astype(str).value_counts().reindex(dados.PERMANENCIA_CATEGORIAS).fillna(0)
    fig = px.bar(x=counts.index, y=counts.values, labels={"x": "Permanência", "y": "Contagem"}, title="Distribuição por Permanência")
    fig.update_layout(template="adotai")
    return fig
