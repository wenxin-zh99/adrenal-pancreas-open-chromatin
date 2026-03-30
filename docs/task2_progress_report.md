# Task 2 Progress Report: Cross-Species OCR Mapping in Pancreas

Updated on 2026-03-30.

## Status

Task 2 is complete.

Completed now:
- Project scaffold for Task 2 is in place.
- Human and mouse pancreas OCR inputs are configured and automatically discovered.
- Peak standardization is implemented and verified.
- Optional lightweight annotation is implemented and verified.
- HAL-based cross-species liftover completed in both directions.
- Orthologous and non-orthologous OCR outputs were generated.
- Mapping summary tables and figures were generated.
- Logging, config support, manifests, and job script support are in place.

## Final Run Summary

The full Task 2 pipeline completed successfully on an `RM-shared` node after configuring the explicit course-space HAL binary:

- `halLiftover`: `/ocean/projects/bio230007p/gdu1/repos/hal/bin/halLiftover`
- HAL file: `/ocean/projects/bio230007p/ikaplow/Alignments/10plusway-master.hal`
- HAL species names verified with `halStats`: `Human`, `Mouse`
- Slurm job ID: `38273968`

The log confirms the following milestones:
- human pancreas OCR preprocessing completed
- mouse pancreas OCR preprocessing completed
- `human -> mouse` HAL liftover completed
- `mouse -> human` HAL liftover completed
- reciprocal mapping and summary output generation completed

## What Was Verified

The following command classes were verified successfully:

```bash
PYTHONPATH=src python3 -m py_compile scripts/run_task2_pancreas_mapping.py src/cross_species_ocr/*.py
PYTHONPATH=src python3 scripts/run_task2_pancreas_mapping.py discover --config config/task2_pancreas_mapping.yaml
PYTHONPATH=src python3 scripts/run_task2_pancreas_mapping.py run --config config/task2_pancreas_mapping.yaml --skip-mapping
python3 scripts/run_task2_pancreas_mapping.py run --config config/task2_pancreas_mapping.yaml
```

The full end-to-end run was executed through Slurm on `RM-shared` using the repository job script.

## Final Outputs

Generated and present now:
- `results/mapping/human_pancreas_ocr.processed.bed`
- `results/mapping/mouse_pancreas_ocr.processed.bed`
- `results/mapping/human_pancreas_ocr.processed.tsv`
- `results/mapping/mouse_pancreas_ocr.processed.tsv`
- `results/mapping/orthologous_ocr_pairs.tsv`
- `results/mapping/human_non_orthologous_ocr.tsv`
- `results/mapping/mouse_non_orthologous_ocr.tsv`
- `results/mapping/tmp/human_to_mouse.lifted.bed`
- `results/mapping/tmp/mouse_to_human.lifted.bed`
- `results/tables/task2_input_manifest.tsv`
- `results/tables/task2_mapping_summary.tsv`
- `results/figures/task2_mapping_counts.png`
- `results/figures/task2_mapping_rates.png`
- `results/logs/task2_pancreas_mapping.log`
- `results/logs/task2_pancreas_mapping.38273968.err`
- `results/logs/task2_pancreas_mapping.38273968.out`

## Final Counts

### Processed OCR totals

- Human pancreas OCRs: 89,476
- Mouse pancreas OCRs: 47,189

### Lifted OCR totals

- Human OCRs with at least one liftover result: 71,464
- Mouse OCRs with at least one liftover result: 39,878

### Ortholog mapping summary

- Orthologous OCR pairs: 2,566
- Human non-orthologous OCRs: 87,261
- Mouse non-orthologous OCRs: 44,979
- Human orthologous rate: 0.02475524162904019
- Mouse orthologous rate: 0.046832948356608534

## Non-Orthologous Breakdown

### Human non-orthologous OCRs

- `no_target_overlap`: 66,010
- `no_liftover`: 18,012
- `non_reciprocal_best_hit`: 3,239

### Mouse non-orthologous OCRs

- `no_target_overlap`: 36,816
- `no_liftover`: 7,311
- `non_reciprocal_best_hit`: 852

## Inputs In Use

Configured defaults used for the completed run:
- Human peaks: `/ocean/projects/bio230007p/ikaplow/HumanAtac/Pancreas/peak/idr_reproducibility/idr.optimal_peak.narrowPeak.gz`
- Mouse peaks: `/ocean/projects/bio230007p/ikaplow/MouseAtac/Pancreas/peak/idr_reproducibility/idr.optimal_peak.narrowPeak.gz`
- HAL alignment: `/ocean/projects/bio230007p/ikaplow/Alignments/10plusway-master.hal`
- Human TSS bed: `/ocean/projects/bio230007p/ikaplow/HumanGenomeInfo/gencode.v27.annotation.protTranscript.TSSsWithStrand_sorted.bed`
- Mouse TSS bed: `/ocean/projects/bio230007p/ikaplow/MouseGenomeInfo/gencode.vM15.annotation.protTranscript.geneNames_TSSWithStrand_sorted.bed`
- HAL liftover binary: `/ocean/projects/bio230007p/gdu1/repos/hal/bin/halLiftover`

## Caveats

### 1. Ortholog calls are conservative

The current pipeline uses reciprocal best-hit overlap after HAL liftover rather than HALPER post-processing. This gives a clean, reproducible Task 2 result, but it is a conservative strategy and may under-call orthologous OCRs compared with a more lecture-aligned `halLiftover + HALPER` workflow.

### 2. Many liftover results do not overlap target OCRs

The largest non-orthologous category in both species is `no_target_overlap`. This means many successfully lifted regions do not intersect a called OCR in the other species under the current overlap threshold and matching logic.

### 3. Annotation is lightweight by design

Nearest-gene and promoter/distal labels are included only to make downstream team tasks easier. They are not a substitute for later enrichment, promoter-enhancer, or TF analyses.

### 4. Temporary liftover files are retained

The lifted BED outputs in `results/mapping/tmp/` were kept for traceability and debugging. They can be removed later if you want a cleaner final output directory.

## Interpretation

This Task 2 deliverable is now complete and usable for downstream project tasks. The pipeline successfully produced:
- a standardized human pancreas OCR set
- a standardized mouse pancreas OCR set
- a unified orthologous OCR table
- human-specific OCR output
- mouse-specific OCR output
- summary tables and figures for project reporting

The relatively low orthologous rates suggest that the current mapping criteria are fairly strict, which is scientifically defensible for a first-pass Task 2 deliverable but worth noting in the methods and discussion.

## Recommended Next Step

For the team project, the next step is to use:
- `results/mapping/orthologous_ocr_pairs.tsv`
- `results/mapping/human_non_orthologous_ocr.tsv`
- `results/mapping/mouse_non_orthologous_ocr.tsv`

as the starting point for:
- Task 3 conserved vs species-specific OCR comparison
- Task 4 GO or pathway enrichment
- Task 5 promoter vs enhancer comparison
- Task 6 TF motif analysis
