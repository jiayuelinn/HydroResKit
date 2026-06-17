import numpy as np
import pandas as pd

from hydroreskit.adapters.hydroatlas import derive_hydroatlas_indicators


def test_derive_hydroatlas_indicators_from_available_columns():
    frame = pd.DataFrame(
        {
            "HYBAS_ID": [1, 2],
            **{f"pre_mm_s{month:02d}": [month, month * 2] for month in range(1, 13)},
            "cmi_ix_syr": [10.0, -5.0],
            "inu_pc_slt": [2.0, 8.0],
            "ppd_pk_sav": [100.0, 250.0],
            "urb_pc_sse": [5.0, 20.0],
            "crp_pc_sse": [30.0, 50.0],
            "slp_dg_sav": [1.5, 6.0],
            "for_pc_sse": [70.0, 30.0],
            "pet_mm_syr": [900.0, 1100.0],
            "aet_mm_syr": [700.0, 500.0],
            "lka_pc_sse": [1.0, 4.0],
            "wet_pc_sg1": [2.0, 3.0],
            "wet_pc_sg2": [1.0, 2.0],
            "gdp_ud_sav": [1000.0, 3000.0],
        }
    )

    indicators, metadata = derive_hydroatlas_indicators(frame)

    assert indicators["HYBAS_ID"].tolist() == [1, 2]
    assert metadata.query("status == 'derived'").shape[0] == 12
    assert "h_precip_variability" in indicators.columns
    assert np.isclose(indicators.loc[0, "h_drought_intensity"], -10.0)
    assert np.isclose(indicators.loc[1, "s_ecological_fragility"], 70.0)
    assert np.isclose(indicators.loc[0, "a_green_blue_space_fraction"], 74.0)


def test_derive_hydroatlas_indicators_skips_missing_columns():
    frame = pd.DataFrame({"HYBAS_ID": [1], "ppd_pk_sav": [100.0]})

    indicators, metadata = derive_hydroatlas_indicators(frame)

    assert list(indicators.columns) == ["HYBAS_ID", "e_population_density"]
    assert metadata.query("status == 'derived'")["indicator_id"].tolist() == ["e_population_density"]
    assert metadata.query("status == 'skipped'").shape[0] == 11
