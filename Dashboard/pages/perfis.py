"""Página de perfis: grupos de animais encontrados pelo K-Means.

Ordem da página: achados primeiro, método depois.
  1. resposta direta à pergunta do título
  2. um cartão por grupo
  3. gráfico de bolhas (idade x permanência)
  4. método (cotovelo e silhueta) e conclusão
"""
from pathlib import Path

import dash
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import dcc, html

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

# Nomes em linguagem simples, atribuídos pela ORDEM DE IDADE (do mais novo ao
# mais velho) e não pelo número do cluster, que pode mudar se o notebook rodar de novo.
NOMES_POR_IDADE = ["Filhotes", "Jovens", "Idosos"]

ESPECIES_PT = {
    "Dog": "Cães",
    "Cat": "Gatos",
    "Bird": "Aves",
    "Other": "Outras espécies",
    "Livestock": "Animais de criação",
}
ENTRADAS_PT = {
    "Stray": "Animal de rua",
    "Owner Surrender": "Entregue pelo tutor",
    "Public Assist": "Ajuda pública",
    "Abandoned": "Abandonado",
    "Wildlife": "Animal silvestre",
    "Euthanasia Request": "Pedido de eutanásia",
}

CONFIG_GRAFICO = {"displayModeBar": False, "responsive": True}


def _grafico(figura, altura=350):
    """dcc.Graph com altura fixa: sem ela, o modo responsivo colapsa o gráfico."""
    return dcc.Graph(
        figure=figura,
        config=CONFIG_GRAFICO,
        style={"height": f"{altura}px", "width": "100%"},
    )


# ---------------------------------------------------------------- utilitários
def _br(valor, casas=1):
    """Número no formato brasileiro (1.234,5)."""
    texto = f"{valor:,.{casas}f}"
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")


def _formatar_idade(dias):
    """Idade em linguagem simples: '~9 meses', '~1 ano', '~8 anos'."""
    dias = pd.to_numeric(dias, errors="coerce")
    if pd.isna(dias):
        return "não informada"
    if dias / 365.25 < 0.9:
        meses = max(1, round(dias / 30.4375))
        return f"~{meses} meses"
    anos = max(1, round(dias / 365.25))
    return f"~{anos} {'ano' if anos == 1 else 'anos'}"


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
        df = pd.read_csv(caminho, encoding="utf-8-sig")
    except (OSError, pd.errors.ParserError, UnicodeDecodeError):
        return None
    if not set(colunas_obrigatorias).issubset(df.columns):
        return None
    return df


def _preparar_perfis(df):
    """Converte tipos, ordena por idade e dá nome e cor a cada grupo."""
    df = df.copy()
    for col in [
        "n_animais", "idade_mediana_dias", "especie_percentual",
        "permanencia_mediana_dias", "permanencia_media_dias",
    ]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.sort_values("idade_mediana_dias").reset_index(drop=True)
    if len(df) == len(NOMES_POR_IDADE):
        df["grupo"] = NOMES_POR_IDADE
    else:
        df["grupo"] = [f"Grupo {i + 1}" for i in range(len(df))]
    df["cor"] = [tema.CORES_CLUSTER[i % len(tema.CORES_CLUSTER)] for i in range(len(df))]
    df["idade_anos"] = df["idade_mediana_dias"] / 365.25
    df["idade_formatada"] = df["idade_mediana_dias"].apply(_formatar_idade)
    return df


# ------------------------------------------------------------ blocos de texto
def _bloco_resposta(texto):
    """Resposta direta à pergunta do título, em destaque, no topo da página."""
    return html.Div(
        [html.Span("Resposta curta", className="rotulo"), html.P(texto)],
        className="bloco resposta",
    )


def _linha(rotulo, valor, destaque=False):
    return html.Div(
        [html.Span(rotulo, className="perfil-rotulo"), html.Span(valor, className="perfil-valor")],
        className="perfil-linha destaque" if destaque else "perfil-linha",
    )


