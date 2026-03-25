"""
mechanics.py - Combat, Debate, and Survival mechanics for 縁起 ENGI
"""

import random
import math
from data import *

# ─────────────────────────────────────────────────────────────
# COMBAT SYSTEM
# ─────────────────────────────────────────────────────────────


class CombatManager:
    """Handles all combat resolution."""

    def __init__(self):
        self.log = []  # recent combat messages
        self.active = False
        self.enemy = None
        self.round = 0

    # ── Entry/Exit ─────────────────────────────────────────
    def start_combat(self, player, enemy):
        self.active = True
        self.enemy = enemy
        self.round = 0
        self.log = []
        enemy.ai_state = "chase"

        msgs = []
        msgs.append(f"⚔  COMBAT — {enemy.name}")
        msgs.append(
            f"HP: {enemy.hp}/{enemy.max_hp} | Your HP: {player.hp}/{player.max_hp}"
        )
        if enemy.is_animal:
            msgs.append("It lunges at you!")
        elif enemy.is_undead:
            msgs.append("Cold dread grips you. A spirit attacks!")
        elif enemy.hostile:
            msgs.append(f"{enemy.name} draws their weapon!")
        else:
            msgs.append(f"{enemy.name} turns hostile!")
        return msgs

    def end_combat(self, reason=""):
        self.active = False
        self.enemy = None
        return reason

    # ── Resolution ─────────────────────────────────────────
    def player_attack(self, player, technique_name, world):
        """Resolve player's attack action. Returns list of messages."""
        if not self.active or not self.enemy:
            return ["No enemy to attack."]

        msgs = []
        self.round += 1
        tech = TECHNIQUES.get(technique_name, TECHNIQUES["strike"])

        # Check Ki cost
        ki_cost = tech["ki"]
        if player.stamina < ki_cost:
            msgs.append("Not enough Ki for that technique!")
            tech = TECHNIQUES["strike"]
            ki_cost = 0

        player.stamina = max(0, player.stamina - ki_cost)

        # Special: flee
        if technique_name == "flee":
            return self._resolve_flee(player)

        # Special: parry / dodge
        if technique_name in ("parry", "dodge"):
            return self._resolve_defense(player, technique_name)

        # Hit check
        skill = tech["skill"]
        skill_val = player.skills.get(skill, 1)
        hit_chance = 0.5 + skill_val * 0.04 + tech["acc"] * 0.1
        # Accuracy penalties
        acc_pen = 1.0
        for cond in player.conditions:
            cdef = CONDITIONS.get(cond, {})
            acc_pen *= cdef.get("acc_pen", 1.0)
        hit_chance *= acc_pen

        if random.random() > hit_chance:
            msgs.append(f"Your {tech['name']} misses!")
            # Enemy counter-attacks
            msgs.extend(self._enemy_attack(player))
            return msgs

        # Damage
        atk, _ = player.get_effective_attack()
        damage = int(atk * tech["dmg_mod"])
        damage = max(1, damage)

        # Enemy defense
        en_def = self.enemy.get_defense()
        damage = max(1, damage - en_def // 2)

        # Critical hit?
        is_crit = random.random() < 0.05 + skill_val * 0.01
        if is_crit:
            damage = int(damage * 1.75)
            msgs.append(f"CRITICAL HIT! {tech['name']} strikes true!")
        else:
            msgs.append(f"Your {tech['name']} hits {self.enemy.name}!")

        msgs.append(
            f"  → {damage} damage. ({self.enemy.hp}-{damage}/{self.enemy.max_hp} HP)"
        )

        # Apply special effects
        effect = tech.get("effect")
        if effect == "off_balance" and random.random() < 0.5:
            self.enemy.conditions["off_balance"] = 2
            msgs.append(f"  {self.enemy.name} is off-balance!")
        elif effect == "knocked_down" and random.random() < 0.4:
            self.enemy.conditions["immobilized"] = 2
            msgs.append(f"  {self.enemy.name} is knocked down!")
        elif effect == "immobilized" and random.random() < 0.3:
            self.enemy.conditions["immobilized"] = 3
            msgs.append(f"  {self.enemy.name}'s limb is locked!")

        # Apply damage
        dead = self.enemy.take_damage(damage)

        # Skill XP
        xp_msg = player.gain_skill_xp(skill, 10 + self.round)
        if xp_msg:
            msgs.append(xp_msg)

        if dead:
            msgs.extend(self._enemy_killed(player, world))
            return msgs

        # Morale check for enemy
        if not self.enemy.morale_check():
            msgs.append(f"{self.enemy.name} loses nerve and tries to flee!")
            self.enemy.ai_state = "flee"
            msgs.extend(self._end_combat_player_win(player))
            return msgs

        # Enemy counter-attacks (unless immobilized)
        if "immobilized" not in self.enemy.conditions:
            msgs.extend(self._enemy_attack(player))
        else:
            msgs.append(f"{self.enemy.name} struggles to recover.")
            self.enemy.conditions["immobilized"] = max(
                0, self.enemy.conditions.get("immobilized", 0) - 1
            )
            if self.enemy.conditions["immobilized"] <= 0:
                del self.enemy.conditions["immobilized"]

        return msgs

    def _enemy_attack(self, player):
        """Resolve enemy's attack. Returns messages."""
        msgs = []
        if not self.enemy or not self.enemy.alive:
            return msgs

        enemy = self.enemy
        # Hit check based on enemy speed vs player defense
        hit_chance = 0.45 + enemy.spd * 0.02
        if player.stance == "defensive":
            hit_chance -= 0.15
        if player.stance == "aggressive":
            hit_chance += 0.1
        if "off_balance" in player.conditions:
            hit_chance += 0.2
        if "dodged" in player.conditions:
            hit_chance -= 0.4
            del player.conditions["dodged"]

        if random.random() > hit_chance:
            msgs.append(f"  {enemy.name}'s attack misses you.")
            return msgs

        # Damage
        raw_dmg = enemy.get_attack()
        player_def = player.get_effective_defense()
        damage = max(1, raw_dmg - player_def // 2)

        # Parry absorption
        if "defended" in player.conditions:
            damage = int(damage * 0.3)
            msgs.append(
                f"  You parry {enemy.name}'s blow! ({damage} damage through guard.)"
            )
            del player.conditions["defended"]
        else:
            msgs.append(f"  {enemy.name} hits you for {damage} damage!")

        player.hp = max(0, player.hp - damage)

        # Chance of causing bleeding on heavy hit
        if damage > 8 and random.random() < 0.3:
            player.add_condition("bleeding", -1)
            msgs.append("  The wound bleeds!")

        # Chance of dizziness on very heavy hit
        if damage > player.max_hp * 0.25:
            player.add_condition("dizzy", 5)
            msgs.append("  The blow dazes you!")

        msgs.append(f"  Your HP: {player.hp}/{player.max_hp}")
        return msgs

    def _resolve_flee(self, player):
        """Attempt to flee from combat."""
        msgs = []
        flee_chance = 0.4 + player.skills.get("survival", 1) * 0.05
        if player.stance == "mobile":
            flee_chance += 0.15
        if "immobilized" in player.conditions:
            flee_chance = 0.05

        if random.random() < flee_chance:
            self.end_combat()
            msgs.append("You break away and flee!")
            player.apply_honor_change(-5, "fled combat")
            player.morale = max(0, player.morale - 10)
            player.stamina = max(0, player.stamina - 10)
            self.active = False
        else:
            msgs.append("You try to flee but can't get away!")
            msgs.extend(self._enemy_attack(player))
        return msgs

    def _resolve_defense(self, player, tech_name):
        """Set up defensive condition for next enemy attack."""
        msgs = []
        if tech_name == "parry":
            player.conditions["defended"] = 1
            msgs.append("You take a defensive stance, ready to parry.")
            skill_xp = player.gain_skill_xp("kenjutsu", 5)
            if skill_xp:
                msgs.append(skill_xp)
        elif tech_name == "dodge":
            player.conditions["dodged"] = 1
            player.stamina = max(0, player.stamina - 5)
            msgs.append("You step aside, ready to evade.")
            skill_xp = player.gain_skill_xp("stealth", 5)
            if skill_xp:
                msgs.append(skill_xp)
        # Enemy still attacks
        msgs.extend(self._enemy_attack(player))
        return msgs

    def _enemy_killed(self, player, world):
        """Handle enemy death. Returns messages."""
        msgs = []
        enemy = self.enemy
        enemy.alive = False
        enemy.hp = 0

        msgs.append(f"{enemy.name} falls defeated!")

        # Honor change
        if enemy.is_animal:
            honor = 0
        elif enemy.faction == "bandit":
            honor = 3
            msgs.append("You feel justified.")
        elif enemy.hostile:
            honor = 1
        else:
            honor = -15  # Killing non-hostile NPCs
            msgs.append("You feel a stain on your honor.")

        if honor != 0:
            player.apply_honor_change(honor)

        player.kills += 1
        player.morale = min(100, player.morale + 10)

        # Drop items
        drops = enemy.generate_drops()
        tile = world.get_tile(enemy.col, enemy.row)
        if tile:
            for item_name in drops:
                from entities import create_item

                item = create_item(item_name)
                if item:
                    iid = f"drop_{id(item)}"
                    item["id"] = iid
                    tile.items.append(iid)
                    world.items[iid] = item

            if enemy.weapon:
                iid = f"weapon_{id(enemy)}"
                enemy.weapon["id"] = iid
                tile.items.append(iid)
                world.items[iid] = enemy.weapon
                msgs.append(f"  {enemy.name} drops their {enemy.weapon['name']}.")

        if drops:
            msgs.append(f"  Items on the ground: {', '.join(drops)}")

        # Remove NPC from world
        world.remove_npc(enemy)

        # Skill XP for the kill
        if enemy.is_animal:
            xp_msg = player.gain_skill_xp("survival", 15)
        else:
            xp_msg = player.gain_skill_xp("kenjutsu", 20)
        if xp_msg:
            msgs.append(xp_msg)

        msgs.extend(self._end_combat_player_win(player))
        return msgs

    def _end_combat_player_win(self, player):
        self.active = False
        self.enemy = None
        return ["Combat ends."]


# ─────────────────────────────────────────────────────────────
# DEBATE SYSTEM
# ─────────────────────────────────────────────────────────────


class DebateManager:
    """Manages the debate/persuasion system."""

    def __init__(self):
        self.active = False
        self.target = None
        self.topic = ""
        self.momentum = 50  # 0=opponent winning, 100=player winning
        self.ap = 3  # argument points available per round
        self.round = 0
        self.topic_def = None
        self.result = None  # "won","lost","draw","fled"

    def start_debate(self, player, npc, topic=None):
        """Begin a debate with an NPC."""
        self.active = True
        self.target = npc
        self.momentum = 50
        self.ap = 3 + player.skills.get("rhetoric", 1) // 3
        self.round = 0
        self.result = None

        if topic:
            self.topic = topic
            self.topic_def = DEBATE_TOPICS.get(topic)
        else:
            npc_topic, _ = npc.get_debate_stance()
            self.topic = npc_topic
            self.topic_def = DEBATE_TOPICS.get(npc_topic)

        msgs = []
        t_name = self.topic_def["name"] if self.topic_def else self.topic
        msgs.append(f"辯  DEBATE — {npc.name}")
        msgs.append(f"Topic: {t_name}")
        msgs.append(
            f"Your rhetoric: {player.skills['rhetoric']} | Argument points: {self.ap}"
        )
        greeting_lines = npc.get_dialog()
        msgs.append(f"{npc.name}: '{random.choice(greeting_lines)}'")
        return msgs

    def make_argument(self, player, arg_type_name):
        """Player makes an argument. Returns messages."""
        if not self.active or not self.target:
            return ["No debate active."]

        arg = ARGUMENT_TYPES.get(arg_type_name)
        if not arg:
            return ["Unknown argument type."]

        msgs = []
        self.round += 1

        # Check Ki cost
        ki_cost = arg["ki"]
        if player.stamina < ki_cost:
            msgs.append("Not enough Ki for that argument!")
            return msgs
        player.stamina = max(0, player.stamina - ki_cost)

        # Check money cost (for bribery)
        if "money_cost" in arg:
            if player.money < arg["money_cost"]:
                msgs.append(f"You need {arg['money_cost']} mon to bribe.")
                return msgs
            player.money -= arg["money_cost"]

        # Calculate argument power
        rhetoric = player.skills.get("rhetoric", 1)
        base_power = arg["power"]

        # Honor bonus for authority arguments
        if arg_type_name == "authority":
            base_power += player.honor // 10
        if arg_type_name == "intimidate":
            combat_skill = max(
                player.skills.get("kenjutsu", 1), player.skills.get("jujutsu", 1)
            )
            base_power += combat_skill * 2
            if player.honor < 30:
                base_power = int(base_power * 0.6)
                msgs.append("Low honor undercuts your threat.")

        # Faction rep bonus
        npc_faction = self.target.faction
        if player.rep.get(npc_faction, 0) > 30:
            base_power = int(base_power * 1.2)

        # Skill roll
        skill_roll = random.randint(1, 10) + rhetoric
        power = int(base_power * (skill_roll / 10.0))

        # Check counter/countered-by for NPC stance
        _, npc_stance = self.target.get_debate_stance()
        npc_preferred = self._get_npc_argument(npc_stance)

        # Counter relationships
        if npc_preferred in arg.get("counters", []):
            power = int(power * 1.4)
            msgs.append("  Your argument effectively counters their position!")
        elif npc_preferred in arg.get("countered_by", []):
            power = int(power * 0.6)
            msgs.append("  Their position is strong against this type of argument.")

        # Apply momentum shift
        old_momentum = self.momentum
        self.momentum = min(100, self.momentum + power // 2)
        msgs.insert(0, f"You present a {arg['name']}.")
        msgs.append(f"  Momentum: {old_momentum} → {self.momentum}")

        # Skill XP
        xp_msg = player.gain_skill_xp("rhetoric", 8 + self.round)
        if xp_msg:
            msgs.append(xp_msg)

        # NPC responds
        msgs.extend(self._npc_argument(player, npc_preferred))

        # Check for resolution
        msgs.extend(self._check_resolution(player))

        return msgs

    def _get_npc_argument(self, stance):
        """Get the argument type this stance uses."""
        stance_args = {
            "honor_above_all": "authority",
            "free_trade": "logical",
            "buddhism": "emotional",
            "rebel": "emotional",
            "freedom": "logical",
            "tradition": "authority",
            "pragmatism": "logical",
            "law_and_order": "authority",
            "might_makes_right": "intimidate",
            "neutral": "logical",
            "peasant": "emotional",
            "survival": "emotional",
            "shinto": "authority",
        }
        return stance_args.get(stance, "logical")

    def _npc_argument(self, player, arg_type_name):
        """NPC makes their counter-argument."""
        msgs = []
        npc = self.target
        npc_rhetoric = npc.skills.get("rhetoric", 1) + npc.honor // 15

        arg = ARGUMENT_TYPES.get(arg_type_name, ARGUMENT_TYPES["logical"])
        base_power = arg["power"]

        # NPC skill roll
        npc_roll = random.randint(1, 10) + npc_rhetoric
        npc_power = int(base_power * (npc_roll / 10.0))

        self.momentum = max(0, self.momentum - npc_power // 3)

        # NPC dialog response (generic based on argument type)
        responses = {
            "logical": [
                f"{npc.name}: 'The logic of it is straightforward — you cannot deny the facts.'",
                f"{npc.name}: 'Consider the consequences carefully before you commit to that position.'",
                f"{npc.name}: 'That argument collapses under scrutiny. Let me show you why.'",
            ],
            "emotional": [
                f"{npc.name}: 'Think of those who suffer under this! Have you no heart?'",
                f"{npc.name}: 'My ancestors did not sacrifice themselves for such cowardice!'",
                f"{npc.name}: 'Does duty mean nothing to you?'",
            ],
            "authority": [
                f"{npc.name}: 'The Emperor's decree stands above all personal opinions.'",
                f"{npc.name}: 'Tradition is not a cage — it is the spine of civilization.'",
                f"{npc.name}: 'These have been the laws since before your grandfather was born.'",
            ],
            "evidence": [
                f"{npc.name}: 'I have seen this myself. The facts do not lie as men do.'",
                f"{npc.name}: 'Three harvests. I have counted them. The numbers are clear.'",
            ],
            "intimidate": [
                f"{npc.name} places a hand on their weapon. 'Choose your next words carefully.'",
                f"{npc.name}: 'I have ended debates... permanently. Continue?'",
            ],
        }
        resp_list = responses.get(arg_type_name, responses["logical"])
        msgs.append(random.choice(resp_list))
        return msgs

    def _check_resolution(self, player):
        """Check if debate is over. Returns messages."""
        msgs = []
        if self.momentum >= 80:
            # Player wins
            msgs.extend(self._debate_won(player))
        elif self.momentum <= 20:
            # Player loses
            msgs.extend(self._debate_lost(player))
        elif self.round >= 8:
            # Draw
            msgs.extend(self._debate_draw(player))
        return msgs

    def _debate_won(self, player):
        msgs = []
        self.result = "won"
        self.active = False
        npc = self.target

        msgs.append(f"You WIN the debate! {npc.name} is persuaded.")
        player.debates_won += 1

        # Rewards
        honor_gain = 5 + player.skills.get("rhetoric", 1)
        player.apply_honor_change(honor_gain)
        msgs.append(f"Honor +{honor_gain}")

        # Faction reputation
        faction = npc.faction
        player.rep[faction] = min(100, player.rep.get(faction, 0) + 10)
        msgs.append(f"{faction.title()} faction reputation improved.")

        # NPC attitude change
        npc.attitude = max(npc.attitude, 1)
        npc.hostile = False
        npc.ai_state = "idle"

        # Skill XP
        xp_msg = player.gain_skill_xp("rhetoric", 30)
        if xp_msg:
            msgs.append(xp_msg)

        return msgs

    def _debate_lost(self, player):
        msgs = []
        self.result = "lost"
        self.active = False
        npc = self.target

        msgs.append(f"You LOSE the debate. {npc.name} is unconvinced.")

        honor_loss = 2
        player.apply_honor_change(-honor_loss)
        player.morale = max(0, player.morale - 10)
        msgs.append(f"Honor -{honor_loss}. Morale reduced.")

        return msgs

    def _debate_draw(self, player):
        msgs = []
        self.result = "draw"
        self.active = False
        msgs.append(
            "The debate reaches an impasse. Neither side fully convinces the other."
        )
        player.gain_skill_xp("rhetoric", 15)
        return msgs

    def concede(self, player):
        """Player concedes the debate."""
        self.result = "fled"
        self.active = False
        msgs = [f"You concede the debate with {self.target.name}."]
        player.apply_honor_change(-3)
        return msgs


# ─────────────────────────────────────────────────────────────
# CRAFTING / FORAGING SYSTEM
# ─────────────────────────────────────────────────────────────

CRAFT_RECIPES = {
    "crude_bandage": {
        "name": "Crude Bandage",
        "ingredients": [
            ("wood", 0),
            ("mushroom", 0),
        ],  # no quantity system, just check for item
        "result": "bandage",
        "skill": "medicine",
        "min_skill": 2,
        "desc": "Tear cloth from clothing and pack with herbs to form a field bandage.",
    },
    "fire": {
        "name": "Campfire",
        "ingredients": [("wood", 0), ("flint_steel", 0)],
        "result": "campfire",
        "skill": "survival",
        "min_skill": 1,
        "desc": "Build a fire for warmth, cooking, and light.",
        "terrain": [T_PLAINS, T_FOREST, T_BEACH, T_MOUNTAIN],
    },
    "snare": {
        "name": "Game Snare",
        "ingredients": [("rope", 0)],
        "result": "trap",
        "skill": "survival",
        "min_skill": 2,
        "desc": "Set a snare to catch small game overnight.",
    },
    "herb_medicine": {
        "name": "Herb Medicine",
        "ingredients": [("mushroom", 0), ("bamboo", 0)],
        "result": "herb_poultice",
        "skill": "medicine",
        "min_skill": 3,
        "desc": "Grind herbs with bamboo sap into a medicinal poultice.",
    },
}


def forage(player, terrain_type, season, rng=None):
    """Attempt to forage for food. Returns (success, item_name, message)."""
    rng = rng or random
    survival = player.skills.get("survival", 1)

    forage_tables = {
        T_FOREST: [
            ("mushroom", 40),
            ("herb_poultice", 20),
            ("wood", 25),
            ("bamboo", 15),
        ],
        T_DENSE_FOREST: [
            ("mushroom", 35),
            ("herb_poultice", 25),
            ("wood", 30),
            ("bamboo", 10),
        ],
        T_BAMBOO: [("bamboo", 50), ("mushroom", 25), ("herb_poultice", 25)],
        T_MOUNTAIN: [
            ("mushroom", 25),
            ("herb_poultice", 20),
            ("wood", 30),
            ("iron_ore", 10),
            ("spring_water", 15),
        ],
        T_PLAINS: [
            ("mushroom", 30),
            ("vegetable", 35),
            ("wood", 20),
            ("herb_poultice", 15),
        ],
        T_FARMLAND: [("vegetable", 50), ("rice", 35), ("wood", 15)],
        T_RICE_PADDY: [("rice", 70), ("vegetable", 20), ("water", 10)],
        T_BEACH: [("dried_fish", 40), ("water", 30), ("bamboo", 20), ("rope", 10)],
        T_SWAMP: [
            ("herb_poultice", 40),
            ("bamboo", 30),
            ("mushroom", 20),
            ("wood", 10),
        ],
        T_ONSEN: [("spring_water", 60), ("herb_poultice", 40)],
        T_RIVER: [("dried_fish", 50), ("water", 50)],
    }

    table = forage_tables.get(terrain_type)
    if not table:
        return False, None, "Nothing to forage here."

    # Skill check
    success_chance = 0.3 + survival * 0.07
    if season == "Winter":
        success_chance *= 0.5
    elif season == "Summer":
        success_chance *= 1.2

    if rng.random() > success_chance:
        skill_msg = player.gain_skill_xp("survival", 3)
        msgs = ["You search but find nothing useful."]
        if skill_msg:
            msgs.append(skill_msg)
        return False, None, "\n".join(msgs)

    # Pick item from table
    total_w = sum(w for _, w in table)
    roll = rng.uniform(0, total_w)
    cum = 0
    item_name = table[0][0]
    for name, w in table:
        cum += w
        if roll <= cum:
            item_name = name
            break

    skill_msg = player.gain_skill_xp("survival", 8)
    msg = f"You find {ITEMS.get(item_name, {}).get('name', item_name)}!"
    if skill_msg:
        msg += f" {skill_msg}"
    return True, item_name, msg


def attempt_fish(player, rng=None):
    """Try fishing at a river or coast. Returns (success, msg)."""
    rng = rng or random
    skill = player.skills.get("survival", 1)
    if not any(i.get("name_key") == "fishing_line" for i in player.inventory):
        return False, None, "You need a fishing line to fish."

    chance = 0.25 + skill * 0.06
    if rng.random() < chance:
        msg = "You pull up a fish!"
        skill_msg = player.gain_skill_xp("survival", 10)
        return True, "dried_fish", msg + (" " + skill_msg if skill_msg else "")
    return False, None, "The fish aren't biting."


def attempt_hunt(player, terrain_type, rng=None):
    """Try to hunt game. Requires bow or trap. Returns (success, item, msg)."""
    rng = rng or random
    skill = player.skills.get("kyujutsu", 1) + player.skills.get("survival", 1) // 2
    has_bow = (
        player.equipment.get("weapon", {})
        and player.equipment["weapon"].get("skill") == "kyujutsu"
    )

    if not has_bow and not any(i.get("name_key") == "trap" for i in player.inventory):
        return False, None, "You need a bow or trap to hunt."

    game_chance = {
        T_FOREST: 0.4,
        T_DENSE_FOREST: 0.5,
        T_MOUNTAIN: 0.3,
        T_PLAINS: 0.2,
        T_BAMBOO: 0.35,
    }.get(terrain_type, 0.1)

    chance = game_chance * (0.5 + skill * 0.05)
    if rng.random() < chance:
        game = rng.choice(["dried_fish", "dried_fish", "mushroom"])  # simplified
        msg = f"You hunt successfully — {ITEMS[game]['name']}."
        skill_msg = player.gain_skill_xp("kyujutsu" if has_bow else "survival", 12)
        return True, game, msg + (" " + skill_msg if skill_msg else "")
    return False, None, "You hunt but find no game."


# ─────────────────────────────────────────────────────────────
# WORLD TEMPERATURE MODEL
# ─────────────────────────────────────────────────────────────


def get_world_temperature(season, lat):
    """Return base temperature modifier for a location and season."""
    base = {
        "Spring": 3,
        "Summer": 8,
        "Autumn": 2,
        "Winter": -5,
    }.get(season, 0)

    # Latitude effect: north is colder
    lat_mod = (lat - 37) * -0.5  # ~0.5°C per degree of latitude from 37°N
    return base + lat_mod


# ─────────────────────────────────────────────────────────────
# TRAP MECHANICS
# ─────────────────────────────────────────────────────────────


class TrapManager:
    """Manage placed traps."""

    def __init__(self):
        self.traps = {}  # (col,row) -> turns_remaining

    def place_trap(self, col, row, player):
        """Place a trap at location."""
        has_trap = any(i.get("name_key") == "trap" for i in player.inventory)
        if not has_trap:
            return False, "You don't have a trap to set."
        # Remove one trap from inventory
        for i, item in enumerate(player.inventory):
            if item.get("name_key") == "trap":
                player.inventory.pop(i)
                break
        self.traps[(col, row)] = 15  # 15 turns to catch something
        return True, "You set a snare trap. Come back later."

    def tick(self, world, rng=None):
        """Check traps each turn. Returns list of (col, row, item_name) for catches."""
        rng = rng or random
        catches = []
        expired = []
        for (col, row), timer in self.traps.items():
            self.traps[(col, row)] = timer - 1
            if timer <= 0:
                expired.append((col, row))
                continue
            # Chance of catching something
            if rng.random() < 0.05:
                catches.append((col, row, rng.choice(["dried_fish", "mushroom"])))
                expired.append((col, row))
        for pos in expired:
            del self.traps[pos]
        return catches


# ─────────────────────────────────────────────────────────────
# SLEEP SYSTEM
# ─────────────────────────────────────────────────────────────


def attempt_sleep(player, terrain_type, weather, hours, rng=None):
    """Attempt to sleep. Quality depends on terrain and conditions."""
    rng = rng or random
    msgs = []

    # Sleep quality
    quality = "good"
    if terrain_type in (T_HIGH_PEAK, T_MOUNTAIN) and weather in (
        "snow",
        "blizzard",
        "frost",
    ):
        quality = "poor"
        msgs.append("You sleep fitfully in the cold. Rest is incomplete.")
    elif terrain_type == T_SWAMP:
        quality = "poor"
        msgs.append("The damp and insects make sleep difficult.")
    elif terrain_type in (T_VILLAGE, T_TOWN, T_CASTLE, T_TEMPLE, T_PORT):
        quality = "excellent"
        msgs.append("You sleep soundly under a roof.")
    elif terrain_type in (T_FOREST, T_PINE, T_BAMBOO):
        quality = "fair"
        msgs.append("You sleep on a bed of leaves in the forest.")

    # Apply rest
    restore_hp = {"poor": 1, "fair": 2, "good": 3, "excellent": 4}[quality] * hours
    restore_fat = {"poor": 8, "fair": 12, "good": 15, "excellent": 20}[quality] * hours
    restore_morale = {"poor": 2, "fair": 5, "good": 8, "excellent": 12}[quality]

    player.hp = min(player.max_hp, player.hp + restore_hp)
    player.fatigue = max(0, player.fatigue - restore_fat)
    player.morale = min(100, player.morale + restore_morale)

    # Chance of bad event while sleeping
    if quality != "excellent" and rng.random() < 0.05:
        msgs.append("You wake to something rustling nearby! On guard!")
        return msgs, True  # was_interrupted=True

    msgs.append(f"You sleep {hours} hours. HP restored: +{restore_hp}")
    return msgs, False


# ─────────────────────────────────────────────────────────────
# Z-LEVEL MOVEMENT
# ─────────────────────────────────────────────────────────────


def check_fall(player, local_map):
    """Check if player should fall. Returns list of messages."""
    if local_map is None:
        return []
    from z_level import get_fall_distance, calc_fall_damage

    col = local_map.get_column(player.col, player.row)
    if col is None:
        return []
    dist = get_fall_distance(col, player.z)
    if dist <= 0:
        return []
    player.z -= dist
    damage = calc_fall_damage(dist)
    msgs = []
    if damage > 0:
        player.hp = max(0, player.hp - damage)
        msgs.append(f"You fall {dist} meters! ({damage} damage)")
    else:
        msgs.append(f"You drop down {dist} meter{'s' if dist > 1 else ''}.")
    return msgs


def attempt_vertical_move(player, direction, local_map):
    """Attempt to move up or down a Z-level. direction: 'up' or 'down'.
    Returns (success, messages)."""
    if local_map is None:
        return False, ["You can't go that way."]
    from z_level import can_ascend, can_descend, can_climb

    col = local_map.get_column(player.col, player.row)
    if col is None:
        return False, ["Nothing there."]
    msgs = []
    if direction == "up":
        if can_ascend(col, player.z):
            player.z += 1
            msgs.append("You go up.")
            return True, msgs
        elif can_climb(col, player.z):
            player.z += 1
            player.stamina = max(0, player.stamina - 3)
            msgs.append("You climb up. (-3 Ki)")
            return True, msgs
        return False, ["No way up from here."]
    elif direction == "down":
        if can_descend(col, player.z):
            player.z -= 1
            msgs.append("You go down.")
            return True, msgs
        return False, ["No way down from here."]
    return False, ["Invalid direction."]
