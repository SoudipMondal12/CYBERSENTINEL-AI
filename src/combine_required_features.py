from pathlib import Path
import pandas as pd
import numpy as np


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

RAW_DIR = BASE_DIR / "data" / "raw"
OUTPUT_DIR = BASE_DIR / "data" / "processed"

OUTPUT_FILE = (
    OUTPUT_DIR / "cicids_required_features.csv"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# REQUIRED FEATURES
# ============================================================

REQUIRED_FEATURES = [
    "Destination Port",
    "Flow Duration",
    "Total Fwd Packets",
    "Total Backward Packets",
    "Total Length of Fwd Packets",
    "Total Length of Bwd Packets",
    "Flow Bytes/s",
    "Flow Packets/s",
    "Fwd Packets/s",
    "Bwd Packets/s",
    "SYN Flag Count",
    "ACK Flag Count",
    "RST Flag Count",
    "Average Packet Size",
    "Min Packet Length",
    "Max Packet Length",
    "Packet Length Mean",
    "Packet Length Std",
    "Label"
]


# ============================================================
# SETTINGS
# ============================================================

CHUNK_SIZE = 20_000


# ============================================================
# FIND FILES
# ============================================================

files = sorted(
    RAW_DIR.glob("*.csv")
)

if not files:

    raise FileNotFoundError(
        f"No CSV files found in: {RAW_DIR}"
    )


print("=" * 70)
print("CICIDS2017 LOW-RAM FEATURE COMBINER")
print("=" * 70)

print(
    f"Found {len(files)} CSV files."
)

print()


# ============================================================
# REMOVE OLD OUTPUT
# ============================================================

if OUTPUT_FILE.exists():

    OUTPUT_FILE.unlink()

    print(
        "Removed previous output."
    )


first_write = True
total_rows = 0


# ============================================================
# PROCESS EACH FILE
# ============================================================

for file in files:

    print("-" * 70)
    print(
        f"Processing: {file.name}"
    )

    try:

        # ----------------------------------------------------
        # Read ONLY the header
        # ----------------------------------------------------

        header_df = pd.read_csv(
            file,
            nrows=0,
            low_memory=False
        )

        raw_columns = list(
            header_df.columns
        )


        # ----------------------------------------------------
        # Normalize header ONLY for matching
        # ----------------------------------------------------

        normalized_columns = [
            str(col)
            .replace("\ufeff", "")
            .strip()
        for col in raw_columns
        ]


        # Map:
        # normalized name -> column index

        column_index_map = {}

        for index, name in enumerate(
            normalized_columns
        ):

            if name not in column_index_map:

                column_index_map[name] = index


        # ----------------------------------------------------
        # Find required column indexes
        # ----------------------------------------------------

        required_indexes = []
        missing = []


        for feature in REQUIRED_FEATURES:

            if feature in column_index_map:

                required_indexes.append(
                    column_index_map[feature]
                )

            else:

                missing.append(feature)


        # ----------------------------------------------------
        # Check missing
        # ----------------------------------------------------

        if missing:

            print(
                "\nWARNING: Missing columns:"
            )

            for item in missing:

                print(
                    f"  - {item}"
                )

            print(
                "\nNormalized columns found:"
            )

            for item in normalized_columns:

                print(
                    f"  - {item}"
                )

            print(
                "\nSkipping this file."
            )

            continue


        # ----------------------------------------------------
        # Read using COLUMN POSITIONS
        # ----------------------------------------------------

        chunks = pd.read_csv(

            file,

            usecols=required_indexes,

            chunksize=CHUNK_SIZE,

            low_memory=False

        )


        for chunk in chunks:

            # ------------------------------------------------
            # Rename by required feature order
            # ------------------------------------------------

            chunk.columns = (
                REQUIRED_FEATURES
            )


            # ------------------------------------------------
            # Numeric features
            # ------------------------------------------------

            numeric_features = [
                feature
                for feature in REQUIRED_FEATURES
                if feature != "Label"
            ]


            for feature in numeric_features:

                chunk[feature] = pd.to_numeric(
                    chunk[feature],
                    errors="coerce"
                )


            # ------------------------------------------------
            # Remove inf
            # ------------------------------------------------

            chunk = chunk.replace(
                [np.inf, -np.inf],
                np.nan
            )


            # ------------------------------------------------
            # Remove invalid numeric rows
            # ------------------------------------------------

            chunk = chunk.dropna(
                subset=numeric_features
            )


            # ------------------------------------------------
            # Clean labels
            # ------------------------------------------------

            chunk["Label"] = (
                chunk["Label"]
                .astype(str)
                .str.strip()
            )


            # ------------------------------------------------
            # Save
            # ------------------------------------------------

            chunk.to_csv(

                OUTPUT_FILE,

                mode=(
                    "w"
                    if first_write
                    else "a"
                ),

                header=first_write,

                index=False
            )


            first_write = False

            rows = len(chunk)

            total_rows += rows


            print(
                f"  Rows written: "
                f"{total_rows:,}",
                end="\r"
            )


        print()


    except Exception as exc:

        print(
            f"\nERROR processing "
            f"{file.name}:"
        )

        print(exc)

        print()


# ============================================================
# FINAL CHECK
# ============================================================

print()
print("=" * 70)
print("COMBINATION FINISHED")
print("=" * 70)


if not OUTPUT_FILE.exists():

    raise RuntimeError(
        "No output file was created. "
        "Check the missing-column messages above."
    )


print(
    f"Total rows: {total_rows:,}"
)

print(
    f"Output:"
)

print(
    OUTPUT_FILE
)


# ============================================================
# VERIFY WITHOUT LOADING EVERYTHING
# ============================================================

print()
print("Checking output...")

check = pd.read_csv(
    OUTPUT_FILE,
    nrows=5
)


print()
print("Columns:")

for column in check.columns:

    print(
        f"  {column}"
    )


print()
print("First 5 rows:")

print(
    check.to_string(
        index=False
    )
)