from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pandas as pd

from .intervals import find_best_overlaps


def hal_liftover_available(binary: str) -> bool:
    return shutil.which(binary) is not None


def run_hal_liftover(binary: str, hal_file: str, src_genome: str, src_bed: str | Path, dst_genome: str, out_bed: str | Path) -> None:
    command = [binary, hal_file, src_genome, str(src_bed), dst_genome, str(out_bed)]
    subprocess.run(command, check=True)


def read_liftover_bed(path: str | Path, source_prefix: str, target_species: str) -> pd.DataFrame:
    rows = []
    with open(path, 'r', encoding='utf-8') as handle:
        for line in handle:
            fields = line.rstrip('\n').split('\t')
            if len(fields) < 4:
                continue
            peak_id = fields[3]
            rows.append({
                'peak_id': peak_id,
                'source_peak_id': peak_id,
                'chrom': fields[0],
                'start': int(fields[1]),
                'end': int(fields[2]),
                'target_species': target_species,
            })
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    df = df[df['source_peak_id'].str.startswith(source_prefix)].copy()
    df['width'] = df['end'] - df['start']
    return df


def build_pair_tables(
    forward_lifted: pd.DataFrame,
    reverse_lifted: pd.DataFrame,
    target_df: pd.DataFrame,
    reverse_target_df: pd.DataFrame,
    min_reciprocal_overlap: float,
    source_label: str,
    target_label: str,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    forward_best = find_best_overlaps(forward_lifted, target_df, min_reciprocal_overlap)
    reverse_best = find_best_overlaps(reverse_lifted, reverse_target_df, min_reciprocal_overlap)

    if forward_best.empty:
        return forward_best, reverse_best

    reverse_lookup = {
        (row.query_peak_id, row.target_peak_id)
        for row in reverse_best.itertuples(index=False)
    }
    forward_best['reciprocal_best_hit'] = [
        (row.target_peak_id, row.query_peak_id) in reverse_lookup
        for row in forward_best.itertuples(index=False)
    ]
    forward_best['source_species'] = source_label
    forward_best['target_species'] = target_label
    return forward_best, reverse_best
