# Task 2 Progress Report: Cross-Species OCR Mapping in Pancreas

Generated on 2026-03-27.

## Status

Task 2 is partially complete.

Completed now:
- Project scaffold for Task 2 is in place.
- Human and mouse pancreas OCR inputs are configured and automatically discovered.
- Peak standardization is implemented and verified.
- Optional lightweight annotation is implemented and verified.
- Logging, config support, manifests, and output directories are implemented.
- The HAL-based mapping step is implemented in code.
- The full pipeline entry point is wired up.

Not yet completed in a successful end-to-end run:
- Human-to-mouse liftover execution
- Mouse-to-human liftover execution
- Orthologous OCR table generation
- Human non-orthologous OCR table generation
- Mouse non-orthologous OCR table generation
- Mapping summary TSV and summary figures

## What Was Verified

The following commands were run successfully from the project directory:

```bash
PYTHONPATH=src python3 -m py_compile scripts/run_task2_pancreas_mapping.py src/cross_species_ocr/*.py
PYTHONPATH=src python3 scripts/run_task2_pancreas_mapping.py discover --config config/task2_pancreas_mapping.yaml
PYTHONPATH=src python3 scripts/run_task2_pancreas_mapping.py run --config config/task2_pancreas_mapping.yaml --skip-mapping
```

The preprocessing-only run completed successfully on the real pancreas datasets.

## Current Processed Outputs

Generated and present now:
- `results/mapping/human_pancreas_ocr.processed.bed`
- `results/mapping/mouse_pancreas_ocr.processed.bed`
- `results/mapping/human_pancreas_ocr.processed.tsv`
- `results/mapping/mouse_pancreas_ocr.processed.tsv`
- `results/tables/task2_input_manifest.tsv`
- `results/logs/task2_pancreas_mapping.log`

## Current Counts

After standardization and duplicate cleanup:
- Human pancreas OCRs: 89,476
- Mouse pancreas OCRs: 47,189

These counts are lower than the raw line counts in the compressed input files because the pipeline removes duplicate coordinate rows and invalid intervals.

## Inputs In Use

Configured defaults:
- Human peaks: `/ocean/projects/bio230007p/ikaplow/HumanAtac/Pancreas/peak/idr_reproducibility/idr.optimal_peak.narrowPeak.gz`
- Mouse peaks: `/ocean/projects/bio230007p/ikaplow/MouseAtac/Pancreas/peak/idr_reproducibility/idr.optimal_peak.narrowPeak.gz`
- HAL alignment: `/ocean/projects/bio230007p/ikaplow/Alignments/10plusway-master.hal`
- Human TSS bed: `/ocean/projects/bio230007p/ikaplow/HumanGenomeInfo/gencode.v27.annotation.protTranscript.TSSsWithStrand_sorted.bed`
- Mouse TSS bed: `/ocean/projects/bio230007p/ikaplow/MouseGenomeInfo/gencode.vM15.annotation.protTranscript.geneNames_TSSWithStrand_sorted.bed`

HAL species names configured in YAML:
- `Human`
- `Mouse`

## Caveats Right Now

### 1. Main blocker: `halLiftover` is not available on PATH

The full pipeline was run and stopped at the mapping stage with this effective blocker:
- `RuntimeError: halLiftover is not available on PATH.`

This means the code is ready to attempt mapping, but the required external HAL executable is not currently visible in this session.

### 2. End-to-end Task 2 is not fully finished yet

The project is not fully done because the actual cross-species mapping outputs have not been produced yet. The implemented code path is there, but the environment dependency still needs to be resolved.

### 3. Mapping logic is conservative by design

The current implementation calls orthologous OCRs using reciprocal best-hit overlap after liftover. That is a reasonable Task 2 default, but if your team later wants a looser or stricter definition, the overlap threshold and matching logic can be adjusted in the YAML or code.

### 4. Annotation is intentionally lightweight

Nearest-gene and promoter/distal labels are included to help later tasks, but this is not meant to replace downstream enrichment, promoter-enhancer analysis, or motif analysis.

## What I Need From You To Finish The Full Run

I do need one thing from you before I can finish the full end-to-end run:
- access to `halLiftover`, either by
  - telling me the correct module to load on Bridges-2, or
  - giving me the full path to the `halLiftover` executable, or
  - confirming the command you normally use to access HAL tools on a regular memory node

Once that is available, I can run the full Task 2 pipeline and generate:
- orthologous OCR pairs
- species-specific OCR tables
- mapping summary TSV
- summary figures

## Is The Task Done Already?

Not fully.

What is done:
- the Task 2 scaffold
- preprocessing and annotation
- verified runnable CLI
- verified processed OCR outputs
- verified clean failure mode when HAL mapping is unavailable

What is not done:
- the actual cross-species OCR mapping results

## Recommended Next Step

After `halLiftover` is available, run:

```bash
PYTHONPATH=src python3 scripts/run_task2_pancreas_mapping.py run --config config/task2_pancreas_mapping.yaml
```

If that should run on a regular memory node, the same command can be placed into a job script once the HAL environment is known.