def _cartao_perfil(linha, total):
    """Cartão de um grupo: nome, tamanho e características típicas."""
    especie = str(linha["especie_principal"]).strip()
    especie_txt = ESPECIES_PT.get(especie, especie)
    if pd.notna(linha["especie_percentual"]):
        especie_txt += f" ({_br(linha['especie_percentual'], 0)}%)"

    linhas = [
        _linha("Idade típica", _formatar_idade(linha["idade_mediana_dias"])),
        _linha("Espécie mais comum", especie_txt),
    ]
    entrada = linha.get("tipo_entrada_principal")
    if isinstance(entrada, str) and entrada.strip():
        linhas.append(_linha("Entrada mais comum", ENTRADAS_PT.get(entrada.strip(), entrada.strip())))
    if "permanencia_media_dias" in linha.index and pd.notna(linha["permanencia_media_dias"]):
        linhas.append(_linha("Permanência média", f"{_br(linha['permanencia_media_dias'])} dias"))
    linhas.append(
        _linha("Permanência mediana", f"{_br(linha['permanencia_mediana_dias'])} dias", destaque=True)
    )

    pct = linha["n_animais"] / total * 100
    return html.Div(
        [
            html.Div(linha["grupo"], className="perfil-nome", style={"color": linha["cor"]}),
            html.Div(
                f"{_br(pct)}% da base · {_br(linha['n_animais'], 0)} registros",
                className="perfil-tamanho",
            ),
            *linhas,
        ],
        className="perfil-card",
        style={"borderTopColor": linha["cor"]},
    )


# -------------------------------------------------------------------- gráficos
def _grafico_bolhas(perfis):
    """Uma cor por grupo, eixo Y a partir de zero (sem exagerar diferenças pequenas)."""
    ordem = list(perfis["grupo"])
    total_animais = perfis["n_animais"].sum()
    mediana_geral_pond = (
        (perfis["permanencia_mediana_dias"] * perfis["n_animais"]).sum() / total_animais
    )

    fig = px.scatter(
        perfis,
        x="idade_anos",
        y="permanencia_mediana_dias",
        size="n_animais",
        color="grupo",
        color_discrete_map=dict(zip(perfis["grupo"], perfis["cor"])),
        category_orders={"grupo": ordem},
        custom_data=["grupo", "idade_formatada", "permanencia_mediana_dias", "n_animais"],
        labels={
            "idade_anos": "Idade mediana na entrada (anos)",
            "permanencia_mediana_dias": "Permanência mediana (dias)",
            "n_animais": "Quantidade de animais",
            "grupo": "Grupo",
        },
        title="Idade mediana na entrada vs. Permanência mediana (dias)",
        size_max=46,
    )
    fig.update_traces(
        marker=dict(opacity=0.85, line=dict(width=1.5, color="#FFFFFF")),
        cliponaxis=False,
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            "Idade típica: %{customdata[1]} (%{x:.1f} anos)<br>"
            "Permanência mediana: <b>%{customdata[2]:.1f} dias</b><br>"
            "Tamanho do grupo: %{customdata[3]:,.0f} animais"
            "<extra></extra>"
        ),
    )

    # Posicionamento em coordenadas reais dos eixos (X, Y) para nunca colidir:
    # - Filhotes (y=5.1): rótulo ACIMA da bolha azul (y + 1.15)
    # - Jovens (y=4.9): rótulo ABAIXO da bolha roxa (y - 1.15)
    # - Idosos (y=4.3): rótulo ABAIXO da bolha marrom (y - 0.95), longe da linha tracejada!
    posicoes_grupos = {
        "Filhotes": (-0.1, 1.15),
        "Jovens": (0.1, -1.15),
        "Idosos": (0.0, -0.95),
    }
    for _, linha in perfis.iterrows():
        nome_grupo = linha["grupo"]
        dx, dy = posicoes_grupos.get(nome_grupo, (0.0, 1.1))
        fig.add_annotation(
            x=float(linha["idade_anos"]) + dx,
            y=float(linha["permanencia_mediana_dias"]) + dy,
            text=f"<b>{nome_grupo}</b> ({_br(linha['permanencia_mediana_dias'], 1)}d)",
            showarrow=False,
            font=dict(size=12, color=tema.TEXTO),
        )

    # Linha tracejada sem texto embutido nas pontas (para não bater nas bolhas)
    fig.add_hline(
        y=mediana_geral_pond,
        line_dash="dot",
        line_color=tema.TEXTO_SEC,
        opacity=0.65,
    )
    # Rótulo da linha posicionado no centro livre do gráfico (x = 4.5), logo abaixo da linha
    fig.add_annotation(
        x=4.5,
        y=mediana_geral_pond - 0.35,
        text=f"Média das medianas (~{_br(mediana_geral_pond, 1)} dias)",
        showarrow=False,
        font=dict(size=11, color=tema.TEXTO_SEC),
    )

    topo = float(perfis["permanencia_mediana_dias"].max())
    max_x = float(perfis["idade_anos"].max()) * 1.15
    y_max = max(topo * 1.65, 1)

    # Caixa de leitura posicionada no espaço central superior (x = 4.5, y ~ 7.3)
    fig.add_annotation(
        x=4.5,
        y=y_max * 0.86,
        text=(
            "<b>Como ler:</b> mesmo avançando na idade (eixo X),<br>"
            "os 3 grupos permanecem próximos de ~5 dias (eixo Y)."
        ),
        showarrow=False,
        align="left",
        font=dict(size=11.5, color=tema.TEXTO_SEC),
        bgcolor="rgba(255, 255, 255, 0.9)",
        bordercolor="rgba(0, 0, 0, 0.08)",
        borderwidth=1,
        borderpad=6,
    )

    fig.update_xaxes(range=[0, max_x], dtick=1)
    fig.update_yaxes(range=[0, y_max])
    fig.update_layout(
        height=400,
        margin=dict(l=55, r=30, t=65, b=55),
        legend_title_text="Grupo (tamanho da bolha = nº de animais)",
    )
    return fig

