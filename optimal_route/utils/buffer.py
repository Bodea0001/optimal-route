from typing import TypeVar, overload

from pyproj import Proj, Transformer, CRS
from shapely.ops import transform
from shapely.geometry import MultiPolygon, Polygon
from shapely.geometry.base import BaseGeometry


default_crs = "WGS84"

@overload
def buffer_geometry_in_metres(
    geometry: MultiPolygon,
    buffer_distance: float,
    coord_system: str = ...
) -> Polygon | MultiPolygon:
    ...

@overload
def buffer_geometry_in_metres(
    geometry: BaseGeometry,
    buffer_distance: float,
    coord_system: str = ...
) -> Polygon:
    ...


def buffer_geometry_in_metres(  # type: ignore
    geometry: BaseGeometry, 
    buffer_distance: float,
    coord_system: str = "WGS84"
) -> Polygon | MultiPolygon:
    """Функция для буферизации запретных зон"""

    # Получение центроида
    centroid = geometry.centroid

    # Азимутальная равнопромежуточноя проекция
    local_projection = Proj(
        proj="aeqd",
        ellps=coord_system,
        datum=coord_system,
        lat_0=centroid.y,
        lon_0=centroid.x
    )

    # Преобразование геометрической фигуры в локальную систему координат
    geometry_local = _to_local(geometry, local_projection, coord_system)

    # Буферизация геометрической фигуры
    buffered_geometry_local = geometry_local.buffer(buffer_distance, join_style="mitre")

    # Преобразование обратно в WGS84
    buffered_geometry = _from_local(buffered_geometry_local, local_projection, coord_system)

    return buffered_geometry


BaseShapelyGeometry = TypeVar("BaseShapelyGeometry", bound=BaseGeometry)


def _to_local(geometry: BaseShapelyGeometry, projection, crs: str) -> BaseShapelyGeometry:
    """Преобразование геометрической фигуры в локальную систему координат"""
    project_to_local = Transformer.from_proj(CRS(crs), projection, always_xy=True)
    return transform(project_to_local.transform, geometry)

def _from_local(geometry: BaseShapelyGeometry, projection, crs: str) -> BaseShapelyGeometry:
    """Преобразование геометрической фигуры из локальной системы координат"""
    project_to_wgs84 = Transformer.from_proj(projection, CRS(crs), always_xy=True)
    return transform(project_to_wgs84.transform, geometry)
