# Phase 1 Task 1: Human and Mouse Pancreas & Adrenal QC Workflow

## Completed Workflow Steps

### 1. Data Inventory and Selection
* Scanned directories for human and mouse open chromatin datasets for the assigned tissues: **adrenal alternative** and **pancreas**.  

### 2. QC Evaluation Using Provided Metrics
* Assessed dataset quality based on the provided QC metrics, including:  
  * % mapped reads  
  * % properly paired reads  
  * Fragment periodicity  
  * Transcription Start Site (TSS) enrichment  
  * Number of distinct fragments  
  * Non-redundant fraction (NRF)  
  * Irreproducible Discovery Rate (IDR) between replicates  
  * Additional metrics supplied in the QC data  
* Reviewed QC summaries and plots to identify tissue/species datasets with higher quality.

### 3. Tissue Selection Based on QC
* **Pancreas tissue** demonstrated higher data quality across both human and mouse datasets, with:  
  * Stronger TSS enrichment  
  * Better fragment periodicity  
  * More consistent replicates  
* **Adrenal alternative tissue** was lower quality and deprioritized for cross-species mapping.

### 4. Outputs
* QC summary table organized under `results/qc/`.  
* Markdown QC report summarizing metrics, replicate comparisons, and tissue selection rationale.  

## Reproducibility and Organization
* Paths, filenames, and species/tissue choices are configurable via `config/project_config.yaml`.  
* No hard-coded file paths were used.  
* All outputs are versioned and organized for transparency and reproducibility.
