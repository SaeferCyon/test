"""
world.py - World generation for 縁起 ENGI
Accurate geographic representation of Japan's main islands.
"""

import math
import random
from data import *

# ─────────────────────────────────────────────────────────────
# GEOGRAPHIC CONSTANTS
# ─────────────────────────────────────────────────────────────
# Grid coordinate from lat/lon
def geo_to_grid(lat, lon):
    col = int((lon - LON_MIN) / (LON_MAX - LON_MIN) * (WORLD_W - 1))
    row = int((LAT_MAX - lat) / (LAT_MAX - LAT_MIN) * (WORLD_H - 1))
    return max(0, min(WORLD_W-1, col)), max(0, min(WORLD_H-1, row))

def grid_to_geo(col, row):
    lon = LON_MIN + col / (WORLD_W - 1) * (LON_MAX - LON_MIN)
    lat = LAT_MAX - row / (WORLD_H - 1) * (LAT_MAX - LAT_MIN)
    return lat, lon

# ─────────────────────────────────────────────────────────────
# ISLAND OUTLINES (lat, lon) - Simplified but geographically accurate
# ─────────────────────────────────────────────────────────────

# Hokkaido - northeastern main island
HOKKAIDO_OUTLINE = [
    (45.52, 141.94),  # Cape Soya (northernmost point of Japan)
    (45.42, 142.70),
    (45.00, 143.42),
    (44.37, 145.33),  # Shiretoko Peninsula east
    (43.46, 145.75),  # Cape Nosappu (easternmost)
    (43.08, 144.58),
    (42.92, 143.81),
    (42.47, 143.44),
    (42.05, 143.20),
    (41.93, 142.70),
    (41.80, 142.05),  # Cape Erimo area
    (41.63, 141.88),
    (41.49, 140.68),  # SW Oshima Peninsula south tip
    (41.52, 140.46),  # Matsumae
    (41.55, 139.97),  # SW coast
    (42.20, 139.88),  # Western coast south
    (43.00, 140.55),
    (43.90, 141.63),  # Western coast center
    (44.62, 141.88),
    (45.24, 141.80),
    (45.52, 141.94),  # Return to Cape Soya
]

# Honshu - main island (complex outline, clockwise from NE)
HONSHU_OUTLINE = [
    # NE tip
    (41.55, 140.90),  # Aomori NE
    (41.30, 141.07),
    (40.57, 141.97),  # Iwate Pacific coast
    (39.60, 141.95),
    (38.27, 141.37),  # Sendai coast
    (37.83, 141.07),
    (37.54, 141.48),  # Fukushima coast
    (36.77, 140.89),  # Ibaraki
    (36.11, 140.55),
    (35.73, 140.87),  # Cape Inubo
    (35.59, 140.51),
    (35.31, 139.87),  # Tokyo Bay entrance
    (34.92, 139.87),  # Miura Peninsula
    (34.63, 138.97),  # Izu Peninsula tip
    (34.88, 138.54),  # Izu west base
    (34.62, 137.90),  # Shizuoka coast
    (34.62, 136.85),  # Mikawa / Ise entrance
    (34.30, 136.73),
    (33.45, 135.77),  # Cape Kushimoto (Kii Peninsula south)
    (33.84, 135.09),  # Kii west
    (34.30, 135.35),  # Osaka Bay
    (34.07, 134.57),  # Naruto Strait (east Shikoku connection)
    (34.14, 134.00),
    (34.26, 132.54),  # Hiroshima area
    (34.04, 131.97),
    (33.96, 131.63),  # Shimonoseki Strait
    # Now Japan Sea coast going NE
    (34.20, 131.07),  # Yamaguchi north coast
    (34.52, 131.36),
    (34.69, 131.56),
    (35.10, 132.57),  # Shimane coast
    (35.44, 133.30),  # Tottori
    (35.50, 134.23),  # Hyogo
    (35.57, 134.87),
    (35.57, 135.72),  # Fukui
    (37.10, 136.82),  # Noto Peninsula tip
    (37.50, 137.03),  # Noto base east
    (37.88, 138.92),  # Niigata area
    (38.31, 139.44),
    (38.55, 139.78),
    (39.03, 139.83),  # Akita coast
    (39.64, 140.26),
    (40.25, 141.09),  # Aomori south
    (40.68, 141.20),
    (41.21, 141.08),
    (41.55, 140.90),  # Return NE tip
]

