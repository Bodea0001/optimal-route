from typing import Callable

from networkx import Graph
from networkx.exception import NetworkXNoPath
from networkx.algorithms.shortest_paths.astar import astar_path
from shapely.geometry import LineString, Point


def find_fastest_route_in_graph(
    graph: Graph, 
    start_point: Point,
    finish_point: Point, 
    edge_weight: str | Callable
) -> LineString:
    # Начальная и конечная точки
    source = (start_point.x, start_point.y)
    target = (finish_point.x, finish_point.y)

    try:
        optimal_route = astar_path(graph, source, target, weight=edge_weight)  # type: ignore
        optimal_route = LineString(optimal_route)
    except NetworkXNoPath:
        raise ValueError("Невозможно проложить маршрут: нет пути между начальной и конечной точками")

    return optimal_route
    