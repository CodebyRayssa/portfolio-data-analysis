import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

DATA_PATH = Path("outputs/trips_2025_clean.csv")

# Carregar apenas colunas necessárias
cols = ["member_casual", "ride_length_sec", "day_of_week", "started_at"]
df = pd.read_csv(DATA_PATH, usecols=cols)

df["started_at"] = pd.to_datetime(df["started_at"])
df["hour"] = df["started_at"].dt.hour

# ==============================
# 1) Duração média
# ==============================
avg_duration = df.groupby("member_casual")["ride_length_sec"].mean() / 60

plt.figure(figsize=(6,4))
avg_duration.plot(kind="bar")
plt.title("Duração média (minutos)")
plt.ylabel("Minutos")
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig("outputs/duracao_media.png")
plt.close()

# ==============================
# 2) Uso por hora
# ==============================
hour_usage = df.groupby(["hour", "member_casual"]).size().unstack()

plt.figure(figsize=(10,5))
hour_usage.plot()
plt.title("Uso por Hora do Dia")
plt.xlabel("Hora")
plt.ylabel("Quantidade de Viagens")
plt.tight_layout()
plt.savefig("outputs/uso_por_hora.png")
plt.close()

# ==============================
# 3) Uso por dia da semana
# ==============================
weekday_usage = df.groupby(["day_of_week", "member_casual"]).size().unstack()

# Reordenar dias
order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
weekday_usage = weekday_usage.reindex(order)

plt.figure(figsize=(8,5))
weekday_usage.plot(kind="bar")
plt.title("Uso por Dia da Semana")
plt.ylabel("Quantidade de Viagens")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("outputs/uso_por_dia.png")
plt.close()

print("Gráficos salvos na pasta outputs.")
