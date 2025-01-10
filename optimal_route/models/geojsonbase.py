from typing import Any

from pydantic import BaseModel, field_validator, model_serializer, SerializationInfo

from models.geotypes import BBox


class _GeoJsonBase(BaseModel):
    bbox: BBox | None = None

    __geojson_exclude_if_none__: set[str] = {"bbox"}


    @property
    def __geo_interface__(self) -> dict[str, Any]:
        return self.model_dump(mode="json")

    @field_validator("bbox")
    def _validate_bbox(cls, bbox: BBox | None) -> BBox | None:
        if bbox is None:
            return None

        if bbox.min_lat > bbox.max_lat:
            raise ValueError("Минимальная широта не может быть больше максимальной")
        
        if bbox.min_lon > bbox.max_lon:
            raise ValueError("Минимальная долгота не может быть больше максимальной")

        return bbox
        
    @model_serializer(when_used="always", mode="wrap")
    def clean_model(self, serializer: Any, info: SerializationInfo):
        data: dict[str, Any] = serializer(self)

        if info.mode_is_json():
            for field in self.__geojson_exclude_if_none__:
                if field in data and data[field] is None:
                    del data[field]

        return data
