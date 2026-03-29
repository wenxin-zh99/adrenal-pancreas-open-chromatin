from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class SpeciesConfig:
    name: str
    genome_name: str
    peak_candidates: list[str]
    tss_bed: str | None


@dataclass(frozen=True)
class MappingConfig:
    hal_file: str
    hal_liftover_bin: str
    human_genome: str
    mouse_genome: str
    min_reciprocal_overlap: float


@dataclass(frozen=True)
class AnnotationConfig:
    enabled: bool
    promoter_window_bp: int


@dataclass(frozen=True)
class OutputConfig:
    mapping_dir: Path
    tables_dir: Path
    figures_dir: Path
    logs_dir: Path
    temp_dir: Path


@dataclass(frozen=True)
class RuntimeConfig:
    overwrite: bool


@dataclass(frozen=True)
class AppConfig:
    project_name: str
    tissue: str
    human: SpeciesConfig
    mouse: SpeciesConfig
    mapping: MappingConfig
    annotation: AnnotationConfig
    outputs: OutputConfig
    runtime: RuntimeConfig
    raw: dict[str, Any]


def load_config(path: str | Path) -> AppConfig:
    config_path = Path(path)
    data = yaml.safe_load(config_path.read_text(encoding='utf-8'))
    inputs = data['inputs']
    mapping = data['mapping']
    annotation = data['annotation']
    outputs = data['outputs']
    runtime = data['runtime']

    return AppConfig(
        project_name=data['project_name'],
        tissue=data['tissue'],
        human=SpeciesConfig(
            name='human',
            genome_name=mapping['human_genome'],
            peak_candidates=list(inputs['human_peak_candidates']),
            tss_bed=inputs.get('human_tss_bed'),
        ),
        mouse=SpeciesConfig(
            name='mouse',
            genome_name=mapping['mouse_genome'],
            peak_candidates=list(inputs['mouse_peak_candidates']),
            tss_bed=inputs.get('mouse_tss_bed'),
        ),
        mapping=MappingConfig(
            hal_file=mapping['hal_file'],
            hal_liftover_bin=mapping.get('hal_liftover_bin', 'halLiftover'),
            human_genome=mapping['human_genome'],
            mouse_genome=mapping['mouse_genome'],
            min_reciprocal_overlap=float(mapping.get('min_reciprocal_overlap', 0.2)),
        ),
        annotation=AnnotationConfig(
            enabled=bool(annotation.get('enabled', True)),
            promoter_window_bp=int(annotation.get('promoter_window_bp', 2000)),
        ),
        outputs=OutputConfig(
            mapping_dir=Path(outputs['mapping_dir']),
            tables_dir=Path(outputs['tables_dir']),
            figures_dir=Path(outputs['figures_dir']),
            logs_dir=Path(outputs['logs_dir']),
            temp_dir=Path(outputs['temp_dir']),
        ),
        runtime=RuntimeConfig(overwrite=bool(runtime.get('overwrite', True))),
        raw=data,
    )
