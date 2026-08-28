from pathlib import Path
import pandas as pd


RAW_DIR = Path("data/raw")
OUTPUT = Path(
    "data/processed/cicids2017_combined.csv"
)


files = list(
    RAW_DIR.glob("*.csv")
)

if not files:
    raise FileNotFoundError(
        "No CSV files found in data/raw/"
    )

print(f"Found {len(files)} CSV files.")

frames = []

for file in files:

    print(f"Reading: {file.name}")

    df = pd.read_csv(
        file,
        low_memory=False
    )

    # Remove whitespace from column names
    df.columns = (
        df.columns
        .str.strip()
        .str.replace(
            "\ufeff",
            "",
            regex=False
        )
    )

    frames.append(df)


combined = pd.concat(
    frames,
    ignore_index=True
)


print("\nCombined shape:")
print(combined.shape)


print("\nLabels:")
print(
    combined["Label"]
    .value_counts()
)


OUTPUT.parent.mkdir(
    parents=True,
    exist_ok=True
)

combined.to_csv(
    OUTPUT,
    index=False
)

print(
    f"\nSaved to: {OUTPUT}"
)