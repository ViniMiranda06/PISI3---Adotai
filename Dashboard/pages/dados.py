"""Os dados. Responsável: P2, deixando um esqueleto para um pontapé inicial."""
import dash
from dash import dcc, html

from componentes import a_fazer, cabecalho_pagina, card, conclusao, interpretacao
import tema  # cores: tema.CORES_PERMANENCIA, tema.PRIMARIA, ...

dash.register_page(__name__, path="/dados", name="Os dados", order=1)

layout = html.Div(
    [
        cabecalho_pagina(
            "Quanto tempo os animais ficam no abrigo?",
            "Distribuição da permanência, por espécie e por tipo de entrada.",
        ),
        # TODO (P2): substituir pelo gráfico real. Ex.: card("Título", dcc.Graph(figure=fig))
        card("Distribuição da permanência", a_fazer("gráfico desta seção")),
        interpretacao("TODO: explique em 2 a 3 linhas o que o gráfico mostra, para quem não conhece o projeto."),
        conclusao("TODO: uma frase com a conclusão desta página."),
    ]
)
