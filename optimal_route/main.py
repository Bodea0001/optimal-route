from itertools import combinations
from typing import Any, Iterable, NamedTuple

from pyproj import Geod
from networkx import Graph
from shapely import MultiPolygon, Point, LineString, Polygon
from shapely.validation import explain_validity

from optimal_route.models.routes import RouteFindDTO, RouteSendDTO
from optimal_route.utils.buffer import buffer_geometry_in_metres
from optimal_route.utils.route import find_fastest_route_in_graph


def find_optimal_route_with_geojson(geojson: str) -> str:
    """
    Функция для нахождения оптимального пути с помощью GeoJSON
    """

    route_data = _validate_route_geojson_to_data(geojson)

    route_send_data = find_optimal_route_with_pydantic_model(route_data)
    
    geojson_to_send = _serialize_route_data_to_geojson(route_send_data)
    return geojson_to_send


def find_optimal_route_with_pydantic_model(data: RouteFindDTO) -> RouteSendDTO:
    """
    Функция для нахождения оптимального пути с помощью pydantic моделей
    """

    route_search_data = _process_data_to_find_route(data)

    optimal_route = find_optimal_route(**route_search_data._asdict())

    route_send_data = _process_data_to_send_route(optimal_route)

    return route_send_data


def find_optimal_route(
    start_point: Point,
    finish_point: Point,
    restricted_polygons: MultiPolygon | None = None,
    buffer_distance: float | None = None,
    coord_system: str = "WGS84"
) -> LineString:
    """
    Функция для нахождения оптимального маршрута исходя из наличия зон запрета
    """

    fastest_route = LineString([start_point, finish_point])

    # Проверка на наличие запретных зон
    if not restricted_polygons:
        return fastest_route

    # Проверка на валидность запретных зон
    if not restricted_polygons.is_valid:
        raise ValueError("Запретные зоны не валидны: " + explain_validity(restricted_polygons))

    # Буферизация запретных зон
    if buffer_distance:
        buffered = buffer_geometry_in_metres(restricted_polygons, buffer_distance)
        restricted_polygons = _make_multipolygon(buffered)

    # Проверка на пересечение самого оптимального маршрута (прямая от стартовой точки до финишной)
    # с запретными зонами
    if not (
        fastest_route.crosses(restricted_polygons) or 
        restricted_polygons.contains(fastest_route)
    ):
        return fastest_route
    
    # Проверка на наличие точек в запретных зонах
    if (
        restricted_polygons.contains(start_point) or 
        restricted_polygons.contains(finish_point)
    ):
        raise ValueError("Точки не могут находиться в запретной зоне")

    # Создание списка с вершинами
    vertices = {(start_point.x, start_point.y), (finish_point.x, finish_point.y)}

    for polygon in restricted_polygons.geoms:
        # Проверка на наличие маршрута от начальной точки до финишной
        # (проверяется, не запечатана ли начальная или конечная точки, т.е.не находится ли какая-то из этих точек
        # в отверстии, которое находится в одном из многоугольников)
        holes = MultiPolygon(tuple(Polygon(interior) for interior in polygon.interiors))
        
        start_point_in_holes = _exists_point_in_multipolygon(holes, start_point)
        finish_point_in_holes = _exists_point_in_multipolygon(holes, finish_point)
        
        if start_point_in_holes:
            raise ValueError("Невозможно проложить маршрут: начальная точка находится в отверстии одного из полигонов")
        elif finish_point_in_holes:
            raise ValueError("Невозможно проложить маршрут: конечная точка находится в отверстии одного из полигонов")

        # Добавление вершин, которые находятся в запретных зонах
        vertices.update(polygon.exterior.coords)
    
    # Создание списка ребер
    edges = combinations(vertices, 2)

    # Отбор тех ребер, которые не пересекают запретные зоны
    filtered_edges = _filter_edges(edges, restricted_polygons)

    # Создание графа
    graph = Graph()

    # Добавление вершин в граф
    graph.add_nodes_from(vertices)

    # Добавление тех ребер в граф, которые не пересекают запретные зоны
    graph.add_edges_from(filtered_edges)

    # Создание вызываемого объекта для вычисления веса ребер
    geod = Geod(ellps=coord_system)
    edge_weight = _EgdeWeight(geod)
    
    # Поиск кратчайшего пути
    optimal_route = find_fastest_route_in_graph(graph, start_point, finish_point, edge_weight)

    return optimal_route


def _validate_route_geojson_to_data(geojson: str) -> RouteFindDTO:
    """
    Функция для получения данных для поиска маршрута из GeoJSON
    """

    return RouteFindDTO.model_validate_json(geojson)


def _serialize_route_data_to_geojson(data: RouteSendDTO) -> str:
    """
    Функция для передачи обработанных данных уже найденного оптимального маршрута в GeoJSON
    """

    return data.model_dump_json()


RouteSearch = NamedTuple(
    "RouteSearch", 
    [
        ("start_point", Point),
        ("finish_point", Point),
        ("restricted_polygons", MultiPolygon | None),
        ("buffer_distance", float | None)
    ]
)


def _process_data_to_find_route(data: RouteFindDTO) -> RouteSearch:
    """
    Функция для передачи обработанных данных для последующего поиска маршрута
    """

    start_point = data.start_point.geometry.shape
    finish_point = data.finish_point.geometry.shape

    if data.restricted_polygons:
        restricted_polygons = data.restricted_polygons.geometry.shape
        buffer_distance = data.restricted_polygons.properties.get("buffer_distance")
    else:
        restricted_polygons = None
        buffer_distance = None

    return RouteSearch(start_point, finish_point, restricted_polygons, buffer_distance)


def _process_data_to_send_route(data: LineString) -> RouteSendDTO:
    """
    Функция для передачи обработанных данных уже найденного оптимального маршрута
    """

    return RouteSendDTO.model_validate(data)


def _make_multipolygon(geometry: Polygon | MultiPolygon) -> MultiPolygon:
    """
    Функция для создания объекта типа MultiPolygon
    """
    
    if isinstance(geometry, MultiPolygon):
        return geometry

    return MultiPolygon([geometry])


def _exists_point_in_multipolygon(polygon: MultiPolygon, point: Point) -> bool:
    return any((polygon.contains(point), polygon.touches(point)))


#! Долгое время работы
def _filter_edges(
    edges: Iterable[tuple[tuple[float, float], tuple[float, float]]],
    zone: MultiPolygon
) -> set[tuple[tuple[float, float], tuple[float, float]]]:
    """
    Функция для отбора тех ребер, которые не пересекают зону и не входят в него
    """

    filtered_edges = set() 

    for edge in edges:
        line = LineString(edge)
        if not line.crosses(zone) and not zone.contains(line):
            filtered_edges.add(edge)

    return filtered_edges


class _EgdeWeight:
    def __init__(self, geod: Geod) -> None:
        self._geod = geod

    def __call__(self, u: tuple[float, float], v: tuple[float, float], d: Any | None = None) -> float:
        ux, uy = u
        vx, vy = v
        return self._geod.inv(ux, uy, vx, vy)[2]
