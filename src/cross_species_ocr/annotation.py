from __future__ import annotations

from bisect import bisect_left
from collections import defaultdict
from pathlib import Path

import pandas as pd


def load_tss_index(path: str | Path) -> dict[str, dict[str, list]]:
    chrom_to_rows: dict[str, list[tuple[int, str, str]]] = defaultdict(list)
    with open(path, 'r', encoding='utf-8') as handle:
        for line in handle:
            fields = line.rstrip('\n').split('\t')
            if len(fields) < 4:
                continue
            chrom = fields[0]
            start = int(fields[1])
            gene = fields[3]
            strand = fields[4] if len(fields) > 4 else '.'
            chrom_to_rows[chrom].append((start, gene, strand))

    index: dict[str, dict[str, list]] = {}
    for chrom, rows in chrom_to_rows.items():
        rows.sort(key=lambda item: item[0])
        index[chrom] = {
            'positions': [row[0] for row in rows],
            'genes': [row[1] for row in rows],
            'strands': [row[2] for row in rows],
        }
    return index


def annotate_with_nearest_tss(df: pd.DataFrame, tss_index: dict[str, dict[str, list]], promoter_window_bp: int) -> pd.DataFrame:
    nearest_gene = []
    nearest_distance = []
    nearest_strand = []
    regulatory_class = []

    for row in df.itertuples(index=False):
        midpoint = (int(row.start) + int(row.end)) // 2
        chrom_index = tss_index.get(row.chrom)
        if chrom_index is None:
            nearest_gene.append('NA')
            nearest_distance.append(pd.NA)
            nearest_strand.append('NA')
            regulatory_class.append('unannotated')
            continue

        positions = chrom_index['positions']
        idx = bisect_left(positions, midpoint)
        candidate_indexes = []
        if idx < len(positions):
            candidate_indexes.append(idx)
        if idx > 0:
            candidate_indexes.append(idx - 1)

        best_index = min(candidate_indexes, key=lambda i: abs(positions[i] - midpoint))
        distance = abs(positions[best_index] - midpoint)
        nearest_gene.append(chrom_index['genes'][best_index])
        nearest_distance.append(distance)
        nearest_strand.append(chrom_index['strands'][best_index])
        regulatory_class.append('promoter' if distance <= promoter_window_bp else 'distal')

    annotated = df.copy()
    annotated['nearest_gene'] = nearest_gene
    annotated['distance_to_nearest_tss'] = nearest_distance
    annotated['nearest_gene_strand'] = nearest_strand
    annotated['regulatory_class'] = regulatory_class
    return annotated
