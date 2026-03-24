"""
road_network.py - Historical Road Network for ENGI
Five Gokaido highways, waystations, signposts, and checkpoints.
"""

import math
from data import (GOKAIDO, TOKAIDO_STATIONS, WAYSTATION_SERVICES,
                  SIGN_DIRECTIONS, AREA_W, AREA_H)
from world import geo_to_grid


def distance_km(lat1, lon1, lat2, lon2):
    """Haversine distance between two lat/lon points in km."""
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def compass_direction(lat1, lon1, lat2, lon2):
    """Return compass direction from point 1 to point 2."""
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    angle = math.degrees(math.atan2(dlon, dlat))
    if angle < 0:
        angle += 360
    dirs = ["north", "northeast", "east", "southeast",
            "south", "southwest", "west", "northwest"]
    idx = int((angle + 22.5) / 45) % 8
    return dirs[idx]


def ri_to_km(ri):
    return ri * 3.93


def km_to_ri(km):
    return km / 3.93


class Waystation:
    __slots__ = ('name', 'lat', 'lon', 'region_col', 'region_row',
                 'services', 'highway', 'station_number', 'desc',
                 'next_station', 'prev_station')

    def __init__(self, name, lat, lon, services, highway, station_number, desc=""):
        self.name = name
        self.lat = lat
        self.lon = lon
        self.region_col, self.region_row = geo_to_grid(lat, lon)
        self.services = services
        self.highway = highway
        self.station_number = station_number
        self.desc = desc
        self.next_station = None
        self.prev_station = None


class SignPost:
    __slots__ = ('x', 'y', 'z', 'directions', 'text')

    def __init__(self, x=0, y=0, z=0, directions=None):
        self.x = x
        self.y = y
        self.z = z
        self.directions = directions or []
        self.text = self._format_text()

    def _format_text(self):
        parts = []
        for d in self.directions:
            jp_dir = SIGN_DIRECTIONS.get(d.get("direction", ""), "")
            dist_ri = km_to_ri(d.get("distance_km", 0))
            parts.append(f"{jp_dir} {d['destination']} {dist_ri:.0f}ri")
        return " | ".join(parts)


NAKASENDO_STATIONS = [
    {"name":"Itabashi","lat":35.751,"lon":139.716,"services":["inn","teahouse"],"desc":"First Nakasendo station."},
    {"name":"Takasaki","lat":36.322,"lon":139.002,"services":["inn","market","checkpoint"],"desc":"Mountain gateway."},
    {"name":"Karuizawa","lat":36.348,"lon":138.636,"services":["inn","teahouse"],"desc":"Cool highland retreat."},
    {"name":"Shimosuwa","lat":36.075,"lon":138.084,"services":["inn","hot_spring","shrine"],"desc":"Junction with Koshu Kaido."},
    {"name":"Narai","lat":35.963,"lon":137.817,"services":["inn","teahouse"],"desc":"Kiso Valley jewel."},
    {"name":"Magome","lat":35.526,"lon":137.566,"services":["inn","teahouse"],"desc":"Steep stone-paved streets."},
    {"name":"Tsumago","lat":35.576,"lon":137.595,"services":["inn","teahouse"],"desc":"Perfectly preserved post town."},
    {"name":"Gifu","lat":35.423,"lon":136.761,"services":["inn","market","blacksmith"],"desc":"Castle town."},
    {"name":"Kusatsu","lat":35.014,"lon":135.958,"services":["inn","teahouse"],"desc":"Last station before Kyoto."},
]

KOSHU_KAIDO_STATIONS = [
    {"name":"Naito-Shinjuku","lat":35.690,"lon":139.699,"services":["inn","teahouse"],"desc":"Western Edo start."},
    {"name":"Hachioji","lat":35.666,"lon":139.316,"services":["inn","market"],"desc":"Silk trade hub."},
    {"name":"Kobotoke","lat":35.636,"lon":139.200,"services":["inn"],"desc":"Mountain pass."},
    {"name":"Uenohara","lat":35.621,"lon":139.113,"services":["inn","teahouse"],"desc":"Kai border."},
    {"name":"Kofu","lat":35.664,"lon":138.568,"services":["inn","market","blacksmith","checkpoint"],"desc":"Takeda capital."},
    {"name":"Shimosuwa-K","lat":36.075,"lon":138.084,"services":["inn","shrine"],"desc":"Terminus, joins Nakasendo."},
]

NIKKO_KAIDO_STATIONS = [
    {"name":"Senju","lat":35.748,"lon":139.802,"services":["inn","teahouse"],"desc":"Northern Edo departure."},
    {"name":"Kasukabe","lat":35.975,"lon":139.753,"services":["inn","teahouse"],"desc":"Kanto plain station."},
    {"name":"Utsunomiya-N","lat":36.555,"lon":139.883,"services":["inn","market","checkpoint"],"desc":"Castle crossroads."},
    {"name":"Imaichi","lat":36.721,"lon":139.683,"services":["inn","teahouse"],"desc":"Cedar avenue begins."},
    {"name":"Nikko","lat":36.750,"lon":139.600,"services":["inn","shrine","teahouse"],"desc":"Sacred mountain shrines."},
]

