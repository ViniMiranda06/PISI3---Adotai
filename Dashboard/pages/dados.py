"""Página de apresentação dos dados: permanência, espécie e tipo de entrada."""
from pathlib import Path

import dash
import pandas as pd
import plotly.express as px
from dash import dcc, html

from componentes import cabecalho_pagina, card, conclusao, interpretacao, kpi, grade
import tema

dash.register_page(__name__, path="/dados", name="Os dados", order=1)

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
CSV_PATH = DATA_DIR / "permanencia.csv"


def formatar_numero(valor):
    """Formata número para exibição em português (duas casas)."""
    try:
        return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return str(valor)


def carregar_dados():
    if not CSV_PATH.exists():
        return None

    try:
        df = pd.read_csv(CSV_PATH, encoding="utf-8-sig")
    except Exception:
        return None

    colunas_necessarias = {"time_in_shelter_days", "animal_type", "intake_type", "stay_category"}
    if not colunas_necessarias.issubset(df.columns):
        return None

    df = df.copy()
    df["time_in_shelter_days"] = pd.to_numeric(df["time_in_shelter_days"], errors="coerce")
    df = df.dropna(subset=["time_in_shelter_days"])
    # descarta valores não positivos (escala log não aceita zero)
    df = df[df["time_in_shelter_days"] > 0].copy()

    # normaliza categorias stay_category esperadas pelo tema
    mapping = {
        "curta": "Curta",
        "média": "Média",
        "media": "Média",
        "longa": "Longa",
    }
    df["stay_category"] = df["stay_category"].astype(str).str.strip().replace(mapping)

    return df


df = carregar_dados()

if df is None:
    layout = html.Div(
        [
            cabecalho_pagina(
                "Quanto tempo os animais ficam no abrigo?",
                "Distribuição da permanência, por espécie e por tipo de entrada.",
            ),
            html.Div(
                "CSV de dados não encontrado ou em formato inválido. Gere o arquivo Dashboard/data/permanencia.csv (colunas: time_in_shelter_days, animal_type, intake_type, stay_category) e volte a abrir a página.",
                className="a-fazer",
            ),
        ]
    )
else:
    permanencia = df["time_in_shelter_days"]

    media = permanencia.mean()
    mediana = permanencia.median()
    q3 = permanencia.quantile(0.75)
    maximo = permanencia.max()
    p95 = permanencia.quantile(0.95)

    # 1) KPIs
    kpis = grade(
        kpi(formatar_numero(media), "média de permanência", "dias"),
        kpi(formatar_numero(mediana), "mediana", "dias"),
        kpi(formatar_numero(q3), "3º quartil", "dias"),
        kpi(formatar_numero(maximo), "máximo", "dias"),
        colunas=4,
    )

    # 2) Histograma (até percentil 95 para não distorcer a cauda longa)
    hist_df = df[df["time_in_shelter_days"] <= p95].copy()
    fig_hist = px.histogram(
        hist_df,
        x="time_in_shelter_days",
        color="stay_category",
        color_discrete_map=tema.CORES_PERMANENCIA,
        nbins=30,
        title="Distribuição da permanência",
        labels={"time_in_shelter_days": "Permanência (dias)", "stay_category": "Categoria"},
    )
    fig_hist.update_layout(template=tema.TEMPLATE, height=380)
    fig_hist.update_xaxes(title="Permanência (dias)")
    fig_hist.update_yaxes(title="Contagem")

    # 3) Boxplot por espécie (escala log)
    fig_especie = px.box(
        df,
        x="animal_type",
        y="time_in_shelter_days",
        log_y=True,
        title="Permanência por espécie",
        labels={"animal_type": "Espécie", "time_in_shelter_days": "Permanência (dias)"},
        category_orders={"animal_type": ["Dog", "Cat", "Bird", "Other", "Livestock"]},
    )
    fig_especie.update_layout(template=tema.TEMPLATE, height=380)

    # 4) Boxplot por tipo de entrada (escala log)
    fig_entrada = px.box(
        df,
        x="intake_type",
        y="time_in_shelter_days",
        log_y=True,
        title="Permanência por tipo de entrada",
        labels={"intake_type": "Tipo de entrada", "time_in_shelter_days": "Permanência (dias)"},
    )
    fig_entrada.update_layout(template=tema.TEMPLATE, height=380)

    layout = html.Div(
        [
            cabecalho_pagina(
                "Quanto tempo os animais ficam no abrigo?",
                "Distribuição da permanência, por espécie e por tipo de entrada.",
            ),
            kpis,
            card(
                "Distribuição da permanência",
                dcc.Graph(figure=fig_hist, config={"displayModeBar": False, "responsive": True}),
            ),
            interpretacao(
                "A mediana (4,99 dias) é bem menor que a média (16,76 dias): a maioria dos animais sai rápido, mas alguns ficam por muito tempo e puxam a média para cima. Isso indica presença de cauda longa na distribuição."
            ),
            card(
                "Permanência por espécie",
                dcc.Graph(figure=fig_especie, config={"displayModeBar": False, "responsive": True}),
            ),
            interpretacao(
                "Cães, gatos e aves apresentam distribuições diferentes de permanência. Em geral, cães e gatos tendem a ter mais casos de permanência longa que a categoria 'Other'."
            ),
            card(
                "Permanência por tipo de entrada",
                dcc.Graph(figure=fig_entrada, config={"displayModeBar": False, "responsive": True}),
            ),
            interpretacao(
                "Entradas como Stray, Public Assist e Owner Surrender tendem a apresentar permanências maiores; entradas como Euthanasia Request e Wildlife têm permanências menores."
            ),
            conclusao(
                "A permanência é assimétrica: muitos animais saem rapidamente, mas existe uma cauda com casos muito prolongados. Esses padrões ajudam a justificar o balanceamento e as escolhas de pré-processamento nos modelos."
            ),
        ]
    )
