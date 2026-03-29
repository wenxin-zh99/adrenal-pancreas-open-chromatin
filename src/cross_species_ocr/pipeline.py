from __future__ import annotations

from pathlib import Path

from .annotation import annotate_with_nearest_tss, load_tss_index
from .config import AppConfig, AnnotationConfig
from .logging_utils import setup_logging
from .mapping import build_pair_tables, hal_liftover_available, read_liftover_bed, run_hal_liftover
from .peaks import discover_peak_file, read_peak_table, standardize_peak_table, write_bed, write_manifest, write_table
from .reporting import plot_count_summary, plot_rate_summary, write_summary_table


def ensure_output_dirs(config: AppConfig) -> None:
    for path in [
        config.outputs.mapping_dir,
        config.outputs.tables_dir,
        config.outputs.figures_dir,
        config.outputs.logs_dir,
        config.outputs.temp_dir,
    ]:
        path.mkdir(parents=True, exist_ok=True)


def discover_inputs(config: AppConfig) -> dict[str, str]:
    return {
        'human_peak_file': discover_peak_file(config.human.peak_candidates),
        'mouse_peak_file': discover_peak_file(config.mouse.peak_candidates),
        'hal_file': config.mapping.hal_file,
        'human_tss_bed': config.human.tss_bed or '',
        'mouse_tss_bed': config.mouse.tss_bed or '',
    }


def prepare_species_table(species: str, peak_path: str, tss_bed: str | None, config: AppConfig, logger):
    logger.info('Reading %s peaks from %s', species, peak_path)
    raw = read_peak_table(peak_path)
    standardized = standardize_peak_table(raw, species)
    logger.info('Standardized %s OCRs: %s', species, len(standardized))
    if config.annotation.enabled and tss_bed and Path(tss_bed).exists():
        logger.info('Annotating %s OCRs with nearest TSS from %s', species, tss_bed)
        tss_index = load_tss_index(tss_bed)
        standardized = annotate_with_nearest_tss(
            standardized,
            tss_index=tss_index,
            promoter_window_bp=config.annotation.promoter_window_bp,
        )
    return standardized


def write_processed_outputs(df, species: str, mapping_dir: Path) -> tuple[Path, Path]:
    bed_path = mapping_dir / f'{species}_pancreas_ocr.processed.bed'
    table_path = mapping_dir / f'{species}_pancreas_ocr.processed.tsv'
    write_bed(df, bed_path)
    write_table(df, table_path)
    return bed_path, table_path


def build_non_orthologous_table(df, orthologous_ids: set[str], lifted_ids: set[str], overlapped_ids: set[str]):
    non_orth = df[~df['peak_id'].isin(orthologous_ids)].copy()
    reasons = []
    for row in non_orth.itertuples(index=False):
        if row.peak_id not in lifted_ids:
            reasons.append('no_liftover')
        elif row.peak_id not in overlapped_ids:
            reasons.append('no_target_overlap')
        else:
            reasons.append('non_reciprocal_best_hit')
    non_orth['mapping_status'] = 'non_orthologous'
    non_orth['non_orthologous_reason'] = reasons
    return non_orth


