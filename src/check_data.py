import pandas as pd
from pathlib import Path

files = list(
    Path("data/raw").glob("*.csv")
)

print("CSV files found:")
for file in files:
    print(file)

if not files:
    raise FileNotFoundError(
        "No CSV files found in data/raw/"
    )

df = pd.read_csv(
    files[0],
    low_memory=False
)

print("\nFirst file:")
print(files[0])

print("\nShape:")
print(df.shape)

print("\nColumns:")
for col in df.columns:
    print(col)

print("\nLabels:")
print(df[" Label"].value_counts()
      if " Label" in df.columns
      else df["Label"].value_counts())