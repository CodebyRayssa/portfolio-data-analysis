from pathlib import Path
import pandas as pd

# raiz do projeto: .../02. Estudo de Caso
BASE_DIR = Path(__file__).resolve().parents[1]

RAW = BASE_DIR / "data_raw"
CLEAN = BASE_DIR / "data_clean"
CLEAN.mkdir(exist_ok=True)

activity_path = RAW / "dailyActivity_merged.csv"
sleep_path = RAW / "minuteSleep_merged.csv"

print("BASE_DIR:", BASE_DIR)
print("Procurando em:", RAW)

if not activity_path.exists():
    raise FileNotFoundError(f"Não achei: {activity_path}")
if not sleep_path.exists():
    raise FileNotFoundError(f"Não achei: {sleep_path}")

# ✅ separador correto: ;
activity = pd.read_csv(activity_path, sep=";", encoding="utf-8")
sleep = pd.read_csv(sleep_path, sep=";", encoding="utf-8")


# padronizar nomes
activity.columns = activity.columns.str.strip()
sleep.columns = sleep.columns.str.strip()

# converter datas
activity["ActivityDate"] = pd.to_datetime(activity["ActivityDate"], errors="coerce")

sleep["date"] = pd.to_datetime(sleep["date"], errors="coerce")
sleep["ActivityDate"] = pd.to_datetime(sleep["date"].dt.date)

# ---------------------------------------------------
# AGREGAR MINUTE SLEEP → DAILY SLEEP
# value == 1 significa dormindo
# ---------------------------------------------------
daily_sleep = (
    sleep[sleep["value"] == 1]
    .groupby(["Id", "ActivityDate"])
    .size()
    .reset_index(name="TotalMinutesAsleep")
)

# ---------------------------------------------------
# MERGE (atividade diária + sono agregado)
# ---------------------------------------------------
df = activity.merge(
    daily_sleep,
    on=["Id", "ActivityDate"],
    how="left"
)

df["TotalMinutesAsleep"] = df["TotalMinutesAsleep"].fillna(0)

# features úteis
df["weekday"] = df["ActivityDate"].dt.day_name()
df["month"] = df["ActivityDate"].dt.to_period("M").astype(str)

out = CLEAN / "fitbit_daily_clean.csv"
df.to_csv(out, index=False)

print("✅ Base limpa criada:", out)
print("Linhas:", len(df), "| Colunas:", len(df.columns))
print("Usuários únicos:", df["Id"].nunique())

print("Colunas activity:", activity.columns.tolist())
print("Colunas sleep:", sleep.columns.tolist())



