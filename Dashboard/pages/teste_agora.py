"""Página interativa de teste e simulação de previsibilidade de novos animais."""

from pathlib import Path
import dash
from dash import Input, Output, State, callback, dcc, html
import joblib
import pandas as pd
import plotly.graph_objects as go

from componentes import cabecalho_pagina, card, conclusao, grade, interpretacao
import tema

dash.register_page(
    __name__,
    path="/teste-agora",
    name="Teste agora",
    order=5,
)

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
BUNDLE_PATH = DATA_DIR / "models_bundle.joblib"


def carregar_bundle():
    """Carrega os modelos treinados e os metadados de pré-processamento."""
    if not BUNDLE_PATH.exists():
        return None
    try:
        return joblib.load(BUNDLE_PATH)
    except Exception:
        return None


BUNDLE = carregar_bundle()

# Mapeamentos amigáveis para interface em Português
ESPECIES_OPCOES = [
    {"label": "🐕 Cão (Dog)", "value": "Dog"},
    {"label": "🐱 Gato (Cat)", "value": "Cat"},
    {"label": "🐦 Ave (Bird)", "value": "Bird"},
    {"label": "🐾 Outras espécies (Other)", "value": "Other"},
    {"label": "🐎 Animal de criação (Livestock)", "value": "Livestock"},
]

SEXO_OPCOES = [
    {"label": "Macho Castrado (Neutered Male)", "value": "Neutered Male"},
    {"label": "Fêmea Castrada (Spayed Female)", "value": "Spayed Female"},
    {"label": "Macho Não Castrado (Intact Male)", "value": "Intact Male"},
    {"label": "Fêmea Não Castrada (Intact Female)", "value": "Intact Female"},
    {"label": "Desconhecido / Não informado (Unknown)", "value": "Unknown"},
]

CONDICAO_OPCOES_BASE = [
    {"label": "Normal / Saudável (Normal)", "value": "Normal"},
    {"label": "Ferido / Lesionado (Injured)", "value": "Injured"},
    {"label": "Doente (Sick)", "value": "Sick"},
    {"label": "Filhote em amamentação (Nursing)", "value": "Nursing"},
    {"label": "Idoso / Debilitado (Aged)", "value": "Aged"},
    {"label": "Feral / Arisco (Feral)", "value": "Feral"},
    {"label": "Outro estado (Other)", "value": "Other"},
]

OPCAO_PREGNANT = {"label": "Prenha (Pregnant)", "value": "Pregnant"}
# Como o sexo padrão inicial é Macho Castrado, a opção Prenha não aparece por padrão
CONDICAO_OPCOES = CONDICAO_OPCOES_BASE

# Opções de entrada: no banco de dados, 'Wildlife' ocorreu EXCLUSIVAMENTE em 'Other' (3.396 casos) e 'Bird' (68 casos).
# Cães e Gatos possuem ZERO registros de Wildlife.
TIPO_ENTRADA_OPCOES_DOMESTICOS = [
    {"label": "Animal de rua / Encontrado (Stray)", "value": "Stray"},
    {"label": "Entregue pelo tutor (Owner Surrender)", "value": "Owner Surrender"},
    {"label": "Assistência pública / Resgate (Public Assist)", "value": "Public Assist"},
    {"label": "Abandonado (Abandoned)", "value": "Abandoned"},
    {"label": "Pedido de eutanásia médica (Euthanasia Request)", "value": "Euthanasia Request"},
]

OPCAO_WILDLIFE = {"label": "Animal silvestre resgatado (Wildlife)", "value": "Wildlife"}
TIPO_ENTRADA_OPCOES = TIPO_ENTRADA_OPCOES_DOMESTICOS

DIAS_SEMANA_OPCOES = [
    {"label": "Segunda-feira", "value": "Monday"},
    {"label": "Terça-feira", "value": "Tuesday"},
    {"label": "Quarta-feira", "value": "Wednesday"},
    {"label": "Quinta-feira", "value": "Thursday"},
    {"label": "Sexta-feira", "value": "Friday"},
    {"label": "Sábado", "value": "Saturday"},
    {"label": "Domingo", "value": "Sunday"},
]

MESES_OPCOES = [
    {"label": "Janeiro (Mês 1)", "value": 1},
    {"label": "Fevereiro (Mês 2)", "value": 2},
    {"label": "Março (Mês 3)", "value": 3},
    {"label": "Abril (Mês 4)", "value": 4},
    {"label": "Maio (Mês 5)", "value": 5},
    {"label": "Junho (Mês 6)", "value": 6},
    {"label": "Julho (Mês 7)", "value": 7},
    {"label": "Agosto (Mês 8)", "value": 8},
    {"label": "Setembro (Mês 9)", "value": 9},
    {"label": "Outubro (Mês 10)", "value": 10},
    {"label": "Novembro (Mês 11)", "value": 11},
    {"label": "Dezembro (Mês 12)", "value": 12},
]

