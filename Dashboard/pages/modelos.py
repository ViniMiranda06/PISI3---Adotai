"""Modelos. Responsável: P4. esqueleto deixado para ajudar a se ter uma base"""
import dash
from dash import dcc, html

from componentes import a_fazer, cabecalho_pagina, card, conclusao, interpretacao
import tema  # cores: tema.CORES_PERMANENCIA, tema.PRIMARIA, ...

dash.register_page(__name__, path="/modelos", name="Modelos", order=3)

layout = html.Div(
    [
        cabecalho_pagina(
            "Dá para prever a permanência de um animal?",
            "Random Forest, Regressão Logística e KNN, com e sem SMOTE.",
        ),
        # TODO (P4): substituir pelo gráfico real. Ex.: card("Título", dcc.Graph(figure=fig))
        card("Comparação dos modelos", a_fazer("gráfico desta seção")),
        interpretacao("TODO: explique em 2 a 3 linhas o que o gráfico mostra, para quem não conhece o projeto."),
        conclusao("TODO: uma frase com a conclusão desta página."),
    ]
)
