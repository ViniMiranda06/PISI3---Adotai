"""
Tema Visual do Dashboard Adotai.
Todas as páginas devem importar daqui. A fim de manter a identidade visual intacta.
"""

# Paleta de cores (Base)
FUNDO = "#FFF8F0"
CARTAO = "#FFFFFF"
TEXTO = "#2B2B2B"
TEXTO_SEC = "#6B6B6B"
PRIMARIA = "#E8743B"
SECUNDARIA = "#2A6F6B"

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


def aplicar_tema_graficos():
    """Aplica o tema aos gráficos matplotlib/seaborn. Chamar uma vez no início da página."""
    import matplotlib.pyplot as plt
    import seaborn as sns

    sns.set_theme(style="whitegrid")
    plt.rcParams.update({
        "figure.facecolor": CARTAO,
        "axes.facecolor": CARTAO,
        "axes.edgecolor": "#E5E0D8",
        "axes.labelcolor": TEXTO_SEC,
        "axes.titlecolor": TEXTO,
        "axes.titleweight": "bold",
        "xtick.color": TEXTO_SEC,
        "ytick.color": TEXTO_SEC,
        "text.color": TEXTO,
        "grid.color": "#EFEAE2",
        "font.family": "sans-serif",
        "font.sans-serif": [FONTE_TEXTO, "DejaVu Sans"],
    })
    # Cor padrão das séries sem categoria: laranja, depois verde-petróleo
    plt.rcParams["axes.prop_cycle"] = plt.cycler(color=[PRIMARIA, SECUNDARIA])
