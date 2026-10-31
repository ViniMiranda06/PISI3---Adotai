"""Página "Teste agora": o usuário descreve um animal e vê a previsão de permanência.

ESQUELETO. Quem for implementar: siga o roteiro das outras páginas
(pergunta -> formulário/gráfico -> "o que isso significa" -> conclusão) e
REMOVA os avisos `a_fazer(...)` conforme cada parte ficar pronta.
"""
from pathlib import Path

import dash
from dash import Input, Output, State, callback, dcc, html  # noqa: F401  (usados na implementação)

from componentes import a_fazer, cabecalho_pagina, card, conclusao, grade, interpretacao
import tema  # noqa: F401  (usado na implementação)

dash.register_page(
    __name__,
    path="/teste-agora",
    name="Teste agora",
    order=5,  # depois de "Explicabilidade e app" (order=4)
)

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
BUNDLE_PATH = DATA_DIR / "models_bundle.joblib"

# TODO 1: carregar o bundle UMA vez, no import da página, tolerando falha:
#   import joblib
#   def carregar_bundle():
#       if not BUNDLE_PATH.exists():
#           return None
#       try:
#           return joblib.load(BUNDLE_PATH)
#       except Exception:
#           return None
#   BUNDLE = carregar_bundle()
BUNDLE = None


# TODO 2: função pura de previsão (fácil de testar sem abrir o Dash):
#   def prever(bundle, modelo_nome, entrada: dict) -> dict[str, float]:
#       """Devolve {'Curta': p1, 'Média': p2, 'Longa': p3}."""
#       ...


layout = html.Div(
    [
        cabecalho_pagina(
            "Qual será o tempo de permanência deste animal?",
            "Descreva um animal na entrada do abrigo e veja o que os modelos preveem.",
        ),
        grade(
            card(
                "Dados do animal",
                # TODO 3: formulário. Dropdowns para as colunas categóricas
                # (use BUNDLE["options"]), campos numéricos para idade, mês,
                # hora etc., dropdown de modelo e botão "Prever".
                # Classes de CSS prontas em assets/style.css:
                #   .form-grupo, .form-label, .form-dica, .btn-preset, .btn-primario
                a_fazer("formulário com as características do animal."),
            ),
            card(
                "Previsão",
                # TODO 4: resultado. Caixa com a categoria mais provável
                # (.resultado-box / .resultado-badge / .resultado-detalhe) e um
                # gráfico de barras com a probabilidade de Curta/Média/Longa.
                a_fazer("resultado da previsão e probabilidades por categoria."),
            ),
            colunas=2,
        ),
        # TODO 5: textos finais (2 a 3 linhas, linguagem simples, sem jargão).
        interpretacao(
            "Texto provisório: explique aqui como ler as probabilidades e por que "
            "a previsão é uma estimativa, não uma garantia."
        ),
        conclusao("Texto provisório: conclusão da página em uma ou duas frases."),
    ]
)


# TODO 6: callbacks (ex.: botão "Prever" -> resultado). Cuidado com ids únicos:
# prefixe com "teste-" para não colidir com ids de outras páginas.
#
# @callback(
#     Output("teste-resultado", "children"),
#     Input("teste-btn-prever", "n_clicks"),
#     State("teste-animal-type", "value"),
#     ...
#     prevent_initial_call=True,
# )
# def atualizar_resultado(n_clicks, animal_type, ...):
#     ...