# Shikoku - southern island
SHIKOKU_OUTLINE = [
    (34.07, 134.57),  # NE Naruto
    (34.33, 133.98),  # Takamatsu area
    (34.20, 133.07),  # Matsuyama area
    (33.84, 132.77),  # Uwajima
    (33.43, 132.53),  # Cape Sada
    (32.90, 132.70),  # Cape Ashizuri south
    (33.35, 133.24),  # Pacific coast
    (33.45, 134.00),  # Muroto area
    (33.75, 134.60),  # Cape Muroto east
    (34.07, 134.57),  # Return
]

# Kyushu - southwestern island
KYUSHU_OUTLINE = [
    (33.90, 130.85),  # N Kyushu, Kitakyushu area
    (33.59, 131.35),  # Beppu east
    (33.24, 131.61),  # Oita east coast
    (32.67, 131.90),  # Miyazaki coast
    (31.90, 131.42),  # Miyazaki SE
    (31.05, 130.55),  # Kagoshima south
    (31.28, 130.12),  # Kagoshima west
    (31.60, 130.56),  # Kagoshima Bay
    (32.09, 130.19),  # SW coast
    (32.40, 129.95),
    (32.72, 129.87),  # Nagasaki area
    (33.20, 129.72),  # Sasebo / NW Kyushu
    (33.48, 129.80),
    (33.65, 130.22),
    (33.90, 130.85),  # Return N
]

# Smaller island groups
AWAJI_OUTLINE = [
    (34.67, 134.91), (34.41, 134.72), (34.26, 134.82),
    (34.33, 135.03), (34.57, 135.02), (34.67, 134.91),
]

SADO_OUTLINE = [
    (38.40, 138.27), (38.10, 138.50), (37.88, 138.52),
    (37.75, 138.37), (38.00, 138.13), (38.25, 138.10), (38.40, 138.27),
]

TSUSHIMA_OUTLINE = [
    (34.70, 129.34), (34.40, 129.30), (34.20, 129.28),
    (34.10, 129.40), (34.30, 129.47), (34.55, 129.45), (34.70, 129.34),
]

IKI_OUTLINE = [
    (33.80, 129.72), (33.68, 129.64), (33.62, 129.78),
    (33.72, 129.87), (33.80, 129.80), (33.80, 129.72),
]

OSHIMA_OUTLINE = [  # Oshima near Hokkaido
    (41.40, 140.00), (41.33, 139.93), (41.25, 140.03),
    (41.32, 140.12), (41.40, 140.00),
]

ALL_ISLANDS = [
    HOKKAIDO_OUTLINE,
    HONSHU_OUTLINE,
    SHIKOKU_OUTLINE,
    KYUSHU_OUTLINE,
    AWAJI_OUTLINE,
    SADO_OUTLINE,
    TSUSHIMA_OUTLINE,
    IKI_OUTLINE,
    OSHIMA_OUTLINE,
]

# ─────────────────────────────────────────────────────────────
# MOUNTAIN RIDGE DEFINITIONS (lat, lon, elevation 0-10)
# ─────────────────────────────────────────────────────────────
MOUNTAIN_CENTERS = [
    # Hida Mountains (Northern Alps) - Central Honshu
    {"lat":36.30,"lon":137.60,"radius":1.5,"elev":9.0,"name":"Northern Alps"},
    {"lat":35.90,"lon":137.70,"radius":1.2,"elev":8.5,"name":"Central Alps"},
    {"lat":35.60,"lon":138.10,"radius":1.0,"elev":8.0,"name":"Southern Alps"},
    # Mt Fuji
    {"lat":35.36,"lon":138.73,"radius":0.5,"elev":9.5,"name":"Mt Fuji"},
    # Ou Mountains (Tohoku backbone)
    {"lat":39.50,"lon":140.60,"radius":0.8,"elev":6.5,"name":"Ou Mts North"},
    {"lat":38.50,"lon":140.50,"radius":0.8,"elev":6.5,"name":"Ou Mts Central"},
    {"lat":37.50,"lon":140.30,"radius":0.8,"elev":6.0,"name":"Ou Mts South"},
    # Dewa Range
    {"lat":39.80,"lon":140.20,"radius":0.6,"elev":5.5,"name":"Dewa Range"},
    {"lat":38.80,"lon":139.80,"radius":0.6,"elev":5.0,"name":"Dewa Range S"},
    # Kitakami Mountains (Iwate coast)
    {"lat":39.70,"lon":141.50,"radius":0.7,"elev":5.0,"name":"Kitakami Mts"},
    # Kii Mountains
    {"lat":34.10,"lon":135.80,"radius":0.8,"elev":6.5,"name":"Kii Mts"},
    {"lat":33.85,"lon":136.10,"radius":0.6,"elev":6.0,"name":"Kii Mts E"},
    # Chugoku Mountains (W Honshu)
    {"lat":35.00,"lon":133.00,"radius":0.9,"elev":5.5,"name":"Chugoku Mts"},
    {"lat":34.70,"lon":131.80,"radius":0.7,"elev":5.0,"name":"Chugoku W"},
    # Shikoku Mountains
    {"lat":33.65,"lon":133.60,"radius":0.7,"elev":7.0,"name":"Shikoku Mts"},
    {"lat":33.45,"lon":133.00,"radius":0.6,"elev":6.5,"name":"Shikoku W"},
    # Kyushu Mountains
    {"lat":32.85,"lon":130.85,"radius":0.5,"elev":5.5,"name":"Kyushu Mts"},
    {"lat":32.20,"lon":131.00,"radius":0.4,"elev":5.0,"name":"Kyushu S Mts"},
    # Mt Aso (volcano, Kyushu)
    {"lat":32.88,"lon":131.10,"radius":0.3,"elev":5.5,"name":"Mt Aso"},
    # Mt Zao (Tohoku)
    {"lat":38.13,"lon":140.44,"radius":0.3,"elev":6.0,"name":"Mt Zao"},
    # Hidaka Mountains (Hokkaido)
    {"lat":42.60,"lon":142.80,"radius":1.0,"elev":7.5,"name":"Hidaka Mts"},
    # Daisetsuzan (Hokkaido center)
    {"lat":43.60,"lon":142.80,"radius":1.2,"elev":8.0,"name":"Daisetsuzan"},
    # Hokkaido NE mountains
    {"lat":44.00,"lon":144.30,"radius":0.8,"elev":6.5,"name":"Hokkaido E Mts"},
    # Noto Peninsula hills
    {"lat":37.30,"lon":136.70,"radius":0.4,"elev":3.5,"name":"Noto Hills"},
    # Izu Peninsula hills
    {"lat":34.80,"lon":138.93,"radius":0.4,"elev":4.0,"name":"Izu Hills"},
    # Hakone / Tanzawa
    {"lat":35.23,"lon":139.02,"radius":0.4,"elev":5.0,"name":"Hakone"},
]

