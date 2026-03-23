"""
data.py - Static game data for 縁起 ENGI
All terrain types, items, NPCs, skills, dialogs, and game constants.
"""

# ─────────────────────────────────────────────────────────────
# WORLD CONSTANTS
# ─────────────────────────────────────────────────────────────
WORLD_W = 240
WORLD_H = 130
# Geographic bounds (excluding Okinawa)
LAT_MIN = 30.5
LAT_MAX = 45.5
LON_MIN = 129.0
LON_MAX = 146.0

TURNS_PER_HOUR = 10
TURNS_PER_DAY  = TURNS_PER_HOUR * 24

FOV_RADIUS     = 12   # default sight radius
COMBAT_XP_BASE = 10

# ─────────────────────────────────────────────────────────────
# TERRAIN DEFINITIONS
# (id, name_en, name_jp, char, color_pair, move_cost,
#  walkable, swimmable, blocks_sight, temp_mod, description)
# ─────────────────────────────────────────────────────────────
T_DEEP_SEA   = 0
T_SEA        = 1
T_COAST      = 2
T_BEACH      = 3
T_PLAINS     = 4
T_FARMLAND   = 5
T_FOREST     = 6
T_PINE       = 7
T_BAMBOO     = 8
T_DENSE_FOREST=9
T_MOUNTAIN   = 10
T_HIGH_PEAK  = 11
T_RIVER      = 12
T_SWAMP      = 13
T_ROAD       = 14
T_VILLAGE    = 15
T_TOWN       = 16
T_CASTLE     = 17
T_TEMPLE     = 18
T_ONSEN      = 19
T_RUINS      = 20
T_PORT       = 21
T_RICE_PADDY = 22

TERRAIN = {
    T_DEEP_SEA:   {"name":"Deep Sea",     "jp":"深海",  "ch":"≈","pair":4, "cost":99,"walk":False,"swim":True, "sight":False,"temp":0,  "desc":"Open ocean. Death by drowning awaits."},
    T_SEA:        {"name":"Sea",          "jp":"海",    "ch":"~","pair":4, "cost":5, "walk":False,"swim":True, "sight":False,"temp":0,  "desc":"Coastal waters. You could swim, barely."},
    T_COAST:      {"name":"Coastal Water","jp":"沿岸",  "ch":"~","pair":4, "cost":4, "walk":False,"swim":True, "sight":False,"temp":0,  "desc":"Shallow coastal waters."},
    T_BEACH:      {"name":"Beach",        "jp":"砂浜",  "ch":".","pair":7, "cost":1, "walk":True, "swim":False,"sight":False,"temp":2,  "desc":"Sandy shore. Warm and exposed."},
    T_PLAINS:     {"name":"Plains",       "jp":"平野",  "ch":".","pair":3, "cost":1, "walk":True, "swim":False,"sight":False,"temp":0,  "desc":"Open grassland. Good visibility."},
    T_FARMLAND:   {"name":"Farmland",     "jp":"農地",  "ch":'"',"pair":3, "cost":1, "walk":True, "swim":False,"sight":False,"temp":0,  "desc":"Tended fields and homesteads."},
    T_RICE_PADDY: {"name":"Rice Paddy",   "jp":"田んぼ","ch":'"',"pair":3, "cost":2, "walk":True, "swim":False,"sight":False,"temp":-1, "desc":"Flooded rice fields."},
    T_FOREST:     {"name":"Forest",       "jp":"森",    "ch":"T","pair":2, "cost":2, "walk":True, "swim":False,"sight":True, "temp":-1, "desc":"Broadleaf forest."},
    T_PINE:       {"name":"Pine Forest",  "jp":"松林",  "ch":"T","pair":2, "cost":2, "walk":True, "swim":False,"sight":True, "temp":-1, "desc":"Coastal pine forest."},
    T_BAMBOO:     {"name":"Bamboo Grove", "jp":"竹林",  "ch":"|","pair":2, "cost":2, "walk":True, "swim":False,"sight":True, "temp":-1, "desc":"Thick bamboo. Rustles in the wind."},
    T_DENSE_FOREST:{"name":"Dense Forest","jp":"密林",  "ch":"T","pair":2, "cost":3, "walk":True, "swim":False,"sight":True, "temp":-2, "desc":"Impenetrable dark forest."},
    T_MOUNTAIN:   {"name":"Mountain",     "jp":"山",    "ch":"^","pair":8, "cost":3, "walk":True, "swim":False,"sight":True, "temp":-3, "desc":"Steep rocky slopes."},
    T_HIGH_PEAK:  {"name":"High Peak",    "jp":"高山",  "ch":"^","pair":1, "cost":4, "walk":True, "swim":False,"sight":True, "temp":-6, "desc":"Snow-capped peak. Extreme cold."},
    T_RIVER:      {"name":"River",        "jp":"川",    "ch":"~","pair":4, "cost":3, "walk":False,"swim":True, "sight":False,"temp":-1, "desc":"Fast-moving river. Dangerous to ford."},
    T_SWAMP:      {"name":"Swamp",        "jp":"沼",    "ch":"≈","pair":5, "cost":3, "walk":True, "swim":False,"sight":False,"temp":-1, "desc":"Boggy wetland. Disease risk."},
    T_ROAD:       {"name":"Road",         "jp":"道",    "ch":"·","pair":7, "cost":1, "walk":True, "swim":False,"sight":False,"temp":0,  "desc":"Packed earth road."},
    T_VILLAGE:    {"name":"Village",      "jp":"村",    "ch":"Δ","pair":7, "cost":1, "walk":True, "swim":False,"sight":False,"temp":1,  "desc":"A farming village."},
    T_TOWN:       {"name":"Town",         "jp":"町",    "ch":"#","pair":7, "cost":1, "walk":True, "swim":False,"sight":False,"temp":2,  "desc":"A busy market town."},
    T_CASTLE:     {"name":"Castle Town",  "jp":"城下町","ch":"♦","pair":6, "cost":1, "walk":True, "swim":False,"sight":False,"temp":2,  "desc":"A castle town. Warriors everywhere."},
    T_TEMPLE:     {"name":"Temple",       "jp":"寺社",  "ch":"☆","pair":6, "cost":1, "walk":True, "swim":False,"sight":False,"temp":1,  "desc":"A sacred place of worship."},
    T_ONSEN:      {"name":"Hot Spring",   "jp":"温泉",  "ch":"♨","pair":9, "cost":1, "walk":True, "swim":False,"sight":False,"temp":8,  "desc":"Volcanic hot spring. Restores body."},
    T_RUINS:      {"name":"Ruins",        "jp":"廃墟",  "ch":"%","pair":8, "cost":2, "walk":True, "swim":False,"sight":True, "temp":-1, "desc":"Ancient crumbled structures."},
    T_PORT:       {"name":"Port Town",    "jp":"港町",  "ch":"⚓","pair":7, "cost":1, "walk":True, "swim":False,"sight":False,"temp":1,  "desc":"A harbor settlement."},
}

