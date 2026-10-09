"""Perfis. Responsável: P3. esqueleto montado para dar um pontapé inicial"""
import dash
from dash import dcc, html

from componentes import a_fazer, cabecalho_pagina, card, conclusao, interpretacao
import tema  # cores: tema.CORES_PERMANENCIA, tema.PRIMARIA, ...

dash.register_page(__name__, path="/perfis", name="Perfis", order=2)

layout = html.Div(
    [
        cabecalho_pagina(
            "Existem tipos de animais com estadias diferentes?",
            "Agrupamento K-Means: quantos grupos e como é cada um.",
        ),
        # TODO (P3): substituir pelo gráfico real. Ex.: card("Título", dcc.Graph(figure=fig))
        card("Escolha do número de grupos", a_fazer("gráfico desta seção")),
        interpretacao("TODO: explique em 2 a 3 linhas o que o gráfico mostra, para quem não conhece o projeto."),
        conclusao("TODO: uma frase com a conclusão desta página."),
    ]
)