# ─────────────────────────────────────────────────────────────
# MAJOR RIVERS (lat, lon waypoints)
# ─────────────────────────────────────────────────────────────
RIVERS = [
    # Shinano River (longest in Japan) - Niigata
    [(36.90,138.40),(37.20,138.60),(37.50,138.80),(37.80,138.93),(38.00,139.10)],
    # Tone River (Kanto) - Choshi
    [(36.30,138.90),(36.40,139.20),(36.00,139.60),(35.90,140.10),(35.75,140.85)],
    # Mogami River (Tohoku) - Sakata
    [(38.55,140.40),(38.70,139.70),(38.80,139.50),(38.92,139.62)],
    # Kitakami River (Iwate)
    [(40.10,141.30),(39.50,141.10),(39.00,141.00),(38.50,141.10)],
    # Yodo River (Osaka) - Lake Biwa connection
    [(35.05,135.98),(34.87,135.85),(34.70,135.70),(34.69,135.50)],
    # Kiso River (central)
    [(36.20,137.70),(35.90,137.50),(35.50,137.00),(35.30,136.70),(35.08,136.81)],
    # Tenryu River (Shizuoka)
    [(35.50,138.10),(35.10,137.80),(34.85,137.80),(34.72,137.82)],
    # Abe River (Shizuoka)
    [(35.40,138.30),(35.10,138.40),(34.99,138.40)],
    # Chikugo River (Kyushu)
    [(33.30,130.75),(33.15,130.55),(33.08,130.45),(33.00,130.40)],
    # Agano River (Niigata)
    [(37.40,139.40),(37.60,139.10),(37.80,139.05)],
    # Abukuma River (Fukushima/Miyagi)
    [(37.40,140.60),(37.80,140.80),(38.10,140.90)],
    # Ishikari River (Hokkaido - longest in Hokkaido)
    [(43.40,141.00),(43.20,141.40),(43.00,141.70),(42.90,141.90),(43.05,141.93)],
    # Tokachi River (Hokkaido)
    [(43.00,143.50),(42.85,143.70),(42.70,143.90),(42.60,143.91)],
]