# ─────────────────────────────────────────────────────────────
# HISTORICAL CITIES & LOCATIONS (lat, lon, type, name, faction, desc)
# ─────────────────────────────────────────────────────────────
CITIES = [
    # Hokkaido
    {"name":"Matsumae",   "lat":41.43,"lon":140.11,"type":T_CASTLE,"faction":"Matsumae","pop":"small",
     "desc":"Southernmost Hokkaido castle. Gateway to Ezo (Ainu) lands."},
    {"name":"Hakodate",   "lat":41.77,"lon":140.73,"type":T_PORT,  "faction":"Matsumae","pop":"small",
     "desc":"A fishing port on the southern Hokkaido coast."},
    # Tohoku
    {"name":"Aomori",     "lat":40.82,"lon":140.74,"type":T_TOWN,  "faction":"Tsugaru","pop":"small",
     "desc":"Northern gateway. Ferry crossing to Hokkaido."},
    {"name":"Morioka",    "lat":39.70,"lon":141.15,"type":T_CASTLE,"faction":"Nanbu","pop":"medium",
     "desc":"Nanbu clan stronghold deep in northern mountains."},
    {"name":"Sendai",     "lat":38.27,"lon":140.87,"type":T_CASTLE,"faction":"Date","pop":"large",
     "desc":"The great castle city of Date Masamune, the One-Eyed Dragon."},
    {"name":"Akita",      "lat":39.72,"lon":140.10,"type":T_CASTLE,"faction":"Satake","pop":"medium",
     "desc":"Japan Sea port and northern rice granary."},
    {"name":"Yamagata",   "lat":38.24,"lon":140.35,"type":T_CASTLE,"faction":"Mogami","pop":"small",
     "desc":"Mountain castle commanding the Mogami River valley."},
    # Kanto
    {"name":"Edo",        "lat":35.68,"lon":139.69,"type":T_CASTLE,"faction":"Tokugawa","pop":"huge",
     "desc":"The great castle of the Tokugawa. City growing into the greatest in the land."},
    {"name":"Kamakura",   "lat":35.32,"lon":139.55,"type":T_RUINS, "faction":"Neutral","pop":"small",
     "desc":"Ancient seat of the Minamoto shogunate, now in decline but spiritually revered."},
    {"name":"Odawara",    "lat":35.25,"lon":139.15,"type":T_CASTLE,"faction":"Hojo","pop":"medium",
     "desc":"Great Hojo mountain castle that resisted all siege."},
    {"name":"Utsunomiya", "lat":36.55,"lon":139.88,"type":T_CASTLE,"faction":"Tokugawa","pop":"medium",
     "desc":"Kanto plain fortress guarding the northern road."},
    # Chubu
    {"name":"Niigata",    "lat":37.90,"lon":139.02,"type":T_PORT,  "faction":"Uesugi","pop":"medium",
     "desc":"Japan Sea trading port in Uesugi territory."},
    {"name":"Kanazawa",   "lat":36.57,"lon":136.63,"type":T_CASTLE,"faction":"Maeda","pop":"large",
     "desc":"Maeda clan castle town. Rivaling Kyoto in culture and wealth."},
    {"name":"Nagano",     "lat":36.65,"lon":138.18,"type":T_CASTLE,"faction":"Takeda","pop":"medium",
     "desc":"Mountain fortress. Site of Kawanakajima battles between Takeda and Uesugi."},
    {"name":"Kofu",       "lat":35.66,"lon":138.57,"type":T_CASTLE,"faction":"Takeda","pop":"medium",
     "desc":"Kai Province capital. Stronghold of Takeda Shingen, the Tiger of Kai."},
    {"name":"Shizuoka",   "lat":34.98,"lon":138.38,"type":T_CASTLE,"faction":"Imagawa","pop":"medium",
     "desc":"Imagawa heartland. Warm climate, tea cultivation, and Tokaido Road."},
    {"name":"Nagoya",     "lat":35.18,"lon":136.91,"type":T_CASTLE,"faction":"Oda","pop":"large",
     "desc":"Oda clan seat. Birthplace of Nobunaga, the Demon King of the Sixth Heaven."},
    # Kinki
    {"name":"Kyoto",      "lat":35.01,"lon":135.77,"type":T_CASTLE,"faction":"Imperial","pop":"huge",
     "desc":"Imperial capital. Emperor resides here. Center of culture and politics."},
    {"name":"Osaka",      "lat":34.69,"lon":135.50,"type":T_CASTLE,"faction":"Toyotomi","pop":"huge",
     "desc":"Toyotomi castle city. Greatest fortress in Japan."},
    {"name":"Nara",       "lat":34.69,"lon":135.83,"type":T_TEMPLE,"faction":"Imperial","pop":"medium",
     "desc":"Ancient capital with the great Buddha and sacred deer."},
    {"name":"Kobe",       "lat":34.69,"lon":135.20,"type":T_PORT,  "faction":"Imperial","pop":"medium",
     "desc":"Hyogo port. Foreign trading vessels dock here."},
    {"name":"Sakai",      "lat":34.57,"lon":135.46,"type":T_TOWN,  "faction":"Neutral","pop":"large",
     "desc":"Free merchant city. Cannons, Portuguese goods, and proud independence."},
    # Chugoku
    {"name":"Hiroshima",  "lat":34.39,"lon":132.46,"type":T_CASTLE,"faction":"Mori","pop":"medium",
     "desc":"Mori clan delta castle commanding the western Inland Sea."},
    {"name":"Yamaguchi",  "lat":34.18,"lon":131.47,"type":T_CASTLE,"faction":"Mori","pop":"medium",
     "desc":"Ouchi legacy city. Western gateway controlling routes to Kyushu."},
    {"name":"Tottori",    "lat":35.50,"lon":134.24,"type":T_CASTLE,"faction":"Mori","pop":"small",
     "desc":"Sand dunes meet the sea. Mountain fortress behind the coast."},
    # Shikoku
    {"name":"Kochi",      "lat":33.56,"lon":133.53,"type":T_CASTLE,"faction":"Chosokabe","pop":"medium",
     "desc":"Chosokabe stronghold. Fierce southern warriors who nearly unified Shikoku."},
    {"name":"Matsuyama",  "lat":33.84,"lon":132.77,"type":T_CASTLE,"faction":"Kono","pop":"small",
     "desc":"Inland Sea castle. Commands the Iyo Province."},
    {"name":"Tokushima",  "lat":34.07,"lon":134.55,"type":T_CASTLE,"faction":"Miyoshi","pop":"small",
     "desc":"Gateway to Shikoku from Awaji Island."},
    # Kyushu
    {"name":"Fukuoka",    "lat":33.59,"lon":130.41,"type":T_CASTLE,"faction":"Kuroda","pop":"large",
     "desc":"Northern Kyushu gateway. Hakata merchants control vast trade networks."},
    {"name":"Nagasaki",   "lat":32.75,"lon":129.87,"type":T_PORT,  "faction":"Arima","pop":"medium",
     "desc":"Portuguese Nanban traders. Firearms, Christianity, and exotic goods."},
    {"name":"Kumamoto",   "lat":32.80,"lon":130.74,"type":T_CASTLE,"faction":"Kato","pop":"large",
     "desc":"Kato Kiyomasa's fortress. One of the great castles of western Japan."},
    {"name":"Kagoshima",  "lat":31.60,"lon":130.56,"type":T_CASTLE,"faction":"Shimazu","pop":"large",
     "desc":"Shimazu heartland. Feared warriors who repelled even the Mongol invasions."},
    {"name":"Oita",       "lat":33.24,"lon":131.61,"type":T_CASTLE,"faction":"Otomo","pop":"medium",
     "desc":"Otomo domain. Christian daimyo with Portuguese cannon and ambition."},
    {"name":"Miyazaki",   "lat":31.91,"lon":131.42,"type":T_TOWN,  "faction":"Shimazu","pop":"small",
     "desc":"Remote eastern Kyushu forests shelter ancient cedar and hidden villages."},
    # Mountains/Temples
    {"name":"Mt Fuji",    "lat":35.36,"lon":138.73,"type":T_HIGH_PEAK,"faction":"Neutral","pop":"none",
     "desc":"The sacred peak. Its perfect cone watches over all of eastern Japan."},
    {"name":"Mt Koya",    "lat":34.21,"lon":135.58,"type":T_TEMPLE,"faction":"Temple","pop":"small",
     "desc":"Koyasan — sacred Buddhist mountain monastery. Kobo Daishi rests here."},
    {"name":"Nikko",      "lat":36.76,"lon":139.60,"type":T_TEMPLE,"faction":"Temple","pop":"small",
     "desc":"Sacred mountain shrines deep in the Kanto highlands."},
    {"name":"Zenkoji",    "lat":36.66,"lon":138.19,"type":T_TEMPLE,"faction":"Temple","pop":"small",
     "desc":"The great Zenkoji temple. Pilgrims from all provinces walk here."},
]

