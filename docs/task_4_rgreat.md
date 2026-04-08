# Task 4: GO Biological Process Enrichment with rGREAT

## Goal
Identify biological processes associated with species-specific open chromatin regions.

## Input
- `mouse_specific.bed`
- `human_specific.bed`
- `conserved_human_in_mouse.bed`
- `conserved_mouse_in_human.bed`

## Method
We used `rGREAT` to perform GO Biological Process enrichment analysis on species-specific peak sets.

### Foreground
- mouse: `mouse_specific.bed`
- human: `human_specific.bed`

### Background
- mouse: `mouse_specific.bed + conserved_human_in_mouse.bed`
- human: `human_specific.bed + conserved_mouse_in_human.bed`

We used relevant peak sets rather than the whole genome as background, because our goal was to compare functional enrichment within experimentally observed regulatory regions.

## Main script
- `scripts/task_4_rgreat_go_bp.R`

## Output
Results are saved in:
- `results/task_4_rgreat/`

## Summary
Mouse-specific and human-specific open chromatin regions showed distinct GO BP enrichment patterns, suggesting species-biased regulatory programs.
