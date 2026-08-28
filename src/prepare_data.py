from pathlib import Path
import random

import numpy as np
import pandas as pd


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

RAW_DIR = BASE_DIR / "data" / "raw"

OUTPUT = (
    BASE_DIR
    / "data"
    / "processed"
    / "training_data.csv"
)


# ============================================================
# FEATURES WE WANT
# ============================================================

FEATURES = [
    "Destination Port",
    "Protocol",
    "Flow Duration",
    "Total Fwd Packets",
    "Total Backward Packets",
    "Total Length of Fwd Packets",
    "Total Length of Bwd Packets",
    "Flow Bytes/s",
    "Flow Packets/s"
]


# ============================================================
# SETTINGS
# ============================================================

CHUNK_SIZE = 20_000

# Maximum number of examples per class
MAX_PER_CLASS = 50_000

RANDOM_STATE = 42

random.seed(RANDOM_STATE)


# ============================================================
# FIND CSV FILES
# ============================================================

files = sorted(
    RAW_DIR.glob("*.csv")
)

if not files:

    raise FileNotFoundError(
        f"No CSV files found in {RAW_DIR}"
    )


print("=" * 60)
print("LOW-RAM CICIDS2017 PREPARATION")
print("=" * 60)

print(
    f"Found {len(files)} CSV files."
)


# ============================================================
# STORAGE
# ============================================================

benign_samples = []

attack_samples = []

benign_count = 0

attack_count = 0


# ============================================================
# PROCESS EACH FILE
# ============================================================

for file in files:

    print()
    print("-" * 60)

    print(
        f"Processing: {file.name}"
    )

    # --------------------------------------------------------
    # Read only header first
    # --------------------------------------------------------

    try:

        header = pd.read_csv(
            file,
            nrows=0
        )

        header.columns = (
            header.columns
            .str.strip()
            .str.replace(
                "\ufeff",
                "",
                regex=False
            )
        )

    except Exception as exc:

        print(
            f"Could not read {file.name}: {exc}"
        )

        continue


    # --------------------------------------------------------
    # Find columns case-insensitively
    # --------------------------------------------------------

    normalized = {
        column.lower().strip(): column
        for column in header.columns
    }


    actual_features = []

    missing = []


    for feature in FEATURES:

        key = feature.lower().strip()

        if key in normalized:

            actual_features.append(
                normalized[key]
            )

        else:

            missing.append(feature)


    # --------------------------------------------------------
    # Protocol missing?
    # --------------------------------------------------------

    if missing:

        print(
            "Missing columns:",
            missing
        )

        print(
            "Available columns:"
        )

        print(
            header.columns.tolist()
        )

        print(
            "Skipping this file."
        )

        continue


    # --------------------------------------------------------
    # Process in chunks
    # --------------------------------------------------------

    try:

        chunks = pd.read_csv(
            file,
            usecols=actual_features + ["Label"],
            chunksize=CHUNK_SIZE,
            low_memory=False
        )

    except ValueError:

        # Sometimes Label has whitespace

        label_column = None

        for col in header.columns:

            if col.lower().strip() == "label":

                label_column = col

                break


        if label_column is None:

            print(
                "Label column not found."
            )

            continue


        chunks = pd.read_csv(
            file,
            usecols=actual_features + [
                label_column
            ],
            chunksize=CHUNK_SIZE,
            low_memory=False
        )


    for chunk in chunks:

        # ----------------------------------------------------
        # Normalize column names
        # ----------------------------------------------------

        chunk.columns = (
            chunk.columns
            .str.strip()
            .str.replace(
                "\ufeff",
                "",
                regex=False
            )
        )


        # ----------------------------------------------------
        # Rename columns to standard names
        # ----------------------------------------------------

        rename_map = {}

        for original in chunk.columns:

            key = original.lower().strip()

            for feature in FEATURES:

                if key == feature.lower():

                    rename_map[
                        original
                    ] = feature


        chunk = chunk.rename(
            columns=rename_map
        )


        # ----------------------------------------------------
        # Convert numeric features
        # ----------------------------------------------------

        for feature in FEATURES:

            chunk[feature] = pd.to_numeric(
                chunk[feature],
                errors="coerce"
            )


        # ----------------------------------------------------
        # Clean
        # ----------------------------------------------------

        chunk = chunk.replace(
            [np.inf, -np.inf],
            np.nan
        )

        chunk = chunk.dropna(
            subset=FEATURES
        )


        # ----------------------------------------------------
        # Normalize labels
        # ----------------------------------------------------

        chunk["Label"] = (
            chunk["Label"]
            .astype(str)
            .str.strip()
            .str.upper()
        )


        # ----------------------------------------------------
        # Binary target
        # ----------------------------------------------------

        chunk["target"] = (
            chunk["Label"] != "BENIGN"
        ).astype(np.int8)


        # ----------------------------------------------------
        # Select only required columns
        # ----------------------------------------------------

        data = chunk[
            FEATURES + ["target"]
        ]


        # ----------------------------------------------------
        # Split
        # ----------------------------------------------------

        benign = data[
            data["target"] == 0
        ]

        attack = data[
            data["target"] == 1
        ]


        # ----------------------------------------------------
        # Sample benign
        # ----------------------------------------------------

        if len(benign) > 0:

            remaining = (
                MAX_PER_CLASS
                - benign_count
            )

            if remaining > 0:

                n = min(
                    remaining,
                    len(benign)
                )

                sample = benign.sample(
                    n=n,
                    random_state=RANDOM_STATE
                )

                benign_samples.append(
                    sample
                )

                benign_count += n


        # ----------------------------------------------------
        # Sample attacks
        # ----------------------------------------------------

        if len(attack) > 0:

            remaining = (
                MAX_PER_CLASS
                - attack_count
            )

            if remaining > 0:

                n = min(
                    remaining,
                    len(attack)
                )

                sample = attack.sample(
                    n=n,
                    random_state=RANDOM_STATE
                )

                attack_samples.append(
                    sample
                )

                attack_count += n


        # ----------------------------------------------------
        # Stop if enough samples
        # ----------------------------------------------------

        if (
            benign_count >= MAX_PER_CLASS
            and
            attack_count >= MAX_PER_CLASS
        ):

            break


    print(
        f"Benign collected: {benign_count}"
    )

    print(
        f"Attack collected: {attack_count}"
    )


    if (
        benign_count >= MAX_PER_CLASS
        and
        attack_count >= MAX_PER_CLASS
    ):

        print(
            "\nEnough samples collected."
        )

        break