def _escolher_k(metricas, perfis):
    """k usado nos perfis; se não der para saber, o de maior silhueta."""
    k_melhor = int(metricas.loc[metricas["silhueta"].idxmax(), "k"])
    if perfis is not None and len(perfis) in set(metricas["k"].astype(int)):
        return len(perfis), k_melhor
    return k_melhor, k_melhor


def _figuras_metodo(metricas, k):
    """Cotovelo e silhueta, com o k escolhido destacado e faixas de referência."""
    metricas = metricas.sort_values("k")
    ponto = metricas.loc[metricas["k"] == k].iloc[0]

    # 1. Cotovelo
    fig_cotovelo = px.line(
        metricas, x="k", y="inercia", markers=True,
        labels={"k": "Número de grupos (k)", "inercia": "Inércia"},
        title="Método do cotovelo",
    )
    fig_cotovelo.update_traces(
        line_color=tema.TEXTO_SEC,
        marker_color=tema.TEXTO_SEC,
        hovertemplate="<b>k = %{x} grupos</b><br>Inércia: %{y:,.0f}<extra></extra>",
    )
    fig_cotovelo.add_trace(go.Scatter(
        x=[k], y=[ponto["inercia"]], mode="markers",
        marker=dict(size=14, color=tema.PRIMARIA),
        showlegend=False, hoverinfo="skip",
    ))
    fig_cotovelo.add_annotation(
        x=k, y=ponto["inercia"],
        text=f"<b>k = {k}</b> (escolhido)",
        showarrow=True, arrowhead=2,
        ax=55, ay=-28,  # Aponta para cima à direita, em área limpa fora da linha
        font=dict(color=tema.PRIMARIA, size=12),
        arrowcolor=tema.PRIMARIA,
    )
    fig_cotovelo.update_xaxes(dtick=1)
    fig_cotovelo.update_yaxes(tickformat="~s")
    fig_cotovelo.update_layout(height=340)

    # 2. Silhueta (0 a 0,65 para as faixas de referência caberem no gráfico)
    fig_silhueta = px.line(
        metricas, x="k", y="silhueta", markers=True,
        labels={"k": "Número de grupos (k)", "silhueta": "Coeficiente de silhueta"},
        title="Coeficiente de silhueta",
    )
    fig_silhueta.update_traces(
        line_color=tema.TEXTO_SEC,
        marker_color=tema.TEXTO_SEC,
        hovertemplate="<b>k = %{x} grupos</b><br>Silhueta: %{y:.3f}<extra></extra>",
    )
    # Rótulos das faixas alinhados à DIREITA ("top right" / "bottom right")
    # para não colidirem com o destaque de k = 3 na esquerda.
    fig_silhueta.add_hrect(
        y0=0, y1=0.25, fillcolor=tema.TEXTO_SEC, opacity=0.12, line_width=0,
        annotation_text="Pouco separados (abaixo de 0,25)",
        annotation_position="top right",
        annotation_font=dict(size=11, color=tema.TEXTO_SEC),
    )
    fig_silhueta.add_hrect(
        y0=0.5, y1=0.65, fillcolor=tema.TEXTO_SEC, opacity=0.05, line_width=0,
        annotation_text="Bem definidos (acima de 0,5)",
        annotation_position="bottom right",
        annotation_font=dict(size=11, color=tema.TEXTO_SEC),
    )
    fig_silhueta.add_trace(go.Scatter(
        x=[k], y=[ponto["silhueta"]], mode="markers",
        marker=dict(size=14, color=tema.PRIMARIA),
        showlegend=False, hoverinfo="skip",
    ))
    # Seta apontando para a área livre acima do ponto (y ~ 0.32), fora da faixa cinza
    fig_silhueta.add_annotation(
        x=k, y=ponto["silhueta"],
        text=f"<b>k = {k}: {_br(ponto['silhueta'], 3)}</b> (maior valor)",
        showarrow=True, arrowhead=2,
        ax=25, ay=-58,
        font=dict(color=tema.PRIMARIA, size=12),
        arrowcolor=tema.PRIMARIA,
        bgcolor="rgba(255, 255, 255, 0.85)",
        borderpad=2,
    )
    fig_silhueta.update_xaxes(dtick=1)
    fig_silhueta.update_yaxes(range=[0, 0.65])
    fig_silhueta.update_layout(height=340)
    return fig_cotovelo, fig_silhueta, float(ponto["silhueta"])


