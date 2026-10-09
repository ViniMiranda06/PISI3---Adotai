"""
Ponto de entrada para o nosso dashboard!
Rodar com: python app.py    (deve abrir algo como http://127.0.0.1:8050)
"""

import dash
from dash import Dash, Input, Output, dcc, html

import tema

tema.registrar_tema()

app = Dash(
    __name__,
    use_pages=True,
    external_stylesheets=[tema.GOOGLE_FONTS_URL],
    title="Adotai | Permanência em Abrigos",
    suppress_callback_exceptions=True,
)

# As cores em tema.py viram variaveis em CSS
_VARIAVEIS = f"""
:root {{
    --fundo: {tema.FUNDO}; --cartao: {tema.CARTAO};
    --texto: {tema.TEXTO}; --texto-sec: {tema.TEXTO_SEC};
    --primaria: {tema.PRIMARIA}; --secundaria: {tema.SECUNDARIA};
    --linhas: {tema.LINHAS};
    --curta: {tema.CORES_PERMANENCIA['Curta']};
    --media: {tema.CORES_PERMANENCIA['Média']};
    --longa: {tema.CORES_PERMANENCIA['Longa']};
    --fonte-titulo: '{tema.FONTE_TITULO}', sans-serif;
    --fonte-texto: '{tema.FONTE_TEXTO}', sans-serif;
}}
"""

app.index_string = (
    "<!DOCTYPE html><html lang='pt-BR'><head>{%metas%}<title>{%title%}</title>"
    "{%favicon%}{%css%}<style>" + _VARIAVEIS + "</style></head>"
    "<body>{%app_entry%}<footer>{%config%}{%scripts%}{%renderer%}</footer></body></html>"
)

app.layout = html.Div(
    [
        dcc.Location(id="url"),
        html.Header(
            [
                dcc.Link("🐾 Adotai", href="/", className="marca"),
                html.Nav(id="menu", className="menu"),
            ],
            className="topo",
        ),
        html.Main(dash.page_container, className="conteudo"),
        html.Footer(
            "PISI3 · UFRPE · Dados: Austin Animal Center (Kaggle)", className="rodape"
        ),
    ]
)


@app.callback(Output("menu", "children"), Input("url", "pathname"))
def montar_menu(pathname):
    paginas = sorted(dash.page_registry.values(), key=lambda p: p.get("order", 99))
    return [
        dcc.Link(
            p["name"],
            href=p["relative_path"],
            className="menu-link ativo" if p["path"] == pathname else "menu-link",
        )
        for p in paginas
    ]


if __name__ == "__main__":
    app.run(debug=True)
