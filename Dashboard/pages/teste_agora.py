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
    {"label": "🌲 Random Forest (Melhor Acurácia: ~77,4% | Recomendado)", "value": "Random Forest"},
    {"label": "📈 Regressão Logística (Modelo Linear: ~75,3%)", "value": "Regressão Logística"},
    {"label": "👥 KNN — K-Vizinhos Mais Próximos (~74,7%)", "value": "KNN (K-Nearest Neighbors)"},
]

# Informações de suporte a cada modelo
MODELOS_INFO = {
    "Random Forest": "Combina múltiplas árvores de decisão e pondera não linearmente as características. Apresentou o maior equilíbrio (F1 macro ~0,53) e captou melhor os padrões de entrada do Austin Animal Center.",
    "Regressão Logística": "Modelo paramétrico linear que calcula as probabilidades por funções logísticas. Apresenta alta taxa de acerto para a classe majoritária (Curta), mas menor sensibilidade para estadias médias e longas.",
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
                            html.Button("🐱 Filhote de Gato Saudável", id="btn-preset-filhote-gato", className="btn-preset", n_clicks=0),
                            html.Button("🐕 Cão Adulto Resgatado na Rua", id="btn-preset-cao-rua", className="btn-preset", n_clicks=0),
                            html.Button("🐕 Cão Idoso e Doente do Tutor", id="btn-preset-cao-idoso", className="btn-preset", n_clicks=0),
                            html.Button("🐦 Ave Silvestre Resgatada", id="btn-preset-ave", className="btn-preset", n_clicks=0),
                            html.Button("😿 Gato Adulto Doente do Tutor", id="btn-preset-gato-doente", className="btn-preset", n_clicks=0),
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
                    "🐾 Calcular Previsão de Permanência",
                    id="btn-prever",
                    className="btn-primario",
                    n_clicks=0,
                )
            ],
            style={"margin": "16px 0 24px"},
        ),

        # Seção de Resultados da Previsão
        card(
            "4. Resultado da Previsão de Permanência",
            html.Div(id="resultado-previsao-container"),
        ),

        interpretacao(
            "As previsões refletem as relações aprendidas a partir do histórico do Austin Animal Center. "
            "A classe 'Curta' abrange animais que permanecem até 14 dias; 'Média' entre 15 e 45 dias; e 'Longa' acima de 45 dias. "
            "Como observado na análise SHAP, a idade na admissão, a espécie e a condição de saúde são fatores determinantes para a probabilidade de adoção rápida ou permanência prolongada."
        ),

        conclusao(
            "O uso interativo do modelo permite que os gestores do abrigo identifiquem, logo no primeiro dia de admissão, "
            "animais com maior propensão à permanência longa (ex.: animais idosos, doentes ou de espécies menos procuradas), "
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
        Input("btn-preset-gato-doente", "n_clicks"),
    ],
    prevent_initial_call=True,
)
def preencher_cenarios_rapidos(btn_gato, btn_cao, btn_idoso, btn_ave, btn_gato_doente):
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
    elif button_id == "btn-preset-gato-doente":
        # Gato adulto doente entregue pelo tutor — perfil de maior risco de permanência longa para gatos.
        # Na base real, gatos + Owner Surrender + Sick têm a maior concentração de casos de estadia média e longa.
        return "Cat", "Intact Male", 7, 0, "Sick", "Owner Surrender", 6, "Tuesday", 14

    return dash.no_update


