"""
Componentes reutilizáveis do dashboard Adotai.
Todas as páginas devem montar o layout com estes blocos, para manter o
roteiro: pergunta -> gráfico -> o que isso significa -> conclusão.
"""
from dash import html


def cabecalho_pagina(pergunta, subtitulo=None):
    """Título da página, escrito como uma PERGUNTA."""
    filhos = [html.H1(pergunta, className="pagina-titulo")]
    if subtitulo:
        filhos.append(html.P(subtitulo, className="pagina-subtitulo"))
    return html.Div(filhos, className="pagina-cabecalho")


def card(titulo, *conteudo):
    """Cartão branco com título. Coloque dentro dele o gráfico (dcc.Graph) ou tabela."""
    return html.Div(
        [html.H3(titulo, className="card-titulo"), *conteudo],
        className="card",
    )


def interpretacao(texto):
    """Bloco 'O que isso significa': 2 a 3 linhas explicando o gráfico para leigos."""
    return html.Div(
        [html.Span("O que isso significa", className="rotulo"), html.P(texto)],
        className="bloco interpretacao",
    )


def conclusao(texto):
    """Bloco de conclusão da página, em uma ou duas frases."""
    return html.Div(
        [html.Span("Conclusão", className="rotulo"), html.P(texto)],
        className="bloco conclusao",
    )


def kpi(valor, rotulo, nota=None):
    """Cartão de número grande, usado na landing page."""
    filhos = [html.Div(valor, className="kpi-valor"), html.Div(rotulo, className="kpi-rotulo")]
    if nota:
        filhos.append(html.Div(nota, className="kpi-nota"))
    return html.Div(filhos, className="kpi")


def grade(*filhos, colunas=2):
    """Organiza cartões lado a lado (vira 1 coluna no celular)."""
    return html.Div(list(filhos), className=f"grade grade-{colunas}")


def a_fazer(texto):
    """Aviso temporário para páginas ainda em construção. REMOVER ao concluir a página."""
    return html.Div(f"Em construção: {texto}", className="a-fazer")

### adicão para p2.1

import plotly.express as px

def plot_permanencia_por_especie(df):
    df_valido = df[df['time_in_shelter_days'] > 0]
    fig = px.box(
        df_valido,
        x='animal_type',
        y='time_in_shelter_days',
        log_y=True,
        title='Tempo de Permanência por Espécie (Escala Log)',
        labels={'animal_type': 'Espécie', 'time_in_shelter_days': 'Dias no Abrigo'}
    )
    return fig

def plot_permanencia_por_condicao(df):
    df_valido = df[df['time_in_shelter_days'] > 0]
    fig = px.box(
        df_valido,
        x='intake_condition',
        y='time_in_shelter_days',
        log_y=True,
        title='Tempo de Permanência por Condição de Entrada (Escala Log)',
        labels={'intake_condition': 'Condição de Entrada', 'time_in_shelter_days': 'Dias no Abrigo'}
    )
    return fig

def plot_permanencia_por_tipo_entrada(df):
    df_valido = df[df['time_in_shelter_days'] > 0]
    fig = px.box(
        df_valido,
        x='intake_type',
        y='time_in_shelter_days',
        log_y=True,
        title='Tempo de Permanência por Tipo de Entrada (Escala Log)',
        labels={'intake_type': 'Tipo de Entrada', 'time_in_shelter_days': 'Dias no Abrigo'}
    )
    return fig

### final da adição para p2.1
