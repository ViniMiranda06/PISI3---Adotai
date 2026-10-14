"""Página de perfis dos animais usando resultados exportados do notebook."""
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import dash_table, dcc, html
import dash

from componentes import a_fazer, cabecalho_pagina, card, conclusao, grade, interpretacao
import tema

dash.register_page(
    __name__,
    path="/perfis",
    name="Perfis",
    order=2
)
BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
METRICAS_PATH = DATA_DIR / "cluster_metrics.csv"
PERFIS_PATH = DATA_DIR / "cluster_profiles.csv"

def _figura_indisponivel(mensagem):
    """Figura explicativa usada enquanto os resultados do notebook não existem."""
    fig = go.Figure()
    fig.add_annotation(
        text=mensagem,
        x=0.5, y=0.5, xref="paper", yref="paper",
        showarrow=False, align="center", font=dict(size=14, color=tema.TEXTO_SEC),
    )
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    fig.update_layout(height=300, margin=dict(l=20, r=20, t=30, b=20))
    return fig


def _ler_csv(caminho, colunas_obrigatorias):
    if not caminho.exists():
        return None
    try:
        df = pd.read_csv(caminho)
    except (OSError, pd.errors.ParserError, UnicodeDecodeError):
        return None
    if not set(colunas_obrigatorias).issubset(df.columns):
        return None
    return df

def _nomear_perfil(linha):
    """Cria um nome descritivo com base na espécie e idade medianas."""

    especie = str(linha["especie_principal"]).strip()
    idade_dias = pd.to_numeric(
        linha["idade_mediana_dias"], errors="coerce"
    )

    rotulos_especies = {
        "Dog": "Predomínio canino",
        "Cat": "Predomínio felino",
        "Bird": "Predomínio de aves",
        "Other": "Predomínio de outras espécies",
        "Livestock": "Predomínio de animais de criação",
    }

    rotulo_especie = rotulos_especies.get(
        especie,
        f"Espécie mais frequente: {especie}"
    )

    if pd.isna(idade_dias):
        idade = "idade não informada"
    elif idade_dias / 365.25 < 0.9:
        meses = max(1, round(idade_dias / 30.4375))
        idade = f"~{meses} meses"
    else:
        anos = max(1, round(idade_dias / 365.25))
        unidade = "ano" if anos == 1 else "anos"
        idade = f"~{anos} {unidade}"

    return f"{rotulo_especie} · {idade}"

metricas = _ler_csv(METRICAS_PATH, ["k", "inercia", "silhueta"])
perfis_df = _ler_csv(
    PERFIS_PATH,
    [
        "cluster", "nome_perfil", "n_animais", "idade_mediana_dias",
        "especie_principal", "especie_percentual", "permanencia_mediana_dias",
    ],
)
if metricas is not None and not metricas.empty:
    metricas = metricas.sort_values("k")
    fig_cotovelo = px.line(
        metricas, x="k", y="inercia", markers=True,
        labels={"k": "Número de grupos (k)", "inercia": "Inércia"},
        title="Método do cotovelo",
    )
    fig_cotovelo.update_xaxes(dtick=1)
    fig_cotovelo.update_layout(height=340)

    fig_silhueta = px.line(
        metricas, x="k", y="silhueta", markers=True,
        labels={"k": "Número de grupos (k)", "silhueta": "Coeficiente de silhueta"},
        title="Coeficiente de silhueta",
    )
    fig_silhueta.update_xaxes(dtick=1)
    fig_silhueta.add_hline(y=0, line_dash="dot", line_color=tema.LINHAS)
    melhor = metricas.loc[metricas["silhueta"].idxmax()]
    fig_silhueta.add_trace(
        go.Scatter(
            x=[melhor["k"]], y=[melhor["silhueta"]], mode="markers",
            marker=dict(size=12, symbol="circle-open", line=dict(width=2)),
            name="Maior silhueta", hovertemplate="k=%{x}<br>Silhueta=%{y:.3f}<extra></extra>",
        )
    )
    fig_silhueta.update_layout(height=340)
else:
    mensagem = (
        "Resultados de clusterização não encontrados. Execute a seção de K-Means "
        "no notebook e copie cluster_metrics.csv para a pasta Dashboard/data."
    )
    fig_cotovelo = _figura_indisponivel(mensagem)
    fig_silhueta = _figura_indisponivel(mensagem)