MODELOS_OPCOES = [
    {"label": "🌲 Random Forest (modelo final | F1 macro ~0,66 | Recomendado)", "value": "Random Forest"},
    {"label": "📈 Regressão Logística (linha de base | F1 macro ~0,58)", "value": "Regressão Logística"},
    {"label": "👥 KNN — K-Vizinhos Mais Próximos (comparação)", "value": "KNN (K-Nearest Neighbors)"},
]

# Cores das classes desta página. O tema.py da main-dash tem Curta/Média/Longa;
# a classe Prolongada (> 14 dias) usa a cor que era da Longa.
COR_CLASSE = {
    "Curta": tema.CORES_PERMANENCIA.get("Curta", "#2A9D8F"),
    "Prolongada": tema.CORES_PERMANENCIA.get("Prolongada", tema.CORES_PERMANENCIA.get("Longa", "#D1495B")),
}
COR_ATENCAO = tema.CORES_PERMANENCIA.get("Média", "#F2B134")

# Proporção real de animais com mais de 14 dias na base (24,6%)
MEDIA_ABRIGO = 0.246

# Precisão e recall do modelo final na classe Prolongada (conjunto de teste do notebook)
CONFIANCA_RF = "De cada 10 animais que o modelo final marca como Prolongada, 4 a 5 realmente passam de 14 dias; e ele encontra cerca de 6 em cada 10 animais que passam."

NIVEIS = {
    "prolongada": {
        "titulo": "Estadia Prolongada",
        "texto": "Permanência prevista de mais de 14 dias no abrigo.",
        "acao": "Ação sugerida: incluir em divulgação prioritária desde o primeiro dia, buscar lar temporário e agendar os cuidados necessários.",
    },
    "atencao": {
        "titulo": "Estadia Curta",
        "texto": "Permanência prevista de até 14 dias, mas o risco de passar disso está acima da média do abrigo.",
        "acao": "Ação sugerida: acompanhar o animal e reavaliar após 1 semana; se ainda estiver no abrigo, reforçar a divulgação.",
    },
    "baixo": {
        "titulo": "Estadia Curta",
        "texto": "Permanência prevista de até 14 dias, com risco abaixo da média do abrigo de ficar mais tempo.",
        "acao": "Ação sugerida: fluxo normal de adoção ou devolução ao tutor.",
    },
}

ROTULOS_CAMPOS = {
    "Dog": "Cão", "Cat": "Gato", "Bird": "Ave", "Other": "Outro", "Livestock": "Animal de fazenda",
}

# Informações de suporte a cada modelo
MODELOS_INFO = {
    "Random Forest": "Combina várias árvores de decisão. É o modelo final do projeto: versão regularizada e com pesos por classe, com o melhor equilíbrio entre encontrar animais de permanência prolongada e não decorar o treino.",
    "Regressão Logística": "Modelo linear que calcula a probabilidade por uma função logística. Treinado com pesos por classe; serve como linha de base simples para comparar com a Random Forest.",
    "KNN (K-Nearest Neighbors)": "Compara os atributos do animal cadastrado com os animais históricos mais parecidos no banco de dados para determinar a permanência mais provável por vizinhança.",
}