# ─────────────────────────────────────────────────────────────
# ITEM DEFINITIONS
# ─────────────────────────────────────────────────────────────
ITEMS = {
    # WEAPONS
    "katana":       {"name":"Katana",           "char":"/","pair":1,"type":"weapon",
                     "damage":(8,14),"speed":10,"range":1,"weight":1.2,
                     "ki_cost":0,"skill":"kenjutsu","armor_pen":3,"value":80,
                     "desc":"The soul of the samurai. Razor edge, graceful curve."},
    "wakizashi":    {"name":"Wakizashi",         "char":"/","pair":1,"type":"weapon",
                     "damage":(5,9), "speed":13,"range":1,"weight":0.7,
                     "ki_cost":0,"skill":"kenjutsu","armor_pen":2,"value":40,
                     "desc":"Short companion blade. Worn with the katana."},
    "tanto":        {"name":"Tanto",             "char":"/","pair":1,"type":"weapon",
                     "damage":(3,6), "speed":15,"range":1,"weight":0.3,
                     "ki_cost":0,"skill":"kenjutsu","armor_pen":4,"value":15,
                     "desc":"Fighting knife. Easily concealed under robes."},
    "naginata":     {"name":"Naginata",          "char":"↑","pair":6,"type":"weapon",
                     "damage":(9,15),"speed":8, "range":2,"weight":2.0,
                     "ki_cost":1,"skill":"naginata","armor_pen":2,"value":70,
                     "desc":"Curved blade on a long pole. Monks and women warriors carry this."},
    "yari":         {"name":"Yari",              "char":"↑","pair":1,"type":"weapon",
                     "damage":(7,12),"speed":9, "range":2,"weight":1.8,
                     "ki_cost":0,"skill":"naginata","armor_pen":5,"value":50,
                     "desc":"Straight-bladed spear. Ashigaru foot-soldiers carry these in formation."},
    "yumi":         {"name":"Yumi",              "char":")","pair":7,"type":"weapon",
                     "damage":(6,12),"speed":7, "range":10,"weight":1.5,
                     "ki_cost":1,"skill":"kyujutsu","armor_pen":2,"value":60,
                     "ammo":"arrow","desc":"Great asymmetric bow of laminated wood and bamboo."},
    "teppo":        {"name":"Teppo",             "char":"!","pair":1,"type":"weapon",
                     "damage":(14,22),"speed":3,"range":12,"weight":3.5,
                     "ki_cost":0,"skill":"teppo","armor_pen":8,"value":200,
                     "ammo":"ball","desc":"Portuguese-style matchlock musket. Devastating but slow to reload."},
    "kanabo":       {"name":"Kanabo",            "char":"!","pair":7,"type":"weapon",
                     "damage":(10,18),"speed":7,"range":1,"weight":3.5,
                     "ki_cost":2,"skill":"jujutsu","armor_pen":6,"value":45,
                     "desc":"Iron-studded war club. Crushes armor like paper."},
    "kama":         {"name":"Kama",              "char":"(","pair":1,"type":"weapon",
                     "damage":(4,8), "speed":13,"range":1,"weight":0.8,
                     "ki_cost":0,"skill":"kenjutsu","armor_pen":1,"value":12,
                     "desc":"Farm sickle used as weapon. Cheap and common."},
    "bo_staff":     {"name":"Bo Staff",          "char":"|","pair":7,"type":"weapon",
                     "damage":(5,9), "speed":11,"range":2,"weight":1.5,
                     "ki_cost":1,"skill":"jujutsu","armor_pen":0,"value":10,
                     "desc":"Hardwood staff. Monks and travellers carry these openly."},
    "unarmed":      {"name":"Unarmed",           "char":"*","pair":1,"type":"weapon",
                     "damage":(2,4), "speed":14,"range":1,"weight":0,
                     "ki_cost":0,"skill":"jujutsu","armor_pen":0,"value":0,
                     "desc":"Bare fists. Not ideal, but always available."},
    # ARMOR
    "do_armor":     {"name":"Do (Chest Armor)",  "char":"[","pair":7,"type":"armor","slot":"body",
                     "defense":8,"speed_pen":1,"weight":8,"value":100,
                     "desc":"Lacquered lamellar armor. The mark of a warrior class."},
    "haramaki":     {"name":"Haramaki",          "char":"[","pair":7,"type":"armor","slot":"body",
                     "defense":4,"speed_pen":0,"weight":3,"value":30,
                     "desc":"Belly wrap armor. Light protection for poorer warriors."},
    "leather_vest": {"name":"Leather Vest",      "char":"[","pair":7,"type":"armor","slot":"body",
                     "defense":3,"speed_pen":0,"weight":2,"value":20,
                     "desc":"Cured leather. Common among merchants and hunters."},
    "kabuto":       {"name":"Kabuto",            "char":"]","pair":7,"type":"armor","slot":"head",
                     "defense":5,"speed_pen":0,"weight":2,"value":60,
                     "desc":"Iron war helmet. Fearsome crests identify the wearer."},
    "jingasa":      {"name":"Jingasa",           "char":"]","pair":7,"type":"armor","slot":"head",
                     "defense":2,"speed_pen":0,"weight":0.5,"value":15,
                     "desc":"Wide-brimmed iron hat. Common foot-soldier headgear."},
    "kote":         {"name":"Kote (Gauntlets)",  "char":"}","pair":7,"type":"armor","slot":"hands",
                     "defense":3,"speed_pen":0,"weight":1,"value":35,
                     "desc":"Armored gloves protecting the wrists and forearms."},
    "suneate":      {"name":"Suneate (Shin Guards)","char":"}","pair":7,"type":"armor","slot":"legs",
                     "defense":3,"speed_pen":0,"weight":1.5,"value":30,
                     "desc":"Lower-leg guards. Prevent the knee-strike disabling."},
    # FOOD & DRINK
    "onigiri":      {"name":"Onigiri",           "char":"%","pair":3,"type":"food",
                     "hunger":-30,"thirst":-3,"nutrition":3,"weight":0.2,"value":3,
                     "desc":"Rice ball shaped by hand. The most common travel food."},
    "miso_soup":    {"name":"Miso Soup",         "char":"%","pair":3,"type":"food",
                     "hunger":-20,"thirst":-25,"nutrition":2,"weight":0.5,"value":2,
                     "desc":"Fermented soybean broth. Warming and filling."},
    "dried_fish":   {"name":"Dried Fish",        "char":"%","pair":7,"type":"food",
                     "hunger":-25,"thirst":10,"nutrition":4,"weight":0.3,"value":4,
                     "desc":"Salt-preserved fish. Keeps for weeks but makes you thirsty."},
    "mushroom":     {"name":"Wild Mushroom",     "char":"%","pair":2,"type":"food",
                     "hunger":-15,"thirst":0,"nutrition":1,"weight":0.1,"value":2,
                     "poison_chance":0.15,
                     "desc":"Forest mushroom. Most are edible. Some are not. Know your fungi."},
    "vegetable":    {"name":"Vegetables",        "char":"%","pair":3,"type":"food",
                     "hunger":-18,"thirst":-5,"nutrition":2,"weight":0.3,"value":2,
                     "desc":"Seasonal field vegetables."},
    "sake":         {"name":"Sake",              "char":"!","pair":7,"type":"drink",
                     "hunger":-5,"thirst":-20,"morale":15,"weight":0.5,"value":8,
                     "effect":"drunk","desc":"Rice wine. Warms the blood and loosens the tongue."},
    "water":        {"name":"Water",             "char":"!","pair":4,"type":"drink",
                     "hunger":0,"thirst":-50,"morale":0,"weight":0.5,"value":1,
                     "desc":"Clean water. The most precious thing after a long march."},
    "spring_water": {"name":"Hot Spring Water",  "char":"!","pair":9,"type":"drink",
                     "hunger":0,"thirst":-40,"morale":5,"hp":5,"weight":0.5,"value":5,
                     "desc":"Mineral-rich onsen water. They say it heals the sick."},
    "rice":         {"name":"Raw Rice",          "char":"%","pair":7,"type":"material",
                     "weight":0.5,"value":1,"desc":"Unmilled rice. Must be cooked to eat."},
    # MEDICINE
    "bandage":      {"name":"Bandage",           "char":"+","pair":1,"type":"medicine",
                     "hp":15,"bleed_stop":True,"weight":0.2,"value":10,
                     "desc":"Clean cloth. Stops bleeding and aids wound closure."},
    "herb_poultice":{"name":"Herb Poultice",     "char":"*","pair":2,"type":"medicine",
                     "hp":8,"poison_cure":True,"weight":0.1,"value":8,
                     "desc":"Crushed medicinal herbs. Treats minor wounds and light poison."},
    "nanban_medicine":{"name":"Nanban Medicine", "char":"+","pair":6,"type":"medicine",
                     "hp":30,"bleed_stop":True,"fever_cure":True,"weight":0.2,"value":50,
                     "desc":"Portuguese medicine via Nagasaki. Far superior to local remedies."},
    "acupuncture":  {"name":"Acupuncture Kit",   "char":"+","pair":1,"type":"medicine",
                     "hp":5,"stamina":20,"pain_reduce":True,"weight":0.3,"value":25,
                     "desc":"Needles for pressure points. Skilled use restores Ki and reduces pain."},
    # TOOLS
    "flint_steel":  {"name":"Flint & Steel",     "char":"*","pair":7,"type":"tool",
                     "tool_type":"fire","weight":0.2,"value":8,
                     "desc":"Essential for starting fires in rain or cold."},
    "rope":         {"name":"Hemp Rope",         "char":"~","pair":7,"type":"tool",
                     "tool_type":"rope","weight":0.8,"value":5,
                     "desc":"Strong hemp rope. Climbing, binding, setting traps."},
    "lantern":      {"name":"Paper Lantern",     "char":"*","pair":7,"type":"tool",
                     "tool_type":"light","fov_bonus":3,"weight":0.5,"value":12,
                     "desc":"Oil lantern in a paper shade. Extends sight at night. Fragile in rain."},
    "trap":         {"name":"Snare Trap",        "char":"^","pair":7,"type":"tool",
                     "tool_type":"trap","weight":0.5,"value":8,
                     "desc":"Wire snare for catching small game."},
    "fishing_line": {"name":"Fishing Line",      "char":"~","pair":4,"type":"tool",
                     "tool_type":"fish","weight":0.2,"value":5,
                     "desc":"Silk fishing line with hook. Fish near rivers and coasts."},
    "pickaxe":      {"name":"Pickaxe",           "char":"(","pair":7,"type":"tool",
                     "tool_type":"mine","weight":2.5,"value":15,
                     "desc":"For mining ore or breaking walls."},
    # MISC
    "coin_pouch":   {"name":"Coin Pouch",        "char":"$","pair":7,"type":"money",
                     "money":0,"weight":0.1,"value":0,
                     "desc":"A leather pouch of coins (mon)."},
    "prayer_beads": {"name":"Juzu (Prayer Beads)","char":'"',"pair":6,"type":"misc",
                     "morale":8,"weight":0.1,"value":15,
                     "desc":"Buddhist prayer beads. Calming to handle in dark moments."},
    "sutra_scroll": {"name":"Buddhist Sutra",    "char":"?","pair":6,"type":"scroll",
                     "morale":12,"weight":0.2,"value":20,
                     "desc":"A sacred text. Reading aloud steadies the mind."},
    "map_scroll":   {"name":"Province Map",      "char":"?","pair":7,"type":"scroll",
                     "reveals_map":True,"weight":0.3,"value":30,
                     "desc":"Hand-drawn map of a province. Reveals terrain in the area."},
    "arrow":        {"name":"Arrow Bundle (12)", "char":"/","pair":7,"type":"ammo",
                     "ammo_type":"arrow","count":12,"weight":0.6,"value":8,
                     "desc":"War arrows fletched with hawk feather."},
    "ball":         {"name":"Teppo Ball & Powder","char":"*","pair":1,"type":"ammo",
                     "ammo_type":"ball","count":5,"weight":0.4,"value":15,
                     "desc":"Five rounds of gunpowder and lead ball."},
    "torch":        {"name":"Torch",             "char":"!","pair":7,"type":"tool",
                     "tool_type":"light","fov_bonus":4,"weight":0.3,"value":3,
                     "desc":"Resinous wood torch. Burns for 100 turns. Obvious at night."},
    "wood":         {"name":"Firewood",          "char":"/","pair":7,"type":"material",
                     "weight":1.0,"value":1,"desc":"Dry wood for fires."},
    "bamboo":       {"name":"Bamboo",            "char":"|","pair":2,"type":"material",
                     "weight":0.5,"value":1,"desc":"Cut bamboo. Strong and versatile."},
    "iron_ore":     {"name":"Iron Ore",          "char":"*","pair":1,"type":"material",
                     "weight":3.0,"value":8,"desc":"Raw iron ore for smithing."},
}

