from decimal import Decimal
from typing import NamedTuple, Annotated

from pydantic import Field


BBox = NamedTuple("BBox", [("min_lon", Decimal), ("min_lat", Decimal), ("max_lon", Decimal), ("max_lat", Decimal)])

Position = NamedTuple("Position", [("longitude", Decimal), ("latitude", Decimal)])

LineStringCoords = Annotated[list[Position], Field(min_length=2)]
LinearRing = Annotated[list[Position], Field(min_length=4)]
MultiPointCoords = list[Position]
MultiLineStringCoords = list[LineStringCoords]
PolygonCoords = list[LinearRing]
MultiPolygonCoords = list[PolygonCoords]
