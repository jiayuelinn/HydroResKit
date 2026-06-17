import geopandas as gpd
from shapely.geometry import Polygon

from hydroreskit.adapters.boundary import find_containing_boundary, select_main_basin_by_point


def test_select_main_basin_by_point():
    gdf = gpd.GeoDataFrame(
        {
            "HYBAS_ID": [1, 2, 3],
            "MAIN_BAS": [10, 10, 20],
            "geometry": [
                Polygon([(0, 0), (1, 0), (1, 1), (0, 1)]),
                Polygon([(1, 0), (2, 0), (2, 1), (1, 1)]),
                Polygon([(3, 0), (4, 0), (4, 1), (3, 1)]),
            ],
        },
        crs="EPSG:4326",
    )
    containing = find_containing_boundary(gdf, 0.5, 0.5)
    assert containing["HYBAS_ID"].iloc[0] == 1
    selected = select_main_basin_by_point(gdf, lon=0.5, lat=0.5)
    assert selected["HYBAS_ID"].tolist() == [1, 2]