def run_pipeline(config: AppConfig, skip_mapping: bool = False, skip_annotation: bool = False) -> dict[str, Path | str]:
    if skip_annotation:
        config = AppConfig(
            project_name=config.project_name,
            tissue=config.tissue,
            human=config.human,
            mouse=config.mouse,
            mapping=config.mapping,
            annotation=AnnotationConfig(enabled=False, promoter_window_bp=config.annotation.promoter_window_bp),
            outputs=config.outputs,
            runtime=config.runtime,
            raw=config.raw,
        )

    ensure_output_dirs(config)
    log_file = config.outputs.logs_dir / 'task2_pancreas_mapping.log'
    logger = setup_logging(log_file)
    discovered = discover_inputs(config)
    logger.info('Discovered inputs: %s', discovered)

    human_df = prepare_species_table('human', discovered['human_peak_file'], config.human.tss_bed, config, logger)
    mouse_df = prepare_species_table('mouse', discovered['mouse_peak_file'], config.mouse.tss_bed, config, logger)
    human_bed, human_table = write_processed_outputs(human_df, 'human', config.outputs.mapping_dir)
    mouse_bed, mouse_table = write_processed_outputs(mouse_df, 'mouse', config.outputs.mapping_dir)

    write_manifest([
        {
            'species': 'human',
            'input_peak_file': discovered['human_peak_file'],
            'processed_bed': str(human_bed),
            'processed_table': str(human_table),
        },
        {
            'species': 'mouse',
            'input_peak_file': discovered['mouse_peak_file'],
            'processed_bed': str(mouse_bed),
            'processed_table': str(mouse_table),
        },
    ], config.outputs.tables_dir / 'task2_input_manifest.tsv')

    if skip_mapping:
        logger.info('Skipping HAL mapping by request.')
        return {
            'human_bed': human_bed,
            'mouse_bed': mouse_bed,
            'human_table': human_table,
            'mouse_table': mouse_table,
            'log_file': log_file,
        }

    if not hal_liftover_available(config.mapping.hal_liftover_bin):
        raise RuntimeError(
            'halLiftover is not available on PATH. Load the HAL module on Bridges-2 or set mapping.hal_liftover_bin in the YAML config.'
        )

    human_to_mouse_bed = config.outputs.temp_dir / 'human_to_mouse.lifted.bed'
    mouse_to_human_bed = config.outputs.temp_dir / 'mouse_to_human.lifted.bed'
    logger.info('Running HAL liftover: human -> mouse')
    run_hal_liftover(
        config.mapping.hal_liftover_bin,
        config.mapping.hal_file,
        config.mapping.human_genome,
        human_bed,
        config.mapping.mouse_genome,
        human_to_mouse_bed,
    )
    logger.info('Running HAL liftover: mouse -> human')
    run_hal_liftover(
        config.mapping.hal_liftover_bin,
        config.mapping.hal_file,
        config.mapping.mouse_genome,
        mouse_bed,
        config.mapping.human_genome,
        mouse_to_human_bed,
    )

    human_lifted = read_liftover_bed(human_to_mouse_bed, 'human_ocr_', 'mouse')
    mouse_lifted = read_liftover_bed(mouse_to_human_bed, 'mouse_ocr_', 'human')
    logger.info('Lifted OCR counts | human -> mouse: %s | mouse -> human: %s', len(human_lifted), len(mouse_lifted))

    forward_pairs, reverse_pairs = build_pair_tables(
        forward_lifted=human_lifted,
        reverse_lifted=mouse_lifted,
        target_df=mouse_df,
        reverse_target_df=human_df,
        min_reciprocal_overlap=config.mapping.min_reciprocal_overlap,
        source_label='human',
        target_label='mouse',
    )

    orthologous_pairs = forward_pairs[forward_pairs['reciprocal_best_hit']].copy()
    orthologous_pairs_path = config.outputs.mapping_dir / 'orthologous_ocr_pairs.tsv'
    orthologous_pairs.to_csv(orthologous_pairs_path, sep='\t', index=False)

    human_orthologous_ids = set(orthologous_pairs['query_peak_id']) if not orthologous_pairs.empty else set()
    mouse_orthologous_ids = set(orthologous_pairs['target_peak_id']) if not orthologous_pairs.empty else set()
    human_lifted_ids = set(human_lifted['source_peak_id']) if not human_lifted.empty else set()
    mouse_lifted_ids = set(mouse_lifted['source_peak_id']) if not mouse_lifted.empty else set()
    human_overlapped_ids = set(forward_pairs['query_peak_id']) if not forward_pairs.empty else set()
    mouse_overlapped_ids = set(reverse_pairs['query_peak_id']) if not reverse_pairs.empty else set()

    human_non_orth = build_non_orthologous_table(human_df, human_orthologous_ids, human_lifted_ids, human_overlapped_ids)
    mouse_non_orth = build_non_orthologous_table(mouse_df, mouse_orthologous_ids, mouse_lifted_ids, mouse_overlapped_ids)
    human_non_orth_path = config.outputs.mapping_dir / 'human_non_orthologous_ocr.tsv'
    mouse_non_orth_path = config.outputs.mapping_dir / 'mouse_non_orthologous_ocr.tsv'
    human_non_orth.to_csv(human_non_orth_path, sep='\t', index=False)
    mouse_non_orth.to_csv(mouse_non_orth_path, sep='\t', index=False)

    summary_rows = [
        {'metric': 'human_total', 'value': int(len(human_df))},
        {'metric': 'mouse_total', 'value': int(len(mouse_df))},
        {'metric': 'human_lifted', 'value': int(len(human_lifted_ids))},
        {'metric': 'mouse_lifted', 'value': int(len(mouse_lifted_ids))},
        {'metric': 'orthologous_pairs', 'value': int(len(orthologous_pairs))},
        {'metric': 'human_non_orthologous', 'value': int(len(human_non_orth))},
        {'metric': 'mouse_non_orthologous', 'value': int(len(mouse_non_orth))},
        {'metric': 'human_orthologous_rate', 'value': float(len(human_orthologous_ids) / len(human_df) if len(human_df) else 0.0)},
        {'metric': 'mouse_orthologous_rate', 'value': float(len(mouse_orthologous_ids) / len(mouse_df) if len(mouse_df) else 0.0)},
    ]
    summary_path = config.outputs.tables_dir / 'task2_mapping_summary.tsv'
    summary = write_summary_table(summary_rows, summary_path)
    count_figure = config.outputs.figures_dir / 'task2_mapping_counts.png'
    rate_figure = config.outputs.figures_dir / 'task2_mapping_rates.png'
    plot_count_summary(summary, count_figure)
    plot_rate_summary(summary, rate_figure)

    logger.info('Task 2 pipeline complete.')
    return {
        'human_bed': human_bed,
        'mouse_bed': mouse_bed,
        'human_table': human_table,
        'mouse_table': mouse_table,
        'orthologous_pairs': orthologous_pairs_path,
        'human_non_orthologous': human_non_orth_path,
        'mouse_non_orthologous': mouse_non_orth_path,
        'summary_table': summary_path,
        'count_figure': count_figure,
        'rate_figure': rate_figure,
        'log_file': log_file,
    }
