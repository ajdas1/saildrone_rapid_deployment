
import geopandas
import numpy as np
import pandas as pd


from typing import Dict


def lat_lon_coordinates(
        lon_min: float = -100., lon_max: float = -80.,
        lat_min: float = 15., lat_max: float = 33.,
        dlon: float = 0.05, dlat: float=0.05,
) -> Dict:

    longitudes = np.arange(lon_min, lon_max+dlon, dlon)
    latitudes = np.arange(lat_min, lat_max+dlat, dlat)

    return {
        "lat": latitudes,
        "lon": longitudes
    }

def lat_lon_grid(lon_min: float = -100., lon_max: float = -80.,
        lat_min: float = 15., lat_max: float = 33.,
        dlon: float = 0.05, dlat: float=0.05
) -> Dict:

    coords = lat_lon_coordinates(lon_min=lon_min, lon_max=lon_max, lat_min=lat_min, lat_max=lat_max, dlon=dlon, dlat=dlat)
    longrid, latgrid = np.meshgrid(coords["lon"], coords["lat"])

    return {
        "lat": latgrid,
        "lon": longrid
    }

def lat_lon_points(
        lon_min: float = -100., lon_max: float = -80.,
        lat_min: float = 15., lat_max: float = 33.,
        dlon: float = 0.05, dlat: float=0.05
) -> geopandas.array.GeometryArray:

    grid = lat_lon_grid(lon_min=lon_min, lon_max=lon_max, lat_min=lat_min, lat_max=lat_max, dlon=dlon, dlat=dlat)

    df = pd.DataFrame({"longitude": np.ravel(grid["lon"]), "latitude": np.ravel(grid["lat"])})
    geometry = geopandas.points_from_xy(df.longitude, df.latitude, crs="EPSG:4326")

    return geometry


def mask_point_grid_in_polygon(gom_points: geopandas.GeoSeries, polygon: geopandas.GeoSeries, point_coordinates: Dict, mask_value: int = 1) -> np.ndarray:

    polygon_overlap_grid = np.zeros((len(point_coordinates["lat"]), len(point_coordinates["lon"])))

    if polygon is not None:

        for point in gom_points:
            if polygon.contains(point):
                lonval = point.x
                latval = point.y
                lonidx = list(point_coordinates["lon"]).index(lonval)
                latidx = list(point_coordinates["lat"]).index(latval)
                polygon_overlap_grid[latidx, lonidx] = mask_value

    return polygon_overlap_grid