def _faixa_silhueta(valor):
    if valor < 0.25:
        return "na faixa de grupos pouco separados"
    if valor > 0.5:
        return "na faixa de grupos bem definidos"
    return "numa faixa intermediária de separação"


# --------------------------------------------------------------- montagem
metricas = _ler_csv(METRICAS_PATH, ["k", "inercia", "silhueta"])
perfis_df = _ler_csv(
    PERFIS_PATH,
    [
        "cluster", "n_animais", "idade_mediana_dias",
        "especie_principal", "especie_percentual", "permanencia_mediana_dias",
    ],
)
if metricas is not None and metricas.empty:
    metricas = None
if perfis_df is not None and perfis_df.empty:
    perfis_df = None

perfis = _preparar_perfis(perfis_df) if perfis_df is not None else None

pergunta = "Existem tipos de animais com estadias diferentes?"
subtitulo = (
    "O K-Means reuniu os registros do abrigo em grupos parecidos entre si. "
    "Veja quem são esses grupos e se a estadia muda de um para outro."
)

blocos = [cabecalho_pagina(pergunta, subtitulo)]

# 1) Achados: resposta, cartões e gráfico de bolhas
if perfis is not None:
    total = perfis["n_animais"].sum()
    p_min = perfis["permanencia_mediana_dias"].min()
    p_max = perfis["permanencia_mediana_dias"].max()
    idade_min = _formatar_idade(perfis["idade_mediana_dias"].min())
    idade_max = _formatar_idade(perfis["idade_mediana_dias"].max())

    blocos.append(_bloco_resposta(
        f"Pouco. Os grupos diferem mais na idade (de {idade_min} a {idade_max}) "
        f"do que na estadia: a permanência mediana fica entre {_br(p_min)} e "
        f"{_br(p_max)} dias em todos."
    ))
    blocos.append(grade(
        *[_cartao_perfil(linha, total) for _, linha in perfis.iterrows()],
        colunas=3,
    ))
    blocos.append(html.P(
        "A média de permanência é maior que a mediana porque alguns animais "
        "ficam muito mais tempo que os outros (outliers que puxam a média para cima).",
        className="nota-grafico",
    ))
    blocos.append(card(
        "Idade e permanência de cada grupo",
        _grafico(_grafico_bolhas(perfis), 410),
    ))
    blocos.append(interpretacao(
        "Cada bolha é um grupo e o tamanho mostra quantos animais ele reúne. "
        "As bolhas ficam quase na mesma altura (próximas à linha tracejada de referência): "
        "mesmo com idades bem diferentes, a permanência mediana muda pouco. Os dois grupos "
        "mais novos têm idades parecidas; para separá-los, o agrupamento também usou sexo, "
        "condição, tipo e data de entrada, que este resumo não mostra."
    ))
