"""
game.py - Main game loop for 縁起 ENGI
"""

import curses
import random
import sys
import math
from data import *
from world import World, geo_to_grid
from entities import Player, NPC, create_item
from mechanics import (
    CombatManager,
    DebateManager,
    forage,
    attempt_fish,
    attempt_hunt,
    attempt_sleep,
    get_world_temperature,
    TrapManager,
    CRAFT_RECIPES,
)
from renderer import Renderer


# ─────────────────────────────────────────────────────────────
# GAME STATE
# ─────────────────────────────────────────────────────────────
class GameState:
    def __init__(self):
        self.turn = 0
        self.day = 1
        self.hour = 6  # start at dawn
        self.minute = 0
        self.season = "Spring"
        self.season_turn = 0
        self.weather = "clear"
        self.weather_timer = 0
        self.rng = random.Random()
        self.game_over = False
        self.death_cause = ""
        self.paused = False
        self.sneak_mode = False

    @property
    def is_night(self):
        return self.hour < 5 or self.hour >= 20

    @property
    def time_str(self):
        period = "AM" if self.hour < 12 else "PM"
        h = self.hour if self.hour <= 12 else self.hour - 12
        h = 12 if h == 0 else h
        return f"{h:02d}:{self.minute:02d} {period}"

    @property
    def world_temp(self):
        return get_world_temperature(self.season, 35.0)  # approx center lat

    def advance_turn(self):
        self.turn += 1
        self.season_turn += 1

        # Advance time (10 turns = 1 hour)
        self.minute += 6
        if self.minute >= 60:
            self.minute = 0
            self.hour += 1
            if self.hour >= 24:
                self.hour = 0
                self.day += 1

        # Season change
        total_season_turns = SEASON_LENGTHS[SEASONS.index(self.season)]
        if self.season_turn >= total_season_turns:
            self.season_turn = 0
            idx = SEASONS.index(self.season)
            self.season = SEASONS[(idx + 1) % 4]

        # Weather change
        self.weather_timer -= 1
        if self.weather_timer <= 0:
            self._change_weather()

    def _change_weather(self):
        table = WEATHER_BY_SEASON.get(self.season, [("clear", 100)])
        total = sum(w for _, w in table)
        roll = self.rng.uniform(0, total)
        cum = 0
        for weather, w in table:
            cum += w
            if roll <= cum:
                self.weather = weather
                break
        self.weather_timer = self.rng.randint(15, 40)

    def is_dawn(self):
        return self.hour == 5 and self.minute < 6

    def is_dusk(self):
        return self.hour == 19 and self.minute < 6


# ─────────────────────────────────────────────────────────────
# REGION START POSITIONS
# ─────────────────────────────────────────────────────────────
REGION_STARTS = {
    "kanto": (35.68, 139.69),  # Edo
    "kinki": (35.01, 135.77),  # Kyoto
    "tohoku": (38.27, 140.87),  # Sendai
    "kyushu": (33.59, 130.41),  # Fukuoka
}

# ─────────────────────────────────────────────────────────────
# KEY MAPPINGS
# ─────────────────────────────────────────────────────────────
MOVE_KEYS = {
    ord("h"): (-1, 0),
    ord("j"): (0, 1),
    ord("k"): (0, -1),
    ord("l"): (1, 0),
    ord("y"): (-1, -1),
    ord("u"): (1, -1),
    ord("b"): (-1, 1),
    ord("n"): (1, 1),
    curses.KEY_LEFT: (-1, 0),
    curses.KEY_DOWN: (0, 1),
    curses.KEY_UP: (0, -1),
    curses.KEY_RIGHT: (1, 0),
    ord("4"): (-1, 0),
    ord("2"): (0, 1),
    ord("8"): (0, -1),
    ord("6"): (1, 0),
    ord("7"): (-1, -1),
    ord("9"): (1, -1),
    ord("1"): (-1, 1),
    ord("3"): (1, 1),
}

COMBAT_TECH_KEYS = {
    ord("1"): "strike",
    ord("2"): "feint",
    ord("3"): "power",
    ord("4"): "parry",
    ord("5"): "dodge",
    ord("6"): "riposte",
    ord("7"): "throw",
    ord("8"): "aimed_shot",
}

DEBATE_ARG_KEYS = {
    ord("1"): "logical",
    ord("2"): "emotional",
    ord("3"): "evidence",
    ord("4"): "authority",
    ord("5"): "rhetoric",
    ord("6"): "intimidate",
    ord("7"): "bribe",
    ord("8"): "concede",
}