OSHU_KAIDO_STATIONS = [
    {"name":"Senju-O","lat":35.750,"lon":139.804,"services":["inn","teahouse"],"desc":"Shares with Nikko Kaido."},
    {"name":"Koga","lat":36.175,"lon":139.725,"services":["inn","teahouse"],"desc":"Shimosa border."},
    {"name":"Oyama","lat":36.315,"lon":139.801,"services":["inn","market"],"desc":"Shimotsuke trading town."},
    {"name":"Utsunomiya-O","lat":36.555,"lon":139.883,"services":["inn","market"],"desc":"Routes diverge here."},
    {"name":"Otawara","lat":36.871,"lon":140.012,"services":["inn","teahouse"],"desc":"Northern plains."},
    {"name":"Shirakawa","lat":37.131,"lon":140.211,"services":["inn","checkpoint"],"desc":"Gateway to Tohoku."},
]


class RoadNetwork:
    def __init__(self):
        self.highways = {}
        self.all_stations = {}
        self._build_highways()

    def _build_highways(self):
        highway_data = {
            "tokaido": TOKAIDO_STATIONS,
            "nakasendo": NAKASENDO_STATIONS,
            "koshu_kaido": KOSHU_KAIDO_STATIONS,
            "nikko_kaido": NIKKO_KAIDO_STATIONS,
            "oshu_kaido": OSHU_KAIDO_STATIONS,
        }
        for hw_name, stations_data in highway_data.items():
            stations = []
            for i, sd in enumerate(stations_data):
                ws = Waystation(
                    name=sd["name"], lat=sd["lat"], lon=sd["lon"],
                    services=sd.get("services", []),
                    highway=hw_name, station_number=i + 1,
                    desc=sd.get("desc", ""),
                )
                stations.append(ws)
                self.all_stations[sd["name"]] = ws
            for i, ws in enumerate(stations):
                if i > 0:
                    ws.prev_station = stations[i - 1].name
                if i < len(stations) - 1:
                    ws.next_station = stations[i + 1].name
            self.highways[hw_name] = stations

    def get_highway(self, name):
        return self.highways.get(name)

    def get_station(self, name):
        return self.all_stations.get(name)

    def get_nearest_station(self, lat, lon):
        best = None
        best_dist = float('inf')
        for ws in self.all_stations.values():
            d = distance_km(lat, lon, ws.lat, ws.lon)
            if d < best_dist:
                best_dist = d
                best = ws
        return best

    def get_stations_in_region(self, region_col, region_row):
        return [ws for ws in self.all_stations.values()
                if ws.region_col == region_col and ws.region_row == region_row]

    def place_roads_on_area_map(self, area_map, region_col, region_row):
        stations = self.get_stations_in_region(region_col, region_row)
        for ws in stations:
            cx, cy = AREA_W // 2, AREA_H // 2
            road_type = "highway" if ws.highway == "tokaido" else "secondary"
            if ws.next_station and ws.next_station in self.all_stations:
                ns = self.all_stations[ws.next_station]
                d = compass_direction(ws.lat, ws.lon, ns.lat, ns.lon)
            elif ws.prev_station and ws.prev_station in self.all_stations:
                ps = self.all_stations[ws.prev_station]
                d = compass_direction(ps.lat, ps.lon, ws.lat, ws.lon)
            else:
                d = "north"
            dx, dy = _compass_to_delta(d)
            x = 0 if dx > 0 else (AREA_W - 1 if dx < 0 else cx)
            y = 0 if dy > 0 else (AREA_H - 1 if dy < 0 else cy)
            for _ in range(max(AREA_W, AREA_H)):
                tile = area_map.get_tile(x, y)
                if tile:
                    tile.road_type = road_type
                    tile.road_dir = (dx, dy)
                x += dx
                y += dy
                if x < 0 or x >= AREA_W or y < 0 or y >= AREA_H:
                    break

    def create_signpost(self, station):
        directions = []
        if station.next_station and station.next_station in self.all_stations:
            ns = self.all_stations[station.next_station]
            d = compass_direction(station.lat, station.lon, ns.lat, ns.lon)
            dist = distance_km(station.lat, station.lon, ns.lat, ns.lon)
            directions.append({"destination": ns.name, "distance_km": dist, "direction": d})
        if station.prev_station and station.prev_station in self.all_stations:
            ps = self.all_stations[station.prev_station]
            d = compass_direction(station.lat, station.lon, ps.lat, ps.lon)
            dist = distance_km(station.lat, station.lon, ps.lat, ps.lon)
            directions.append({"destination": ps.name, "distance_km": dist, "direction": d})
        return SignPost(directions=directions)

    def get_road_between(self, station_a_name, station_b_name):
        a = self.all_stations.get(station_a_name)
        b = self.all_stations.get(station_b_name)
        if not a or not b:
            return []
        steps = max(5, int(distance_km(a.lat, a.lon, b.lat, b.lon)))
        points = []
        for i in range(steps + 1):
            t = i / steps
            lat = a.lat + (b.lat - a.lat) * t
            lon = a.lon + (b.lon - a.lon) * t
            points.append((lat, lon))
        return points


def _compass_to_delta(direction):
    deltas = {
        "north": (0, -1), "south": (0, 1),
        "east": (1, 0), "west": (-1, 0),
        "northeast": (1, -1), "northwest": (-1, -1),
        "southeast": (1, 1), "southwest": (-1, 1),
    }
    return deltas.get(direction, (0, -1))