# Layout da página
layout = html.Div(
    [
        cabecalho_pagina(
            "Qual será o tempo de permanência deste animal?",
            "Insira as informações de um animal na entrada do abrigo, selecione o algoritmo de Machine Learning e teste a previsão em tempo real.",
        ),


        # Seção de seleção do modelo e Presets rápidos
        card(
            "1. Escolha o Modelo de Machine Learning & Cenários Prontos",
            html.Div(
                [
                    html.Label("Modelo preditivo:", className="form-label"),
                    dcc.Dropdown(
                        id="teste-modelo-select",
                        options=MODELOS_OPCOES,
                        value="Random Forest",
                        clearable=False,
                        style={"color": "#222"},
                    ),
                    html.P(
                        id="teste-modelo-desc",
                        className="nota-grafico",
                        style={"marginTop": "8px"},
                    ),
                    html.Hr(style={"borderColor": tema.LINHAS, "margin": "16px 0"}),
                    html.Div(
                        [
                            html.Span("Ou teste um cenário rápido com 1 clique:", style={"fontSize": "14px", "fontWeight": "600", "display": "block", "marginBottom": "8px"}),
                            html.Span("Tendem a sair em até 14 dias:", style={"fontSize": "13px", "display": "block", "margin": "4px 0"}),
                            html.Button("🐱 Filhote de Gato Saudável", id="btn-preset-filhote-gato", className="btn-preset", n_clicks=0),
                            html.Button("🐕 Cão Adulto Resgatado na Rua", id="btn-preset-cao-rua", className="btn-preset", n_clicks=0),
                            html.Button("🐦 Ave Silvestre Resgatada", id="btn-preset-ave", className="btn-preset", n_clicks=0),
                            html.Button("🐕 Cão Idoso e Debilitado do Tutor", id="btn-preset-cao-idoso", className="btn-preset", n_clicks=0),
                            html.Span("Tendem a ficar mais de 14 dias:", style={"fontSize": "13px", "display": "block", "margin": "10px 0 4px"}),
                            html.Button("🐈 Gata Adulta Entregue pelo Tutor", id="btn-preset-gata-tutor", className="btn-preset", n_clicks=0),
                            html.Button("🩹 Cão Jovem Ferido na Rua", id="btn-preset-cao-ferido", className="btn-preset", n_clicks=0),
                            html.Button("🍼 Filhote de Cão em Amamentação", id="btn-preset-filhote-cao-amamentacao", className="btn-preset", n_clicks=0),
                        ]
                    ),
                ]
            ),
        ),

        # Formulário de entrada dos atributos do animal
        grade(
            card(
                "2. Características do Animal",
                html.Div(
                    [
                        html.Div(
                            [
                                html.Label("Espécie:", className="form-label"),
                                dcc.Dropdown(
                                    id="input-animal-type",
                                    options=ESPECIES_OPCOES,
                                    value="Dog",
                                    clearable=False,
                                    style={"color": "#222"},
                                ),
                        ],
                            className="form-grupo",
                        ),
                        html.Div(
                            [
                                html.Label("Sexo e Castração na Entrada:", className="form-label"),
                                dcc.Dropdown(
                                    id="input-sex",
                                    options=SEXO_OPCOES,
                                    value="Neutered Male",
                                    clearable=False,
                                    style={"color": "#222"},
                                ),
                        ],
                            className="form-grupo",
                        ),
                        html.Div(
                            [
                                html.Label("Idade estimada na admissão:", className="form-label"),
                                html.Div(
                                    [
                                        html.Div(
                                            [
                                                html.Span("Anos:", style={"fontSize": "13px", "color": tema.TEXTO_SEC}),
                                                dcc.Input(
                                                    id="input-idade-anos",
                                                    type="number",
                                                    min=0,
                                                    max=25,
                                                    step=1,
                                                    value=2,
                                                    style={"width": "100%", "padding": "8px", "borderRadius": "8px", "border": f"1px solid {tema.LINHAS}"},
                                                ),
                        ],
                                            style={"flex": "1"},
                                        ),
                                        html.Div(
                                            [
                                                html.Span("Meses:", style={"fontSize": "13px", "color": tema.TEXTO_SEC}),
                                                dcc.Input(
                                                    id="input-idade-meses",
                                                    type="number",
                                                    min=0,
                                                    max=11,
                                                    step=1,
                                                    value=0,
                                                    style={"width": "100%", "padding": "8px", "borderRadius": "8px", "border": f"1px solid {tema.LINHAS}"},
                                                ),
                        ],
                                            style={"flex": "1"},
                                        ),
                        ],
                                    style={"display": "flex", "gap": "12px"},
                                ),
                                html.Div(id="label-idade-dias", className="form-dica"),
                        ],
                            className="form-grupo",
                        ),
                    ]
                ),
            ),
            card(
                "3. Condições de Admissão no Abrigo",
                html.Div(
                    [
                        html.Div(
                            [
                                html.Label("Condição de Saúde:", className="form-label"),
                                dcc.Dropdown(
                                    id="input-condicao",
                                    options=CONDICAO_OPCOES,
                                    value="Normal",
                                    clearable=False,
                                    style={"color": "#222"},
                                ),
                        ],
                            className="form-grupo",
                        ),
                        html.Div(
                            [
                                html.Label("Tipo de Entrada no Abrigo:", className="form-label"),
                                dcc.Dropdown(
                                    id="input-tipo-entrada",
                                    options=TIPO_ENTRADA_OPCOES,
                                    value="Stray",
                                    clearable=False,
                                    style={"color": "#222"},
                                ),
                        ],
                            className="form-grupo",
                        ),
                        html.Div(
                            [
                                html.Label("Momento da Entrada (Mês / Dia da semana / Horário):", className="form-label"),
                                html.Div(
                                    [
                                        dcc.Dropdown(
                                            id="input-mes",
                                            options=MESES_OPCOES,
                                            value=5,
                                            clearable=False,
                                            style={"flex": "1", "color": "#222"},
                                        ),
                                        dcc.Dropdown(
                                            id="input-dia-semana",
                                            options=DIAS_SEMANA_OPCOES,
                                            value="Monday",
                                            clearable=False,
                                            style={"flex": "1", "color": "#222"},
                                        ),
                        ],
                                    style={"display": "flex", "gap": "10px", "marginBottom": "10px"},
                                ),
                                html.Div(
                                    [
                                        html.Span("Hora da entrada (0 a 23h):", style={"fontSize": "13px", "color": tema.TEXTO_SEC}),
                                        dcc.Slider(
                                            id="input-hora",
                                            min=0,
                                            max=23,
                                            step=1,
                                            value=12,
                                            marks={0: "0h", 6: "6h", 12: "12h", 18: "18h", 23: "23h"},
                                            tooltip={"placement": "bottom", "always_visible": False},
                                        ),
                        ]
                                ),
                        ],
                            className="form-grupo",
                        ),
                    ]
                ),
            ),
            colunas=2,
        ),

        # Botão de Ação para acionar a predição
        html.Div(
            [
                html.Button(
                    "📌 Guardar este animal no histórico",
                    id="btn-prever",
                    className="btn-primario",
                    n_clicks=0,
                ),
                html.Div(
                    "A previsão abaixo atualiza sozinha a cada mudança. Use o botão para guardar o animal "
                    "no histórico e comparar cenários.",
                    className="nota-grafico",
                    style={"marginTop": "8px"},
                ),
            ],
            style={"margin": "16px 0 24px"},
        ),

        # Seção de Resultados da Previsão
        card(
            "4. Resultado da Previsão de Permanência",
            html.Div(id="resultado-previsao-container"),
        ),

        dcc.Store(id="historico-store", data=[]),
        card(
            "5. Histórico desta sessão",
            html.Div(
                html.P("Nenhum animal guardado ainda.", className="nota-grafico"),
                id="historico-container",
            ),
        ),

        interpretacao(
            "As previsões refletem as relações aprendidas a partir do histórico do Austin Animal Center. "
            "A classe 'Curta' abrange animais que permanecem até 14 dias e a classe 'Prolongada', acima de 14 dias. "
            "Na análise SHAP do modelo final, a idade na entrada, o tipo de entrada (principalmente a entrega pelo tutor) e a espécie são os atributos que mais pesam na previsão."
        ),

        conclusao(
            "O uso interativo do modelo permite que os gestores do abrigo identifiquem, logo no primeiro dia de admissão, "
            "animais com maior propensão à permanência prolongada (ex.: gatos entregues pelo tutor, filhotes em amamentação ou cães jovens feridos), "
            "possibilitando ações preventivas como campanhas prioritárias de adoção, lares temporários e cuidados médicos imediatos."
        ),
    ]
)