# ─────────────────────────────────────────────────────────────
# NPC DEFINITIONS
# ─────────────────────────────────────────────────────────────
NPCS = {
    "farmer": {
        "name":"Farmer","char":"@","pair":3,"faction":"peasant",
        "hp":(8,15),"atk":(1,3),"def":(0,1),"spd":8,
        "weapons":["kama","bo_staff"],"armor":[],
        "hostile":False,"morale":30,"honor":20,
        "skills":{"kenjutsu":1,"survival":4,"rhetoric":2},
        "drops":[("onigiri",0.5),("vegetable",0.4),("rice",0.3)],
        "dialog":"farmer","desc":"A weathered farmer. Tired eyes, calloused hands.",
    },
    "elder": {
        "name":"Village Elder","char":"@","pair":7,"faction":"peasant",
        "hp":(5,10),"atk":(1,2),"def":(0,0),"spd":6,
        "weapons":["bo_staff"],"armor":[],
        "hostile":False,"morale":20,"honor":60,
        "skills":{"rhetoric":7,"medicine":5,"survival":4},
        "drops":[("herb_poultice",0.4),("sutra_scroll",0.2)],
        "dialog":"elder","desc":"The village elder. Speaks with measured weight.",
    },
    "samurai": {
        "name":"Samurai","char":"@","pair":6,"faction":"tokugawa",
        "hp":(25,40),"atk":(8,14),"def":(4,7),"spd":10,
        "weapons":["katana","wakizashi"],"armor":["do_armor","kabuto"],
        "hostile":False,"morale":75,"honor":75,
        "skills":{"kenjutsu":6,"rhetoric":5,"survival":2},
        "drops":[("katana",0.3),("coin_pouch",0.6),("sake",0.4)],
        "dialog":"samurai","desc":"An armored samurai, hand resting on his hilt.",
    },
    "ronin": {
        "name":"Ronin","char":"@","pair":7,"faction":"neutral",
        "hp":(20,35),"atk":(9,14),"def":(2,5),"spd":11,
        "weapons":["katana"],"armor":["haramaki"],
        "hostile":False,"morale":55,"honor":25,
        "skills":{"kenjutsu":7,"survival":5,"rhetoric":3},
        "drops":[("katana",0.4),("sake",0.5),("bandage",0.4)],
        "dialog":"ronin","desc":"A masterless samurai. Hollow eyes, worn scabbard.",
    },
    "bandit": {
        "name":"Bandit","char":"@","pair":5,"faction":"bandit",
        "hp":(12,20),"atk":(6,10),"def":(1,3),"spd":10,
        "weapons":["tanto","kama","bo_staff"],"armor":[],
        "hostile":True,"morale":40,"honor":5,
        "skills":{"kenjutsu":3,"survival":5,"rhetoric":2},
        "drops":[("coin_pouch",0.5),("tanto",0.3),("onigiri",0.4)],
        "dialog":"bandit","desc":"A desperate brigand. Eyes darting, blade ready.",
    },
    "bandit_chief": {
        "name":"Bandit Chief","char":"@","pair":5,"faction":"bandit",
        "hp":(30,50),"atk":(11,16),"def":(3,6),"spd":10,
        "weapons":["katana"],"armor":["haramaki"],
        "hostile":True,"morale":70,"honor":15,
        "skills":{"kenjutsu":6,"rhetoric":4,"survival":5},
        "drops":[("katana",0.6),("coin_pouch",0.7),("leather_vest",0.5)],
        "dialog":"bandit_chief","desc":"Battle-scarred. Commands through fear and force.",
    },
    "monk": {
        "name":"Warrior Monk","char":"@","pair":6,"faction":"temple",
        "hp":(20,32),"atk":(7,12),"def":(3,5),"spd":9,
        "weapons":["naginata","bo_staff"],"armor":[],
        "hostile":False,"morale":70,"honor":65,
        "skills":{"naginata":5,"jujutsu":4,"rhetoric":7,"medicine":5},
        "drops":[("herb_poultice",0.5),("sutra_scroll",0.4),("bandage",0.4)],
        "dialog":"monk","desc":"Shaven head, white robes, naginata on shoulder.",
    },
    "pilgrim": {
        "name":"Pilgrim","char":"@","pair":1,"faction":"temple",
        "hp":(6,12),"atk":(1,3),"def":(0,1),"spd":8,
        "weapons":["bo_staff"],"armor":[],
        "hostile":False,"morale":50,"honor":55,
        "skills":{"rhetoric":4,"medicine":3,"survival":4},
        "drops":[("prayer_beads",0.4),("onigiri",0.5),("sutra_scroll",0.2)],
        "dialog":"pilgrim","desc":"White robes, walking staff, 88-temple beads.",
    },
    "merchant": {
        "name":"Merchant","char":"@","pair":7,"faction":"merchant",
        "hp":(8,14),"atk":(2,4),"def":(1,2),"spd":9,
        "weapons":["tanto"],"armor":[],
        "hostile":False,"morale":30,"honor":35,
        "skills":{"rhetoric":8,"survival":3,"medicine":2},
        "drops":[("coin_pouch",0.8),("sake",0.5),("dried_fish",0.4)],
        "dialog":"merchant","desc":"Pack-laden, shrewd-eyed, always counting profit.",
    },
    "guard": {
        "name":"Castle Guard","char":"@","pair":6,"faction":"tokugawa",
        "hp":(18,28),"atk":(7,11),"def":(5,8),"spd":9,
        "weapons":["yari"],"armor":["do_armor","jingasa"],
        "hostile":False,"morale":75,"honor":55,
        "skills":{"kenjutsu":4,"naginata":3,"rhetoric":3},
        "drops":[("yari",0.2),("bandage",0.5)],
        "dialog":"guard","desc":"Standing watch. Bored but alert.",
    },
    "lord": {
        "name":"Domain Lord","char":"@","pair":6,"faction":"tokugawa",
        "hp":(40,60),"atk":(13,18),"def":(8,12),"spd":9,
        "weapons":["katana"],"armor":["do_armor","kabuto","kote"],
        "hostile":False,"morale":90,"honor":90,
        "skills":{"kenjutsu":9,"rhetoric":9,"survival":4},
        "drops":[("katana",0.7),("do_armor",0.5),("coin_pouch",0.8)],
        "dialog":"lord","desc":"Sits with absolute stillness. Radiates authority.",
    },
    "hunter": {
        "name":"Hunter","char":"@","pair":2,"faction":"neutral",
        "hp":(14,22),"atk":(6,10),"def":(1,3),"spd":11,
        "weapons":["yumi","tanto"],"armor":[],
        "hostile":False,"morale":60,"honor":30,
        "skills":{"kyujutsu":6,"survival":8,"stealth":5},
        "drops":[("dried_fish",0.5),("mushroom",0.4),("arrow",0.6)],
        "dialog":"hunter","desc":"Rough-clad, sharp-eyed, quiet as the forest.",
    },
    "ninja": {
        "name":"Shinobi","char":"@","pair":8,"faction":"neutral",
        "hp":(15,25),"atk":(9,14),"def":(2,4),"spd":14,
        "weapons":["tanto","wakizashi"],"armor":[],
        "hostile":False,"morale":80,"honor":15,
        "skills":{"kenjutsu":5,"stealth":9,"medicine":5,"rhetoric":4},
        "drops":[("tanto",0.4),("bandage",0.5),("rope",0.4)],
        "dialog":"ninja","desc":"Moves without sound. Arrived when you weren't looking.",
    },
    "yamabushi": {
        "name":"Yamabushi","char":"@","pair":6,"faction":"temple",
        "hp":(18,28),"atk":(6,10),"def":(2,4),"spd":9,
        "weapons":["naginata","bo_staff"],"armor":[],
        "hostile":False,"morale":70,"honor":70,
        "skills":{"rhetoric":7,"medicine":7,"survival":8,"jujutsu":3},
        "drops":[("herb_poultice",0.6),("sutra_scroll",0.4),("spring_water",0.3)],
        "dialog":"yamabushi","desc":"Mountain ascetic. Bear-pelt hood, conch shell at belt.",
    },
    "innkeeper": {
        "name":"Innkeeper","char":"@","pair":7,"faction":"merchant",
        "hp":(12,18),"atk":(3,5),"def":(1,2),"spd":8,
        "weapons":["tanto"],"armor":[],
        "hostile":False,"morale":40,"honor":40,
        "skills":{"rhetoric":5,"medicine":2,"survival":3},
        "drops":[("sake",0.7),("onigiri",0.6),("water",0.5)],
        "dialog":"innkeeper","desc":"Round, welcoming, hands perpetually damp from work.",
    },
    "blacksmith": {
        "name":"Blacksmith","char":"@","pair":7,"faction":"merchant",
        "hp":(20,30),"atk":(5,8),"def":(2,4),"spd":8,
        "weapons":["kanabo"],"armor":[],
        "hostile":False,"morale":50,"honor":45,
        "skills":{"kenjutsu":2,"rhetoric":3,"survival":4},
        "drops":[("iron_ore",0.5),("tanto",0.4)],
        "dialog":"blacksmith","desc":"Arms thick as logs. Listens more than he speaks.",
    },
    "wolf": {
        "name":"Wolf","char":"w","pair":5,"faction":"wildlife",
        "hp":(12,20),"atk":(6,10),"def":(1,2),"spd":13,
        "weapons":[],"armor":[],"is_animal":True,
        "hostile":True,"morale":60,"honor":0,
        "skills":{},
        "drops":[("dried_fish",0.2)],
        "dialog":None,"desc":"Grey wolf, hackles raised.",
    },
    "bear": {
        "name":"Bear","char":"B","pair":5,"faction":"wildlife",
        "hp":(35,55),"atk":(13,20),"def":(4,6),"spd":9,
        "weapons":[],"armor":[],"is_animal":True,
        "hostile":True,"morale":70,"honor":0,
        "skills":{},
        "drops":[("dried_fish",0.3)],
        "dialog":None,"desc":"Enormous brown bear. Every instinct says run.",
    },
    "ghost": {
        "name":"Yurei","char":"G","pair":4,"faction":"undead",
        "hp":(10,18),"atk":(7,11),"def":(0,0),"spd":11,
        "weapons":[],"armor":[],"is_undead":True,
        "hostile":True,"morale":999,"honor":0,
        "skills":{},
        "drops":[("sutra_scroll",0.2)],
        "dialog":None,"desc":"White-shrouded spirit. Eyes like cold coals.",
    },
}

