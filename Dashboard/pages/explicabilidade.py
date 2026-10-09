"""Explicabilidade e app. Responsável: P1 (app) e P3 (SHAP). minha parte enquanto p1? montar o esqueleto. pode seguir P3."""
import dash
from dash import dcc, html

from componentes import a_fazer, cabecalho_pagina, card, conclusao, interpretacao
import tema  # cores: tema.CORES_PERMANENCIA, tema.PRIMARIA, ...

dash.register_page(__name__, path="/explicabilidade", name="Explicabilidade e app", order=4)

layout = html.Div(
    [
        cabecalho_pagina(
            "O que pesa na previsão e como ajudar na adoção?",
            "SHAP do Random Forest e o aplicativo de adoção.",
        ),
        # TODO (P1 (app) e P3 (SHAP)): substituir pelo gráfico real. Ex.: card("Título", dcc.Graph(figure=fig))
        card("O que mais influencia a previsão", a_fazer("gráfico desta seção")),
        interpretacao("TODO: explique em 2 a 3 linhas o que o gráfico mostra, para quem não conhece o projeto."),
        conclusao("TODO: uma frase com a conclusão desta página."),
    ]
)
