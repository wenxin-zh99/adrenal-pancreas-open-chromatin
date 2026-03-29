# Task 2 Workflow: Cross-Species OCR Mapping in Pancreas

## Goal

Build a reproducible mapping workflow that links human and mouse pancreas OCRs into a unified cross-species map.

## Pipeline Stages

1. Discover the configured human and mouse pancreas peak files.
2. Standardize each narrowPeak file into:
   - a clean BED file for mapping
   - a richer TSV table for downstream analysis
3. Optionally annotate each OCR with:
   - nearest gene
   - distance to nearest TSS
   - promoter or distal label
4. Lift OCR coordinates from human to mouse and mouse to human using `halLiftover`.
5. Intersect lifted OCRs with target-species OCRs and score candidate matches by reciprocal overlap.
6. Call reciprocal best-hit OCR pairs as orthologous mappings.
7. Label remaining OCRs as non-orthologous with reason categories such as:
   - `no_liftover`
   - `no_target_overlap`
   - `non_reciprocal_best_hit`
8. Write summary tables and simple count and proportion figures.

## Why Reciprocal Best Hits

Reciprocal best-hit matching is a conservative default for Task 2 because it yields a clean orthologous table for downstream team tasks while still preserving a separate non-orthologous set. It avoids over-claiming conservation when one lifted OCR overlaps multiple candidate peaks.

## Downstream Compatibility

The written tables are intended to support later tasks by preserving stable IDs, standardized coordinates, species labels, annotation fields, and mapping status fields.