# ============================================================
# CHECK
# ============================================================

if not benign_samples:

    raise RuntimeError(
        "No BENIGN samples collected."
    )


if not attack_samples:

    raise RuntimeError(
        "No ATTACK samples collected."
    )


# ============================================================
# COMBINE ONLY SMALL SAMPLES
# ============================================================

benign_df = pd.concat(
    benign_samples,
    ignore_index=True
)

attack_df = pd.concat(
    attack_samples,
    ignore_index=True
)


# Limit once again

benign_df = benign_df.sample(
    n=min(
        MAX_PER_CLASS,
        len(benign_df)
    ),
    random_state=RANDOM_STATE
)

attack_df = attack_df.sample(
    n=min(
        MAX_PER_CLASS,
        len(attack_df)
    ),
    random_state=RANDOM_STATE
)


# ============================================================
# FINAL DATASET
# ============================================================

final_df = pd.concat(
    [
        benign_df,
        attack_df
    ],
    ignore_index=True
)


final_df = final_df.sample(
    frac=1,
    random_state=RANDOM_STATE
).reset_index(
    drop=True
)


# ============================================================
# SAVE
# ============================================================

OUTPUT.parent.mkdir(
    parents=True,
    exist_ok=True
)


final_df.to_csv(
    OUTPUT,
    index=False
)


# ============================================================
# RESULTS
# ============================================================

print()
print("=" * 60)

print(
    "FINAL DATASET"
)

print("=" * 60)

print(
    "Shape:",
    final_df.shape
)

print()

print(
    "Class distribution:"
)

print(
    final_df["target"]
    .value_counts()
)

print()

print(
    "Saved to:"
)

print(
    OUTPUT
)