else:
    blocos.append(card(
        "Grupos encontrados",
        _grafico(
            _figura_indisponivel(
                "Perfis ainda não exportados. Execute o notebook, gere cluster_profiles.csv "
                "e coloque o arquivo em Dashboard/data."
            ),
            300,
        ),
        a_fazer(
            "depois de executar a célula de exportação do notebook, coloque "
            "cluster_profiles.csv na pasta Dashboard/data."
        ),
    ))

# 2) Método: cotovelo e silhueta, no final
blocos.append(html.H2("Como chegamos a esses grupos", className="secao-titulo"))
if metricas is not None:
    k_escolhido, k_melhor = _escolher_k(metricas, perfis)
    fig_cotovelo, fig_silhueta, sil = _figuras_metodo(metricas, k_escolhido)
    maior = " (a maior entre as testadas)" if k_escolhido == k_melhor else ""

    blocos.append(grade(
        card(
            "Quantos grupos usar?",
            _grafico(fig_cotovelo, 350),
            html.P(
                "Quanto menor a inércia, mais parecidos são os animais dentro de cada "
                "grupo. A curva desce de forma gradual, sem uma 'quebra' brusca (cotovelo nítido), "
                "então o k foi definido pelo pico do gráfico ao lado (silhueta).",
                className="nota-grafico",
            ),
        ),
        card(
            "Os grupos são bem separados?",
            _grafico(fig_silhueta, 350),
            html.P(
                "A silhueta vai de −1 a 1 e, quanto mais perto de 1, mais distintos são "
                f"os grupos. Com k = {k_escolhido} ela vale {_br(sil, 3)}{maior}, "
                f"{_faixa_silhueta(sil)}.",
                className="nota-grafico",
            ),
        ),
        colunas=2,
    ))
    blocos.append(conclusao(
        "Os grupos ajudam a resumir quem chega ao abrigo, mas a separação entre eles "
        f"é fraca (silhueta de {_br(sil, 3)}). Isso ocorre porque características de abrigo "
        "são contínuas (não existem barreiras rígidas entre um filhote de 10 meses e um jovem "
        "de 1 ano). Use os perfis como tendências gerais, não como categorias isoladas."
    ))
else:
    mensagem = (
        "Resultados de clusterização não encontrados. Execute a seção de K-Means "
        "no notebook e copie cluster_metrics.csv para a pasta Dashboard/data."
    )
    blocos.append(grade(
        card("Quantos grupos usar?", _grafico(_figura_indisponivel(mensagem), 300)),
        card("Os grupos são bem separados?", _grafico(_figura_indisponivel(mensagem), 300)),
        colunas=2,
    ))

layout = html.Div(blocos)
