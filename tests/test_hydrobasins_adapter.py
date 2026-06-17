import numpy as np
import pandas as pd

from hydroreskit.adapters.hydrobasins import derive_hydrobasins_attribute_indicators


def test_derive_hydrobasins_attribute_indicators():
    boundaries = pd.DataFrame(
        {
            "HYBAS_ID": [1, 2],
            "UP_AREA": [99.0, 999.0],
            "SUB_AREA": [10.0, 20.0],
            "DIST_MAIN": [100.0, 200.0],
        }
    )

    indicators = derive_hydrobasins_attribute_indicators(boundaries)

    assert indicators["HYBAS_ID"].tolist() == [1, 2]
    assert "h_flood_prone_terrain" in indicators.columns
    assert np.isclose(indicators.loc[0, "h_flood_prone_terrain"], np.log1p(99.0))
    assert np.isclose(indicators.loc[1, "hydrobasins_upstream_to_local_area_ratio"], 49.95)
    assert "hydrobasins_dist_main" in indicators.columns