@callback(
    Output("teste-modelo-desc", "children"),
    Input("teste-modelo-select", "value"),
)
def atualizar_descricao_modelo(modelo_nome):
    return MODELOS_INFO.get(modelo_nome, "")


@callback(
    Output("label-idade-dias", "children"),
    Input("input-idade-anos", "value"),
    Input("input-idade-meses", "value"),
)
def atualizar_calculo_idade_dias(anos, meses):
    anos = int(anos) if anos is not None else 0
    meses = int(meses) if meses is not None else 0
    dias = (anos * 365) + (meses * 30)
    return f"Equivalente a aproximadamente {dias:,} dias de vida.".replace(",", ".")


@callback(
    [
        Output("input-tipo-entrada", "options"),
        Output("input-tipo-entrada", "value", allow_duplicate=True),
    ],
    Input("input-animal-type", "value"),
    State("input-tipo-entrada", "value"),
    prevent_initial_call=True,
)
def atualizar_opcoes_tipo_entrada(especie, valor_atual):
    """
    Filtra as opções de tipo de entrada conforme os dados reais do abrigo.
    No Austin Animal Center, 'Wildlife' ocorreu EXCLUSIVAMENTE em aves (Bird) e outros animais silvestres (Other).
    Cães e gatos nunca foram registrados como 'Wildlife'.
    """
    opcoes = list(TIPO_ENTRADA_OPCOES_DOMESTICOS)
    if especie in ["Bird", "Other", "Livestock"]:
        opcoes.insert(3, OPCAO_WILDLIFE)

    # Se a espécie for cão ou gato e o valor anterior era Wildlife, ajusta para Stray
    if especie in ["Dog", "Cat"] and valor_atual == "Wildlife":
        novo_valor = "Stray"
    else:
        novo_valor = valor_atual if valor_atual else "Stray"

    return opcoes, novo_valor


