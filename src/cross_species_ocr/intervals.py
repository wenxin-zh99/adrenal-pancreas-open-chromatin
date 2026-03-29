from __future__ import annotations

import pandas as pd


def reciprocal_overlap(a_start: int, a_end: int, b_start: int, b_end: int) -> tuple[int, float, float]:
    overlap = max(0, min(a_end, b_end) - max(a_start, b_start))
    if overlap == 0:
        return 0, 0.0, 0.0
    frac_a = overlap / max(1, a_end - a_start)
    frac_b = overlap / max(1, b_end - b_start)
    return overlap, frac_a, frac_b


def split_by_chrom(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    grouped: dict[str, pd.DataFrame] = {}
    for chrom, subset in df.sort_values(['chrom', 'start', 'end']).groupby('chrom', sort=False):
        grouped[str(chrom)] = subset.reset_index(drop=True)
    return grouped


def find_best_overlaps(query_df: pd.DataFrame, target_df: pd.DataFrame, min_reciprocal_overlap: float) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    query_by_chrom = split_by_chrom(query_df)
    target_by_chrom = split_by_chrom(target_df)

    for chrom, queries in query_by_chrom.items():
        targets = target_by_chrom.get(chrom)
        if targets is None or targets.empty:
            continue

        target_records = list(targets.itertuples(index=False))
        left = 0
        for query in queries.itertuples(index=False):
            while left < len(target_records) and int(target_records[left].end) <= int(query.start):
                left += 1

            best_row = None
            best_score = -1.0
            scan = left
            while scan < len(target_records) and int(target_records[scan].start) < int(query.end):
                target = target_records[scan]
                overlap_bp, frac_query, frac_target = reciprocal_overlap(
                    int(query.start),
                    int(query.end),
                    int(target.start),
                    int(target.end),
                )
                if min(frac_query, frac_target) >= min_reciprocal_overlap:
                    score = min(frac_query, frac_target)
                    if score > best_score:
                        best_score = score
                        best_row = {
                            'query_peak_id': query.peak_id,
                            'query_chrom': query.chrom,
                            'query_start': int(query.start),
                            'query_end': int(query.end),
                            'target_peak_id': target.peak_id,
                            'target_chrom': target.chrom,
                            'target_start': int(target.start),
                            'target_end': int(target.end),
                            'overlap_bp': overlap_bp,
                            'query_overlap_fraction': frac_query,
                            'target_overlap_fraction': frac_target,
                            'reciprocal_overlap_score': score,
                        }
                scan += 1

            if best_row is not None:
                rows.append(best_row)

    return pd.DataFrame(rows)
