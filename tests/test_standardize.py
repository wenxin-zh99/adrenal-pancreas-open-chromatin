import pandas as pd

from cross_species_ocr.peaks import standardize_peak_table


def test_standardize_peak_table_assigns_ids_and_widths():
    df = pd.DataFrame([
        ['chr1', 10, 30, '.', 1000, '.', 5.0, 10.0, 9.0, 4],
        ['chr1', 40, 60, '.', 500, '.', 3.0, 8.0, 7.0, 5],
    ], columns=['chrom', 'start', 'end', 'name', 'score', 'strand', 'signal_value', 'p_value', 'q_value', 'summit'])

    standardized = standardize_peak_table(df, 'human')

    assert list(standardized['peak_id']) == ['human_ocr_0000001', 'human_ocr_0000002']
    assert list(standardized['width']) == [20, 20]
    assert set(standardized['species']) == {'human'}
