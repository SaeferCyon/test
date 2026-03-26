"""
entities.py - Player, NPC, and Item entities for 縁起 ENGI
"""

import random
import math
from data import *
from social_data import NPC_DEFAULT_RANK, RANK_FARMER, RANK_RONIN, PLAYER_CLASS_RANK



# ─────────────────────────────────────────────────────────────
# ITEM INSTANCE
# ─────────────────────────────────────────────────────────────
def create_item(name, rng=None):
    """Create an item instance from a name key."""
    if name not in ITEMS:
        return None
    rng = rng or random
    defn = ITEMS[name]
    item = dict(defn)
    item["name_key"] = name
    item["stack"] = defn.get("count", 1)
    item["durability"] = defn.get("durability", 100)
    if name == "coin_pouch":
        item["money"] = rng.randint(5, 50)
    return item


# ─────────────────────────────────────────────────────────────
# PLAYER
# ─────────────────────────────────────────────────────────────
class Player:
    def __init__(self):
        self.col = 0
        self.row = 0
        self.z = 0
        self.name = "Nameless"
        self.cls = "ronin"

        # Core stats
        self.hp = 65
        self.max_hp = 65
        self.stamina = 55  # Ki / stamina for techniques
        self.max_stamina = 55

        # Survival stats (0=fine, 100=crisis)
        self.hunger = 0  # 0=full, 100=starving
        self.thirst = 0  # 0=hydrated, 100=dying
        self.fatigue = 0  # 0=rested, 100=collapse
        self.warmth = 50  # 0=freezing, 100=burning

        # Social stats
        self.morale = 80  # 0=broken, 100=inspired
        self.honor = 30  # affects some dialog options
        self.money = 10  # mon coins

        # Skills (1-10)
        self.skills = {k: 1 for k in SKILLS}

        # Skill experience
        self.skill_xp = {k: 0 for k in SKILLS}

        # Conditions (name -> turns_remaining, -1=permanent until cured)
        self.conditions = {}

        # Equipment slots
        self.equipment = {
            "weapon": None,
            "offhand": None,
            "body": None,
            "head": None,
            "hands": None,
            "legs": None,
        }

        # Inventory (list of item dicts)
        self.inventory = []
        self.max_carry_weight = 25.0  # kg

        # Combat state
        self.stance = "balanced"
        self.in_combat = False

        # Faction reputation (-100 to 100)
        self.rep = {f: 0 for f in FACTIONS}
        self.rep["neutral"] = 10

        # Known locations (col, row) -> name
        self.known_locations = {}

        # Stats tracking
        self.turns_played = 0
        self.kills = 0
        self.debates_won = 0
        self.distance_moved = 0
        self.days_survived = 1

        # Ammo tracking
        self.ammo = {"arrow": 0, "ball": 0}

        # Light source bonus (from lantern/torch)
        self.light_bonus = 0

        # Society simulation attributes
        self.traits = []  # list of trait keys
        self.body_map = None  # BodyMap instance (lazy init)
        self.age = 20  # starting age in years
        self.gender = "male"  # "male" or "female"
        self.social_rank = RANK_RONIN  # from social_data
        self.known_topics = set()  # topic keys discovered
        self.family_id = None  # char_id in life_sim family tree
        self.spouse_id = None  # NPC id of spouse
        self.children_ids = []  # NPC ids of children
        self.parent_ids = []  # NPC ids of parents
        self.discovered_traits = {}  # npc_id -> set of trait keys we've discovered about them

    def setup_class(self, cls_name, rng=None):
        """Initialize player from class definition."""
        rng = rng or random
        self.cls = cls_name
        cdef = CLASSES[cls_name]

        self.hp = self.max_hp = cdef["hp"]
        self.stamina = self.max_stamina = cdef["stamina"]
        self.honor = cdef["start_honor"]
        self.money = cdef["start_money"]
        self.skills = dict(cdef["skills"])
        self.skill_xp = {k: 0 for k in SKILLS}
        self.social_rank = PLAYER_CLASS_RANK.get(cls_name, RANK_RONIN)

        # Starting equipment
        if cdef["start_weapon"]:
            w = create_item(cdef["start_weapon"], rng)
            if w:
                self.inventory.append(w)
                self.equipment["weapon"] = w
        if cdef["start_armor"]:
            a = create_item(cdef["start_armor"], rng)
            if a:
                self.inventory.append(a)
                self.equipment["body"] = a
        if cdef["start_offhand"]:
            o = create_item(cdef["start_offhand"], rng)
            if o:
                self.inventory.append(o)
                self.equipment["offhand"] = o

        # Starting items
        for item_name in cdef["start_items"]:
            item = create_item(item_name, rng)
            if item:
                self.inventory.append(item)
                if item.get("ammo_type") == "arrow":
                    self.ammo["arrow"] += item.get("stack", 12)
                elif item.get("ammo_type") == "ball":
                    self.ammo["ball"] += item.get("stack", 5)

        self.rep["temple"] = 20 if cls_name == "monk" else 0
        self.rep["merchant"] = 20 if cls_name == "merchant" else 0

    @property
    def current_weight(self):
        return sum(i.get("weight", 0) * i.get("stack", 1) for i in self.inventory)

    @property
    def is_encumbered(self):
        return self.current_weight > self.max_carry_weight

    @property
    def defense_total(self):
        d = 0
        for slot, item in self.equipment.items():
            if item and item.get("type") == "armor":
                d += item.get("defense", 0)
        if "immobilized" in self.conditions:
            d = int(d * 0.5)
        if "off_balance" in self.conditions:
            d = int(d * 0.7)
        return d

    @property
    def attack_bonus(self):
        """Bonus from skills for current weapon."""
        w = self.equipment.get("weapon")
        if not w:
            return self.skills.get("jujutsu", 1)
        skill = w.get("skill", "kenjutsu")
        return self.skills.get(skill, 1)

    @property
    def fov_radius(self):
        r = FOV_RADIUS
        r += self.light_bonus
        if "fog" in self.conditions:
            r -= 4
        if self.has_condition("drunk"):
            r -= 1
        return max(2, r)

    def has_condition(self, name):
        return name in self.conditions

    def add_condition(self, name, turns=-1):
        """Add or refresh a condition."""
        if name in CONDITIONS:
            self.conditions[name] = turns

    def remove_condition(self, name):
        self.conditions.pop(name, None)

    def tick_conditions(self):
        """Process condition effects each turn. Returns list of messages."""
        msgs = []
        to_remove = []
        for cond_name, turns in list(self.conditions.items()):
            cdef = CONDITIONS.get(cond_name, {})
            # Apply per-turn effects
            if "per_turn_hp" in cdef:
                self.hp = max(0, self.hp + cdef["per_turn_hp"])
                if cdef["per_turn_hp"] < 0:
                    msgs.append(
                        (f"[{cond_name}] {abs(cdef['per_turn_hp'])} damage.", 5)
                    )
            # Count down
            if turns > 0:
                self.conditions[cond_name] = turns - 1
                if self.conditions[cond_name] <= 0:
                    to_remove.append(cond_name)
                    msgs.append((f"The {cond_name} condition fades.", 3))
        for c in to_remove:
            self.conditions.pop(c, None)
        return msgs

    def tick_survival(self, world_temp, terrain_type, weather, season):
        """Process survival mechanics each turn. Returns list of messages."""
        msgs = []
        td_def = CLASSES.get(self.cls, {})

        # Hunger (per 10 turns ≈ 1 hunger point)
        hunger_rate = 1
        if "exhausted" in self.conditions:
            hunger_rate = 2
        if self.turns_played % 10 == 0:
            self.hunger = min(100, self.hunger + hunger_rate)

        # Thirst (faster than hunger)
        thirst_rate = 1
        if WEATHER_EFFECTS.get(weather, {}).get("temp_mod", 0) > 3:
            thirst_rate = 2  # hot weather
        if self.turns_played % 6 == 0:
            self.thirst = min(100, self.thirst + thirst_rate)

        # Fatigue (accumulates over time, reduced by rest)
        if self.turns_played % 20 == 0:
            fatigue_gain = 1
            if terrain_type in (T_MOUNTAIN, T_HIGH_PEAK, T_DENSE_FOREST):
                fatigue_gain = 2
            self.fatigue = min(100, self.fatigue + fatigue_gain)

        # Temperature system
        base_temp = world_temp + TERRAIN[terrain_type].get("temp_mod", 0)
        base_temp += WEATHER_EFFECTS.get(weather, {}).get("temp_mod", 0)

        # Armor provides warmth
        if self.equipment.get("body"):
            base_temp += 3
        if self.equipment.get("head"):
            base_temp += 1

        # Adjust warmth toward base_temp
        if base_temp < 0:
            self.warmth = max(0, self.warmth - 1)
        elif base_temp > 10:
            self.warmth = min(100, self.warmth + 1)
        else:
            # Slowly normalize
            if self.warmth > 50:
                self.warmth -= 0 if self.warmth < 60 else 1
            else:
                self.warmth += 0 if self.warmth > 40 else 1

        # Apply hunger/thirst/temperature conditions
        if self.hunger >= 90 and "starving" not in self.conditions:
            self.add_condition("starving", -1)
            msgs.append(("You are starving. Find food immediately.", 5))
        elif self.hunger >= 60 and "hungry" not in self.conditions:
            self.add_condition("hungry", -1)
            msgs.append(("Your stomach growls painfully.", 7))
        elif self.hunger < 50:
            self.remove_condition("hungry")
            self.remove_condition("starving")

        if self.thirst >= 85 and "dehydrated" not in self.conditions:
            self.add_condition("dehydrated", -1)
            msgs.append(("Your throat is parched. Drink soon.", 5))
        elif self.thirst < 50:
            self.remove_condition("dehydrated")

        if self.warmth <= 10 and "hypothermia" not in self.conditions:
            self.add_condition("hypothermia", -1)
            msgs.append(("You are dangerously cold. Find fire or shelter.", 5))
        elif self.warmth >= 20:
            self.remove_condition("hypothermia")

        if self.fatigue >= 90 and "exhausted" not in self.conditions:
            self.add_condition("exhausted", -1)
            msgs.append(("You are exhausted. You must sleep.", 5))
        elif self.fatigue < 40:
            self.remove_condition("exhausted")
            if self.fatigue < 20 and "well_rested" not in self.conditions:
                self.add_condition("well_rested", 30)

        # Natural recovery when not in bad conditions
        if self.hp < self.max_hp and self.turns_played % 30 == 0:
            if "bleeding" not in self.conditions and "poisoned" not in self.conditions:
                self.hp = min(self.max_hp, self.hp + 1)

        # Stamina recovery
        if self.stamina < self.max_stamina and self.turns_played % 5 == 0:
            self.stamina = min(self.max_stamina, self.stamina + 2)

        return msgs

    def eat(self, item):
        """Eat a food/drink item. Returns message."""
        if item.get("type") not in ("food", "drink"):
            return "You can't eat that.", False
        if self.hunger <= 0 and item.get("type") == "food":
            return "You're not hungry.", False

        self.hunger = max(0, self.hunger + item.get("hunger", 0))
        self.thirst = max(0, self.thirst + item.get("thirst", 0))
        self.morale = min(100, self.morale + item.get("morale", 0))
        if "hp" in item:
            self.hp = min(self.max_hp, self.hp + item["hp"])

        if item.get("effect") == "drunk":
            self.add_condition("drunk", 20)

        # Poison chance for mushrooms
        if item.get("poison_chance", 0) > 0:
            if random.random() < item["poison_chance"]:
                self.add_condition("poisoned", -1)
                return (
                    f"You eat the {item['name']}... it tastes wrong. You feel sick!",
                    True,
                )

        return f"You eat the {item['name']}.", True

    def use_medicine(self, item):
        """Use a medicine item. Returns message."""
        if item.get("type") != "medicine":
            return "That's not medicine.", False
        if "hp" in item:
            self.hp = min(self.max_hp, self.hp + item["hp"])
        if item.get("bleed_stop"):
            self.remove_condition("bleeding")
        if item.get("poison_cure"):
            self.remove_condition("poisoned")
        if item.get("fever_cure"):
            self.remove_condition("fever")
        if item.get("stamina"):
            self.stamina = min(self.max_stamina, self.stamina + item["stamina"])
        if item.get("pain_reduce"):
            self.remove_condition("dizzy")
        return f"You apply the {item['name']}. ({item.get('hp', 0):+} HP)", True

    def gain_skill_xp(self, skill_name, amount):
        """Gain XP in a skill, potentially leveling it up. Returns message or None."""
        if skill_name not in self.skills:
            return None
        current_level = self.skills[skill_name]
        if current_level >= SKILL_MAX:
            return None
        self.skill_xp[skill_name] = self.skill_xp.get(skill_name, 0) + amount
        needed = SKILL_XP_CURVE[current_level]
        if self.skill_xp[skill_name] >= needed:
            self.skill_xp[skill_name] -= needed
            self.skills[skill_name] = min(SKILL_MAX, current_level + 1)
            return f"Your {SKILLS[skill_name]['name']} improves to level {self.skills[skill_name]}!"
        return None

    def rest(self, hours=1):
        """Rest to recover fatigue and HP. Returns messages."""
        msgs = []
        fatigue_recover = hours * 15
        self.fatigue = max(0, self.fatigue - fatigue_recover)
        if hours >= 6:
            self.hp = min(self.max_hp, self.hp + hours * 2)
            msgs.append(("You rest deeply. HP partially restored.", 3))
            self.remove_condition("exhausted")
            if self.fatigue < 20:
                self.add_condition("well_rested", 50)
                msgs.append(("You feel well rested.", 3))
        else:
            msgs.append(("You rest briefly.", 7))
        return msgs

    def stat_multiplier(self):
        """Overall stat multiplier from conditions."""
        mult = 1.0
        for cond_name in self.conditions:
            cdef = CONDITIONS.get(cond_name, {})
            mult *= cdef.get("stat_pen", 1.0)
            mult *= cdef.get("stat_bon", 1.0)
        if self.is_encumbered:
            mult *= 0.75
        return mult

    def get_effective_attack(self):
        """Get effective attack rating."""
        w = self.equipment.get("weapon")
        if w:
            lo, hi = w["damage"]
            base = random.randint(lo, hi)
        else:
            base = random.randint(1, 4)  # unarmed

        skill_bonus = self.attack_bonus
        stance_mod = STANCES[self.stance]["atk_mod"]
        stat_mod = self.stat_multiplier()

        acc_mod = 1.0
        for cond in self.conditions:
            cdef = CONDITIONS.get(cond, {})
            acc_mod *= cdef.get("acc_pen", 1.0)

        if "drunk" in self.conditions:
            acc_mod *= 0.8

        return int(base * (1 + skill_bonus * 0.1) * stance_mod * stat_mod), acc_mod

    def get_effective_defense(self):
        d = self.defense_total
        skill_bonus = self.skills.get("kenjutsu", 1)
        stance_mod = STANCES[self.stance]["def_mod"]
        return int((d + skill_bonus) * stance_mod * self.stat_multiplier())

    def equip(self, item):
        """Try to equip an item. Returns message."""
        if item.get("type") not in ("weapon", "armor"):
            return f"You can't equip {item['name']}."
        slot = item.get("slot", "weapon") if item["type"] == "armor" else "weapon"
        old = self.equipment.get(slot)
        self.equipment[slot] = item
        if old:
            return f"You swap {old['name']} for {item['name']}."
        return f"You equip {item['name']}."

    def unequip(self, slot):
        """Unequip from a slot. Returns message."""
        old = self.equipment.get(slot)
        if old:
            self.equipment[slot] = None
            return f"You unequip {old['name']}."
        return "Nothing equipped there."

    def drop_item(self, item, world, log):
        """Drop item at current location."""
        if item in self.inventory:
            if self.equipment.get("weapon") == item:
                self.equipment["weapon"] = None
            for slot in self.equipment:
                if self.equipment[slot] == item:
                    self.equipment[slot] = None
            self.inventory.remove(item)
            tile = world.get_tile(self.col, self.row)
            if tile:
                iid = f"d_{id(item)}"
                item["id"] = iid
                tile.items.append(iid)
                world.items[iid] = item
            return f"You drop the {item['name']}."
        return "You don't have that."

    def pick_up(self, iid, world):
        """Pick up item from ground. Returns message."""
        tile = world.get_tile(self.col, self.row)
        if not tile or iid not in tile.items:
            return "Nothing there."
        item = world.items.get(iid)
        if not item:
            return "Item not found."
        if self.current_weight + item.get("weight", 0) > self.max_carry_weight * 1.5:
            return "Too heavy to carry."
        tile.items.remove(iid)
        del world.items[iid]
        # Handle ammo stacking
        if item.get("ammo_type") == "arrow":
            self.ammo["arrow"] += item.get("stack", 12)
            return f"You pick up {item['name']} (+{item.get('stack', 12)} arrows)."
        elif item.get("ammo_type") == "ball":
            self.ammo["ball"] += item.get("stack", 5)
            return f"You pick up {item['name']} (+{item.get('stack', 5)} balls)."
        elif item.get("type") == "money":
            self.money += item.get("money", 0)
            return f"You pick up {item['name']} (+{item.get('money', 0)} mon)."
        self.inventory.append(item)
        return f"You pick up the {item['name']}."

    def morale_check(self):
        """Check morale vs break threshold. Returns True if holding."""
        return self.morale > 20 or random.random() < self.morale / 100.0

    def sleep(self, turns):
        """Sleep for a number of turns. Returns messages."""
        hours = turns / TURNS_PER_HOUR
        msgs = self.rest(hours)
        self.morale = min(100, self.morale + int(hours * 3))
        if "fever" in self.conditions and random.random() < 0.3:
            self.remove_condition("fever")
            msgs.append(("Your fever breaks during the night.", 3))
        self.turns_played += turns
        self.days_survived = self.turns_played // TURNS_PER_DAY + 1
        return msgs

    def apply_honor_change(self, delta, reason=""):
        old = self.honor
        self.honor = max(0, min(100, self.honor + delta))
        return delta

    def summary(self):
        """Return brief summary string."""
        cdef = CLASSES[self.cls]
        return (
            f"{self.name} ({cdef['name']}) "
            f"HP:{self.hp}/{self.max_hp} Ki:{self.stamina}/{self.max_stamina} "
            f"Honor:{self.honor} Money:{self.money}mon"
        )