@callback(
    Output("resultado-previsao-container", "children"),
    [
        Input("btn-prever", "n_clicks"),
        Input("teste-modelo-select", "value"),
    ],
    [
        State("input-animal-type", "value"),
        State("input-sex", "value"),
        State("input-idade-anos", "value"),
        State("input-idade-meses", "value"),
        State("input-condicao", "value"),
        State("input-tipo-entrada", "value"),
        State("input-mes", "value"),
        State("input-dia-semana", "value"),
        State("input-hora", "value"),
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

    anos = int(idade_anos) if idade_anos is not None else 0
    meses = int(idade_meses) if idade_meses is not None else 0
    dias_idade = max(1, (anos * 365) + (meses * 30))

    # Monta a linha com os mesmos atributos originais
    amostra = {
        "animal_type": str(animal_type or "Dog"),
        "age_upon_intake_(days)": float(dias_idade),
        "sex_upon_intake": str(sex_upon_intake or "Neutered Male"),
        "intake_condition": str(condicao or "Normal"),
        "intake_type": str(tipo_entrada or "Stray"),
        "intake_month": int(mes or 6),
        "intake_year": 2024,
        "intake_weekday": str(dia_semana or "Monday"),
        "intake_hour": float(hora or 12),
    }

    df_amostra = pd.DataFrame([amostra])

    # One-hot encoding alinhado exatamente às colunas de treino
    df_encoded = pd.get_dummies(df_amostra, columns=BUNDLE["categorical_cols"], drop_first=True)
    for col in BUNDLE["encoded_columns"]:
        if col not in df_encoded.columns:
            df_encoded[col] = 0

    df_encoded = df_encoded[BUNDLE["encoded_columns"]]
    df_encoded[BUNDLE["numeric_features"]] = BUNDLE["scaler"].transform(
        df_encoded[BUNDLE["numeric_features"]]
    )

    # Executa a predição e probabilidades
    pred_categoria = modelo.predict(df_encoded)[0]
    probabilidades = modelo.predict_proba(df_encoded)[0]

    # Normaliza mapeamento de classes
    classes_modelo = list(modelo.classes_)
    prob_dict = {}
    for cls_name, prob in zip(classes_modelo, probabilidades):
        nome_norm = "Média" if "di" in cls_name else cls_name
        prob_dict[nome_norm] = float(prob)

    categoria_norm = "Média" if "di" in pred_categoria else pred_categoria

    cor_categoria = tema.CORES_PERMANENCIA.get(categoria_norm, tema.PRIMARIA)

    detalhe_categoria = {
        "Curta": "Permanência prevista de até 14 dias no abrigo. Alta probabilidade de adoção ou devolução rápida ao tutor.",
        "Média": "Permanência prevista entre 15 e 45 dias no abrigo. Requer monitoramento e engajamento moderado.",
        "Longa": "Permanência prevista de mais de 45 dias no abrigo. Animal com perfil crítico que requer intervenções prioritárias.",
    }.get(categoria_norm, "")

    # Gráfico de probabilidades por categoria
    categorias_ordem = ["Curta", "Média", "Longa"]
    probs_ordenadas = [prob_dict.get(c, 0.0) * 100 for c in categorias_ordem]
    cores_barras = [tema.CORES_PERMANENCIA[c] for c in categorias_ordem]

    fig_prob = go.Figure(
        go.Bar(
            x=probs_ordenadas,
            y=categorias_ordem,
            orientation="h",
            marker_color=cores_barras,
            text=[f"{p:.1f}%" for p in probs_ordenadas],
            textposition="outside",
            cliponaxis=False,
            hovertemplate="<b>%{y}</b>: %{x:.1f}% de chance<extra></extra>",
        )
    )

    fig_prob.update_layout(
        template=tema.TEMPLATE,
        title="Probabilidade Estimada para Cada Categoria de Permanência",
        xaxis=dict(range=[0, 105], ticksuffix="%", title="Probabilidade (%)"),
        yaxis=dict(autorange="reversed", title=""),
        height=260,
        margin=dict(l=70, r=60, t=50, b=40),
    )

    # Identificação do perfil K-Means correspondente
    if dias_idade < 365:
        perfil_kmeans = "Filhotes (Idade mediana ~9 meses)"
        cor_perfil = tema.CORES_CLUSTER[0]
    elif dias_idade <= 4 * 365:
        perfil_kmeans = "Jovens (Idade mediana ~1 ano)"
        cor_perfil = tema.CORES_CLUSTER[1]
    else:
        perfil_kmeans = "Idosos (Idade mediana ~8 anos)"
        cor_perfil = tema.CORES_CLUSTER[2]

    return html.Div(
        [
            html.Div(
                [
                    html.Div(
                        [
                            html.Span("Categoria Prevista", className="rotulo", style={"color": "#fff", "opacity": 0.9}),
                            html.Div(f"Estadia {categoria_norm}", className="resultado-badge"),
                            html.Div(detalhe_categoria, className="resultado-detalhe"),
                        ],
                        className="resultado-box",
                        style={"backgroundColor": cor_categoria},
                    ),
                ]
            ),
            dcc.Graph(figure=fig_prob, config={"displayModeBar": False, "responsive": True}),
            html.Div(
                [
                    html.Div(
                        [
                            html.Strong("Grupo no K-Means: "),
                            html.Span(perfil_kmeans, style={"color": cor_perfil, "fontWeight": "600"}),
                        ],
                        style={"fontSize": "14px", "marginBottom": "6px"},
                    ),
                    html.Div(
                        [
                            html.Strong("Modelo utilizado no teste: "),
                            html.Span(f"{modelo_nome} ({MODELOS_INFO.get(modelo_nome, '')})"),
                        ],
                        style={"fontSize": "13px", "color": tema.TEXTO_SEC},
                    ),
                ],
                style={"marginTop": "14px", "padding": "12px", "background": tema.FUNDO, "borderRadius": "10px"},
            ),
        ]
    )
