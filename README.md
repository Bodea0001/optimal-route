## Описание:
`optimal_route` - модуль, реализующий поиск оптимального маршрута между двумя геопозициями исходя из наличия зон запрета для передвижения.

## Установка:
```shell
python -m pip install git+https://github.com/Bodea0001/optimal-route.git
```

## Использование:

- Пример данных
```json
{
	"type": "FeatureCollection",
	"features": [
		{
			"type": "Feature",
			"geometry": {
				"type": "Point",
				"coordinates": [
					73.35857,
					54.99629
				]
			},
			"properties": {
				"name": "start_point"
			}
		},
		{
			"type": "Feature",
			"geometry": {
				"type": "Point",
				"coordinates": [
					82.88871,
					54.98093
				]
			},
			"properties": {
				"name": "finish_point"
			}
		},
		{
			"type": "Feature",
			"geometry": {
				"type": "MultiPolygon",
				"coordinates": [
					[
						[
							[78.36354, 53.97930],
							[78.46006, 52.86596],
							[81.67985, 52.89925],
							[81.58333, 55.05971],
							[80.07340, 54.99648],
							[78.94958, 54.54308],
							[78.36354, 53.97930]
						]
					],
					[
						[
							[77.23969, 56.09846],
							[78.13330, 54.92263],
							[79.74431, 55.64655],
							[78.83812, 56.32245],
							[77.23969, 56.09846]
						]
					],
					[
						[
							[74.84552, 54.07576],
							[76.09654, 54.34116],
							[76.63007, 55.06049],
							[76.24372, 56.02501],
							[74.97430, 56.14818],
							[74.18322, 55.71880],
							[74.13416, 54.60841],
							[74.84552, 54.07576]
						]
					]
				]
			},
			"properties": {
				"name": "restricted_polygons",
				"buffer_distance": 1000
			}
		}
	]
}
```

```python
import json

geojson_to_find_route = json.dumps({"type": "FeatureCollection","features": [{"type": "Feature","geometry": {"type": "Point","coordinates": [73.35857,54.99629]},"properties": {"name": "start_point"}},{"type": "Feature","geometry": {"type": "Point","coordinates": [82.88871,54.98093]},"properties": {"name": "finish_point"}},{"type": "Feature","geometry": {"type": "MultiPolygon","coordinates": [[[[78.36354, 53.97930],[78.46006, 52.86596],[81.67985, 52.89925],[81.58333, 55.05971],[80.07340, 54.99648],[78.94958, 54.54308],[78.36354, 53.97930]]],[[[77.23969, 56.09846],[78.13330, 54.92263],[79.74431, 55.64655],[78.83812, 56.32245],[77.23969, 56.09846]]],[[[74.84552, 54.07576],[76.09654, 54.34116],[76.63007, 55.06049],[76.24372, 56.02501],[74.97430, 56.14818],[74.18322, 55.71880],[74.13416, 54.60841],[74.84552, 54.07576]]]]},"properties": {"name": "restricted_polygons","buffer_distance": 1000}}]})
```

- Поиск оптимального маршрута с помощью GeoJSON
```python
from optimal_route import find_optimal_route_with_geojson

optimal_route = find_optimal_route_with_geojson(geojson_to_find_route)

print(optimal_route)
# '{"type":"LineString","coordinates":[["73.35857","54.99629"],["74.84030147521223","54.065034789584864"],["80.06797275842449","55.00523243286125"],["81.5985466806419","55.06924940451989"],["82.88871","54.98093"]]}'
```

- Поиск оптимального маршрута с помощью pydantic модели
```python
from optimal_route import find_optimal_route_with_pydantic_model, RouteFindDTO

data_to_find_route = RouteFindDTO.model_validate_json(geojson_to_find_route)

optimal_route = find_optimal_route_with_pydantic_model(data_to_find_route)

print(optimal_route)
# RouteSendDTO(bbox=None, type='LineString', coordinates=[Position(longitude=Decimal('73.35857'), latitude=Decimal('54.99629')), Position(longitude=Decimal('74.84030147521223'), latitude=Decimal('54.065034789584864')), Position(longitude=Decimal('80.06797275842449'), latitude=Decimal('55.00523243286125')), Position(longitude=Decimal('81.5985466806419'), latitude=Decimal('55.06924940451989')), Position(longitude=Decimal('82.88871'), latitude=Decimal('54.98093'))])
```

- Поиск оптимального маршрута с помощью геометрических объектов из библиотеки [`Shapely`](https://shapely.readthedocs.io/en/stable/index.html)
```python
from shapely.geometry import Point, MultiPolygon
from optimal_route import find_optimal_route

start_point = Point([73.35857, 54.99629])
finish_point = Point([82.88871, 54.98093])
restricted_polygons = MultiPolygon([[[[78.36354, 53.97930], [78.46006, 52.86596], [81.67985, 52.89925], [81.58333, 55.05971], [80.07340, 54.99648], [78.94958, 54.54308], [78.36354, 53.97930]]], [[[77.23969, 56.09846], [78.13330, 54.92263], [79.74431, 55.64655], [78.83812, 56.32245], [77.23969, 56.09846]]], [[[74.84552, 54.07576], [76.09654, 54.34116], [76.63007, 55.06049], [76.24372, 56.02501], [74.97430, 56.14818], [74.18322, 55.71880], [74.13416, 54.60841], [74.84552, 54.07576]]]])
buffer_distance = 1000

optimal_route = find_optimal_route(start_point, finish_point, restricted_polygons, buffer_distance)

print(optimal_route)
# <LINESTRING (73.359 54.996, 74.84 54.065, 80.068 55.005, 81.599 55.069, 82.8...>
```

## Свойства
- `name` - наименование геометрического объекта
- `buffer_distance` - расстояние в метрах, на которое будут расширены запретные зоны
