from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def write_summary_table(summary_rows: list[dict[str, object]], path: str | Path) -> pd.DataFrame:
    summary = pd.DataFrame(summary_rows)
    summary.to_csv(path, sep='\t', index=False)
    return summary


def plot_count_summary(summary: pd.DataFrame, path: str | Path) -> None:
    fig, ax = plt.subplots(figsize=(8, 5))
    subset = summary[summary['metric'].isin([
        'human_total',
        'mouse_total',
        'orthologous_pairs',
        'human_non_orthologous',
        'mouse_non_orthologous',
    ])]
    ax.bar(subset['metric'], subset['value'], color=['#4C78A8', '#F58518', '#54A24B', '#E45756', '#72B7B2'])
    ax.set_ylabel('Count')
    ax.set_title('Pancreas OCR Mapping Counts')
    ax.tick_params(axis='x', rotation=30)
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


def plot_rate_summary(summary: pd.DataFrame, path: str | Path) -> None:
    fig, ax = plt.subplots(figsize=(6, 5))
    subset = summary[summary['metric'].isin(['human_orthologous_rate', 'mouse_orthologous_rate'])]
    ax.bar(subset['metric'], subset['value'], color=['#4C78A8', '#F58518'])
    ax.set_ylabel('Rate')
    ax.set_ylim(0, 1)
    ax.set_title('Orthologous OCR Mapping Rates')
    ax.tick_params(axis='x', rotation=20)
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)
