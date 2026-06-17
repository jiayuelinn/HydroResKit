import pandas as pd

from hydroreskit.adapters.merge import merge_indicator_tables


def test_merge_indicator_tables_without_duplicates():
    left = pd.DataFrame({"HYBAS_ID": [2, 1], "a": [20, 10]})
    right = pd.DataFrame({"HYBAS_ID": [1, 2], "b": [100, 200]})

    merged = merge_indicator_tables([left, right], unit_id_column="HYBAS_ID")

    assert merged["HYBAS_ID"].tolist() == [1, 2]
    assert merged["a"].tolist() == [10, 20]
    assert merged["b"].tolist() == [100, 200]


def test_merge_indicator_tables_duplicate_error():
    left = pd.DataFrame({"HYBAS_ID": [1], "a": [10]})
    right = pd.DataFrame({"HYBAS_ID": [1], "a": [100]})

    try:
        merge_indicator_tables([left, right], unit_id_column="HYBAS_ID")
    except ValueError as exc:
        assert "Duplicate indicator columns" in str(exc)
    else:
        raise AssertionError("Duplicate columns should fail with duplicate_policy='error'.")


def test_merge_indicator_tables_duplicate_coalesce():
    left = pd.DataFrame({"HYBAS_ID": [1, 2], "a": [pd.NA, 20]})
    right = pd.DataFrame({"HYBAS_ID": [1, 2], "a": [100, 200]})

    merged = merge_indicator_tables(
        [left, right],
        unit_id_column="HYBAS_ID",
        duplicate_policy="coalesce",
    )

    assert merged["a"].tolist() == [100, 20]