if perfis_df is not None and not perfis_df.empty:
    perfis_df = perfis_df.sort_values("cluster").copy()
    perfis_df["idade_mediana_anos"] = pd.to_numeric(
        perfis_df["idade_mediana_dias"], errors="coerce"
    ) / 365.25
    perfis_df["permanencia_mediana_dias"] = pd.to_numeric(
        perfis_df["permanencia_mediana_dias"], errors="coerce"
    )
    perfis_df["n_animais"] = pd.to_numeric(
        perfis_df["n_animais"], errors="coerce"
    )
    perfis_df["nome_perfil"] = perfis_df.apply(
        _nomear_perfil, axis=1
    )
    fig_perfis = px.scatter(
        perfis_df,
        x="idade_mediana_anos",
        y="permanencia_mediana_dias",
        size="n_animais",
        color="especie_principal",
        text="nome_perfil",
        hover_name="nome_perfil",
        hover_data={
            "idade_mediana_anos": ":.1f",
            "permanencia_mediana_dias": ":.1f",
            "n_animais": ":,.0f",
            "especie_principal": True,
            "especie_percentual": ":.1f",
        },
        labels={
            "idade_mediana_anos": "Idade mediana na entrada (anos)",
            "permanencia_mediana_dias": "Permanência mediana (dias)",
            "n_animais": "Quantidade de animais",
            "especie_principal": "Espécie mais frequente",
        },
        title="Idade e permanência mediana por perfil",
        size_max=42,
    )
    fig_perfis.update_traces(textposition="top center")
    fig_perfis.update_layout(height=390)

    colunas = [
        {"name": "Perfil", "id": "nome_perfil"},
        {"name": "Animais", "id": "n_animais", "type": "numeric", "format": {"specifier": ",.0f"}},
        {"name": "Idade mediana (dias)", "id": "idade_mediana_dias", "type": "numeric", "format": {"specifier": ",.1f"}},
        {"name": "Espécie mais frequente", "id": "especie_principal"},
        {"name": "Espécie no perfil (%)", "id": "especie_percentual", "type": "numeric", "format": {"specifier": ".1f"}},
        {"name": "Permanência mediana (dias)", "id": "permanencia_mediana_dias", "type": "numeric", "format": {"specifier": ",.1f"}},
    ]
    tabela = dash_table.DataTable(
        data=perfis_df.to_dict("records"),
        columns=colunas,
        page_size=3,
        sort_action="native",
        style_table={"overflowX": "auto"},
        style_cell={"padding": "10px", "textAlign": "left", "fontFamily": tema.FONTE_TEXTO, "fontSize": "13px", "whiteSpace": "normal", "height": "auto"},
        style_header={"fontWeight": "600", "backgroundColor": tema.FUNDO, "borderBottom": f"1px solid {tema.LINHAS}"},
        style_data={"backgroundColor": tema.CARTAO, "borderBottom": f"1px solid {tema.LINHAS}"},
    )
else:
    fig_perfis = _figura_indisponivel(
        "Perfis ainda não exportados. Execute o notebook, gere cluster_profiles.csv "
        "e coloque o arquivo em Dashboard/data."
    )
    tabela = a_fazer(
        "Depois de executar a célula de exportação do notebook, coloque cluster_profiles.csv "
        "na pasta Dashboard/data. A tabela mostrará idade, espécie e permanência de cada cluster."
    )

layout = html.Div(
    [
        cabecalho_pagina(
            "Existem tipos de animais com estadias diferentes?",
            "O K-Means agrupa registros com características semelhantes. Os perfis devem ser interpretados como tendências, não como categorias rígidas.",
        ),
        grade(
            card(
                "Como escolher o número de grupos",
                dcc.Graph(
                    figure=fig_cotovelo,
                    config={
                        "displayModeBar": False,
                        "responsive": True,
                    },
                    style={"height": "350px", "width": "100%"},
                ),
            ),
            card(
                "Qualidade da separação dos grupos",
                dcc.Graph(
                    figure=fig_silhueta,
                    config={
                        "displayModeBar": False,
                        "responsive": True,
                    },
                    style={"height": "350px", "width": "100%"},
                ),
            ),
            colunas=2,
        ),
        interpretacao(
            "O método do cotovelo mostra quanto a variação interna diminui quando aumentamos o número de grupos. "
            "A silhueta avalia a coesão e a separação; um valor próximo de zero, como o resultado aproximado de 0,131 observado no estudo, sugere sobreposição entre os grupos."
        ),
        card("Como são os perfis encontrados?", dcc.Graph(figure=fig_perfis, config={"displayModeBar": False, "responsive": True})),
        card("Resumo dos três clusters", tabela),
        conclusao(
            "Os três clusters ajudam a resumir padrões dos registros. Os nomes descritivos de cada perfil devem ser definidos após examinar sua idade, espécie predominante e permanência mediana; a silhueta baixa recomenda cautela ao interpretar as diferenças."
        ),
    ]
)
