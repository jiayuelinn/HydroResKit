import pandas as pd

from hydroreskit.adapters.source_resolution import SourceTable, resolve_source_conflicts


def test_resolve_source_conflicts_renames_lower_priority_indicator():
    hydrobasins = SourceTable(
        source_id="hydrobasins_attribute",
        path="hydrobasins.csv",
        frame=pd.DataFrame({"HYBAS_ID": [1], "h_flood_prone_terrain": [10.0]}),
    )
    hydroatlas = SourceTable(
        source_id="hydroatlas",
        path="hydroatlas.csv",
        frame=pd.DataFrame({"HYBAS_ID": [1], "h_flood_prone_terrain": [2.0]}),
    )

    sources, resolution = resolve_source_conflicts(
        [hydrobasins, hydroatlas],
        schema_ids={"h_flood_prone_terrain"},
        unit_id_column="HYBAS_ID",
        priority={"h_flood_prone_terrain": ["hydroatlas", "hydrobasins_attribute"]},
    )

    by_source = {source.source_id: source.frame for source in sources}
    assert "hydrobasins_attribute__h_flood_prone_terrain" in by_source["hydrobasins_attribute"].columns
    assert "h_flood_prone_terrain" in by_source["hydroatlas"].columns
    assert resolution.loc[0, "selected_source"] == "hydroatlas"


def test_resolve_source_conflicts_requires_priority_for_duplicates():
    left = SourceTable(
        source_id="left",
        path="left.csv",
        frame=pd.DataFrame({"HYBAS_ID": [1], "x": [10.0]}),
    )
    right = SourceTable(
        source_id="right",
        path="right.csv",
        frame=pd.DataFrame({"HYBAS_ID": [1], "x": [20.0]}),
    )

    try:
        resolve_source_conflicts([left, right], schema_ids={"x"}, unit_id_column="HYBAS_ID")
    except ValueError as exc:
        assert "no priority rule" in str(exc)
    else:
        raise AssertionError("Duplicate schema indicators should require a priority rule.")
