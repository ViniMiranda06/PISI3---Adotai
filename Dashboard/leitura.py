"""
Leitura das tabelas de Dashboard/data em Parquet ou CSV.

O notebook exporta cada tabela nos dois formatos. O dashboard usa o .parquet
quando ele existe e consegue ser lido (precisa da biblioteca pyarrow) e, se não,
volta para o .csv de mesmo nome. Assim nada quebra se só um dos formatos estiver
na pasta ou se o pyarrow não estiver instalado.
"""
from pathlib import Path

import pandas as pd


def _caminhos(caminho):
    caminho = Path(caminho)
    return caminho.with_suffix(".parquet"), caminho.with_suffix(".csv")


def existe_tabela(caminho):
    """True se a tabela existe em Parquet ou em CSV."""
    parquet, csv = _caminhos(caminho)
    return parquet.exists() or csv.exists()


def ler_tabela(caminho):
    """Lê a tabela em Parquet (preferência) ou CSV. Recebe o caminho com qualquer uma das extensões."""
    parquet, csv = _caminhos(caminho)
    if parquet.exists():
        try:
            return pd.read_parquet(parquet)
        except Exception:
            # sem pyarrow ou arquivo inválido: tenta o CSV
            pass
    return pd.read_csv(csv, encoding="utf-8-sig")
