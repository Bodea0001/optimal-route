from abc import ABC
from typing import Any, Literal, Annotated, Union, Iterator, TypeVar

from shapely.geometry import (
    shape,
    Point as ShapelyPoint,
    MultiPoint as ShapelyMultiPoint,
    LineString as ShapelyLineString,
    MultiLineString as ShapelyMultiLineString,
    Polygon as ShapelyPolygon,
    MultiPolygon as ShapelyMultiPolygon,
    GeometryCollection as ShapelyGeometryCollection
)
from shapely.geometry.base import BaseGeometry as ShapelyBaseGeomerty
from pydantic import model_validator, field_validator, Field

from models.geojsonbase import _GeoJsonBase
from models.geotypes import (
    Position,    
    PolygonCoords,
    LineStringCoords,
    MultiPointCoords,
    MultiPolygonCoords,
    MultiLineStringCoords,
)

T = TypeVar("T", bound=ShapelyBaseGeomerty)

class _GeometryBase[T](_GeoJsonBase, ABC):
    """Base class for geometry models"""

    type: str
    coordinates: Any

    @property
    def shape(self) -> T:
        return shape(self.__geo_interface__)  # type: ignore


    @model_validator(mode="before")
    def validate_shapely_geometry(cls, data: Any) -> Any:
        if hasattr(data, "__geo_interface__"):
            return data.__geo_interface__

        return data


class Point(_GeometryBase[ShapelyPoint]):
    """Point model"""

    type: Literal["Point"]
    coordinates: Position


class MultiPoint(_GeometryBase[ShapelyMultiPoint]):
    """MultiPoint model"""

    type: Literal["MultiPoint"]
    coordinates: MultiPointCoords


class LineString(_GeometryBase[ShapelyLineString]):
    """LineString model"""

    type: Literal["LineString"]
    coordinates: LineStringCoords


class MultiLineString(_GeometryBase[ShapelyMultiLineString]):
    """MultiLineString model"""

    type: Literal["MultiLineString"]
    coordinates: MultiLineStringCoords


class Polygon(_GeometryBase[ShapelyPolygon]):
    """Polygon model"""

    type: Literal["Polygon"]
    coordinates: PolygonCoords

    @field_validator("coordinates")
    def check_closure(cls, coordinates: list) -> list:
        """Validate that Polygon is closed (first and last coordinate are the same)."""
        if any(ring[-1] != ring[0] for ring in coordinates):
            raise ValueError("Все линейные кольца должны иметь одинаковые начальные и конечные координаты")

        return coordinates


class MultiPolygon(_GeometryBase[ShapelyMultiPolygon]):
    """MultiPolygon model"""

    type: Literal["MultiPolygon"]
    coordinates: MultiPolygonCoords

    @field_validator("coordinates")
    def check_closure(cls, coordinates: list) -> list:
        """Validate that Polygon is closed (first and last coordinate are the same)."""
        if any(ring[-1] != ring[0] for polygon in coordinates for ring in polygon):
            raise ValueError("Все линейные кольца должны иметь одинаковые начальные и конечные координаты")

        return coordinates


class GeometryCollection(_GeoJsonBase):
    """GeometryCollection model"""

    type: Literal["GeometryCollection"]
    geometries: list["Geometry"]

    def __iter__(self) -> Iterator["Geometry"]:
        """iterate over geometries"""
        return iter(self.geometries)

    def __len__(self) -> int:
        """return geometries length"""
        return len(self.geometries)

    def __getitem__(self, index: int) -> "Geometry":
        """get geometry at a given index"""
        return self.geometries[index]

    def shape(self) -> ShapelyGeometryCollection:
        """return shapely geometry collection"""
        return shape(self.__geo_interface__)  # type: ignore


Geometry = Annotated[
    Union[
        Point,
        MultiPoint,
        LineString,
        MultiLineString,
        Polygon,
        MultiPolygon,
        GeometryCollection,
    ],
    Field(discriminator="type"),
]

GeometryCollection.model_rebuild()
