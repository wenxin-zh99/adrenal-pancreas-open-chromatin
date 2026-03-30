#!/bin/bash
#SBATCH -A bio230007p
#SBATCH -p RM-shared
#SBATCH --qos=rm
#SBATCH -J task2_pancreas_map
#SBATCH -N 1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=12
#SBATCH --mem=20G
#SBATCH -t 08:00:00
#SBATCH -o results/logs/task2_pancreas_mapping.%j.out
#SBATCH -e results/logs/task2_pancreas_mapping.%j.err

set -euo pipefail

cd /ocean/projects/bio230007p/aguda1/adrenal-pancreas-open-chromatin
export PYTHONPATH=src

python3 scripts/run_task2_pancreas_mapping.py run --config config/task2_pancreas_mapping.yaml