# ─────────────────────────────────────────────────────────────
# MAIN GAME
# ─────────────────────────────────────────────────────────────
class Game:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.renderer = Renderer(stdscr)
        self.world = World()
        self.player = Player()
        self.state = GameState()
        self.combat = CombatManager()
        self.debate = DebateManager()
        self.traps = TrapManager()

        # Dialog state
        self.dialog_npc = None
        self.dialog_topics = {}
        self.dialog_sel = 0

        # UI mode
        self.mode = (
            "normal"  # normal, combat, debate, dialog, inventory, help, map, char
        )

        # Society simulation systems (initialized after world gen)
        self.event_bus = None
        self.trait_manager = None
        self.memory_manager = None
        self.relationship_manager = None
        self.conversation_system = None
        self.life_simulation = None
        self.encounter_manager = None

    # ─────────────────────────────────────────────────────
    # STARTUP
    # ─────────────────────────────────────────────────────
    def run(self):
        """Main entry point."""
        self._show_splash()
        self._init_world()
        self._character_creation()
        self._init_society_for_player()
        self._post_creation_messages()
        self._game_loop()

    def _show_splash(self):
        self.renderer.draw_splash()
        while True:
            k = self.renderer.get_key()
            if k in (ord("n"), ord("N")):
                return
            if k in (ord("q"), ord("Q")):
                sys.exit(0)

    def _character_creation(self):
        """Run character creation screen."""
        class_keys = list(CLASSES.keys())
        region_keys = ["kanto", "kinki", "tohoku", "kyushu"]
        sel_class = "ronin"
        sel_region = "kanto"
        ci = class_keys.index(sel_class)
        ri = region_keys.index(sel_region)

        while True:
            self.renderer.draw_char_creation(sel_class, sel_region)
            k = self.renderer.get_key()

            if k in (curses.KEY_RIGHT, ord("d")):
                ci = (ci + 1) % len(class_keys)
                sel_class = class_keys[ci]
            elif k in (curses.KEY_LEFT, ord("a")):
                ci = (ci - 1) % len(class_keys)
                sel_class = class_keys[ci]
            elif k == curses.KEY_DOWN:
                ri = (ri + 1) % len(region_keys)
                sel_region = region_keys[ri]
            elif k == curses.KEY_UP:
                ri = (ri - 1) % len(region_keys)
                sel_region = region_keys[ri]
            elif k in (ord("\n"), ord("\r"), curses.KEY_ENTER, 10, 13):
                # Get name
                name = self.renderer.prompt_string("Your name:")
                self.player.name = name or "Nameless"
                self.player.setup_class(sel_class, self.state.rng)
                self.state.rng = random.Random()
                self._set_start_pos(sel_region)
                return
            elif k in (ord("q"), ord("Q")):
                sys.exit(0)

    def _set_start_pos(self, region):
        lat, lon = REGION_STARTS.get(region, (35.68, 139.69))
        col, row = geo_to_grid(lat, lon)
        # Find walkable tile near start
        for r in range(15):
            for dc in range(-r, r + 1):
                for dr in range(-r, r + 1):
                    nc, nr = col + dc, row + dr
                    if 0 <= nc < WORLD_W and 0 <= nr < WORLD_H:
                        t = self.world.tiles[nr][nc]
                        if TERRAIN[t.terrain]["walk"]:
                            self.player.col = nc
                            self.player.row = nr
                            return
        self.player.col = col
        self.player.row = row

    def _init_world(self):
        """Generate the world tiles (before character creation)."""
        self.stdscr.clear()
        self.renderer.safe_addstr(
            self.stdscr,
            self.renderer.term_h // 2 - 2,
            self.renderer.term_w // 2 - 20,
            "  Generating the land of Japan...  ",
            curses.color_pair(6) | curses.A_BOLD,
        )
        self.stdscr.refresh()
        self.world.generate(seed=42)

        # Initialize society simulation systems
        from event_bus import EventBus
        from traits import TraitManager
        from memories import MemoryManager
        from relationships import RelationshipManager
        from conversations import ConversationSystem
        from life_sim import LifeSimulation
        from encounters import EncounterManager

        self.event_bus = EventBus()
        self.trait_manager = TraitManager()
        self.memory_manager = MemoryManager()
        self.relationship_manager = RelationshipManager(
            trait_manager=self.trait_manager,
            memory_manager=self.memory_manager,
        )
        self.conversation_system = ConversationSystem(
            relationship_manager=self.relationship_manager,
        )
        self.life_simulation = LifeSimulation(
            trait_manager=self.trait_manager,
            relationship_manager=self.relationship_manager,
        )
        self.encounter_manager = EncounterManager()

    def _init_society_for_player(self):
        """Initialize society systems for the player after character creation."""
        # Give player starting topics
        self.conversation_system.init_starting_topics("player")
        # Register player in life simulation
        self.life_simulation.register_character(
            "player",
            self.player.name,
            self.player.age,
            self.player.gender,
            list(self.player.traits),
        )

    def _post_creation_messages(self):
        """Queue intro messages after player name/class are known."""
        self.world.compute_fov(self.player.col, self.player.row, self.player.fov_radius)
        self._msg("The winds carry the smell of pine and distant iron.", 7)
        self._msg(
            f"You are {self.player.name}, a {CLASSES[self.player.cls]['name']}.", 6
        )
        self._msg("Your story begins. [? for help]", 3)

    # ─────────────────────────────────────────────────────
    # GAME LOOP
    # ─────────────────────────────────────────────────────
    def _game_loop(self):
        """Main loop."""
        while not self.state.game_over:
            # Recompute FOV
            self.world.compute_fov(
                self.player.col, self.player.row, self.player.fov_radius
            )

            # Draw
            if self.mode == "combat" and self.combat.active and self.combat.enemy:
                self.renderer.draw(self.world, self.player, self.state)
                self.renderer.draw_combat_overlay(
                    self.player, self.combat.enemy, self.combat
                )
            elif self.mode == "debate" and self.debate.active and self.debate.target:
                self.renderer.draw(self.world, self.player, self.state)
                self.renderer.draw_debate_overlay(
                    self.player, self.debate.target, self.debate
                )
            elif self.mode == "dialog" and self.dialog_npc:
                self.renderer.draw(self.world, self.player, self.state)
                greeting = self.dialog_npc.get_dialog()
                self.renderer.draw_dialog(
                    self.dialog_npc, greeting, self.dialog_topics, self.dialog_sel
                )
            elif self.mode == "help":
                self.renderer.draw(self.world, self.player, self.state)
                self.renderer.draw_help()
            elif self.mode == "map":
                self.renderer.draw(self.world, self.player, self.state)
                self.renderer.draw_world_map(self.world, self.player)
            elif self.mode == "inventory":
                self.renderer.draw(self.world, self.player, self.state)
                self.renderer.draw_inventory(self.player)
            elif self.mode == "char":
                self.renderer.draw(self.world, self.player, self.state)
                self.renderer.draw_character_sheet(self.player)
            else:
                self.renderer.draw(self.world, self.player, self.state)

            # Handle input
            k = self.renderer.get_key()

            if self.mode == "combat":
                self._handle_combat_input(k)
            elif self.mode == "debate":
                self._handle_debate_input(k)
            elif self.mode == "dialog":
                self._handle_dialog_input(k)
            elif self.mode == "help":
                self.mode = "normal"
            elif self.mode == "map":
                if k in (ord("m"), ord("M"), 27):
                    self.mode = "normal"
            elif self.mode == "inventory":
                self._handle_inventory_input(k)
            elif self.mode == "char":
                if k in (ord("@"), 27, ord("q")):
                    self.mode = "normal"
            else:
                self._handle_normal_input(k)

            # Death check
            if self.player.hp <= 0:
                self._die("wounds in battle")

        # Game over
        if self.state.game_over:
            self.renderer.draw(self.world, self.player, self.state)
            self.renderer.draw_death_screen(self.player, self.state.death_cause)
            while True:
                k = self.renderer.get_key()
                if k in (ord("q"), ord("Q")):
                    break
                if k in (ord("n"), ord("N")):
                    # New game
                    self.__init__(self.stdscr)
                    self.run()
                    break

    # ─────────────────────────────────────────────────────
    # INPUT HANDLERS
    # ─────────────────────────────────────────────────────
    def _handle_normal_input(self, k):
        """Handle input in normal mode."""
        # Movement
        if k in MOVE_KEYS:
            dc, dr = MOVE_KEYS[k]
            self._try_move(dc, dr)

        # Wait
        elif k == ord("."):
            self._pass_turn()

        # Pick up
        elif k == ord(","):
            self._pick_up()

        # Inventory
        elif k in (ord("i"),):
            self.mode = "inventory"

        # Eat
        elif k == ord("e"):
            self._eat_menu()

        # Apply / use item
        elif k == ord("a"):
            self._use_item_menu()

        # Drop
        elif k == ord("d"):
            self._drop_menu()

        # Equip
        elif k == ord("w"):
            self._equip_menu()

        # Rest (10 turns)
        elif k == ord("r"):
            self._rest_short()

        # Sleep until dawn
        elif k == ord("R"):
            self._sleep_long()

        # Sneak toggle
        elif k == ord("s"):
            self.state.sneak_mode = not self.state.sneak_mode
            mode = "ON" if self.state.sneak_mode else "OFF"
            self._msg(f"Sneak mode: {mode}", 7)

        # Forage
        elif k == ord("F"):
            self._forage()

        # Hunt
        elif k == ord("H"):
            self._hunt()

        # Fish
        elif k == ord("f"):
            self._fish()

        # Set trap
        elif k == ord("t"):
            self._set_trap()

        # Talk
        elif k in (ord("T"), ord("\n"), ord("\r"), 10, 13):
            self._talk_to_adjacent()

        # Debate
        elif k == ord("D"):
            self._debate_adjacent()

        # Examine terrain
        elif k == ord("x"):
            tile = self.world.get_tile(self.player.col, self.player.row)
            if tile:
                td = TERRAIN[tile.terrain]
                self._msg(f"{td['name']}: {td['desc']}", 7)
                if tile.feature:
                    desc = self.world.get_feature_desc(self.player.col, self.player.row)
                    if desc:
                        self._msg(desc, 6)

        # Look at location
        elif k == ord("l") and False:  # disable (l = move right)
            pass

        # World map
        elif k in (ord("M"), ord("m")):
            self.mode = "map"

        # Character sheet
        elif k == ord("@"):
            self.mode = "char"

        # Help
        elif k == ord("?"):
            self.mode = "help"

        # Quit
        elif k in (ord("Q"),):
            self._confirm_quit()

        # Stance cycling
        elif k == ord("\t"):
            stances = list(STANCES.keys())
            idx = stances.index(self.player.stance)
            self.player.stance = stances[(idx + 1) % len(stances)]
            self._msg(f"Combat stance: {self.player.stance.title()}", 7)

        # Look at adjacent NPC info
        elif k == ord("v"):
            self._describe_adjacent()

    def _handle_combat_input(self, k):
        """Handle input during combat."""
        if not self.combat.active:
            self.mode = "normal"
            return

        tech = COMBAT_TECH_KEYS.get(k)
        if tech:
            msgs = self.combat.player_attack(self.player, tech, self.world)
            for m in msgs:
                pair = (
                    5
                    if any(w in m.lower() for w in ["critical", "hit", "damage"])
                    else 1
                )
                if "miss" in m.lower():
                    pair = 8
                self._msg(m, pair)
            if not self.combat.active:
                self.mode = "normal"

        elif k == ord("\t"):
            stances = list(STANCES.keys())
            idx = stances.index(self.player.stance)
            self.player.stance = stances[(idx + 1) % len(stances)]
            self._msg(f"Stance → {self.player.stance.title()}", 7)

        elif k == 27:  # Escape = flee
            msgs = self.combat.player_attack(self.player, "flee", self.world)
            for m in msgs:
                self._msg(m, 5)
            if not self.combat.active:
                self.mode = "normal"

        # Check death
        if self.player.hp <= 0:
            self._die(
                f"killed by {self.combat.enemy.name if self.combat.enemy else 'an enemy'}"
            )

    def _handle_debate_input(self, k):
        """Handle input during debate."""
        if not self.debate.active:
            self.mode = "normal"
            return

        arg_type = DEBATE_ARG_KEYS.get(k)
        if arg_type:
            msgs = self.debate.make_argument(self.player, arg_type)
            for m in msgs:
                pair = 6 if "WIN" in m or "LOSE" in m or "impasse" in m else 7
                self._msg(m, pair)
            if not self.debate.active:
                self.mode = "normal"

        elif k == 27:  # Escape = concede
            msgs = self.debate.concede(self.player)
            for m in msgs:
                self._msg(m, 5)
            self.mode = "normal"

    def _handle_dialog_input(self, k):
        """Handle NPC dialog input."""
        npc = self.dialog_npc
        if not npc:
            self.mode = "normal"
            return

        topics = self.dialog_topics
        topic_keys = list(topics.keys())

        if k == 27 or k == ord("q"):
            # Leave
            farewell = npc.get_farewell()
            self._msg(f'{npc.name}: "{farewell}"', 7)
            self.dialog_npc = None
            self.mode = "normal"

        elif k == curses.KEY_DOWN or k == ord("j"):
            self.dialog_sel = (self.dialog_sel + 1) % max(1, len(topic_keys))

        elif k == curses.KEY_UP or k == ord("k"):
            self.dialog_sel = (self.dialog_sel - 1) % max(1, len(topic_keys))

        elif k in (ord("\n"), ord("\r"), 10, 13, ord(" ")):
            if topic_keys and 0 <= self.dialog_sel < len(topic_keys):
                topic = topic_keys[self.dialog_sel]
                response = topics[topic]
                # Replace faction placeholder
                faction_name = FACTIONS.get(npc.faction, {}).get("name", npc.faction)
                if isinstance(response, str):
                    response = response.replace("{faction}", faction_name)
                    self._show_topic_response(npc, topic, response)

        elif ord("1") <= k <= ord("9"):
            idx = k - ord("1")
            if 0 <= idx < len(topic_keys):
                topic = topic_keys[idx]
                response = topics[topic]
                faction_name = FACTIONS.get(npc.faction, {}).get("name", npc.faction)
                if isinstance(response, str):
                    response = response.replace("{faction}", faction_name)
                self._show_topic_response(npc, topic, response)

        elif k in (ord("D"), ord("d")):
            # Start debate
            self.dialog_npc = None
            self.mode = "normal"
            self._start_debate(npc)

        elif k in (ord("B"), ord("b")):
            # Trade/bribe
            self._trade_with(npc)

    def _handle_inventory_input(self, k):
        """Handle inventory screen input."""
        inv = self.player.inventory
        if k == 27 or k == ord("i") or k == ord("q"):
            self.mode = "normal"
        elif ord("1") <= k <= ord("9"):
            idx = k - ord("1")
            if 0 <= idx < len(inv):
                item = inv[idx]
                # Show item submenu
                self._item_submenu(item, idx)

    def _item_submenu(self, item, idx):
        """Show options for an item."""
        item_type = item.get("type", "?")
        options = []
        if item_type in ("food", "drink"):
            options.append(("e", "Eat/Drink"))
        if item_type == "medicine":
            options.append(("a", "Apply/Use"))
        if item_type in ("weapon", "armor"):
            options.append(("w", "Equip"))
        options.append(("d", "Drop"))
        options.append(("x", "Examine"))
        options.append(("q", "Cancel"))

        # Draw submenu
        lines = [f"", f"  {item['name']}", f"  {item.get('desc', '')[:50]}", ""]
        for key, name in options:
            lines.append(f"  [{key}] {name}")
        lines.append("")
        self.renderer._draw_modal(lines, title="ITEM")
        self.stdscr.refresh()

        k = self.renderer.get_key()
        for key, name in options:
            if k == ord(key):
                if name == "Eat/Drink":
                    msg, ok = self.player.eat(item)
                    if ok:
                        self.player.inventory.remove(item)
                    self._msg(msg, 3 if ok else 5)
                elif name == "Apply/Use":
                    msg, ok = self.player.use_medicine(item)
                    if ok:
                        self.player.inventory.remove(item)
                    self._msg(msg, 3 if ok else 5)
                elif name == "Equip":
                    msg = self.player.equip(item)
                    self._msg(msg, 3)
                elif name == "Drop":
                    msg = self.player.drop_item(item, self.world, None)
                    self._msg(msg, 7)
                elif name == "Examine":
                    self._msg(f"{item['name']}: {item.get('desc', '')}", 7)
                break

    # ─────────────────────────────────────────────────────
    # MOVEMENT & TURN PROCESSING
    # ─────────────────────────────────────────────────────
    def _try_move(self, dc, dr):
        """Try to move in a direction."""
        nc = self.player.col + dc
        nr = self.player.row + dr

        if not (0 <= nc < WORLD_W and 0 <= nr < WORLD_H):
            self._msg("The edge of the known world.", 8)
            return

        tile = self.world.get_tile(nc, nr)
        if not tile:
            return

        td = TERRAIN[tile.terrain]

        # NPC in the way
        if tile.npc_id:
            npc = self.world.npcs.get(tile.npc_id)
            if npc and npc.alive:
                if npc.hostile or npc.is_animal:
                    # Attack
                    self._start_combat(npc)
                else:
                    # Talk
                    self._talk(npc)
                return

        # Water/impassable
        if not td["walk"]:
            if td.get("swim"):
                # Swimming attempt
                if self.state.rng.random() < 0.4:
                    self._msg(f"The {td['name']} is too dangerous to cross here.", 4)
                    return
                else:
                    self._msg(f"You wade through the {td['name'].lower()}.", 4)
                    self.player.thirst = max(0, self.player.thirst - 5)
                    self.player.hp = max(1, self.player.hp - 1)
            else:
                self._msg(f"You cannot pass through {td['name'].lower()}.", 8)
                return

        # Move cost
        move_cost = td.get("cost", 1)
        if WEATHER_EFFECTS.get(self.state.weather, {}).get("move_mod", 0) > 0:
            move_cost += WEATHER_EFFECTS[self.state.weather]["move_mod"]
        if self.player.is_encumbered:
            move_cost += 1

        # Stealth fatigue
        if self.state.sneak_mode:
            self.player.stamina = max(0, self.player.stamina - 1)

        # Actually move
        old_tile = self.world.get_tile(self.player.col, self.player.row)
        self.player.col = nc
        self.player.row = nr
        self.player.distance_moved += 1

        # Terrain narration (rare)
        if self.state.rng.random() < 0.02:
            self._msg(f"{td['desc']}", 8)

        # Feature announcement
        if tile.feature:
            f = tile.feature
            if f.get("type") in ("city", "temple", "onsen"):
                fname = f.get("name", "?")
                self._msg(f"You arrive at {fname}.", 6)

        # Onsen healing
        if tile.terrain == T_ONSEN:
            self.player.hp = min(self.player.max_hp, self.player.hp + 2)
            self.player.warmth = min(100, self.player.warmth + 10)
            if self.state.turn % 3 == 0:
                self._msg("The hot spring's mineral waters soothe your body.", 9)

        # Process turn
        self._process_turn(move_cost)

    def _pass_turn(self):
        """Wait one turn."""
        self._process_turn(1)
        self._msg("You wait.", 8)

    def _process_turn(self, cost=1):
        """Advance the game world by one turn."""
        for _ in range(cost):
            self.state.advance_turn()
            self.player.turns_played += 1
            self.player.days_survived = self.player.turns_played // TURNS_PER_DAY + 1

            # Condition tick
            msgs = self.player.tick_conditions()
            for m, p in msgs:
                self._msg(m, p)

            # Survival tick (every turn)
            s_msgs = self.player.tick_survival(
                self.state.world_temp,
                self.world.get_tile(self.player.col, self.player.row).terrain
                if self.world.get_tile(self.player.col, self.player.row)
                else T_PLAINS,
                self.state.weather,
                self.state.season,
            )
            for m, p in s_msgs:
                self._msg(m, p)

            # NPC AI ticks
            self._tick_npcs()

            # Trap checks
            catches = self.traps.tick(self.world, self.state.rng)
            for col, row, item_name in catches:
                self._msg(f"Your trap caught something! ({item_name})", 3)
                item = create_item(item_name)
                if item:
                    tile = self.world.get_tile(col, row)
                    if tile:
                        iid = f"catch_{self.state.turn}"
                        item["id"] = iid
                        tile.items.append(iid)
                        self.world.items[iid] = item

            # Dawn/dusk messages
            if self.state.is_dawn():
                self._msg(
                    f"Dawn breaks. Day {self.state.day}. Season: {self.state.season}.",
                    3,
                )
            if self.state.is_dusk():
                self._msg("Dusk falls. The shadows deepen.", 8)

            # Weather change announcement
            if self.state.weather_timer == 39:  # just changed
                we = WEATHER_EFFECTS.get(self.state.weather, {})
                self._msg(
                    f"Weather: {self.state.weather.title()}. {we.get('desc', '')}", 7
                )

        # Player death check
        if self.player.hp <= 0:
            self._die("succumbing to wounds and hardship")

    def _tick_npcs(self):
        """Run AI for all NPCs."""
        for nid, npc in list(self.world.npcs.items()):
            if not npc.alive:
                continue
            actions = npc.ai_tick(self.world, self.player.col, self.player.row)
            for action, data in actions:
                if action == "alert":
                    self._msg(str(data), 5)
                elif action == "attack":
                    # NPC attacks player directly
                    if self.mode != "combat":
                        self._start_combat(npc)
                elif action == "flee_start":
                    self._msg(str(data), 7)
                elif action == "notice":
                    self._msg(str(data), 8)

    # ─────────────────────────────────────────────────────
    # ACTIONS
    # ─────────────────────────────────────────────────────
    def _pick_up(self):
        """Pick up items on the ground."""
        tile = self.world.get_tile(self.player.col, self.player.row)
        if not tile or not tile.items:
            self._msg("Nothing here to pick up.", 8)
            return
        if len(tile.items) == 1:
            iid = tile.items[0]
            msg = self.player.pick_up(iid, self.world)
            self._msg(msg, 3)
            self._process_turn(1)
        else:
            # Multiple items — show list
            lines = ["", "  Pick up which item?"]
            for i, iid in enumerate(tile.items[:9]):
                item = self.world.items.get(iid)
                if item:
                    lines.append(f"  [{i + 1}] {item['name']}")
            lines.append("  [Esc] Cancel")
            self.renderer._draw_modal(lines, title="PICK UP")
            self.stdscr.refresh()
            k = self.renderer.get_key()
            if ord("1") <= k <= ord("9"):
                idx = k - ord("1")
                if 0 <= idx < len(tile.items):
                    iid = tile.items[idx]
                    msg = self.player.pick_up(iid, self.world)
                    self._msg(msg, 3)
                    self._process_turn(1)

    def _eat_menu(self):
        """Quick eat/drink menu."""
        edibles = [
            (i, item)
            for i, item in enumerate(self.player.inventory)
            if item.get("type") in ("food", "drink")
        ]
        if not edibles:
            self._msg("You have nothing to eat or drink.", 8)
            return
        lines = ["", "  Eat or drink which?"]
        for i, (_, item) in enumerate(edibles[:8]):
            lines.append(f"  [{i + 1}] {item['name']}")
        lines.append("  [Esc] Cancel")
        self.renderer._draw_modal(lines, title="EAT/DRINK")
        self.stdscr.refresh()
        k = self.renderer.get_key()
        if ord("1") <= k <= ord("9"):
            idx = k - ord("1")
            if 0 <= idx < len(edibles):
                _, item = edibles[idx]
                msg, ok = self.player.eat(item)
                if ok:
                    self.player.inventory.remove(item)
                    self._process_turn(1)
                self._msg(msg, 3 if ok else 8)

    def _use_item_menu(self):
        """Use/apply item menu."""
        usable = [
            (i, item)
            for i, item in enumerate(self.player.inventory)
            if item.get("type") in ("medicine", "tool", "misc", "scroll")
        ]
        if not usable:
            self._msg("Nothing applicable to use.", 8)
            return
        lines = ["", "  Use which item?"]
        for i, (_, item) in enumerate(usable[:8]):
            lines.append(f"  [{i + 1}] {item['name']} — {item.get('desc', '')[:35]}")
        lines.append("  [Esc] Cancel")
        self.renderer._draw_modal(lines, title="USE ITEM")
        self.stdscr.refresh()
        k = self.renderer.get_key()
        if ord("1") <= k <= ord("9"):
            idx = k - ord("1")
            if 0 <= idx < len(usable):
                _, item = usable[idx]
                self._use_item(item)

    def _use_item(self, item):
        if item.get("type") == "medicine":
            msg, ok = self.player.use_medicine(item)
            if ok:
                self.player.inventory.remove(item)
                self._process_turn(1)
            self._msg(msg, 3 if ok else 8)

        elif item.get("type") == "tool":
            ttype = item.get("tool_type", "")
            if ttype == "fire":
                self._start_fire(item)
            elif ttype == "light":
                self.player.light_bonus = item.get("fov_bonus", 3)
                self._msg(
                    f"You light the {item['name']}. Visibility +{item.get('fov_bonus', 3)}.",
                    3,
                )
            elif ttype == "fish":
                self._fish()
            elif ttype == "trap":
                self._set_trap()

        elif item.get("type") == "scroll":
            if item.get("reveals_map"):
                lat, lon = None, None
                try:
                    from world import grid_to_geo

                    lat, lon = grid_to_geo(self.player.col, self.player.row)
                except:
                    pass
                # Mark nearby tiles as seen
                r = 25
                for dr in range(-r, r + 1):
                    for dc in range(-r, r + 1):
                        nc = self.player.col + dc
                        nr = self.player.row + dr
                        t = self.world.get_tile(nc, nr)
                        if t:
                            t.seen = True
                self.player.inventory.remove(item)
                self._msg("The map reveals the surrounding region.", 6)
            elif item.get("morale"):
                self.player.morale = min(100, self.player.morale + item["morale"])
                self._msg(f"You read the sutra. Morale +{item['morale']}.", 6)
                self._process_turn(2)
        elif item.get("type") == "misc":
            if item.get("morale"):
                self.player.morale = min(100, self.player.morale + item["morale"])
                self._msg(
                    f"You handle the {item['name']}. Morale +{item['morale']}.", 6
                )

    def _start_fire(self, flint_item):
        terrain = self.world.get_tile(self.player.col, self.player.row).terrain
        has_wood = any(i.get("name_key") == "wood" for i in self.player.inventory)
        if not has_wood:
            self._msg("You need firewood to start a fire.", 8)
            return
        if terrain in (T_RIVER, T_SWAMP, T_BEACH) and self.state.weather in (
            "rain",
            "storm",
        ):
            self._msg("Too wet to start a fire here.", 5)
            return
        # Remove wood from inventory
        for i, item in enumerate(self.player.inventory):
            if item.get("name_key") == "wood":
                self.player.inventory.pop(i)
                break
        self.player.warmth = min(100, self.player.warmth + 25)
        self.player.fatigue = max(0, self.player.fatigue - 10)
        self._msg("You build a fire. Its warmth drives away the cold.", 9)
        self._process_turn(5)

    def _drop_menu(self):
        """Drop item menu."""
        if not self.player.inventory:
            self._msg("You're carrying nothing.", 8)
            return
        lines = ["", "  Drop which item?"]
        for i, item in enumerate(self.player.inventory[:9]):
            lines.append(f"  [{i + 1}] {item['name']}")
        lines.append("  [Esc] Cancel")
        self.renderer._draw_modal(lines, title="DROP")
        self.stdscr.refresh()
        k = self.renderer.get_key()
        if ord("1") <= k <= ord("9"):
            idx = k - ord("1")
            if 0 <= idx < len(self.player.inventory):
                item = self.player.inventory[idx]
                msg = self.player.drop_item(item, self.world, None)
                self._msg(msg, 7)
                self._process_turn(1)

    def _equip_menu(self):
        """Equip weapon/armor menu."""
        equippable = [
            (i, item)
            for i, item in enumerate(self.player.inventory)
            if item.get("type") in ("weapon", "armor")
        ]
        if not equippable:
            self._msg("Nothing to equip.", 8)
            return
        lines = ["", "  Equip which item?"]
        for i, (_, item) in enumerate(equippable[:9]):
            slot = item.get("slot", "weapon") if item["type"] == "armor" else "weapon"
            lines.append(f"  [{i + 1}] {item['name']} [{slot}]")
        lines.append("  [Esc] Cancel")
        self.renderer._draw_modal(lines, title="EQUIP")
        self.stdscr.refresh()
        k = self.renderer.get_key()
        if ord("1") <= k <= ord("9"):
            idx = k - ord("1")
            if 0 <= idx < len(equippable):
                _, item = equippable[idx]
                msg = self.player.equip(item)
                self._msg(msg, 3)

    def _rest_short(self):
        """Rest 10 turns."""
        terrain = self.world.get_tile(self.player.col, self.player.row).terrain
        if any(
            npc
            for npc in self.world.npcs.values()
            if npc.alive
            and npc.hostile
            and math.sqrt(
                (npc.col - self.player.col) ** 2 + (npc.row - self.player.row) ** 2
            )
            < 5
        ):
            self._msg("Enemies are too close to rest!", 5)
            return
        self._process_turn(10)
        msgs = self.player.rest(1)
        for m, _ in msgs:
            self._msg(m, 7)

    def _sleep_long(self):
        """Sleep until dawn."""
        terrain = self.world.get_tile(self.player.col, self.player.row).terrain
        # Calculate hours until dawn
        if self.state.hour >= 20:
            hours = 24 - self.state.hour + 5
        elif self.state.hour < 5:
            hours = 5 - self.state.hour
        else:
            hours = 6  # sleep a standard night

        hours = max(2, min(10, hours))
        msgs, interrupted = attempt_sleep(
            self.player, terrain, self.state.weather, hours, self.state.rng
        )
        for m in msgs:
            self._msg(m, 7)

        turns = hours * TURNS_PER_HOUR
        self._process_turn(turns)

        if interrupted:
            self._msg("You are jolted awake!", 5)
        else:
            self._msg(f"You wake refreshed. Day {self.state.day}.", 3)

    def _forage(self):
        """Forage for food."""
        tile = self.world.get_tile(self.player.col, self.player.row)
        if not tile:
            return
        self._msg("You search the area for food and resources...", 8)
        self._process_turn(5)
        success, item_name, msg = forage(
            self.player, tile.terrain, self.state.season, self.state.rng
        )
        self._msg(msg, 3 if success else 8)
        if success and item_name:
            item = create_item(item_name)
            if item:
                self.player.inventory.append(item)

    def _fish(self):
        """Try to fish."""
        tile = self.world.get_tile(self.player.col, self.player.row)
        if not tile or tile.terrain not in (T_RIVER, T_COAST, T_SEA, T_BEACH):
            self._msg("You need to be near water to fish.", 8)
            return
        self._msg("You cast your line...", 8)
        self._process_turn(8)
        success, item_name, msg = attempt_fish(self.player, self.state.rng)
        self._msg(msg, 3 if success else 8)
        if success and item_name:
            item = create_item(item_name)
            if item:
                self.player.inventory.append(item)

    def _hunt(self):
        """Try to hunt."""
        tile = self.world.get_tile(self.player.col, self.player.row)
        if not tile:
            return
        self._msg("You track game through the area...", 8)
        self._process_turn(12)
        success, item_name, msg = attempt_hunt(
            self.player, tile.terrain, self.state.rng
        )
        self._msg(msg, 3 if success else 8)
        if success and item_name:
            item = create_item(item_name)
            if item:
                self.player.inventory.append(item)

    def _set_trap(self):
        """Set a trap."""
        tile = self.world.get_tile(self.player.col, self.player.row)
        if not tile:
            return
        success, msg = self.traps.place_trap(
            self.player.col, self.player.row, self.player
        )
        self._msg(msg, 3 if success else 8)
        if success:
            self._process_turn(3)

    # ─────────────────────────────────────────────────────
    # SOCIAL
    # ─────────────────────────────────────────────────────
    def _talk_to_adjacent(self):
        """Find adjacent NPC and talk."""
        for dc in range(-1, 2):
            for dr in range(-1, 2):
                if dc == 0 and dr == 0:
                    continue
                tile = self.world.get_tile(self.player.col + dc, self.player.row + dr)
                if tile and tile.npc_id:
                    npc = self.world.npcs.get(tile.npc_id)
                    if npc and npc.alive and not npc.is_animal:
                        self._talk(npc)
                        return
        self._msg("There's no one to talk to nearby.", 8)

    def _talk(self, npc):
        """Start dialog with NPC."""
        if npc.is_animal or npc.is_undead:
            self._msg(f"The {npc.name} does not speak.", 8)
            return
        if npc.hostile:
            self._msg(f"{npc.name} is not in the mood for conversation.", 5)
            self._start_combat(npc)
            return

        greeting_lines = npc.get_dialog()
        greeting = (
            random.choice(greeting_lines)
            if isinstance(greeting_lines, list)
            else str(greeting_lines)
        )
        self._msg(f'{npc.name}: "{greeting}"', 7)

        npc.talked = True
        self.dialog_npc = npc
        self.dialog_topics = npc.get_dialog_topics()
        self.dialog_sel = 0
        self.mode = "dialog"

    def _show_topic_response(self, npc, topic, response):
        """Show NPC's response to a topic."""
        self.renderer.draw_topic_response(npc, topic, response)
        self.renderer.get_key()
        # Gain rhetoric XP for asking questions
        self.player.gain_skill_xp("rhetoric", 3)

    def _debate_adjacent(self):
        """Find adjacent NPC and start debate."""
        for dc in range(-1, 2):
            for dr in range(-1, 2):
                if dc == 0 and dr == 0:
                    continue
                tile = self.world.get_tile(self.player.col + dc, self.player.row + dr)
                if tile and tile.npc_id:
                    npc = self.world.npcs.get(tile.npc_id)
                    if npc and npc.alive and not npc.is_animal:
                        self._start_debate(npc)
                        return
        self._msg("No one nearby to debate.", 8)

    def _start_debate(self, npc):
        if npc.is_animal:
            return
        if self.player.skills.get("rhetoric", 1) < 1:
            self._msg("You lack the rhetoric skill to debate.", 5)
            return
        msgs = self.debate.start_debate(self.player, npc)
        for m in msgs:
            self._msg(m, 6)
        self.mode = "debate"

    def _trade_with(self, npc):
        """Simple trade/merchant interaction."""
        if npc.type not in ("merchant", "innkeeper", "blacksmith"):
            self._msg(f"{npc.name} has nothing to sell.", 8)
            return
        self._msg(f"You browse {npc.name}'s wares. (Trade system in full build)", 7)

    def _describe_adjacent(self):
        """Describe adjacent NPCs/items."""
        for dc in range(-1, 2):
            for dr in range(-1, 2):
                if dc == 0 and dr == 0:
                    continue
                tile = self.world.get_tile(self.player.col + dc, self.player.row + dr)
                if tile and tile.npc_id:
                    npc = self.world.npcs.get(tile.npc_id)
                    if npc:
                        npc_def = NPCS.get(npc.type, {})
                        self._msg(f"{npc.name}: {npc_def.get('desc', '')}", 7)
                        self._msg(
                            f"  HP:{npc.hp}/{npc.max_hp} Hostile:{npc.hostile}", 8
                        )

    # ─────────────────────────────────────────────────────
    # COMBAT
    # ─────────────────────────────────────────────────────
    def _start_combat(self, npc):
        """Initiate combat."""
        msgs = self.combat.start_combat(self.player, npc)
        for m in msgs:
            self._msg(m, 5)
        self.mode = "combat"

    # ─────────────────────────────────────────────────────
    # DEATH
    # ─────────────────────────────────────────────────────
    def _die(self, cause):
        self.state.game_over = True
        self.state.death_cause = cause
        self.combat.active = False
        self.debate.active = False

    # ─────────────────────────────────────────────────────
    # UTILITY
    # ─────────────────────────────────────────────────────
    def _msg(self, text, pair=1):
        """Add message to log."""
        self.renderer.add_message(str(text), pair)

    def _confirm_quit(self):
        """Confirm quit."""
        lines = [
            "",
            "  Quit the game?",
            "  Your progress will be lost.",
            "",
            "  [Y]es  [N]o",
        ]
        self.renderer._draw_modal(lines, title="QUIT?")
        self.stdscr.refresh()
        k = self.renderer.get_key()
        if k in (ord("y"), ord("Y")):
            sys.exit(0)


# ─────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────
def main(stdscr):
    try:
        game = Game(stdscr)
        game.run()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    curses.wrapper(main)
