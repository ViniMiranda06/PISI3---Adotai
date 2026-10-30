"""Página de explicabilidade das previsões do Random Forest com SHAP."""

from pathlib import Path

import dash
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import dcc, html

from componentes import cabecalho_pagina, card, conclusao, interpretacao
import tema


dash.register_page(
    __name__,
    path="/explicabilidade",
    name="Explicabilidade e app",
    order=4,
)


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
SHAP_PATH = DATA_DIR / "shap_importance.csv"


def figura_indisponivel(mensagem):
    """Exibe uma mensagem quando os resultados SHAP não estão disponíveis."""
    fig = go.Figure()

    fig.add_annotation(
        text=mensagem,
        x=0.5,
        y=0.5,
        xref="paper",
        yref="paper",
        showarrow=False,
        align="center",
        font=dict(size=14, color=tema.TEXTO_SEC),
    )

    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)

    fig.update_layout(
        height=350,
        margin=dict(l=25, r=25, t=30, b=25),
    )

    return fig


def carregar_shap():
    """Carrega e valida os resultados SHAP exportados pelo notebook."""
    if not SHAP_PATH.exists():
        return None

    try:
        dados = pd.read_csv(
            SHAP_PATH,
            encoding="utf-8-sig",
        )
    except (
        OSError,
        pd.errors.ParserError,
        pd.errors.EmptyDataError,
        UnicodeDecodeError,
    ):
        return None

    colunas_obrigatorias = {
        "atributo",
        "importancia_media_absoluta",
    }

    if not colunas_obrigatorias.issubset(dados.columns):
        return None

    dados = dados.copy()

    dados["atributo"] = (
        dados["atributo"]
        .astype("string")
        .str.strip()
    )

    dados["importancia_media_absoluta"] = pd.to_numeric(
        dados["importancia_media_absoluta"],
        errors="coerce",
    )

    dados = dados.dropna(
        subset=[
            "atributo",
            "importancia_media_absoluta",
        ]
    )

    dados = dados[
        dados["importancia_media_absoluta"] >= 0
    ]

    if dados.empty:
        return None

    return dados.sort_values(
        "importancia_media_absoluta",
        ascending=False,
    )


def rotular_atributo(nome):
    """Traduz nomes técnicos comuns para rótulos legíveis no gráfico."""
    nome = str(nome).strip()

    nomes_diretos = {
        "age_upon_intake_(days)": "Idade na entrada (dias)",
        "intake_hour": "Hora da entrada",
        "intake_month": "Mês da entrada",
        "intake_year": "Ano da entrada",
    }

    if nome in nomes_diretos:
        return nomes_diretos[nome]

    prefixos = {
        "animal_type_": "Espécie",
        "intake_type_": "Tipo de entrada",
        "intake_condition_": "Condição de entrada",
        "intake_weekday_": "Dia da semana",
        "sex_upon_intake_": "Sexo/condição na entrada",
    }

    traducoes = {
        "Dog": "cão",
        "Cat": "gato",
        "Bird": "ave",
        "Other": "outras espécies",
        "Livestock": "animal de criação",
        "Owner Surrender": "entrega pelo tutor",
        "Stray": "animal encontrado",
        "Public Assist": "assistência pública",
        "Wildlife": "animal silvestre",
        "Unknown": "desconhecido",
        "Normal": "normal",
        "Injured": "lesionado",
        "Sick": "doente",
        "Nursing": "amamentando",
        "Aged": "idoso",
        "Monday": "segunda-feira",
        "Tuesday": "terça-feira",
        "Wednesday": "quarta-feira",
        "Thursday": "quinta-feira",
        "Friday": "sexta-feira",
        "Saturday": "sábado",
        "Sunday": "domingo",
        "Neutered Male": "macho castrado",
        "Spayed Female": "fêmea castrada",
        "Intact Male": "macho não castrado",
        "Intact Female": "fêmea não castrada",
    }

    for prefixo, rotulo in prefixos.items():
        if nome.startswith(prefixo):
            categoria = nome[len(prefixo):].strip()

            categoria = traducoes.get(
                categoria,
                categoria.replace("_", " "),
            )

            return f"{rotulo}: {categoria}"

    return nome.replace("_", " ")