@callback(
    [
        Output("input-condicao", "options"),
        Output("input-condicao", "value", allow_duplicate=True),
    ],
    Input("input-sex", "value"),
    State("input-condicao", "value"),
    prevent_initial_call=True,
)
def atualizar_opcoes_condicao_por_sexo(sexo, condicao_atual):
    """
    Remove a opção 'Prenha (Pregnant)' para machos e fêmeas castradas.
    Machos e fêmeas castradas não engravidam. A opção só é exibida para fêmeas não castradas (Intact Female) ou desconhecido.
    """
    opcoes = list(CONDICAO_OPCOES_BASE)
    machos_ou_castradas = ["Neutered Male", "Intact Male", "Spayed Female"]

    if sexo not in machos_ou_castradas:
        opcoes.insert(5, OPCAO_PREGNANT)

    # Se a condição atual for Pregnant e o sexo virou macho ou castrada, reseta para Normal
    if sexo in machos_ou_castradas and condicao_atual == "Pregnant":
        novo_valor = "Normal"
    else:
        novo_valor = condicao_atual if condicao_atual else "Normal"

    return opcoes, novo_valor


@callback(
    [
        Output("input-animal-type", "value"),
        Output("input-sex", "value"),
        Output("input-idade-anos", "value"),
        Output("input-idade-meses", "value"),
        Output("input-condicao", "value", allow_duplicate=True),
        Output("input-tipo-entrada", "value", allow_duplicate=True),
        Output("input-mes", "value"),
        Output("input-dia-semana", "value"),
        Output("input-hora", "value"),
    ],
    [
        Input("btn-preset-filhote-gato", "n_clicks"),
        Input("btn-preset-cao-rua", "n_clicks"),
        Input("btn-preset-cao-idoso", "n_clicks"),
        Input("btn-preset-ave", "n_clicks"),
        Input("btn-preset-gata-tutor", "n_clicks"),
        Input("btn-preset-cao-ferido", "n_clicks"),
        Input("btn-preset-filhote-cao-amamentacao", "n_clicks"),
    ],
    prevent_initial_call=True,
)
def preencher_cenarios_rapidos(*_cliques):
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update

    button_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if button_id == "btn-preset-filhote-gato":
        # Filhote de gato, saudável, 3 meses
        return "Cat", "Intact Female", 0, 3, "Normal", "Stray", 4, "Saturday", 14
    elif button_id == "btn-preset-cao-rua":
        # Cão adulto jovem, castrado, saudável, 2 anos
        return "Dog", "Neutered Male", 2, 0, "Normal", "Stray", 6, "Monday", 11
    elif button_id == "btn-preset-cao-idoso":
        # Cão idoso (9 anos), não castrado, entregue pelo tutor, debilitado
        return "Dog", "Intact Male", 9, 0, "Aged", "Owner Surrender", 10, "Wednesday", 16
    elif button_id == "btn-preset-ave":
        # Ave silvestre machucada
        return "Bird", "Unknown", 1, 0, "Injured", "Wildlife", 8, "Tuesday", 9
    # Cenários que o modelo final classifica como Prolongada (> 14 dias). Na base real, esses
    # grupos estão entre os que mais passam de 14 dias: gatos saudáveis entregues pelo tutor
    # (~42%), cães feridos de rua com até 2 anos (~37% a 41%) e filhotes de cão em
    # amamentação (~50%), contra ~25% na média do abrigo.
    elif button_id == "btn-preset-gata-tutor":
        # Gata adulta (6 anos), castrada e saudável, entregue pelo tutor
        return "Cat", "Spayed Female", 6, 0, "Normal", "Owner Surrender", 10, "Saturday", 15
    elif button_id == "btn-preset-cao-ferido":
        # Cão jovem (1 ano), não castrado, ferido, encontrado na rua
        return "Dog", "Intact Male", 1, 0, "Injured", "Stray", 5, "Saturday", 17
    elif button_id == "btn-preset-filhote-cao-amamentacao":
        # Filhote de cão (2 meses) ainda em amamentação, encontrado na rua
        return "Dog", "Intact Female", 0, 2, "Nursing", "Stray", 3, "Monday", 15

    return dash.no_update


def _codificar(animal_type, sex_upon_intake, dias_idade, condicao, tipo_entrada, mes, dia_semana, hora):
    """Monta uma linha com os atributos originais e aplica o mesmo pré-processamento do treino."""
    amostra = {
        "animal_type": str(animal_type or "Dog"),
        "age_upon_intake_(days)": float(dias_idade),
        "sex_upon_intake": str(sex_upon_intake or "Neutered Male"),
        "intake_condition": str(condicao or "Normal"),
        "intake_type": str(tipo_entrada or "Stray"),
        "intake_month": int(mes or 6),
        "intake_year": 2018,  # último ano presente nos dados de treino (2013-2018)
        "intake_weekday": str(dia_semana or "Monday"),
        "intake_hour": float(hora or 12),
    }
    df_amostra = pd.DataFrame([amostra])
    # Com uma linha só, drop_first=True apagaria a única categoria de cada coluna e o modelo
    # passaria a ignorar espécie, sexo, condição, tipo de entrada e dia da semana. Por isso
    # geramos todas as colunas e depois alinhamos com as colunas usadas no treino.
    df_encoded = pd.get_dummies(df_amostra, columns=BUNDLE["categorical_cols"])
    df_encoded = df_encoded.reindex(columns=BUNDLE["encoded_columns"], fill_value=0).astype(float)
    df_encoded[BUNDLE["numeric_features"]] = BUNDLE["scaler"].transform(df_encoded[BUNDLE["numeric_features"]])
    return df_encoded


