# Cross-Species OCR Mapping Pipeline for Pancreas

This repository now contains a reproducible Task 2 pipeline for building a cross-species open chromatin region (OCR) map between human and mouse pancreas ATAC-seq peak sets.

The implementation is intentionally scoped to Task 2 only. It prepares standardized OCR peak files, performs optional lightweight annotation, runs HAL-based cross-species liftover, classifies orthologous versus non-orthologous OCRs, and writes downstream-friendly tables and figures for later team tasks.

## Current Scope

Implemented here:
- Locate human and mouse pancreas peak files from the course data root
- Standardize peak files into clean OCR tables and BED outputs
- Optionally annotate OCRs with nearest gene and promoter/distal labels
- Lift OCRs between species using a HAL alignment via `halLiftover`
- Build orthologous and species-specific OCR outputs
- Write summary tables, figures, logs, and reproducible metadata

Not implemented here:
- Task 3 conserved-vs-species-specific biological interpretation
- Task 4 GO or pathway enrichment
- Task 5 promoter-vs-enhancer downstream analysis beyond simple labels
- Task 6 TF motif analysis

## Default Data Inputs

The default pancreas inputs are configured to use the reproducible IDR optimal peak calls:

- Human: `/ocean/projects/bio230007p/ikaplow/HumanAtac/Pancreas/peak/idr_reproducibility/idr.optimal_peak.narrowPeak.gz`
- Mouse: `/ocean/projects/bio230007p/ikaplow/MouseAtac/Pancreas/peak/idr_reproducibility/idr.optimal_peak.narrowPeak.gz`
- HAL alignment: `/ocean/projects/bio230007p/ikaplow/Alignments/10plusway-master.hal`

HAL species names in the provided alignment are configured as `Human` and `Mouse`.

## Repository Layout

```
config/
  task2_pancreas_mapping.yaml
docs/
  task2_cross_species_mapping.md
scripts/
  run_task2_pancreas_mapping.py
src/cross_species_ocr/
  __init__.py
  annotation.py
  cli.py
  config.py
  intervals.py
  logging_utils.py
  mapping.py
  peaks.py
  pipeline.py
  reporting.py
tests/
  test_standardize.py
results/
  mapping/
  tables/
  figures/
  logs/
```

## Environment

Python dependencies are listed in `requirements.txt`. The mapping step also requires an external HAL executable:

- `halLiftover`

If `halLiftover` is not already on `PATH`, load the appropriate module or supply an explicit binary path in the YAML config.

## How To Run

1. Create or activate your Python environment.
2. Adjust `config/task2_pancreas_mapping.yaml` only if you need non-default inputs or output paths.
3. Run input discovery:

```bash
PYTHONPATH=src python3 scripts/run_task2_pancreas_mapping.py discover --config config/task2_pancreas_mapping.yaml
```

4. Run the full Task 2 pipeline:

```bash
PYTHONPATH=src python3 scripts/run_task2_pancreas_mapping.py run --config config/task2_pancreas_mapping.yaml
```

5. If you want to validate preprocessing before HAL mapping is available:

```bash
PYTHONPATH=src python3 scripts/run_task2_pancreas_mapping.py run --config config/task2_pancreas_mapping.yaml --skip-mapping
```

## Main Outputs

- `results/mapping/human_pancreas_ocr.processed.bed`
- `results/mapping/mouse_pancreas_ocr.processed.bed`
- `results/mapping/human_pancreas_ocr.processed.tsv`
- `results/mapping/mouse_pancreas_ocr.processed.tsv`
- `results/mapping/orthologous_ocr_pairs.tsv`
- `results/mapping/human_non_orthologous_ocr.tsv`
- `results/mapping/mouse_non_orthologous_ocr.tsv`
- `results/tables/task2_mapping_summary.tsv`
- `results/figures/task2_mapping_counts.png`
- `results/figures/task2_mapping_rates.png`
- `results/logs/task2_pancreas_mapping.log`

## Design Notes

The pipeline keeps Task 2 outputs easy to reuse later by preserving stable OCR IDs, genomic coordinates, optional nearest-gene annotations, and explicit mapping-status labels.