# ─────────────────────────────────────────────────────────────
# PLAYER CLASS DEFINITIONS
# ─────────────────────────────────────────────────────────────
CLASSES = {
    "ronin": {
        "name":"浪人 Ronin","hp":65,"stamina":55,
        "skills":{"kenjutsu":7,"kyujutsu":2,"jujutsu":3,"naginata":1,
                  "stealth":4,"rhetoric":3,"survival":4,"medicine":2,"teppo":0},
        "start_weapon":"katana","start_armor":None,"start_offhand":"wakizashi",
        "start_honor":20,"start_money":15,
        "start_items":["onigiri","onigiri","water","bandage","sake"],
        "desc":"Masterless samurai. Swordsman without equal, honor in tatters, free to go anywhere.",
    },
    "samurai": {
        "name":"侍 Samurai","hp":75,"stamina":60,
        "skills":{"kenjutsu":6,"kyujutsu":3,"jujutsu":2,"naginata":2,
                  "stealth":1,"rhetoric":5,"survival":2,"medicine":2,"teppo":1},
        "start_weapon":"katana","start_armor":"do_armor","start_offhand":"wakizashi",
        "start_honor":70,"start_money":30,
        "start_items":["onigiri","onigiri","water","bandage"],
        "desc":"Clan warrior bound by bushido. Respected and restricted in equal measure.",
    },
    "ninja": {
        "name":"忍者 Ninja","hp":50,"stamina":70,
        "skills":{"kenjutsu":4,"kyujutsu":3,"jujutsu":5,"naginata":1,
                  "stealth":9,"rhetoric":3,"survival":6,"medicine":4,"teppo":0},
        "start_weapon":"tanto","start_armor":None,"start_offhand":"tanto",
        "start_honor":10,"start_money":20,
        "start_items":["onigiri","bandage","rope","herb_poultice"],
        "desc":"Shadow operative. Master of stealth and assassination. Terrible in open combat.",
    },
    "monk": {
        "name":"僧 Warrior Monk","hp":65,"stamina":65,
        "skills":{"kenjutsu":2,"kyujutsu":1,"jujutsu":5,"naginata":7,
                  "stealth":2,"rhetoric":7,"survival":4,"medicine":7,"teppo":0},
        "start_weapon":"naginata","start_armor":None,"start_offhand":"bo_staff",
        "start_honor":65,"start_money":10,
        "start_items":["onigiri","water","herb_poultice","sutra_scroll","prayer_beads"],
        "desc":"Temple soldier. Skilled healer and debater. Dangerous with polearms.",
    },
    "merchant": {
        "name":"商人 Merchant","hp":45,"stamina":45,
        "skills":{"kenjutsu":1,"kyujutsu":1,"jujutsu":1,"naginata":0,
                  "stealth":3,"rhetoric":9,"survival":3,"medicine":3,"teppo":1},
        "start_weapon":"tanto","start_armor":None,"start_offhand":None,
        "start_honor":35,"start_money":80,
        "start_items":["onigiri","onigiri","onigiri","water","sake","nanban_medicine"],
        "desc":"Traveling trader. Master of rhetoric and negotiation. Weak in combat.",
    },
    "hunter": {
        "name":"狩人 Hunter","hp":55,"stamina":60,
        "skills":{"kenjutsu":2,"kyujutsu":8,"jujutsu":2,"naginata":1,
                  "stealth":7,"rhetoric":2,"survival":9,"medicine":4,"teppo":2},
        "start_weapon":"yumi","start_armor":"leather_vest","start_offhand":None,
        "start_honor":30,"start_money":10,
        "start_items":["onigiri","water","mushroom","dried_fish","arrow","trap","flint_steel"],
        "desc":"Forest survival expert. Master archer. Can live off the land indefinitely.",
    },
}

# ─────────────────────────────────────────────────────────────
# DEBATE SYSTEM DATA
# ─────────────────────────────────────────────────────────────
# Argument types: name, skill_req, ki_cost, base_power, counter_bonus, desc
ARGUMENT_TYPES = {
    "logical":    {"name":"Logical Argument",   "skill":"rhetoric","ki":1,"power":12,
                   "counters":["emotional"],"countered_by":["evidence"],
                   "desc":"Appeal to reason and internal consistency."},
    "emotional":  {"name":"Emotional Appeal",   "skill":"rhetoric","ki":1,"power":10,
                   "counters":["evidence"],"countered_by":["logical"],
                   "desc":"Appeal to feeling, honor, or duty."},
    "evidence":   {"name":"Present Evidence",   "skill":"rhetoric","ki":2,"power":15,
                   "counters":["logical"],"countered_by":["emotional"],
                   "desc":"Cite facts, examples, or witness accounts."},
    "authority":  {"name":"Cite Authority",     "skill":"rhetoric","ki":1,"power":8,
                   "counters":["emotional"],"countered_by":["evidence"],
                   "desc":"Appeal to clan, emperor, Buddha, or tradition."},
    "rhetoric":   {"name":"Rhetorical Flourish","skill":"rhetoric","ki":3,"power":18,
                   "counters":[],"countered_by":["evidence","logical"],
                   "desc":"Powerful oratory that overwhelms with style."},
    "intimidate": {"name":"Intimidation",       "skill":"kenjutsu","ki":0,"power":10,
                   "counters":["emotional"],"countered_by":["authority"],
                   "desc":"Threaten consequences. Requires high honor or strength."},
    "bribe":      {"name":"Bribery",            "skill":"rhetoric","ki":0,"power":0,
                   "counters":[],"countered_by":["authority"],
                   "money_cost":20,
                   "desc":"Pay your way. Costs money. Very effective on certain types."},
    "concede":    {"name":"Concede a Point",    "skill":"rhetoric","ki":0,"power":-5,
                   "counters":[],"countered_by":[],
                   "desc":"Give ground strategically. May build trust."},
}

