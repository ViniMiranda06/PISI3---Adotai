"""
Tema Visual do Dashboard Adotai.
Todas as páginas devem importar daqui. A fim de manter a identidade visual intacta.
"""

import plotly.graph_objects as go
import plotly.io as pio

# Paleta de cores (Base)
FUNDO = "#FFF8F0"
CARTAO = "#FFFFFF"
TEXTO = "#2B2B2B"
TEXTO_SEC = "#6B6B6B"
PRIMARIA = "#E8743B"
SECUNDARIA = "#2A6F6B"
LINHAS = "#E5E0D8"  # Cor adicionada para evitar o NameError

# Cores fixas das categorias de permanência (Iguais em TODAS as páginas)
CORES_PERMANENCIA = {
    "Curta": "#2A9D8F",
    "Média": "#F2B134",
    "Longa": "#D1495B",
}
ORDEM_PERMANENCIA = ["Curta", "Média", "Longa"]

# Fontes
FONTE_TITULO = "Poppins"
FONTE_TEXTO = "Inter"
GOOGLE_FONTS_URL = (
    "https://fonts.googleapis.com/css2?"
    "family=Poppins:wght@600&family=Inter:wght@400;500&display=swap"
)

# Template Plotly (padronização dos gráficos em dash)
TEMPLATE = go.layout.Template(
    layout=dict(
        font=dict(family=f"{FONTE_TEXTO}, sans-serif", color=TEXTO, size=13),
        title=dict(font=dict(family=f"{FONTE_TITULO}, sans-serif", size=18, color=TEXTO)),
        paper_bgcolor=CARTAO,
        plot_bgcolor=CARTAO,
        colorway=[PRIMARIA, SECUNDARIA, "#F2B134", "#D1495B", "#2A9D8F"],
        xaxis=dict(
            gridcolor=LINHAS, linecolor=LINHAS, zerolinecolor=LINHAS,
            tickfont=dict(color=TEXTO_SEC), title=dict(font=dict(color=TEXTO_SEC))
        ),
        yaxis=dict(
            gridcolor=LINHAS, linecolor=LINHAS, zerolinecolor=LINHAS,
            tickfont=dict(color=TEXTO_SEC), title=dict(font=dict(color=TEXTO_SEC))
        ),
        legend=dict(font=dict(color=TEXTO_SEC)),
        margin=dict(l=50, r=20, t=60, b=50),
        hoverlabel=dict(font=dict(family=f"{FONTE_TEXTO}, sans-serif")),
    )
)

def registrar_tema():
    """Chamar UMA vez no app.py. Todos os gráficos passam a usar o tema."""
    pio.templates["adotai"] = TEMPLATE
    pio.templates.default = "adotai"
