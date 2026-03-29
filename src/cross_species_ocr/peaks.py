from __future__ import annotations

from pathlib import Path

import pandas as pd


NARROWPEAK_COLUMNS = [
    'chrom',
    'start',
    'end',
    'name',
    'score',
    'strand',
    'signal_value',
    'p_value',
    'q_value',
    'summit',
]


def discover_peak_file(candidates: list[str]) -> str:
    for candidate in candidates:
        if Path(candidate).exists():
            return candidate
    joined = '\n'.join(candidates)
    raise FileNotFoundError(f'Could not locate any configured peak file. Checked:\n{joined}')


def read_peak_table(path: str | Path) -> pd.DataFrame:
    compression = 'gzip' if str(path).endswith('.gz') else None
    return pd.read_csv(
        path,
        sep='\t',
        header=None,
        names=NARROWPEAK_COLUMNS,
        compression=compression,
    )


def standardize_peak_table(df: pd.DataFrame, species: str) -> pd.DataFrame:
    result = df.copy()
    result['start'] = result['start'].astype(int)
    result['end'] = result['end'].astype(int)
    result['score'] = pd.to_numeric(result['score'], errors='coerce').fillna(0).astype(int)
    result['signal_value'] = pd.to_numeric(result['signal_value'], errors='coerce')
    result['p_value'] = pd.to_numeric(result['p_value'], errors='coerce')
    result['q_value'] = pd.to_numeric(result['q_value'], errors='coerce')
    result['summit'] = pd.to_numeric(result['summit'], errors='coerce').fillna(-1).astype(int)
    result = result[result['end'] > result['start']].copy()
    result = result.drop_duplicates(subset=['chrom', 'start', 'end']).reset_index(drop=True)
    result.insert(0, 'peak_id', [f'{species}_ocr_{i:07d}' for i in range(1, len(result) + 1)])
    result['species'] = species
    result['width'] = result['end'] - result['start']
    return result[[
        'peak_id', 'species', 'chrom', 'start', 'end', 'width', 'score', 'signal_value',
        'p_value', 'q_value', 'summit', 'name', 'strand'
    ]]


def write_bed(df: pd.DataFrame, path: str | Path) -> None:
    bed = df[['chrom', 'start', 'end', 'peak_id', 'score']].copy()
    bed['strand'] = '.'
    bed.to_csv(path, sep='\t', header=False, index=False)


def write_table(df: pd.DataFrame, path: str | Path) -> None:
    df.to_csv(path, sep='\t', index=False)


def write_manifest(entries: list[dict[str, str]], path: str | Path) -> None:
    pd.DataFrame(entries).to_csv(path, sep='\t', index=False)