DEBATE_TOPICS = {
    "rice_taxation":       {"name":"Rice Taxation",           "factions":["peasant","merchant"]},
    "bushido":             {"name":"The Way of the Warrior",  "factions":["samurai","ronin"]},
    "trade_policy":        {"name":"Foreign Trade",           "factions":["merchant","tokugawa"]},
    "buddhism_authority":  {"name":"Buddhist Authority",      "factions":["temple","tokugawa"]},
    "clan_loyalty":        {"name":"Clan Loyalty",            "factions":["samurai","ronin"]},
    "peasant_rights":      {"name":"Peasant Rights",          "factions":["peasant","tokugawa"]},
    "political_authority": {"name":"Legitimate Rule",         "factions":["tokugawa","imperial"]},
    "military_strategy":   {"name":"Military Strategy",       "factions":["samurai","ronin"]},
    "spiritual_practice":  {"name":"Shinto vs Buddhism",     "factions":["temple","imperial"]},
    "honor_vs_survival":   {"name":"Honor vs Survival",       "factions":["ronin","bandit"]},
}

# ─────────────────────────────────────────────────────────────
# DIALOG CONTENT
# ─────────────────────────────────────────────────────────────
DIALOGS = {
    "farmer": {
        "greeting": [
            "Ah, a traveler. Times are hard. The lord's men took most of our harvest.",
            "Please, I have nothing worth stealing. We barely survive ourselves.",
            "Water? I can spare a little. The well is just over there.",
        ],
        "topics": {
            "local_danger":    "Bandits on the northern road. Three men disappeared last month.",
            "lord":            "Lord {faction} rules here. His tax collectors are... thorough.",
            "food":            "The harvest was poor. Many families are leaving for the towns.",
            "weather":         "The rains came late this year. The rice paddies are still shallow.",
            "directions":      "The castle is two days east on the main road. Stay on the road.",
        },
        "farewell": ["Safe travels, stranger.", "May the kami watch over you.", "Don't linger on the road after dark."],
    },
    "samurai": {
        "greeting": [
            "State your name and your business in this domain.",
            "A warrior by bearing. Who do you serve?",
            "The road is watched. Where do you come from?",
        ],
        "topics": {
            "bushido":         "Duty, loyalty, rectitude — these are not ideals. They are obligations. Without them we are no better than bandits.",
            "clan":            "I serve my lord without reservation. That is all you need to know.",
            "combat":          "If you seek a duel, choose your moment. I am ready at any time.",
            "current_conflict":"The western lords stir. War may come before the harvest moon.",
            "honor":           "A samurai who questions honor has already lost it.",
        },
        "farewell": ["Be on your way.", "Travel with your hand off your hilt next time.", "May your road be straight."],
    },
    "ronin": {
        "greeting": [
            "What do you want? I'm not looking for trouble.",
            "Another wanderer. What clan? ...No clan. I see. Same as me.",
            "Don't reach for that. Just talk.",
        ],
        "topics": {
            "hire":        "My sword is for hire. If the coin is right, I'll fight anyone but my own kin.",
            "philosophy":  "Is a masterless samurai still a samurai? I ask myself every morning.",
            "clans":       "They fight over rice while good men die in their games. Disgusting.",
            "survival":    "I've slept under pine trees in snow. You learn what matters fast.",
            "advice":      "Stick to the roads. Eat before you're hungry. Sleep before you're tired.",
        },
        "farewell": ["Watch your back.", "Stay dangerous.", "Don't die stupidly."],
    },
    "monk": {
        "greeting": [
            "Peace be with you, traveler. Have you come seeking the Dharma?",
            "All things pass, including this moment of meeting. How may I serve?",
            "You look tired. Come, rest a moment. The Buddha teaches compassion.",
        ],
        "topics": {
            "buddhism":    "All suffering arises from attachment. The warrior suffers because he clings to victory.",
            "meditation":  "The mind trained to stillness can perceive the enemy's intent before his hand moves.",
            "medicine":    "I know herbs that close wounds, teas that fight fever. This knowledge is freely given.",
            "conflict":    "We fight only in defense of what is sacred. The naginata is not for conquest.",
            "impermanence":"This war, this hunger, this triumph — all will pass like clouds over the mountain.",
        },
        "farewell": ["Namu Amida Butsu.", "Go in peace — and keep your blade clean.", "May you find stillness."],
    },
    "bandit": {
        "greeting": [
            "Your money or your life. Make it fast.",
            "Drop the pack and walk away. You might survive.",
            "Don't make this harder than it needs to be.",
        ],
        "topics": {
            "mercy":    "Mercy? Who showed mercy to us when the lord burned our village?",
            "bribe":    "Now you're speaking sense. How much?",
            "reasoning":"We didn't choose this. We were farmers once. Then the war took everything.",
            "threat":   "There are twelve of us in these woods. Count your options.",
        },
        "farewell": ["Smart.", "You're lucky I'm in a good mood.", "Next time, I won't talk first."],
    },
    "bandit_chief": {
        "greeting": [
            "Well. You found our camp. Was that a mistake or a decision?",
            "I've killed samurai with better gear than you. Speak quickly.",
            "My men are watching. Choose your words as carefully as your steps.",
        ],
        "topics": {
            "negotiation": "I'm a practical man. What are you proposing?",
            "join":        "You want to ride with us? Prove yourself first.",
            "challenge":   "One on one? That's either bravery or stupidity. I respect both.",
            "information": "Information costs. What do you offer?",
        },
        "farewell": ["This conversation is over.", "Escort them out. Alive.", "Don't come back without an offering."],
    },
    "elder": {
        "greeting": [
            "Sit, sit. The world moves fast enough without rushing conversation.",
            "You have the look of someone carrying more than a pack. Tell me.",
            "Come. I'll have tea brought. You look like you need it.",
        ],
        "topics": {
            "history":     "This village has stood three hundred years. Lords come and go. The rice still grows.",
            "youth":       "The young men leave for the wars. Who will tend the fields when we are gone?",
            "wisdom":      "The bamboo bends in the storm but does not break. Remember this.",
            "spirits":     "The kami watch this land. Do not disturb the shrine by the ancient oak.",
            "directions":  "I was young when I walked that road. Let me think... yes, go east at the river fork.",
        },
        "farewell": ["Come back when the road wearies you.", "The door is always open.", "May the kami light your way."],
    },
    "merchant": {
        "greeting": [
            "Good day! Fine goods from Nagasaki to Edo. What do you need?",
            "A customer! Come, I have weapons, medicine, food — name your need.",
            "Greetings, traveler. I have coin for goods as well as goods for coin.",
        ],
        "topics": {
            "trade":    "I carry Portuguese firearms from Nagasaki, silk from China, spices from the south seas.",
            "prices":   "Rice is up. Salt is stable. Iron is climbing — war will do that.",
            "news":     "Word from Edo: the shogun is levying new troops. Something big is moving.",
            "roads":    "The eastern road is faster. The western road is safer. Choose.",
        },
        "farewell": ["Come back when you have more coin!", "Safe travels, good for business!", "A pleasure."],
    },
    "guard": {
        "greeting": [
            "Halt. State your purpose in the castle district.",
            "No weapons drawn in the castle grounds. Understood?",
            "Papers? No? Then state your name and business clearly.",
        ],
        "topics": {
            "entry":     "Citizens may pass freely. Armed strangers need authorization from the castellan.",
            "lord":      "I serve my lord with absolute loyalty. Do not speak against him here.",
            "danger":    "Keep your sword sheathed within these walls or I'll find a permanent place for it.",
            "help":      "The steward's office is past the main gate. He handles civilian matters.",
        },
        "farewell": ["Move along.", "Keep your hands visible.", "Good day."],
    },
    "innkeeper": {
        "greeting": [
            "Welcome! A room? Dinner? The sake is from Fushimi, fresh.",
            "Come in, come in! You look like you've been on the road for days.",
            "Travelers welcome! Best prices between here and the capital.",
        ],
        "topics": {
            "lodging":  "A mon per night. Two with dinner. The futon is clean, I swear it.",
            "food":     "Tonight: miso, rice, grilled mackerel, pickles. Simple and honest.",
            "gossip":   "A group of armed men came through yesterday. Wouldn't give names. Paid well.",
            "news":     "Word is the castle lord is raising levies. War comes again.",
            "bath":     "The bath is heated at dusk. Shared, but hot.",
        },
        "farewell": ["Come back any time!", "Safe roads to you.", "Thank you for your custom."],
    },
    "hunter": {
        "greeting": [
            "Quiet — you'll scare the deer. What do you want?",
            "Another city person in the forest. Watch where you step.",
            "I heard you coming from fifty paces. You move like a horse.",
        ],
        "topics": {
            "game":       "Deer follow the river at dusk. Bears den on the north slopes — avoid those caves.",
            "survival":   "Pine bark tea keeps you warm. The red berries north of here will kill you.",
            "paths":      "There's a hunter's trail through the mountain. Faster, but no shelter.",
            "dangers":    "A wolf pack has been bold lately. Don't travel alone after dark in these hills.",
        },
        "farewell": ["Watch the ground. That's where the danger is.", "Stay downwind.", "Go on, then."],
    },
    "lord": {
        "greeting": [
            "You stand before me uninvited. This had better be worth my time.",
            "Speak. My patience is not infinite and my schedule is not empty.",
            "A petitioner? Or something more interesting?",
        ],
        "topics": {
            "fealty":    "Serve my clan faithfully and you will be rewarded. Betray us and you will be used as an example.",
            "strategy":  "The northern pass is the key to this province. Control that, control everything.",
            "taxation":  "Peasants complain about taxes as if armies march on poetry.",
            "emperor":   "The Emperor sits behind silk curtains in Kyoto. We hold the real power.",
            "challenge": "You dare challenge me here? ..I admire the nerve. Choose your seconds.",
        },
        "farewell": ["We are done here.", "Show yourself out.", "Remember this meeting."],
    },
    "pilgrim": {
        "greeting": [
            "Namu Amida Butsu... ah, forgive me, I was in prayer. Greetings.",
            "Fellow traveler on the road of life. Where are you bound?",
            "A kind face. The Buddha sends you at a good moment.",
        ],
        "topics": {
            "route":     "I walk the 88 temples of Shikoku. Forty-three down, forty-five to go.",
            "sacred":    "The shrine at the summit grants wishes to the pure of heart. Or so they say.",
            "advice":    "Release anger. It weighs the soul like a stone in a river.",
            "afterlife": "The next world holds no wars, no taxes, no hunger. I look forward to it.",
        },
        "farewell": ["Namu Amida Butsu.", "May your path be clear.", "Travel with the kami."],
    },
    "yamabushi": {
        "greeting": [
            "The mountain kami greet you. Few walk this high path.",
            "You survived the climb. The mountain tests all things.",
            "I saw your fire from a league away. Sit with me.",
        ],
        "topics": {
            "shugendo":  "We walk through fire and ice to purify the self. The mountain is the training ground of the soul.",
            "spirits":   "The kami are everywhere — in the waterfall, in the old cedar, in the wind itself.",
            "healing":   "I know remedies the city physicians don't. The mountain teaches if you listen.",
            "prophecy":  "I have dreamed of fire on the eastern hills. Change comes. Whether good or ill, I cannot say.",
        },
        "farewell": ["The mountain watches you now.", "Go carefully.", "Return when you are ready to learn."],
    },
    "blacksmith": {
        "greeting": [
            "What d'you need? I'm busy.",
            "Weapon work? Armor? Speak up.",
            "I don't do fancy work. I do good work. There's a difference.",
        ],
        "topics": {
            "craft":    "A blade is only as good as the steel and the man who holds it.",
            "repairs":  "Bring your weapon in. I can repair most damage if the steel's not cracked.",
            "trade":    "Iron is expensive right now. Blame the wars.",
            "advice":   "Keep your edge clean and dry. A rusty blade is a dead man's blade.",
        },
        "farewell": ["Right.", "Come back when it needs sharpening.", "Good."],
    },
    "ninja": {
        "greeting": [
            "You see me. That means I allowed it. Consider what that implies.",
            "...You're better than you look. Or I'm slipping.",
            "Don't reach for your weapon. I just want to talk.",
        ],
        "topics": {
            "mission":  "My business is my own. Different question.",
            "hire":     "I have no current master. Find me at the new moon with a proper offer.",
            "secrets":  "Information has a price. Coin or service — your choice.",
            "skills":   "I can move unseen through a castle, remove a target, and be leagues away by dawn.",
        },
        "farewell": ["This conversation didn't happen.", "Walk away slowly.", "Don't look for me."],
    },
}

