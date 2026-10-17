"""Página inicial (landing): resumo do projeto e menu de cartões. Responsável: P1."""
import dash
from dash import dcc, html

from componentes import kpi

dash.register_page(__name__, path="/", name="Início", order=0)

# Cartões do menu: (caminho, ícone, título, pergunta que a página responde)
MENU = [
    ("/dados", "📊", "Os dados", "Quanto tempo os animais ficam no abrigo?"),
    ("/perfis", "🧩", "Perfis", "Existem tipos de animais com estadias diferentes?"),
    ("/modelos", "🤖", "Modelos", "Dá para prever a permanência de um animal?"),
    ("/explicabilidade", "🔍", "Explicabilidade e app", "O que pesa na previsão e como ajudar na adoção?"),
]

layout = html.Div(
    [
        html.Section(
            [
                html.H1("Quanto tempo um animal espera por um lar?", className="hero-titulo"),
                html.P(
                    "Analisamos quase 80 mil registros do Austin Animal Center para descobrir "
                    "o que faz um animal ficar mais tempo no abrigo e se é possível prever isso "
                    "no momento da entrada.",
                    className="hero-texto",
                ),
            ],
            className="hero",
        ),
        html.Section(
            [
                kpi("79.672", "animais analisados", "registros de entrada e saída"),
                kpi("4,99 dias", "mediana de permanência", "metade fica menos que isso"),
                kpi("3", "perfis de animais", "encontrados por agrupamento (K-Means)"),
                kpi("77,4%", "acurácia do melhor modelo", "Random Forest. F1 macro: 0,53"),
            ],
            className="grade grade-4",
        ),
        html.P(
            "A acurácia é alta porque a maioria dos animais fica pouco tempo. "
            "O F1 macro mostra que prever estadias médias e longas ainda é difícil.",
            className="nota-kpi",
        ),
        html.H2("Explore o projeto", className="secao-titulo"),
        html.Section(
            [
                dcc.Link(
                    [
                        html.Div(icone, className="menu-icone"),
                        html.H3(titulo),
                        html.P(pergunta),
                        html.Span("Abrir →", className="menu-abrir"),
                    ],
                    href=caminho,
                    className="menu-card",
                )
                for caminho, icone, titulo, pergunta in MENU
            ],
            className="grade grade-4",
        ),
    ]
)