# ─────────────────────────────────────────────────────────────
# POINT-IN-POLYGON (Ray casting)
# ─────────────────────────────────────────────────────────────
def point_in_polygon(lat, lon, polygon):
    """Ray casting algorithm to test if (lat, lon) is inside polygon."""
    n = len(polygon)
    inside = False
    j = n - 1
    for i in range(n):
        yi, xi = polygon[i]
        yj, xj = polygon[j]
        if ((yi > lat) != (yj > lat)) and (lon < (xj - xi) * (lat - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside

def is_land(lat, lon):
    """Check if geographic coordinate is land (any island)."""
    for island in ALL_ISLANDS:
        if point_in_polygon(lat, lon, island):
            return True
    return False

# ─────────────────────────────────────────────────────────────
# ELEVATION MODEL
# ─────────────────────────────────────────────────────────────
def get_elevation(lat, lon):
    """Get elevation value (0-10) at a coordinate based on mountain centers."""
    max_elev = 0.0
    for mc in MOUNTAIN_CENTERS:
        d = math.sqrt((lat - mc["lat"])**2 + (lon - mc["lon"])**2)
        if d < mc["radius"] * 2.5:
            # Gaussian-like falloff
            influence = mc["elev"] * math.exp(-(d**2) / (2 * (mc["radius"]*0.7)**2))
            max_elev = max(max_elev, influence)
    return max_elev

# ─────────────────────────────────────────────────────────────
# TILE CLASS
# ─────────────────────────────────────────────────────────────
class Tile:
    __slots__ = ('terrain','elevation','seen','lit','items','npc_id','feature')
    def __init__(self, terrain=T_DEEP_SEA, elevation=0.0):
        self.terrain   = terrain
        self.elevation = elevation
        self.seen      = False
        self.lit       = False
        self.items     = []    # list of item dicts
        self.npc_id    = None  # NPC occupying this tile
        self.feature   = None  # special feature dict

# ─────────────────────────────────────────────────────────────
# NOISE (Simple value noise for terrain variation)
# ─────────────────────────────────────────────────────────────
class ValueNoise:
    def __init__(self, seed=42):
        rng = random.Random(seed)
        self.table = [rng.random() for _ in range(512)]

    def _smooth(self, t):
        return t * t * t * (t * (t * 6 - 15) + 10)

    def _lerp(self, a, b, t):
        return a + (b - a) * t

    def get(self, x, y):
        xi = int(math.floor(x)) & 255
        yi = int(math.floor(y)) & 255
        xf = x - math.floor(x)
        yf = y - math.floor(y)
        u = self._smooth(xf)
        v = self._smooth(yf)
        a  = self.table[(xi + yi*13) % 512]
        b  = self.table[(xi+1 + yi*13) % 512]
        c  = self.table[(xi + (yi+1)*13) % 512]
        d  = self.table[(xi+1 + (yi+1)*13) % 512]
        return self._lerp(self._lerp(a, b, u), self._lerp(c, d, u), v)

    def octave(self, x, y, octaves=4, persistence=0.5):
        total = 0
        amplitude = 1.0
        frequency = 1.0
        max_val = 0
        for _ in range(octaves):
            total += self.get(x * frequency, y * frequency) * amplitude
            max_val += amplitude
            amplitude *= persistence
            frequency *= 2.0
        return total / max_val

# ─────────────────────────────────────────────────────────────
# WORLD CLASS
# ─────────────────────────────────────────────────────────────
class World:
    def __init__(self):
        self.tiles  = None          # 2D list [row][col]
        self.npcs   = {}            # id -> NPC object
        self.items  = {}            # id -> item dict (placed in world)
        self.noise  = None
        self.rng    = random.Random(12345)
        self.cities = {}            # city name -> (col, row)

    # ── Generation ─────────────────────────────────────────
    def generate(self, seed=12345):
        self.rng = random.Random(seed)
        self.noise = ValueNoise(seed)
        # Initialize all tiles as deep sea
        self.tiles = [[Tile() for _ in range(WORLD_W)] for _ in range(WORLD_H)]

        # Pass 1: Determine land/sea based on island polygons
        land_mask = [[False]*WORLD_W for _ in range(WORLD_H)]
        for row in range(WORLD_H):
            for col in range(WORLD_W):
                lat, lon = grid_to_geo(col, row)
                land_mask[row][col] = is_land(lat, lon)

        # Pass 2: Assign base terrain
        for row in range(WORLD_H):
            for col in range(WORLD_W):
                tile = self.tiles[row][col]
                lat, lon = grid_to_geo(col, row)

                if not land_mask[row][col]:
                    # Check how close to land for depth
                    min_land_dist = self._min_land_distance(col, row, land_mask, 8)
                    if min_land_dist == 0:
                        tile.terrain = T_COAST
                    elif min_land_dist <= 2:
                        tile.terrain = T_SEA
                    else:
                        tile.terrain = T_DEEP_SEA
                    continue

                # Land cell
                elev = get_elevation(lat, lon)
                n = self.noise.octave(col * 0.08, row * 0.08, octaves=5)
                tile.elevation = elev

                # Determine if coastal
                is_coastal = self._is_coastal(col, row, land_mask)

                if elev >= 8.5:
                    tile.terrain = T_HIGH_PEAK
                elif elev >= 6.5:
                    tile.terrain = T_MOUNTAIN
                elif elev >= 4.0:
                    tile.terrain = T_MOUNTAIN if n > 0.55 else T_DENSE_FOREST
                elif elev >= 2.5:
                    tile.terrain = T_FOREST if n > 0.4 else T_DENSE_FOREST
                elif is_coastal:
                    tile.terrain = T_BEACH
                else:
                    # Low elevation variety
                    if n > 0.70:
                        tile.terrain = T_PLAINS
                    elif n > 0.45:
                        tile.terrain = T_FARMLAND
                    elif n > 0.30:
                        tile.terrain = T_RICE_PADDY
                    elif n > 0.15:
                        tile.terrain = T_FOREST
                    else:
                        tile.terrain = T_PLAINS

                # Regional bamboo (warmer southern areas)
                if lat < 35.5 and tile.terrain == T_FOREST and n > 0.65:
                    tile.terrain = T_BAMBOO

                # Swamps in certain low coastal areas
                if is_coastal and tile.terrain in (T_PLAINS, T_RICE_PADDY) and n < 0.2:
                    tile.terrain = T_SWAMP

                # Pine forest near coast
                if is_coastal and tile.terrain == T_FOREST:
                    tile.terrain = T_PINE

        # Pass 3: Carve rivers
        self._place_rivers()

        # Pass 4: Place cities
        self._place_cities()

        # Pass 5: Place roads between cities
        self._build_roads()

        # Pass 6: Place hot springs (volcanic areas)
        self._place_hot_springs()

        # Pass 7: Place ruins & temples
        self._place_ruins_and_temples()

        # Pass 8: Scatter loot
        self._scatter_items()

        # Pass 9: Populate NPCs
        self._populate_npcs()


    def _min_land_distance(self, col, row, land_mask, max_r):
        """Find minimum distance to nearest land cell."""
        for r in range(1, max_r + 1):
            for dc in range(-r, r+1):
                for dr in range(-r, r+1):
                    if abs(dc) != r and abs(dr) != r:
                        continue
                    nc, nr = col+dc, row+dr
                    if 0 <= nc < WORLD_W and 0 <= nr < WORLD_H:
                        if land_mask[nr][nc]:
                            return r - 1
        return max_r

    def _is_coastal(self, col, row, land_mask):
        """True if cell is land adjacent to water."""
        for dc in [-1,0,1]:
            for dr in [-1,0,1]:
                if dc == 0 and dr == 0:
                    continue
                nc, nr = col+dc, row+dr
                if 0 <= nc < WORLD_W and 0 <= nr < WORLD_H:
                    if not land_mask[nr][nc]:
                        return True
        return False

    def _place_rivers(self):
        """Rasterize river paths onto the grid."""
        for river in RIVERS:
            for i in range(len(river)-1):
                lat0, lon0 = river[i]
                lat1, lon1 = river[i+1]
                c0, r0 = geo_to_grid(lat0, lon0)
                c1, r1 = geo_to_grid(lat1, lon1)
                # Bresenham line
                points = self._bresenham(c0, r0, c1, r1)
                for c, r in points:
                    if 0 <= c < WORLD_W and 0 <= r < WORLD_H:
                        t = self.tiles[r][c]
                        if t.terrain not in (T_DEEP_SEA, T_SEA, T_COAST, T_HIGH_PEAK):
                            t.terrain = T_RIVER

    def _bresenham(self, x0, y0, x1, y1):
        """Bresenham line algorithm."""
        points = []
        dx = abs(x1-x0); sx = 1 if x0<x1 else -1
        dy = -abs(y1-y0); sy = 1 if y0<y1 else -1
        err = dx + dy
        while True:
            points.append((x0, y0))
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                if x0 == x1: break
                err += dy; x0 += sx
            if e2 <= dx:
                if y0 == y1: break
                err += dx; y0 += sy
        return points

    def _place_cities(self):
        """Place all historical cities."""
        for city in CITIES:
            lat, lon = city["lat"], city["lon"]
            col, row = geo_to_grid(lat, lon)
            # Find nearest walkable cell
            found = False
            for radius in range(5):
                for dc in range(-radius, radius+1):
                    for dr in range(-radius, radius+1):
                        nc, nr = col+dc, row+dr
                        if 0<=nc<WORLD_W and 0<=nr<WORLD_H:
                            t = self.tiles[nr][nc]
                            if TERRAIN[t.terrain]["walk"]:
                                t.terrain = city["type"]
                                t.feature = {
                                    "type":"city",
                                    "name":city["name"],
                                    "faction":city["faction"],
                                    "pop":city["pop"],
                                    "desc":city["desc"],
                                }
                                self.cities[city["name"]] = (nc, nr)
                                found = True
                                break
                    if found: break
                if found: break

            if not found:
                self.cities[city["name"]] = (col, row)

        # Scatter smaller villages
        for _ in range(200):
            col = self.rng.randint(0, WORLD_W-1)
            row = self.rng.randint(0, WORLD_H-1)
            t = self.tiles[row][col]
            if t.terrain in (T_PLAINS, T_FARMLAND, T_RICE_PADDY) and not t.feature:
                t.terrain = T_VILLAGE
                t.feature = {"type":"village","name":self._gen_village_name()}

    def _gen_village_name(self):
        prefixes = ["Kawa","Yama","Mori","Hana","Tsuki","Kaze","Hi","Taki",
                    "Sato","Nishi","Higashi","Kita","Minami","Umi","Ike",
                    "Take","Shiro","Kumo","Hoshi","Koe"]
        suffixes = ["mura","machi","sato","gawa","yama","hara","zaka",
                    "shima","no","zawa","bata","ta"]
        return self.rng.choice(prefixes) + self.rng.choice(suffixes)

    def _build_roads(self):
        """Connect major cities with roads using A* pathfinding."""
        # Define road network connections
        road_connections = [
            ("Edo","Kyoto"),("Edo","Kamakura"),("Kyoto","Osaka"),
            ("Osaka","Hiroshima"),("Hiroshima","Yamaguchi"),("Yamaguchi","Fukuoka"),
            ("Fukuoka","Kumamoto"),("Kumamoto","Kagoshima"),
            ("Edo","Sendai"),("Sendai","Aomori"),("Sendai","Yamagata"),
            ("Kyoto","Nagoya"),("Nagoya","Shizuoka"),("Shizuoka","Edo"),
            ("Nagoya","Kanazawa"),("Kanazawa","Niigata"),
            ("Osaka","Kochi"),("Hiroshima","Matsuyama"),
            ("Fukuoka","Nagasaki"),("Fukuoka","Oita"),
            ("Edo","Utsunomiya"),("Edo","Kofu"),("Nagoya","Nagano"),
        ]
        for a, b in road_connections:
            if a in self.cities and b in self.cities:
                c0, r0 = self.cities[a]
                c1, r1 = self.cities[b]
                self._draw_road(c0, r0, c1, r1)

    def _draw_road(self, c0, r0, c1, r1):
        """Draw a winding road between two points."""
        # Simple pathfinding: Bresenham with slight random deviation
        points = self._bresenham(c0, r0, c1, r1)
        for c, r in points:
            if 0<=c<WORLD_W and 0<=r<WORLD_H:
                t = self.tiles[r][c]
                if t.terrain in (T_PLAINS, T_FARMLAND, T_RICE_PADDY, T_FOREST,
                                  T_PINE, T_BAMBOO, T_BEACH):
                    t.terrain = T_ROAD

    def _place_hot_springs(self):
        """Place hot springs near volcanic areas."""
        volcanic = [
            (35.36,138.73,1.0),  # Fuji area
            (32.88,131.10,0.6),  # Aso
            (38.13,140.44,0.5),  # Zao
            (36.53,138.20,0.4),  # Kusatsu
            (35.23,139.02,0.5),  # Hakone
            (43.60,143.80,0.6),  # Hokkaido (Akan)
            (32.75,130.20,0.4),  # Unzen
        ]
        for lat, lon, radius in volcanic:
            for _ in range(int(radius * 20)):
                dlat = self.rng.uniform(-radius*0.8, radius*0.8)
                dlon = self.rng.uniform(-radius*0.8, radius*0.8)
                c, r = geo_to_grid(lat+dlat, lon+dlon)
                if 0<=c<WORLD_W and 0<=r<WORLD_H:
                    t = self.tiles[r][c]
                    if t.terrain in (T_MOUNTAIN, T_FOREST, T_PLAINS) and not t.feature:
                        if self.rng.random() < 0.3:
                            t.terrain = T_ONSEN
                            t.feature = {"type":"onsen","name":"Hot Spring"}

    def _place_ruins_and_temples(self):
        """Scatter temples and ruins across the map."""
        # Famous temple complexes
        temple_sites = [
            (34.21,135.58,"Koyasan"),
            (35.40,135.73,"Enryakuji"),
            (35.00,135.78,"Kinkakuji"),
            (34.69,135.83,"Todaiji"),
            (34.48,136.72,"Ise Jingu"),
            (36.76,139.60,"Nikko"),
            (36.66,138.19,"Zenkoji"),
            (35.38,139.62,"Tsurugaoka"),
            (34.21,131.47,"Yamaguchi Temple"),
            (33.56,133.53,"Chikurinji"),
        ]
        for lat, lon, name in temple_sites:
            c, r = geo_to_grid(lat, lon)
            for dc in range(-2,3):
                for dr in range(-2,3):
                    nc, nr = c+dc, r+dr
                    if 0<=nc<WORLD_W and 0<=nr<WORLD_H:
                        t = self.tiles[nr][nc]
                        if t.terrain not in (T_DEEP_SEA,T_SEA,T_COAST) and not t.feature:
                            t.terrain = T_TEMPLE
                            t.feature = {"type":"temple","name":name}
                            break

        # Random small temples
        for _ in range(80):
            c = self.rng.randint(0, WORLD_W-1)
            r = self.rng.randint(0, WORLD_H-1)
            t = self.tiles[r][c]
            if t.terrain in (T_MOUNTAIN,T_FOREST,T_DENSE_FOREST,T_PLAINS) and not t.feature:
                t.terrain = T_TEMPLE
                t.feature = {"type":"temple","name":self._gen_temple_name()}

        # Ruins
        for _ in range(60):
            c = self.rng.randint(0, WORLD_W-1)
            r = self.rng.randint(0, WORLD_H-1)
            t = self.tiles[r][c]
            if t.terrain in (T_FOREST,T_PLAINS,T_MOUNTAIN) and not t.feature:
                t.terrain = T_RUINS
                t.feature = {"type":"ruins","name":self._gen_ruins_name()}

    def _gen_temple_name(self):
        prefixes = ["Ryoan","Eiho","Tenryu","Kongou","Myoho","Kongo","Butsuryu",
                    "Daian","Seiyo","Honen","Jodo","Rinzai","Soto","Shingon"]
        suffixes = ["-ji","-dera","-in"]
        return self.rng.choice(prefixes) + self.rng.choice(suffixes)

    def _gen_ruins_name(self):
        r = ["Old Fort","Crumbled Keep","Abandoned Mansion","Sunken Shrine",
             "Overgrown Watchtower","Fallen Gate","Buried Temple","Collapsed Granary"]
        return self.rng.choice(r)

    def _scatter_items(self):
        """Place items on terrain based on loot tables."""
        item_id_counter = [0]
        def next_id():
            item_id_counter[0] += 1
            return f"i{item_id_counter[0]}"

        for row in range(WORLD_H):
            for col in range(WORLD_W):
                t = self.tiles[row][col]
                if not TERRAIN[t.terrain]["walk"]:
                    continue
                if t.terrain not in LOOT_TABLES:
                    continue
                if self.rng.random() > 0.06:
                    continue
                table = LOOT_TABLES[t.terrain]
                total_w = sum(w for _, w in table)
                roll = self.rng.uniform(0, total_w)
                cum = 0
                for item_name, w in table:
                    cum += w
                    if roll <= cum:
                        item = self._create_item(item_name)
                        if item:
                            iid = next_id()
                            item["id"] = iid
                            t.items.append(iid)
                            self.items[iid] = item
                        break

    def _create_item(self, name):
        if name not in ITEMS:
            return None
        defn = ITEMS[name]
        item = dict(defn)
        item["name_key"] = name
        item["stack"] = defn.get("count", 1)
        if name == "coin_pouch":
            item["money"] = self.rng.randint(5, 60)
        return item

    def _populate_npcs(self):
        """Scatter NPCs based on terrain type."""
        npc_spawn = {
            T_VILLAGE: [("farmer",40),("elder",10),("merchant",15),("hunter",10),("ronin",5)],
            T_TOWN:    [("merchant",30),("samurai",20),("innkeeper",15),("guard",10),("blacksmith",10),("pilgrim",5)],
            T_CASTLE:  [("samurai",35),("guard",30),("lord",3),("merchant",10),("blacksmith",8)],
            T_TEMPLE:  [("monk",40),("pilgrim",30),("yamabushi",20)],
            T_PORT:    [("merchant",30),("guard",15),("farmer",15),("pilgrim",10)],
            T_FOREST:  [("bandit",25),("hunter",25),("wolf",20),("pilgrim",10)],
            T_MOUNTAIN:[("yamabushi",20),("hunter",15),("wolf",10),("bear",8)],
            T_RUINS:   [("ghost",20),("bandit",20),("ronin",10)],
            T_PLAINS:  [("farmer",30),("merchant",15),("ronin",10),("bandit",5)],
            T_ROAD:    [("merchant",20),("pilgrim",15),("ronin",10),("bandit",8)],
            T_BAMBOO:  [("ninja",15),("hunter",20),("bandit",10)],
            T_DENSE_FOREST:[("bandit_chief",5),("bandit",20),("wolf",15),("bear",5)],
        }
        npc_id_counter = [0]
        def next_npc_id():
            npc_id_counter[0] += 1
            return f"n{npc_id_counter[0]}"

        from entities import NPC
        for row in range(WORLD_H):
            for col in range(WORLD_W):
                t = self.tiles[row][col]
                if t.terrain not in npc_spawn:
                    continue
                # Spawn probability varies by terrain
                base_chance = {
                    T_VILLAGE:0.10, T_TOWN:0.15, T_CASTLE:0.12, T_TEMPLE:0.08,
                    T_PORT:0.10, T_FOREST:0.03, T_MOUNTAIN:0.02, T_RUINS:0.04,
                    T_PLAINS:0.02, T_ROAD:0.04, T_BAMBOO:0.03, T_DENSE_FOREST:0.02,
                }.get(t.terrain, 0.01)

                if self.rng.random() > base_chance:
                    continue

                table = npc_spawn[t.terrain]
                total_w = sum(w for _, w in table)
                roll = self.rng.uniform(0, total_w)
                cum = 0
                npc_type = None
                for nt, w in table:
                    cum += w
                    if roll <= cum:
                        npc_type = nt
                        break
                if not npc_type or npc_type not in NPCS:
                    continue

                nid = next_npc_id()
                npc = NPC(nid, npc_type, col, row, self.rng)
                t.npc_id = nid
                self.npcs[nid] = npc

    # ── Accessors ───────────────────────────────────────────
    def get_tile(self, col, row):
        if 0 <= col < WORLD_W and 0 <= row < WORLD_H:
            return self.tiles[row][col]
        return None

    def is_walkable(self, col, row):
        t = self.get_tile(col, row)
        if not t:
            return False
        return TERRAIN[t.terrain]["walk"] and t.npc_id is None

    def is_swimmable(self, col, row):
        t = self.get_tile(col, row)
        if not t:
            return False
        return TERRAIN[t.terrain].get("swim", False)

    def move_npc(self, npc, new_col, new_row):
        old_tile = self.get_tile(npc.col, npc.row)
        new_tile = self.get_tile(new_col, new_row)
        if old_tile and old_tile.npc_id == npc.id:
            old_tile.npc_id = None
        if new_tile:
            new_tile.npc_id = npc.id
        npc.col = new_col
        npc.row = new_row

    def place_npc(self, npc):
        tile = self.get_tile(npc.col, npc.row)
        if tile:
            tile.npc_id = npc.id

    def remove_npc(self, npc):
        tile = self.get_tile(npc.col, npc.row)
        if tile and tile.npc_id == npc.id:
            tile.npc_id = None
        if npc.id in self.npcs:
            del self.npcs[npc.id]

    def get_feature_desc(self, col, row):
        t = self.get_tile(col, row)
        if not t or not t.feature:
            return None
        f = t.feature
        td = TERRAIN[t.terrain]
        if f["type"] == "city":
            return f'{f["name"]} ({f.get("faction","")}) — {f.get("desc","")}'
        elif f["type"] == "village":
            return f'Village of {f["name"]}'
        elif f["type"] == "temple":
            return f'{f["name"]} — Sacred ground.'
        elif f["type"] == "ruins":
            return f'{f["name"]} — Crumbling stone and old memories.'
        elif f["type"] == "onsen":
            return f'Hot Spring — Steam rises from the earth.'
        return td["name"]

    # ── FOV ─────────────────────────────────────────────────
    def compute_fov(self, origin_col, origin_row, radius):
        """Compute field of view using recursive shadowcasting."""
        # Clear current lit state in viewport
        r0 = max(0, origin_row - radius - 1)
        r1 = min(WORLD_H, origin_row + radius + 2)
        c0 = max(0, origin_col - radius - 1)
        c1 = min(WORLD_W, origin_col + radius + 2)
        for r in range(r0, r1):
            for c in range(c0, c1):
                self.tiles[r][c].lit = False

        # Mark origin
        t = self.get_tile(origin_col, origin_row)
        if t:
            t.lit = True
            t.seen = True

        # Cast rays
        for angle_step in range(360):
            angle = angle_step * math.pi / 180.0
            dx = math.cos(angle)
            dy = math.sin(angle)
            ox, oy = origin_col + 0.5, origin_row + 0.5
            for r in range(1, radius + 1):
                ox += dx; oy += dy
                cx, cy = int(ox), int(oy)
                if cx < 0 or cx >= WORLD_W or cy < 0 or cy >= WORLD_H:
                    break
                tile = self.tiles[cy][cx]
                tile.lit = True
                tile.seen = True
                td = TERRAIN[tile.terrain]
                if td.get("blocks_sight", False):
                    break