# ─────────────────────────────────────────────────────────────
# COMBAT TECHNIQUES
# ─────────────────────────────────────────────────────────────
TECHNIQUES = {
    # Basic attacks (all weapons)
    "strike":     {"name":"Strike",          "ki":0, "dmg_mod":1.0,"acc":1.0,
                   "effect":None,"skill":"kenjutsu","desc":"Basic attack. No frills."},
    "feint":      {"name":"Feint & Strike",  "ki":1, "dmg_mod":0.8,"acc":1.3,
                   "effect":"off_balance","skill":"kenjutsu",
                   "desc":"Mislead then attack. Reduces enemy's next defense."},
    "power":      {"name":"Power Strike",    "ki":2, "dmg_mod":1.5,"acc":0.8,
                   "effect":None,"skill":"kenjutsu","desc":"Commit all force to one blow."},
    "riposte":    {"name":"Riposte",         "ki":2, "dmg_mod":1.2,"acc":1.0,
                   "effect":"parry_bonus","skill":"kenjutsu",
                   "desc":"Deflect and counter simultaneously."},
    # Grapple (jujutsu)
    "throw":      {"name":"Throw",           "ki":2, "dmg_mod":1.0,"acc":0.9,
                   "effect":"knocked_down","skill":"jujutsu",
                   "desc":"Use the enemy's weight against them."},
    "joint_lock": {"name":"Joint Lock",      "ki":3, "dmg_mod":0.5,"acc":0.85,
                   "effect":"immobilized","skill":"jujutsu",
                   "desc":"Lock a limb. Immobilizes if successful."},
    "choke":      {"name":"Choke Hold",      "ki":3, "dmg_mod":0.8,"acc":0.8,
                   "effect":"unconscious","skill":"jujutsu",
                   "desc":"Cut off air or blood. Risk of killing."},
    # Archery
    "aimed_shot": {"name":"Aimed Shot",      "ki":1, "dmg_mod":1.2,"acc":1.1,
                   "effect":None,"skill":"kyujutsu","desc":"Take time to aim precisely."},
    "rapid_fire": {"name":"Rapid Fire",      "ki":2, "dmg_mod":0.7,"acc":0.8,
                   "effect":"multi_shot","skill":"kyujutsu",
                   "desc":"Two arrows in quick succession. Accuracy suffers."},
    # Defensive
    "parry":      {"name":"Parry",           "ki":1, "dmg_mod":0.0,"acc":0.0,
                   "effect":"defended","skill":"kenjutsu","desc":"Focus entirely on blocking."},
    "dodge":      {"name":"Dodge",           "ki":1, "dmg_mod":0.0,"acc":0.0,
                   "effect":"evaded","skill":"stealth","desc":"Full evasion. Move out of line."},
    "flee":       {"name":"Flee",            "ki":0, "dmg_mod":0.0,"acc":0.0,
                   "effect":"fled","skill":"survival","desc":"Attempt to break away and run."},
}

STANCES = {
    "balanced":   {"name":"Balanced",   "atk_mod":1.0,"def_mod":1.0,"spd_mod":1.0,
                   "desc":"No penalties or bonuses. Adaptable."},
    "aggressive": {"name":"Aggressive", "atk_mod":1.3,"def_mod":0.7,"spd_mod":1.1,
                   "desc":"Press the attack. Risky."},
    "defensive":  {"name":"Defensive",  "atk_mod":0.7,"def_mod":1.4,"spd_mod":0.9,
                   "desc":"Hold firm. Hard to kill, hard to win."},
    "mobile":     {"name":"Mobile",     "atk_mod":0.9,"def_mod":0.9,"spd_mod":1.3,
                   "desc":"Keep moving. Good for archers, bad for grappling."},
}

