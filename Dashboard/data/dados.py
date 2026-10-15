"""
Carregamento e preparação de dados para o Dashboard Adotai.

Funções públicas:
- localizar_csv(): tenta localizar um CSV plausível dentro da pasta data/
- carregar_dados(path=None): carrega e faz parsing básico de datas
- preparar_permanencia(df): cria colunas permanencia_dias e permanencia_cat
"""

from pathlib import Path
import pandas as pd
import numpy as np

# Configuração de categorias (coerente com tema.py)
PERMANENCIA_CATEGORIAS = ["Curta", "Média", "Longa"]


def localizar_csv(data_dir: str = "data"):
    """Procura por um arquivo .csv na pasta data/ e retorna o Path (ou None)."""
    base = Path(__file__).resolve().parents[0]  # Dashboard/data
    p = base / data_dir
    if not p.exists():
        # olhar também um caminho relativo à raiz do repositório
        p = Path.cwd() / data_dir
    if not p.exists():
        return None
    csvs = list(p.glob("*.csv"))
    return csvs[0] if csvs else None


def carregar_dados(path: str | None = None) -> pd.DataFrame:
    """
    Carrega o dataset. Se path for None, tenta localizar dentro de data/.
    Faz parse de colunas de data comuns automaticamente.
    """
    if path:
        p = Path(path)
    else:
        p = localizar_csv()
        if p is None:
            raise FileNotFoundError(
                "Nenhum arquivo CSV encontrado em 'data/' e nenhum path foi informado. "
                "Coloque o CSV em Dashboard/data/ e rode novamente."
            )
    # leitura básica
    df = pd.read_csv(p, low_memory=False)

    # detectar possíveis colunas de datas e converter
    date_cols = []
    for cand in ["intake_datetime", "intake_date", "intake", "outcome_datetime", "outcome_date", "outcome"]:
        if cand in df.columns:
            date_cols.append(cand)
    # parsear colunas detectadas
    for c in date_cols:
        try:
            df[c] = pd.to_datetime(df[c], errors="coerce")
        except Exception:
            df[c] = pd.to_datetime(df[c], errors="coerce", infer_datetime_format=True)

    return df


def preparar_permanencia(df: pd.DataFrame, dias_col_candidates=None) -> pd.DataFrame:
    """
    Garante que o dataframe tenha:
      - permanencia_dias (int)
      - permanencia_cat (Curta/Média/Longa)

    Estratégia:
    1) Se existir coluna de dias (length_of_stay, days_in_shelter), usa ela.
    2) Senão, tenta calcular como (outcome_date - intake_date) em dias.
    3) Se nada disso for possível, retorna df sem alterações (com aviso).
    """
    df = df.copy()
    if dias_col_candidates is None:
        dias_col_candidates = ["length_of_stay", "days_in_shelter", "days_in_shelter_total"]

    # 1) procurar coluna existente
    for c in dias_col_candidates:
        if c in df.columns:
            df["permanencia_dias"] = pd.to_numeric(df[c], errors="coerce").astype("Int64")
            break

    # 2) tentar calcular a partir de datas
    if "permanencia_dias" not in df.columns or df["permanencia_dias"].isna().all():
        intake_cols = [c for c in ["intake_datetime", "intake_date", "intake"] if c in df.columns]
        outcome_cols = [c for c in ["outcome_datetime", "outcome_date", "outcome"] if c in df.columns]
        if intake_cols and outcome_cols:
            intake = df[intake_cols[0]]
            outcome = df[outcome_cols[0]]
            diff = (outcome - intake).dt.days
            df["permanencia_dias"] = diff.astype("Int64")

    # 3) definir categorias
    def cat_from_days(x):
        if pd.isna(x):
            return pd.NA
        try:
            x = int(x)
        except Exception:
            return pd.NA
        if x < 30:
            return "Curta"
        if x < 180:
            return "Média"
        return "Longa"

    if "permanencia_dias" in df.columns:
        df["permanencia_cat"] = df["permanencia_dias"].apply(cat_from_days).astype("category")
        df["permanencia_cat"] = df["permanencia_cat"].cat.set_categories(PERMANENCIA_CATEGORIAS, ordered=True)

    return df
