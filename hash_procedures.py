"""Utility helpers for hashing combinations of DESCR_PRESTAZIONE values."""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Iterable, List, Sequence, Tuple

import pandas as pd
def normalise_tokens(value: Any, delimiter: str | None) -> Tuple[str, ...]:
    """Return a deterministic, alphabetically ordered tuple of tokens."""
    if pd.isna(value):
        return tuple()

    text = str(value).strip()
    if not text:
        return tuple()

    if delimiter is None:
        tokens: List[str] = [text]
    else:
        tokens = [token.strip() for token in text.split(delimiter) if token.strip()]

    return tuple(sorted(tokens, key=str.lower))


def hash_tokens(tokens: Iterable[str], hash_length: int) -> str:
    canonical = "|".join(tokens)
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    if hash_length <= 0:
        raise ValueError("hash-length must be a positive integer")
    return digest[:hash_length]


def build_mapping(group_df: pd.DataFrame) -> pd.DataFrame:
    """Create a mapping dataframe from hash to canonical tokens."""

    mapping_df = group_df[["__hash__", "__canonical__"]].drop_duplicates().copy()
    mapping_df.rename(columns={"__hash__": "hash", "__canonical__": "sorted_combination"}, inplace=True)
    return mapping_df


def combine_group_tokens(token_series: pd.Series) -> Tuple[str, ...]:
    """Aggregate token tuples into a single sorted tuple for the group."""

    combined: set[str] = set()
    for tokens in token_series:
        combined.update(tokens)
    return tuple(sorted(combined, key=str.lower))


def hash_descriptions(
    input_csv: str | Path,
    output_csv: str | Path,
    mapping_csv: str | Path,
    column: str = "DESCR_PRESTAZIONE",
    delimiter: str | None = None,
    hash_length: int = 16,
    group_columns: Sequence[str] = ("ID", "DATA_PREVISTA_EROGAZIONE"),
) -> None:
    """Hash canonicalised combinations in ``column`` and persist lookup tables."""

    input_path = Path(input_csv)
    output_path = Path(output_csv)
    mapping_path = Path(mapping_csv)

    df = pd.read_csv(input_path)

    if column not in df.columns:
        raise KeyError(f"Column '{column}' not found in the input CSV")

    group_cols = list(group_columns)
    missing_group_cols = [name for name in group_cols if name not in df.columns]
    if missing_group_cols:
        raise KeyError(f"Grouping columns missing in input CSV: {', '.join(missing_group_cols)}")

    tokens_col = df[column].apply(lambda val: normalise_tokens(val, delimiter))
    df["__tokens__"] = tokens_col

    group_df = (
        df.groupby(group_cols, dropna=False)["__tokens__"]
        .apply(combine_group_tokens)
        .reset_index()
    )
    group_df["__canonical__"] = group_df["__tokens__"].apply(lambda tokens: "|".join(tokens))
    group_df["__hash__"] = group_df["__tokens__"].apply(lambda tokens: hash_tokens(tokens, hash_length))

    df = df.merge(group_df[group_cols + ["__canonical__", "__hash__"]], on=group_cols, how="left")

    mapping_df = build_mapping(group_df)

    df[column] = df["__hash__"]
    df.drop(columns=["__hash__", "__canonical__", "__tokens__"], inplace=True)

    df.to_csv(output_path, index=False)
    mapping_df.to_csv(mapping_path, index=False)


def lookup_hash_contents(mapping_csv: str | Path, hash_value: str) -> List[str]:
    """Return the canonical tokens stored for ``hash_value`` in ``mapping_csv``."""

    mapping_path = Path(mapping_csv)
    lookup_df = pd.read_csv(mapping_path)

    row = lookup_df.loc[lookup_df["hash"] == hash_value]
    if row.empty:
        raise KeyError(f"Hash '{hash_value}' not found in mapping file")

    combination = row.iloc[0]["sorted_combination"]
    return [token for token in combination.split("|") if token]


def main(
    input_csv: str | Path = "m_prcties_ps_2023_hash.csv",
    output_csv: str | Path = "data/hashed_dataset.csv",
    mapping_csv: str | Path = "data/hashed_dataset_lookup.csv",
    column: str = "DESCR_PRESTAZIONE",
    delimiter: str | None = None,
    hash_length: int = 16,
    group_columns: Sequence[str] = ("ID", "DATA_PREVISTA_EROGAZIONE"),
    hash_to_lookup: str | None = None,
) -> List[str] | None:
    """Execute hashing workflow and optionally resolve a hash back to tokens."""

    hash_descriptions(
        input_csv=input_csv,
        output_csv=output_csv,
        mapping_csv=mapping_csv,
        column=column,
        delimiter=delimiter,
        hash_length=hash_length,
        group_columns=group_columns,
    )

    if hash_to_lookup is None:
        return None

    return lookup_hash_contents(mapping_csv, hash_to_lookup)


if __name__ == "__main__":
    main()