def _prob_prolongada(modelo, df_encoded):
    """Chance de passar de 14 dias. Aceita o modelo retreinado (2 classes) e o antigo (3 classes)."""
    probs = dict(zip(modelo.classes_, modelo.predict_proba(df_encoded)[0]))
    if "Prolongada" in probs:
        return float(probs["Prolongada"])
    # modelo antigo: Média (15-45 dias) + Longa (> 45 dias)
    return float(sum(v for k, v in probs.items() if k != "Curta"))


def _limiar(modelo_nome):
    """O limiar do bundle foi escolhido no notebook para a Random Forest final; os outros usam 0,5."""
    if "limiar_longa" not in BUNDLE:
        return 0.25  # bundle antigo de 3 classes, que raramente passa de 50%
    return float(BUNDLE["limiar_longa"]) if modelo_nome == "Random Forest" else 0.5


def _nivel(prob, limiar):
    if prob >= limiar:
        return "prolongada"
    return "atencao" if prob >= MEDIA_ABRIGO else "baixo"


def _dias_idade(idade_anos, idade_meses):
    anos = int(idade_anos) if idade_anos is not None else 0
    meses = int(idade_meses) if idade_meses is not None else 0
    return max(1, (anos * 365) + (meses * 30))


def _avisos(animal_type, dias_idade, condicao, tipo_entrada):
    """Combinações raras na base real: o modelo prevê, mas com menos exemplos parecidos."""
    avisos = []
    if condicao == "Nursing" and dias_idade >= 365:
        avisos.append("'Filhote em amamentação' quase sempre aparece em animais com menos de 1 ano.")
    if condicao == "Aged" and dias_idade < 7 * 365:
        avisos.append("'Idoso / Debilitado' quase sempre aparece em animais com 7 anos ou mais.")
    if tipo_entrada == "Wildlife" and animal_type in ("Dog", "Cat"):
        avisos.append("Cães e gatos nunca foram registrados como animal silvestre na base.")
    return avisos