# ─────────────────────────────────────────────────────────────
# SKILL DEFINITIONS
# ─────────────────────────────────────────────────────────────
SKILLS = {
    "kenjutsu":  {"name":"Kenjutsu (Swordsmanship)","desc":"Skill with swords and bladed weapons. Affects attack, defense, and technique access."},
    "kyujutsu":  {"name":"Kyujutsu (Archery)",      "desc":"Accuracy and power with bows. Affects ranged attack range and damage."},
    "jujutsu":   {"name":"Jujutsu (Grappling)",     "desc":"Unarmed fighting and throws. Effective against armored foes."},
    "naginata":  {"name":"Naginata",                "desc":"Pole weapon mastery. Range advantage and powerful sweeping attacks."},
    "stealth":   {"name":"Stealth",                 "desc":"Moving unseen and unheard. Affects ambush, escape, and pickpocketing."},
    "rhetoric":  {"name":"Rhetoric (Dialectic)",    "desc":"Persuasion, argument, and debate. Core skill for the debate system."},
    "survival":  {"name":"Survival",                "desc":"Living off the land. Foraging, fire-making, shelter, weather prediction."},
    "medicine":  {"name":"Medicine",                "desc":"Treating wounds, disease, and poison. Affects healing item effectiveness."},
    "teppo":     {"name":"Teppo (Firearms)",        "desc":"Matchlock musket handling. Rare but devastating at range."},
}

SKILL_MAX = 10
SKILL_XP_CURVE = [0, 100, 250, 500, 900, 1500, 2400, 3700, 5500, 8000, 12000]

# ─────────────────────────────────────────────────────────────
# CONDITIONS / STATUS EFFECTS
# ─────────────────────────────────────────────────────────────
CONDITIONS = {
    "bleeding":   {"name":"Bleeding",    "color":5,"per_turn_hp":-2,"desc":"Losing blood. Apply bandage."},
    "poisoned":   {"name":"Poisoned",    "color":2,"per_turn_hp":-1,"desc":"Venom spreading. Use herb poultice."},
    "fever":      {"name":"Fever",       "color":9,"stat_pen":0.8, "desc":"High fever. Stamina and accuracy suffer."},
    "hypothermia":{"name":"Hypothermia","color":4,"per_turn_hp":-1,"stat_pen":0.7,"desc":"Dangerously cold. Find fire."},
    "drunk":      {"name":"Drunk",       "color":7,"acc_pen":0.8, "desc":"Ale-clouded. Accuracy suffers, morale high."},
    "exhausted":  {"name":"Exhausted",   "color":8,"stat_pen":0.6, "desc":"Critically tired. Sleep or performance collapses."},
    "frightened": {"name":"Frightened", "color":5,"def_pen":0.8,  "desc":"Fear affecting combat. Morale low."},
    "off_balance":{"name":"Off-Balance","color":7,"def_pen":0.7,  "desc":"Stance broken. Next defense weakened."},
    "immobilized":{"name":"Immobilized","color":5,"spd_pen":0.0,  "desc":"Cannot move. Danger."},
    "inspired":   {"name":"Inspired",   "color":6,"stat_bon":1.2, "desc":"Battle spirit high. All stats boosted."},
    "sick":       {"name":"Sick",       "color":2,"per_turn_hp":-1,"stat_pen":0.75,"desc":"Disease. Rest and medicine."},
    "hungry":     {"name":"Hungry",     "color":7,"stat_pen":0.9, "desc":"Stomach empty. Performance declining."},
    "starving":   {"name":"Starving",   "color":5,"per_turn_hp":-3,"stat_pen":0.6,"desc":"Starvation. Eat now."},
    "dehydrated": {"name":"Dehydrated", "color":7,"stat_pen":0.85,"desc":"Thirst impairing function."},
    "dizzy":      {"name":"Dizzy",      "color":8,"acc_pen":0.7,  "desc":"Head wound or blood loss."},
    "well_rested":{"name":"Well Rested","color":3,"stat_bon":1.1, "desc":"Slept well. Ready for anything."},
}

# ─────────────────────────────────────────────────────────────
# WEATHER & SEASONS
# ─────────────────────────────────────────────────────────────
SEASONS = ["Spring","Summer","Autumn","Winter"]
SEASON_LENGTHS = [90, 90, 90, 90]  # turns per season

WEATHER_BY_SEASON = {
    "Spring": [("clear",40),("cloudy",25),("rain",25),("fog",10)],
    "Summer": [("clear",35),("cloudy",20),("rain",30),("storm",10),("hot",5)],
    "Autumn": [("clear",35),("cloudy",30),("rain",25),("fog",10)],
    "Winter": [("clear",30),("cloudy",25),("snow",30),("blizzard",10),("frost",5)],
}

WEATHER_EFFECTS = {
    "clear":   {"temp_mod":0, "fov_mod":0,   "move_mod":0,"desc":"Clear skies."},
    "cloudy":  {"temp_mod":-1,"fov_mod":-1,  "move_mod":0,"desc":"Overcast."},
    "rain":    {"temp_mod":-2,"fov_mod":-2,  "move_mod":1,"desc":"Rain. Visibility down, cold."},
    "fog":     {"temp_mod":-1,"fov_mod":-4,  "move_mod":0,"desc":"Heavy fog. Near-blind."},
    "storm":   {"temp_mod":-3,"fov_mod":-3,  "move_mod":2,"desc":"Violent storm."},
    "hot":     {"temp_mod":5, "fov_mod":0,   "move_mod":1,"desc":"Sweltering heat. Fatigue faster."},
    "snow":    {"temp_mod":-5,"fov_mod":-2,  "move_mod":2,"desc":"Snowfall. Cold. Slow."},
    "blizzard":{"temp_mod":-8,"fov_mod":-6,  "move_mod":3,"desc":"Blizzard. Dangerous."},
    "frost":   {"temp_mod":-4,"fov_mod":0,   "move_mod":1,"desc":"Hard frost. Exposed skin at risk."},
}

# ─────────────────────────────────────────────────────────────
# FACTION DEFINITIONS
# ─────────────────────────────────────────────────────────────
FACTIONS = {
    "tokugawa":{"name":"Tokugawa Clan",   "color":4,"desc":"The rising eastern lords. Order and iron rule."},
    "imperial": {"name":"Imperial Court", "color":6,"desc":"The Emperor's court. Ancient authority, little power."},
    "temple":   {"name":"Temple Orders",  "color":6,"desc":"Buddhist temples and Shinto shrines."},
    "merchant": {"name":"Merchant Guild", "color":7,"desc":"Trade networks spanning the entire country."},
    "peasant":  {"name":"Peasantry",      "color":3,"desc":"The foundation of Japan. Ignored until they rebel."},
    "bandit":   {"name":"Bandits",        "color":5,"desc":"Outcasts, desperate farmers, and criminals."},
    "neutral":  {"name":"Neutral",        "color":1,"desc":"Owes loyalty to none."},
    "wildlife": {"name":"Wildlife",       "color":2,"desc":"Animals of the forest and mountains."},
    "undead":   {"name":"Undead",         "color":4,"desc":"Spirits of the unburied dead."},
    "date":     {"name":"Date Clan",      "color":4,"desc":"Northern lords. Masamune rules with an iron eye."},
    "mori":     {"name":"Mori Clan",      "color":2,"desc":"Western lords. Masters of the Inland Sea."},
    "shimazu":  {"name":"Shimazu Clan",   "color":5,"desc":"Southern lords. Feared warriors of Kyushu."},
}

# ─────────────────────────────────────────────────────────────
# LOOT TABLES (terrain -> item list with weights)
# ─────────────────────────────────────────────────────────────
LOOT_TABLES = {
    T_VILLAGE:  [("onigiri",30),("vegetable",25),("water",20),("rice",20),("tanto",3),("rope",5)],
    T_TOWN:     [("onigiri",20),("sake",15),("water",15),("bandage",10),("tanto",5),("coin_pouch",15),("dried_fish",10),("map_scroll",3)],
    T_CASTLE:   [("katana",5),("do_armor",3),("kabuto",3),("coin_pouch",20),("bandage",10),("sake",10),("arrow",10)],
    T_TEMPLE:   [("prayer_beads",20),("sutra_scroll",20),("herb_poultice",25),("bandage",15),("spring_water",10),("incense",10)],
    T_PORT:     [("dried_fish",25),("rope",20),("water",15),("sake",15),("coin_pouch",15),("nanban_medicine",3)],
    T_RUINS:    [("map_scroll",10),("coin_pouch",15),("sutra_scroll",10),("herb_poultice",15),("bandage",10),("tanto",8)],
    T_FOREST:   [("mushroom",30),("wood",25),("herb_poultice",15),("bamboo",20),("trap",5)],
    T_BAMBOO:   [("bamboo",40),("mushroom",20),("herb_poultice",15),("trap",10)],
    T_MOUNTAIN: [("iron_ore",20),("mushroom",20),("wood",20),("herb_poultice",10),("spring_water",5)],
    T_ONSEN:    [("spring_water",50),("herb_poultice",25),("bandage",15),("acupuncture",5)],
    T_FARMLAND: [("rice",35),("vegetable",30),("onigiri",20),("rope",10)],
    T_RICE_PADDY:[("rice",50),("vegetable",20),("onigiri",15),("water",10)],
    T_SWAMP:    [("herb_poultice",25),("mushroom",20),("bamboo",20),("rope",10)],
    T_PLAINS:   [("mushroom",20),("vegetable",15),("wood",20),("herb_poultice",10)],
}
