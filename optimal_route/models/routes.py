from typing import Any

from pydantic import BaseModel, model_validator, ValidationError

from models.features import Feature, FeatureCollection
from models.geometries import Point, MultiPolygon, LineString


class RouteFindDTO(BaseModel):
    start_point: Feature[dict[str, Any], Point]
    finish_point: Feature[dict[str, Any], Point]
    restricted_polygons: Feature[dict[str, Any], MultiPolygon] | None

    @model_validator(mode="before")
    def from_feature_collection(cls, data: Any):
        if not isinstance(data, dict):
            raise ValidationError("Данные поданы в неверном формате")

        feature_collection = FeatureCollection.model_validate(data)

        valid_dict = {
            "start_point": None,
            "finish_point": None,
            "restricted_polygons": None
        }

        for feature in feature_collection:
            name = feature.properties.get("name")
            if name == "start_point":
                valid_dict["start_point"] = feature
            elif name == "finish_point":
                valid_dict["finish_point"] = feature
            elif name == "restricted_polygons":
                valid_dict["restricted_polygons"] = feature

        if not valid_dict["start_point"] or not valid_dict["finish_point"]:
            raise ValueError("Необходимо указать начальную и конечную точку")

        return valid_dict


class RouteSendDTO(LineString):
    pass