def _termometro(prob, limiar):
    """Barra de 0 a 100% com faixas: abaixo da média, acima da média e acima do limiar."""
    fig = go.Figure(
        go.Indicator(
            mode="number+gauge",
            value=prob * 100,
            number={"suffix": "%", "valueformat": ".0f", "font": {"size": 34}},
            gauge={
                "shape": "bullet",
                "axis": {"range": [0, 100], "ticksuffix": "%"},
                "bar": {"color": "#333333", "thickness": 0.35},
                "steps": [
                    {"range": [0, MEDIA_ABRIGO * 100], "color": "#CFEDE8"},
                    {"range": [MEDIA_ABRIGO * 100, limiar * 100], "color": "#FBE7B5"},
                    {"range": [limiar * 100, 100], "color": "#F4C6CC"},
                ],
                "threshold": {"line": {"color": COR_CLASSE["Prolongada"], "width": 3}, "thickness": 0.9,
                              "value": limiar * 100},
            },
            domain={"x": [0.18, 1], "y": [0, 1]},
        )
    )
    fig.update_layout(
        height=130,
        margin=dict(l=10, r=30, t=40, b=20),
        title=dict(text="Chance de passar de 14 dias", x=0, font=dict(size=15)),
        paper_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def _legenda_termometro(limiar):
    def item(cor, txt):
        return html.Span(
            [html.Span(style={"display": "inline-block", "width": "12px", "height": "12px", "background": cor,
                              "borderRadius": "3px", "marginRight": "6px", "verticalAlign": "middle"}), txt],
            style={"marginRight": "16px", "whiteSpace": "nowrap"},
        )
    return html.Div(
        [
            item("#CFEDE8", f"abaixo da média do abrigo (até {MEDIA_ABRIGO * 100:.0f}%)"),
            item("#FBE7B5", f"acima da média, abaixo do limiar ({MEDIA_ABRIGO * 100:.0f}% a {limiar * 100:.0f}%)"),
            item("#F4C6CC", f"acima do limiar ({limiar * 100:.0f}%): Prolongada"),
        ],
        className="nota-grafico",
        style={"display": "flex", "flexWrap": "wrap", "gap": "4px"},
    )


def _comparar_modelos(df_encoded, modelo_escolhido):
    linhas = []
    for nome, modelo in BUNDLE.get("models", {}).items():
        prob = _prob_prolongada(modelo, df_encoded)
        lim = _limiar(nome)
        classe = "Prolongada" if prob >= lim else "Curta"
        estilo = {"fontWeight": "700"} if nome == modelo_escolhido else {}
        linhas.append(html.Tr(
            [
                html.Td(nome, style=estilo),
                html.Td(f"{prob * 100:.0f}%", style={**estilo, "textAlign": "right"}),
                html.Td(f"{lim * 100:.0f}%", style={**estilo, "textAlign": "right"}),
                html.Td(classe, style={**estilo, "color": COR_CLASSE[classe], "paddingLeft": "12px"}),
            ]
        ))
    cab = html.Tr([html.Th("Modelo"), html.Th("Chance > 14 dias", style={"textAlign": "right"}),
                   html.Th("Limiar", style={"textAlign": "right"}), html.Th("Resultado", style={"paddingLeft": "12px"})])
    return html.Table([html.Thead(cab), html.Tbody(linhas)],
                      style={"width": "100%", "fontSize": "14px", "borderCollapse": "collapse"})


@callback(
    Output("resultado-previsao-container", "children"),
    [
        Input("btn-prever", "n_clicks"),
        Input("teste-modelo-select", "value"),
    ],
    [
        Input("input-animal-type", "value"),
        Input("input-sex", "value"),
        Input("input-idade-anos", "value"),
        Input("input-idade-meses", "value"),
        Input("input-condicao", "value"),
        Input("input-tipo-entrada", "value"),
        Input("input-mes", "value"),
        Input("input-dia-semana", "value"),
        Input("input-hora", "value"),
    ],
)
def executar_previsao(
    n_clicks,
    modelo_nome,
    animal_type,
    sex_upon_intake,
    idade_anos,
    idade_meses,
    condicao,
    tipo_entrada,
    mes,
    dia_semana,
    hora,
):
    if BUNDLE is None:
        return html.Div(
            "Erro: Pacote de modelos preditivos não encontrado em Dashboard/data/models_bundle.joblib.",
            className="a-fazer",
        )

    modelos = BUNDLE.get("models", {})
    modelo = modelos.get(modelo_nome)
    if modelo is None:
        return html.Div("Modelo selecionado não disponível.", className="a-fazer")
    dias_idade = _dias_idade(idade_anos, idade_meses)
    df_encoded = _codificar(animal_type, sex_upon_intake, dias_idade, condicao, tipo_entrada, mes, dia_semana, hora)

    prob = _prob_prolongada(modelo, df_encoded)
    limiar = _limiar(modelo_nome)
    nivel = _nivel(prob, limiar)
    info = NIVEIS[nivel]
    cor = {"prolongada": COR_CLASSE["Prolongada"], "atencao": COR_ATENCAO, "baixo": COR_CLASSE["Curta"]}[nivel]

    avisos = _avisos(animal_type, dias_idade, condicao, tipo_entrada)

    # Grupo do K-Means aproximado só pela idade (as faixas usam as idades medianas dos grupos)
    if dias_idade < 365:
        perfil_kmeans, cor_perfil = "Filhotes (idade mediana ~9 meses)", tema.CORES_CLUSTER[0]
    elif dias_idade <= 4 * 365:
        perfil_kmeans, cor_perfil = "Jovens (idade mediana ~1 ano)", tema.CORES_CLUSTER[1]
    else:
        perfil_kmeans, cor_perfil = "Idosos (idade mediana ~8 anos)", tema.CORES_CLUSTER[2]

    confianca = CONFIANCA_RF if modelo_nome == "Random Forest" else (
        "Este modelo serve de comparação; o modelo recomendado é a Random Forest.")

    return html.Div(
        [
            html.Div(
                [
                    html.Span("Categoria Prevista", className="rotulo", style={"color": "#fff", "opacity": 0.9}),
                    html.Div(info["titulo"], className="resultado-badge"),
                    html.Div(
                        f"{info['texto']} Chance estimada de passar de 14 dias: {prob * 100:.0f}% "
                        f"(média do abrigo: ~{MEDIA_ABRIGO * 100:.0f}%; limiar: {limiar * 100:.0f}%).",
                        className="resultado-detalhe",
                    ),
                ],
                className="resultado-box",
                style={"backgroundColor": cor},
            ),
            html.Div(info["acao"], style={"marginTop": "12px", "padding": "10px 14px", "borderRadius": "8px",
                                          "background": tema.FUNDO, "borderLeft": f"4px solid {cor}",
                                          "fontSize": "14px", "fontWeight": "600"}),
            *[html.Div(f"⚠️ Combinação rara: {a}", className="a-fazer", style={"marginTop": "10px"}) for a in avisos],
            dcc.Graph(figure=_termometro(prob, limiar), config={"displayModeBar": False, "responsive": True}),
            _legenda_termometro(limiar),
            html.P(f"Sobre a confiança: {confianca}", className="nota-grafico", style={"marginTop": "10px"}),
            html.H4("Os 3 modelos para este mesmo animal", style={"margin": "18px 0 8px"}),
            _comparar_modelos(df_encoded, modelo_nome),
            html.Div(
                [
                    html.Div(
                        [
                            html.Strong("Grupo no K-Means (aproximado pela idade): "),
                            html.Span(perfil_kmeans, style={"color": cor_perfil, "fontWeight": "600"}),
                        ],
                        style={"fontSize": "14px", "marginBottom": "6px"},
                    ),
                    html.Div(
                        [
                            html.Strong("Modelo utilizado no teste: "),
                            html.Span(f"{modelo_nome} ({MODELOS_INFO.get(modelo_nome, '')})"),
                        ],
                        style={"fontSize": "13px", "color": tema.TEXTO_SEC, "marginBottom": "6px"},
                    ),
                    html.Div(
                        "A previsão considera a entrada em 2018, o último ano dos dados de treino (2013 a 2018).",
                        style={"fontSize": "13px", "color": tema.TEXTO_SEC},
                    ),
                ],
                style={"marginTop": "16px", "padding": "12px", "background": tema.FUNDO, "borderRadius": "10px"},
            ),
        ]
    )


@callback(
    Output("historico-store", "data"),
    Output("historico-container", "children"),
    Input("btn-prever", "n_clicks"),
    State("historico-store", "data"),
    State("teste-modelo-select", "value"),
    State("input-animal-type", "value"),
    State("input-sex", "value"),
    State("input-idade-anos", "value"),
    State("input-idade-meses", "value"),
    State("input-condicao", "value"),
    State("input-tipo-entrada", "value"),
    State("input-mes", "value"),
    State("input-dia-semana", "value"),
    State("input-hora", "value"),
    prevent_initial_call=True,
)
def guardar_no_historico(n_clicks, historico, modelo_nome, animal_type, sex_upon_intake, idade_anos,
                         idade_meses, condicao, tipo_entrada, mes, dia_semana, hora):
    if BUNDLE is None or not n_clicks:
        return dash.no_update, dash.no_update
    modelo = BUNDLE.get("models", {}).get(modelo_nome)
    if modelo is None:
        return dash.no_update, dash.no_update

    dias_idade = _dias_idade(idade_anos, idade_meses)
    df_encoded = _codificar(animal_type, sex_upon_intake, dias_idade, condicao, tipo_entrada, mes, dia_semana, hora)
    prob = _prob_prolongada(modelo, df_encoded)
    classe = "Prolongada" if prob >= _limiar(modelo_nome) else "Curta"

    anos, meses = int(idade_anos or 0), int(idade_meses or 0)
    partes = ([f"{anos} ano" + ("s" if anos > 1 else "")] if anos else []) + \
             ([f"{meses} " + ("meses" if meses > 1 else "mês")] if meses else [])
    idade_txt = " e ".join(partes) or "recém-nascido"
    rotulo = lambda opcoes, v: next((o["label"].split(" (")[0] for o in opcoes if o["value"] == v), v)
    historico = list(historico or [])
    numero = (historico[0]["Nº"] + 1) if historico else 1
    historico.insert(0, {
        "Nº": numero,
        "Animal": ROTULOS_CAMPOS.get(animal_type, animal_type),
        "Idade": idade_txt,
        "Condição": rotulo(CONDICAO_OPCOES_BASE + [OPCAO_PREGNANT], condicao),
        "Entrada": rotulo(TIPO_ENTRADA_OPCOES_DOMESTICOS + [OPCAO_WILDLIFE], tipo_entrada),
        "Modelo": modelo_nome.split(" (")[0],
        "Chance": f"{prob * 100:.0f}%",
        "Resultado": classe,
    })
    historico = historico[:10]

    cab = html.Tr([html.Th(c, style={"textAlign": "left", "paddingRight": "10px"}) for c in historico[0].keys()])
    linhas = [
        html.Tr([
            html.Td(v, style={"paddingRight": "10px",
                              **({"color": COR_CLASSE[h["Resultado"]], "fontWeight": "600"} if k == "Resultado" else {})})
            for k, v in h.items()
        ])
        for h in historico
    ]
    tabela = html.Table([html.Thead(cab), html.Tbody(linhas)],
                        style={"width": "100%", "fontSize": "13px", "borderCollapse": "collapse"})
    return historico, html.Div([tabela, html.P("Mostra os 10 últimos animais guardados.", className="nota-grafico")],
                               style={"overflowX": "auto"})
