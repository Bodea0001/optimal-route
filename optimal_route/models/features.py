from typing import Any, Literal, Iterator

from pydantic import BaseModel, Field, StrictInt, StrictStr, field_validator

from optimal_route.models.geometries import Geometry
from optimal_route.models.geojsonbase import _GeoJsonBase


class Feature[Props: dict[str, Any] | BaseModel, Geom: Geometry](_GeoJsonBase):
    """Feature Model"""

    type: Literal["Feature"] = Field(default="Feature", frozen=True)
    id: StrictInt | StrictStr | None = None
    properties: Props = Field(...)
    geometry: Geom = Field(...)

    __geojson_exclude_if_none__ = {"bbox", "id"}

    @field_validator("geometry", mode="before")
    def set_geometry(cls, geometry: Any) -> Any:
        """set geometry from geo interface or input"""
        if hasattr(geometry, "__geo_interface__"):
            return geometry.__geo_interface__

        return geometry


class FeatureCollection[Feat: Feature](_GeoJsonBase):
    """FeatureCollection Model"""

    type: Literal["FeatureCollection"]
    features: list[Feat]

    def __iter__(self) -> Iterator[Feat]:
        """iterate over features"""
        return iter(self.features)

    def __len__(self) -> int:
        """return features length"""
        return len(self.features)

    def __getitem__(self, index: int) -> Feat:
        """get feature at a given index"""
        return self.features[index]
