import pandas as pd
from pathlib import Path

DATA_PATH = Path("outputs/trips_2025_clean.csv")

cols = ["member_casual", "ride_length_sec", "day_of_week"]
df = pd.read_csv(DATA_PATH, usecols=cols)

df.info()

print("\nDistribuição:")
print(df["member_casual"].value_counts())

print("\nDuração média:")
print(df.groupby("member_casual")["ride_length_sec"].mean())

# Carregar hora também
cols = ["member_casual", "ride_length_sec", "day_of_week", "started_at"]
df = pd.read_csv("outputs/trips_2025_clean.csv", usecols=cols)

df["started_at"] = pd.to_datetime(df["started_at"])
df["hour"] = df["started_at"].dt.hour

print("\nUso por hora:")
print(
    df.groupby(["hour", "member_casual"])
      .size()
      .unstack()
)