# ─────────────────────────────────────────────────────────────
# NPC
# ─────────────────────────────────────────────────────────────
class NPC:
    def __init__(self, npc_id, npc_type, col, row, rng=None):
        self.id = npc_id
        self.type = npc_type
        self.col = col
        self.row = row
        rng = rng or random

        defn = NPCS.get(npc_type, NPCS["farmer"])

        self.name = defn["name"]
        self.char = defn["char"]
        self.pair = defn["pair"]
        self.faction = defn["faction"]
        self.is_animal = defn.get("is_animal", False)
        self.is_undead = defn.get("is_undead", False)

        # Randomize stats in range
        hp_lo, hp_hi = defn["hp"]
        self.max_hp = rng.randint(hp_lo, hp_hi)
        self.hp = self.max_hp

        atk_lo, atk_hi = defn["atk"]
        self.base_atk = rng.randint(atk_lo, atk_hi)

        def_lo, def_hi = defn["def"]
        self.base_def = rng.randint(def_lo, def_hi)

        self.spd = defn["spd"]  # actions per 10 turns
        self.hostile = defn["hostile"]
        self.morale = defn["morale"]
        self.honor = defn["honor"]
        self.skills = dict(defn["skills"])
        self.drops = defn["drops"]
        self.drop_ch = defn.get("drop_chance", 0.3)
        self.dialog_type = defn.get("dialog")

        # Equip starting weapons/armor
        self.weapon = None
        self.armor = 0
        for w_name in defn.get("weapons", []):
            if rng.random() < 0.7:
                self.weapon = create_item(w_name, rng)
                break
        for a_name in defn.get("armor", []):
            item = create_item(a_name, rng)
            if item:
                self.armor += item.get("defense", 0)

        # Conditions
        self.conditions = {}

        # AI state
        self.ai_state = "idle"  # idle, patrol, chase, flee, guard
        self.target_col = col
        self.target_row = row
        self.home_col = col
        self.home_row = row
        self.alert = False
        self.seen_player = False
        self.attitude = 1 if not defn["hostile"] else -1
        self.last_dir = (0, 0)
        self.move_timer = rng.randint(0, 3)

        # Unique name suffix
        if not self.is_animal and rng.random() < 0.3:
            surnames = [
                "Tanaka",
                "Yamamoto",
                "Nakamura",
                "Kobayashi",
                "Ito",
                "Kato",
                "Suzuki",
                "Watanabe",
                "Sasaki",
                "Hayashi",
                "Yamada",
                "Inoue",
                "Matsumoto",
                "Fujiwara",
                "Okawauchi",
            ]
            self.name = defn["name"] + " " + rng.choice(surnames)

        self.alive = True
        self.talked = False

        # Society simulation attributes
        self.traits = []  # list of trait keys
        self.body_map = None  # BodyMap instance (lazy init)
        self.age = rng.randint(18, 55)
        self.gender = rng.choice(["male", "female"])
        self.social_rank = NPC_DEFAULT_RANK.get(npc_type, RANK_FARMER)
        self.known_topics = set()  # topics this NPC knows about
        self.family_id = None
        self.spouse_id = None
        self.children_ids = []
        self.parent_ids = []
        self.travel_destination = None  # for dynamic encounters - where NPC is heading
        self.home_location = None  # where NPC considers home

    @property
    def is_hostile(self):
        return self.hostile or self.ai_state == "chase"

    def get_attack(self):
        """Return random attack value."""
        if self.weapon:
            lo, hi = self.weapon["damage"]
            return random.randint(lo, hi) + self.base_atk // 3
        return self.base_atk

    def get_defense(self):
        return self.base_def + self.armor

    def take_damage(self, amount):
        """Apply damage. Returns True if dead."""
        self.hp = max(0, self.hp - amount)
        # Morale check on heavy hit
        if amount > self.max_hp * 0.25:
            self.morale = max(0, self.morale - 15)
        return self.hp <= 0

    def morale_check(self):
        """True if NPC holds their nerve."""
        if self.hp < self.max_hp * 0.3:
            if random.random() > self.morale / 100.0:
                return False  # Flee
        return True

    def generate_drops(self, rng=None):
        """Generate drops when killed. Returns list of item names."""
        rng = rng or random
        result = []
        for item_name, chance in self.drops:
            if rng.random() < chance:
                result.append(item_name)
        return result

    def ai_tick(self, world, player_col, player_row):
        """Execute one AI tick. Returns list of (action, data) tuples."""
        if not self.alive:
            return []

        self.move_timer -= 1
        if self.move_timer > 0:
            return []
        self.move_timer = max(1, 10 - int(self.spd))

        actions = []
        dist = math.sqrt((self.col - player_col) ** 2 + (self.row - player_row) ** 2)

        # Detect player
        if dist <= 8 and not self.seen_player:
            if self.hostile:
                self.seen_player = True
                self.ai_state = "chase"
                actions.append(("alert", f"{self.name} spots you!"))
            elif random.random() < 0.05:
                self.seen_player = True
                actions.append(("notice", f"{self.name} glances in your direction."))

        # State machine
        if self.ai_state == "idle":
            # Random wander near home
            if random.random() < 0.3:
                dx = random.randint(-1, 1)
                dy = random.randint(-1, 1)
                nc, nr = self.col + dx, self.row + dy
                if world.is_walkable(nc, nr):
                    world.move_npc(self, nc, nr)
                    actions.append(("move", (nc, nr)))

        elif self.ai_state == "chase":
            if dist <= 1.5:
                # Attack
                actions.append(("attack", self))
            else:
                # Move toward player
                dc = (
                    0
                    if player_col == self.col
                    else (1 if player_col > self.col else -1)
                )
                dr = (
                    0
                    if player_row == self.row
                    else (1 if player_row > self.row else -1)
                )
                nc, nr = self.col + dc, self.row + dr
                if world.is_walkable(nc, nr):
                    world.move_npc(self, nc, nr)
                    actions.append(("move", (nc, nr)))
                elif world.is_walkable(self.col + dc, self.row):
                    world.move_npc(self, self.col + dc, self.row)
                    actions.append(("move", (self.col + dc, self.row)))
                elif world.is_walkable(self.col, self.row + dr):
                    world.move_npc(self, self.col, self.row + dr)
                    actions.append(("move", (self.col, self.row + dr)))

            # Check morale
            if not self.morale_check():
                self.ai_state = "flee"
                actions.append(("flee_start", f"{self.name} turns to flee!"))

        elif self.ai_state == "flee":
            # Move away from player
            dc = 0 if player_col == self.col else (-1 if player_col > self.col else 1)
            dr = 0 if player_row == self.row else (-1 if player_row > self.row else 1)
            nc, nr = self.col + dc, self.row + dr
            if world.is_walkable(nc, nr):
                world.move_npc(self, nc, nr)
            if dist > 15:
                self.ai_state = "idle"

        elif self.ai_state == "guard":
            # Stay in place, turn hostile if threatened
            if dist < 3 and self.hostile:
                self.ai_state = "chase"

        return actions

    def get_dialog(self):
        """Get opening dialog lines."""
        if not self.dialog_type or self.dialog_type not in DIALOGS:
            return [f"{self.name} looks at you silently."]
        d = DIALOGS[self.dialog_type]
        return d.get("greeting", ["..."])

    def get_dialog_topics(self):
        """Get available dialog topics."""
        if not self.dialog_type or self.dialog_type not in DIALOGS:
            return {}
        return DIALOGS[self.dialog_type].get("topics", {})

    def get_farewell(self):
        if not self.dialog_type or self.dialog_type not in DIALOGS:
            return "..."
        d = DIALOGS[self.dialog_type]
        farewells = d.get("farewell", ["..."])
        return random.choice(farewells)

    def get_debate_stance(self):
        """Get this NPC's debate topic and stance."""
        npc_debate_topics = {
            "farmer": ("rice_taxation", "peasant"),
            "elder": ("rice_taxation", "tradition"),
            "samurai": ("bushido", "honor_above_all"),
            "lord": ("political_authority", "might_makes_right"),
            "monk": ("buddhism_authority", "buddhism"),
            "merchant": ("trade_policy", "free_trade"),
            "ronin": ("clan_loyalty", "freedom"),
            "bandit": ("peasant_rights", "rebel"),
            "bandit_chief": ("honor_vs_survival", "survival"),
            "pilgrim": ("spiritual_practice", "buddhism"),
            "yamabushi": ("spiritual_practice", "shinto"),
            "guard": ("political_authority", "law_and_order"),
            "captain": ("military_strategy", "order_above_all"),
            "hunter": ("honor_vs_survival", "pragmatism"),
            "innkeeper": ("trade_policy", "neutral"),
            "blacksmith": ("trade_policy", "neutral"),
        }
        return npc_debate_topics.get(self.type, ("clan_loyalty", "neutral"))
