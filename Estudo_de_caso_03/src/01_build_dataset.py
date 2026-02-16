import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
RAW_DIR = BASE_DIR / "data_raw"
OUT_DIR = BASE_DIR / "data_clean"
OUT_DIR.mkdir(exist_ok=True)

files = sorted(RAW_DIR.glob("*.csv"))

dfs = []

for f in files:
    year = f.stem
    df = pd.read_csv(f, sep=";")

    df.columns = df.columns.str.lower().str.replace(" ", "_")

    # Padronizar nomes principais
    if "happiness_score" in df.columns:
        df.rename(columns={"happiness_score": "score"}, inplace=True)

    if "happiness.score" in df.columns:
        df.rename(columns={"happiness.score": "score"}, inplace=True)

    if "score" not in df.columns and "score" in df.columns:
        pass

    if "happiness_rank" in df.columns:
        df.rename(columns={"happiness_rank": "rank"}, inplace=True)

    if "happiness.rank" in df.columns:
        df.rename(columns={"happiness.rank": "rank"}, inplace=True)

    df["year"] = int(year)

    dfs.append(df)

all_years = pd.concat(dfs, ignore_index=True)

all_years.to_csv(OUT_DIR / "happiness_full.csv", index=False)

print("✅ Dataset reconstruído corretamente!")