# Carrega os resultados calculados pelo notebook.
shap_df = carregar_shap()


if shap_df is not None:

    # Seleciona os 15 atributos de maior importância.
    top_shap = shap_df.head(15).copy()

    top_shap["atributo_exibicao"] = (
        top_shap["atributo"].apply(rotular_atributo)
    )

    # Deixa o atributo mais importante no topo do gráfico.
    top_shap = top_shap.sort_values(
        "importancia_media_absoluta",
        ascending=True,
    )

    fig_shap = px.bar(
        top_shap,
        x="importancia_media_absoluta",
        y="atributo_exibicao",
        orientation="h",
        hover_data={
            "atributo": True,
            "importancia_media_absoluta": ":.4f",
            "atributo_exibicao": False,
        },
        labels={
            "atributo_exibicao": "Atributo",
            "atributo": "Nome técnico",
            "importancia_media_absoluta": (
                "Importância média absoluta SHAP"
            ),
        },
        title="Atributos com maior importância nas previsões",
    )

    fig_shap.update_layout(
        height=max(460, 32 * len(top_shap) + 130),
        showlegend=False,
        margin=dict(l=245, r=25, t=65, b=65),
    )

    fig_shap.update_yaxes(
        automargin=True,
        tickfont=dict(size=11),
    )

    fig_shap.update_xaxes(
        rangemode="tozero",
    )

    # Identifica o atributo de maior importância no CSV.
    atributo_principal = str(
        shap_df.iloc[0]["atributo"]
    )

    atributo_legivel = rotular_atributo(
        atributo_principal
    )

    importancia_principal = float(
        shap_df.iloc[0]["importancia_media_absoluta"]
    )

    # Interpretação dos resultados observados.
    texto_interpretacao = (
        f"Na amostra analisada, '{atributo_legivel}' apresentou a maior "
        f"importância média absoluta SHAP ({importancia_principal:.4f}). "
        "Na análise descritiva, 14,29% dos gatos apresentaram permanência "
        "longa (mais de 45 dias), contra 7,86% dos cães. Essa diferença "
        "ajuda a contextualizar por que a espécie pode ser relevante para "
        "o modelo, mas não demonstra causalidade. A importância SHAP, "
        "isoladamente, também não indica se um atributo aumenta ou reduz "
        "a previsão de uma classe."
    )

    texto_conclusao = (
        "A análise SHAP ajuda a identificar quais atributos mais "
        "influenciam as previsões do Random Forest. Os resultados "
        "descrevem o comportamento do modelo na amostra analisada "
        "e não demonstram, por si só, relações de causa e efeito."
    )

else:

    fig_shap = figura_indisponivel(
        "Resultados SHAP não encontrados ou em formato inválido. "
        "Execute a exportação no notebook e coloque shap_importance.csv "
        "na pasta Dashboard/data."
    )

    texto_interpretacao = (
        "A importância global é calculada pela média dos valores "
        "absolutos SHAP. Valores maiores indicam maior magnitude "
        "média de contribuição nas previsões avaliadas."
    )

    texto_conclusao = (
        "Para interpretar os resultados específicos deste projeto, "
        "é necessário gerar os valores SHAP a partir do Random Forest "
        "e disponibilizar o CSV exportado pelo notebook."
    )


layout = html.Div(
    [
        cabecalho_pagina(
            "O que pesa na previsão e como ajudar na adoção?",
            "Importância dos atributos nas previsões do Random Forest "
            "analisada com SHAP.",
        ),

        card(
            "Quais atributos mais influenciam as previsões?",
            dcc.Graph(
                figure=fig_shap,
                config={
                    "displayModeBar": False,
                    "responsive": True,
                },
                style={"width": "100%"},
            ),
        ),

        interpretacao(
            texto_interpretacao,
        ),

        conclusao(
            texto_conclusao,
        ),
    ]
)