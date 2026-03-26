"""
renderer.py - Terminal renderer for 縁起 ENGI using curses
"""

import curses
import math
from data import *

# ─────────────────────────────────────────────────────────────
# COLOR PAIR ASSIGNMENTS
# pair 0 = default
# pair 1 = white/bold   (weapons, crits)
# pair 2 = green        (forest, nature)
# pair 3 = yellow       (plains, food, peasants)
# pair 4 = blue         (water, ocean)
# pair 5 = red          (enemies, danger)
# pair 6 = magenta      (temples, lords, magic)
# pair 7 = cyan         (towns, merchants, misc)
# pair 8 = dark grey    (mountains, ruins)
# pair 9 = bright red   (hot springs, fire)
# pair 10 = bright green (player)
# pair 11 = dim blue     (deep sea)
# pair 12 = dim grey     (unseen tiles)
# ─────────────────────────────────────────────────────────────

COLOR_PAIRS = [
    # pair_num, fg, bg
    (1, curses.COLOR_WHITE, curses.COLOR_BLACK),
    (2, curses.COLOR_GREEN, curses.COLOR_BLACK),
    (3, curses.COLOR_YELLOW, curses.COLOR_BLACK),
    (4, curses.COLOR_BLUE, curses.COLOR_BLACK),
    (5, curses.COLOR_RED, curses.COLOR_BLACK),
    (6, curses.COLOR_MAGENTA, curses.COLOR_BLACK),
    (7, curses.COLOR_CYAN, curses.COLOR_BLACK),
    (8, curses.COLOR_WHITE, curses.COLOR_BLACK),  # mountain (bold)
    (9, curses.COLOR_RED, curses.COLOR_BLACK),  # onsen
    (10, curses.COLOR_GREEN, curses.COLOR_BLACK),  # player
    (11, curses.COLOR_BLUE, curses.COLOR_BLACK),  # deep sea
    (12, curses.COLOR_BLACK, curses.COLOR_BLACK),  # unseen
]

# Dim colors for seen-but-not-lit tiles
DIM_PAIRS = {
    1: (1, False),
    2: (2, False),
    3: (3, False),
    4: (4, False),
    5: (5, False),
    6: (6, False),
    7: (7, False),
    8: (8, False),
    9: (9, False),
    10: (10, False),
    11: (11, False),
    12: (12, False),
}


class Renderer:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.setup_curses()

        # Message log (text, color_pair, turns_to_show)
        self.messages = []
        self.max_messages = 200
        self.visible_msg_lines = 5

        # UI panes
        self.sidebar_w = 22

        # Layout (must come after visible_msg_lines is defined)
        self.recalc_layout()

        # Viewport scroll offset
        self.cam_col = 0
        self.cam_row = 0

        # Special display flags
        self.show_world_map = False
        self.show_help = False
        self.show_char_sheet = False
        self.show_inventory = False

    def setup_curses(self):
        """Initialize curses settings and color pairs."""
        curses.curs_set(0)
        curses.noecho()
        curses.cbreak()
        self.stdscr.keypad(True)
        self.stdscr.nodelay(False)

        if curses.has_colors():
            curses.start_color()
            curses.use_default_colors()
            for pair_num, fg, bg in COLOR_PAIRS:
                try:
                    curses.init_pair(pair_num, fg, bg)
                except:
                    pass

    def recalc_layout(self):
        """Recalculate layout based on terminal size."""
        self.term_h, self.term_w = self.stdscr.getmaxyx()
        self.sidebar_w = min(22, self.term_w // 5)
        self.map_w = self.term_w - self.sidebar_w * 2
        self.map_h = self.term_h - self.visible_msg_lines - 2  # -2 for title + status
        self.msg_y = self.term_h - self.visible_msg_lines - 1
        self.left_sidebar_x = 0
        self.map_x = self.sidebar_w
        self.right_sidebar_x = self.sidebar_w + self.map_w

    def center_camera(self, player_col, player_row):
        """Center the viewport on the player."""
        self.cam_col = player_col - self.map_w // 2
        self.cam_row = player_row - self.map_h // 2
        self.cam_col = max(0, min(WORLD_W - self.map_w, self.cam_col))
        self.cam_row = max(0, min(WORLD_H - self.map_h, self.cam_row))

    def add_message(self, text, color_pair=1, duration=5):
        """Add a message to the log."""
        if isinstance(text, (list, tuple)):
            for t in text:
                if isinstance(t, tuple):
                    self.messages.append(t)
                else:
                    self.messages.append((str(t), color_pair))
        else:
            self.messages.append((str(text), color_pair))
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages :]

    def safe_addstr(self, win, y, x, text, attr=0):
        """Safe addstr that won't crash on boundary."""
        h, w = win.getmaxyx()
        if y < 0 or y >= h or x < 0:
            return
        max_len = w - x - 1
        if max_len <= 0:
            return
        try:
            win.addstr(y, x, text[:max_len], attr)
        except curses.error:
            pass

    # ─────────────────────────────────────────────────────
    # MAIN DRAW
    # ─────────────────────────────────────────────────────
    def draw(self, world, player, game_state):
        """Full redraw."""
        self.stdscr.clear()
        self.recalc_layout()
        self.center_camera(player.col, player.row)

        self._draw_title(game_state)
        self._draw_map(world, player, game_state)
        self._draw_left_sidebar(player, game_state)
        self._draw_right_sidebar(world, player, game_state)
        self._draw_messages()
        self._draw_status_bar(player, game_state)

        self.stdscr.refresh()

    def _draw_title(self, game_state):
        """Draw title bar."""
        t_str = f" 縁起 ENGI — Feudal Japan  |  Day {game_state.day}  |  {game_state.time_str}  |  {game_state.season} | {game_state.weather.title()} "
        attr = curses.color_pair(6) | curses.A_BOLD
        self.safe_addstr(
            self.stdscr, 0, 0, t_str.center(self.term_w)[: self.term_w - 1], attr
        )

    def _draw_status_bar(self, player, game_state):
        """Bottom status bar."""
        w = player.equipment.get("weapon")
        wname = w["name"] if w else "Unarmed"
        conds = (
            ",".join(list(player.conditions.keys())[:4])
            if player.conditions
            else "None"
        )
        s = (
            f" [{player.cls.upper()}] {player.name} | "
            f"HP:{player.hp}/{player.max_hp} Ki:{player.stamina}/{player.max_stamina} | "
            f"Stance:{player.stance.title()} | Weapon:{wname} | "
            f"Conditions:{conds} | Money:{player.money}mon "
        )
        attr = curses.color_pair(7)
        y = self.term_h - 1
        self.safe_addstr(self.stdscr, y, 0, s[: self.term_w - 1], attr)

    # ─────────────────────────────────────────────────────
    # MAP DRAWING
    # ─────────────────────────────────────────────────────
    def _draw_map(self, world, player, game_state):
        """Draw the main map viewport."""
        is_night = game_state.is_night
        map_win_y = 1
        map_win_x = self.map_x

        for screen_r in range(self.map_h):
            world_r = self.cam_row + screen_r
            if world_r < 0 or world_r >= WORLD_H:
                continue

            for screen_c in range(self.map_w):
                world_c = self.cam_col + screen_c
                if world_c < 0 or world_c >= WORLD_W:
                    continue

                draw_y = map_win_y + screen_r
                draw_x = map_win_x + screen_c

                # Player
                if world_c == player.col and world_r == player.row:
                    attr = curses.color_pair(10) | curses.A_BOLD
                    self.safe_addstr(self.stdscr, draw_y, draw_x, "@", attr)
                    continue

                tile = world.tiles[world_r][world_c]

                if not tile.seen:
                    self.safe_addstr(self.stdscr, draw_y, draw_x, " ")
                    continue

                # Get terrain info
                td = TERRAIN[tile.terrain]
                ch = td["ch"]
                pair = td["pair"]

                # NPC takes priority over item
                if tile.lit and tile.npc_id:
                    npc = world.npcs.get(tile.npc_id)
                    if npc and npc.alive:
                        ch = npc.char
                        pair = npc.pair
                        if npc.hostile or npc.is_animal:
                            attr = curses.color_pair(5) | curses.A_BOLD
                        else:
                            attr = curses.color_pair(pair)
                        self.safe_addstr(self.stdscr, draw_y, draw_x, ch, attr)
                        continue

                # Item on ground
                if tile.lit and tile.items:
                    item = world.items.get(tile.items[0])
                    if item:
                        ch = item.get("char", "?")
                        pair = item.get("pair", 7)
                        attr = curses.color_pair(pair)
                        self.safe_addstr(self.stdscr, draw_y, draw_x, ch, attr)
                        continue

                # Terrain rendering
                if not tile.lit:
                    # Seen but not currently visible — dim
                    attr = curses.color_pair(pair) | curses.A_DIM
                elif is_night:
                    # Night: everything slightly dim
                    attr = curses.color_pair(pair) | curses.A_DIM
                else:
                    attr = curses.color_pair(pair)
                    # Bold for key features
                    if tile.terrain in (T_HIGH_PEAK, T_MOUNTAIN):
                        attr |= curses.A_BOLD
                    elif tile.terrain in (T_CASTLE, T_TEMPLE, T_TOWN):
                        attr |= curses.A_BOLD

                self.safe_addstr(self.stdscr, draw_y, draw_x, ch, attr)

        # Map border
        self._draw_map_border(map_win_y, map_win_x)

    def _draw_map_border(self, y, x):
        """Draw simple map border."""
        pass  # Clean look — no border

    # ─────────────────────────────────────────────────────
    # SIDEBARS
    # ─────────────────────────────────────────────────────
    def _draw_left_sidebar(self, player, game_state):
        """Left sidebar: player stats."""
        x = self.left_sidebar_x
        y = 1
        w = self.sidebar_w - 1
        attr_hdr = curses.color_pair(6) | curses.A_BOLD
        attr_lbl = curses.color_pair(7)
        attr_val = curses.color_pair(1)
        attr_crit = curses.color_pair(5) | curses.A_BOLD

        def put(row, text, attr=attr_val):
            self.safe_addstr(self.stdscr, y + row, x, text[:w], attr)

        put(0, "─── CHARACTER ───", attr_hdr)
        put(1, f"{player.name[: w - 1]}", attr_val | curses.A_BOLD)
        put(2, f"{CLASSES[player.cls]['name'][: w - 1]}", attr_lbl)
        put(3, "─────────────────", curses.color_pair(8))
        # HP bar
        hp_pct = player.hp / max(1, player.max_hp)
        hp_bar = self._bar(player.hp, player.max_hp, 14, "█", "░")
        hp_col = 5 if hp_pct < 0.3 else (3 if hp_pct < 0.6 else 2)
        put(4, f"HP  {hp_bar}", curses.color_pair(hp_col))
        put(5, f"    {player.hp:3}/{player.max_hp:3}", attr_lbl)
        # Ki bar
        ki_pct = player.stamina / max(1, player.max_stamina)
        ki_bar = self._bar(player.stamina, player.max_stamina, 14, "▓", "░")
        put(6, f"Ki  {ki_bar}", curses.color_pair(6))
        put(7, f"    {player.stamina:3}/{player.max_stamina:3}", attr_lbl)
        put(8, "─────────────────", curses.color_pair(8))

        # Survival stats
        def surv_color(val, invert=True):
            if invert:
                return 5 if val > 75 else (3 if val > 45 else 2)
            return 2 if val > 60 else (3 if val > 30 else 5)

        def surv_bar(val):
            return self._bar(val, 100, 10, "▪", "·")

        put(
            9,
            f"Food {surv_bar(player.hunger)}",
            curses.color_pair(surv_color(player.hunger)),
        )
        put(
            10,
            f"Watr {surv_bar(player.thirst)}",
            curses.color_pair(surv_color(player.thirst)),
        )
        put(
            11,
            f"Ftg  {surv_bar(player.fatigue)}",
            curses.color_pair(surv_color(player.fatigue)),
        )
        put(
            12,
            f"Warm {surv_bar(player.warmth)}",
            curses.color_pair(surv_color(player.warmth, invert=False)),
        )
        put(
            13,
            f"Morl {surv_bar(player.morale)}",
            curses.color_pair(surv_color(player.morale, invert=False)),
        )
        put(14, "─────────────────", curses.color_pair(8))
        put(15, f"Honor:{player.honor:3}  💰{player.money:5}¥", attr_val)
        put(16, "─────────────────", curses.color_pair(8))
        put(17, "── SKILLS ────────", attr_hdr)
        skill_names = [
            ("kenjutsu", "Sword"),
            ("kyujutsu", "Bow"),
            ("jujutsu", "Grapple"),
            ("naginata", "Polearm"),
            ("stealth", "Stealth"),
            ("rhetoric", "Rhetoric"),
            ("survival", "Survival"),
            ("medicine", "Medicine"),
            ("teppo", "Firearms"),
        ]
        for i, (sk, short) in enumerate(skill_names):
            lv = player.skills.get(sk, 1)
            bar = "●" * lv + "○" * (10 - lv)
            col = (
                curses.color_pair(3)
                if lv >= 7
                else (curses.color_pair(7) if lv >= 4 else curses.color_pair(8))
            )
            put(18 + i, f"{short[:6]:<6} {bar[:10]}", col)

        put(27, "─────────────────", curses.color_pair(8))
        put(28, "── CONDITIONS ────", attr_hdr)
        cond_list = list(player.conditions.keys())[:4]
        if not cond_list:
            put(29, "  (none)", attr_lbl)
        for i, cond in enumerate(cond_list):
            cdef = CONDITIONS.get(cond, {})
            col = curses.color_pair(cdef.get("color", 1))
            put(29 + i, f"  ● {cond[:14]}", col)

    def _draw_right_sidebar(self, world, player, game_state):
        """Right sidebar: location info, ground items, nearby NPCs."""
        x = self.right_sidebar_x + 1
        y = 1
        w = self.sidebar_w - 2
        attr_hdr = curses.color_pair(6) | curses.A_BOLD
        attr_lbl = curses.color_pair(7)
        attr_val = curses.color_pair(1)

        def put(row, text, attr=attr_val):
            if y + row < self.term_h - self.visible_msg_lines - 2:
                self.safe_addstr(self.stdscr, y + row, x, text[:w], attr)

        # Location info
        tile = world.get_tile(player.col, player.row)
        if tile:
            td = TERRAIN[tile.terrain]
            put(0, "── LOCATION ──────", attr_hdr)
            put(1, td["name"][:w], curses.color_pair(td["pair"]) | curses.A_BOLD)
            put(2, td["desc"][:w], attr_lbl)
            if tile.feature:
                fname = tile.feature.get("name", "")
                put(3, fname[:w], curses.color_pair(6))
            else:
                put(3, "", attr_lbl)

        # Terrain & elevation
        lat, lon = None, None
        try:
            from world import grid_to_geo

            lat, lon = grid_to_geo(player.col, player.row)
        except:
            pass
        if lat:
            put(4, f"Pos: {lat:.1f}°N {lon:.1f}°E", attr_lbl)
        put(5, f"Elev: {tile.elevation:.1f}" if tile else "", attr_lbl)
        put(6, "─────────────────", curses.color_pair(8))

        # Equipment
        put(7, "── EQUIPMENT ─────", attr_hdr)
        slots = [
            ("weapon", "Weapon"),
            ("offhand", "Off-hand"),
            ("body", "Body"),
            ("head", "Head"),
            ("hands", "Hands"),
            ("legs", "Legs"),
        ]
        for i, (slot, label) in enumerate(slots):
            item = player.equipment.get(slot)
            if item:
                iname = item["name"][: w - 8]
                put(8 + i, f"  {label[:6]}: {iname}", curses.color_pair(3))
            else:
                put(8 + i, f"  {label[:6]}: —", curses.color_pair(8))

        put(14, "─────────────────", curses.color_pair(8))
        put(
            15,
            f"Weight: {player.current_weight:.1f}/{player.max_carry_weight}kg",
            attr_lbl,
        )
        put(
            16,
            f"Ammo: →{player.ammo.get('arrow', 0)} ●{player.ammo.get('ball', 0)}",
            attr_lbl,
        )
        put(17, "─────────────────", curses.color_pair(8))

        # Ground items
        put(18, "── ON GROUND ─────", attr_hdr)
        if tile and tile.items:
            for i, iid in enumerate(tile.items[:4]):
                item = world.items.get(iid)
                if item:
                    put(19 + i, f"  {item['name'][: w - 3]}", curses.color_pair(3))
            if len(tile.items) > 4:
                put(23, f"  ...+{len(tile.items) - 4} more", attr_lbl)
        else:
            put(19, "  (empty)", attr_lbl)

        put(24, "─────────────────", curses.color_pair(8))

        # Nearby NPCs in FOV
        put(25, "── NEARBY ────────", attr_hdr)
        visible_npcs = []
        for nid, npc in world.npcs.items():
            t = world.get_tile(npc.col, npc.row)
            if t and t.lit and npc.alive:
                dist = math.sqrt(
                    (npc.col - player.col) ** 2 + (npc.row - player.row) ** 2
                )
                visible_npcs.append((dist, npc))
        visible_npcs.sort(key=lambda x: x[0])
        if not visible_npcs:
            put(26, "  (none visible)", attr_lbl)
        for i, (dist, npc) in enumerate(visible_npcs[:5]):
            col = curses.color_pair(5) if npc.hostile else curses.color_pair(7)
            hp_bar = self._bar(npc.hp, npc.max_hp, 5, "█", "░")
            put(26 + i, f"{npc.char} {npc.name[:8]:<8} {hp_bar}", col)

    def _bar(self, current, maximum, length, filled="█", empty="░"):
        """Generate a text progress bar."""
        if maximum <= 0:
            return empty * length
        filled_len = int(length * current / maximum)
        filled_len = max(0, min(length, filled_len))
        return filled * filled_len + empty * (length - filled_len)

    # ─────────────────────────────────────────────────────
    # MESSAGES
    # ─────────────────────────────────────────────────────
    def _draw_messages(self):
        """Draw message log at bottom."""
        y_start = self.msg_y
        # Separator
        self.safe_addstr(
            self.stdscr, y_start, 0, "─" * (self.term_w - 1), curses.color_pair(8)
        )

        recent = self.messages[-(self.visible_msg_lines) :]
        for i, (text, pair) in enumerate(recent):
            attr = curses.color_pair(pair)
            if i == len(recent) - 1:
                attr |= curses.A_BOLD  # Most recent is bold
            # Indent to sidebar width
            full_text = f"  {text}"
            self.safe_addstr(self.stdscr, y_start + 1 + i, 0, full_text, attr)

    # ─────────────────────────────────────────────────────
    # MODAL OVERLAYS
    # ─────────────────────────────────────────────────────
    def draw_help(self):
        """Draw help overlay."""
        lines = [
            "══════════════════════════════════════════",
            "         縁起 ENGI — CONTROLS            ",
            "══════════════════════════════════════════",
            "",
            "MOVEMENT: h j k l  (←↓↑→)  + diagonals",
            "           y u b n  (diagonal corners)   ",
            "  OR:      arrow keys / numpad           ",
            "",
            "── ACTIONS ──────────────────────────────",
            "  .   Wait one turn",
            "  ,   Pick up item",
            "  i   Inventory",
            "  e   Eat/Drink",
            "  d   Drop item",
            "  a   Apply/Use item",
            "  w   Equip weapon/armor",
            "  r   Rest (10 turns)",
            "  R   Sleep until dawn",
            "  s   Sneak mode toggle",
            "  F   Forage for food",
            "  H   Hunt (bow/trap)",
            "  f   Fish (at river/coast)",
            "  t   Set trap",
            "",
            "── COMBAT ───────────────────────────────",
            "  When adjacent to enemy, bump to attack",
            "  During combat popup:",
            "    1-5  Choose technique",
            "    Tab  Cycle stance",
            "    Esc  Flee",
            "",
            "── SOCIAL ───────────────────────────────",
            "  T / Enter  Talk to adjacent NPC",
            "  D          Debate NPC",
            "  B          Bribe NPC",
            "",
            "── INTERFACE ────────────────────────────",
            "  M   World map (you've seen)",
            "  @   Character sheet",
            "  ?   This help",
            "  Q   Quit",
            "",
            "  Press any key to close...",
        ]
        self._draw_modal(lines, title="HELP")

    def draw_inventory(self, player):
        """Draw inventory screen."""
        lines = [""]
        lines.append("  #  Item                    Wt   Type")
        lines.append("  ─────────────────────────────────────")
        for i, item in enumerate(player.inventory):
            equipped = ""
            for slot, eq in player.equipment.items():
                if eq == item:
                    equipped = f"[{slot[:3].upper()}]"
                    break
            lines.append(
                f"  {i + 1:2}. {item['name'][:20]:<20} {item.get('weight', 0):3.1f} {item.get('type', '?')[:8]} {equipped}"
            )
        lines.append("")
        lines.append(
            f"  Carried: {player.current_weight:.1f}/{player.max_carry_weight}kg"
        )
        lines.append("  [a] Use  [e] Equip  [d] Drop  [Esc] Close")
        self._draw_modal(lines, title="INVENTORY")

    def draw_character_sheet(self, player):
        """Draw detailed character sheet."""
        c = CLASSES.get(player.cls, {})
        lines = [
            "",
            f"  Name:  {player.name}",
            f"  Class: {c.get('name', player.cls)}",
            f"  Days:  {player.days_survived}  Kills: {player.kills}  Debates Won: {player.debates_won}",
            f"  Honor: {player.honor}  Money: {player.money} mon",
            "",
            "  ── Vital Stats ─────────────────────",
            f"  HP:      {player.hp}/{player.max_hp}",
            f"  Ki:      {player.stamina}/{player.max_stamina}",
            f"  Hunger:  {player.hunger}/100  Thirst: {player.thirst}/100",
            f"  Fatigue: {player.fatigue}/100  Warmth: {player.warmth}/100",
            f"  Morale:  {player.morale}/100",
            "",
            "  ── Skills ──────────────────────────",
        ]
        for sk, sdef in SKILLS.items():
            lv = player.skills.get(sk, 1)
            xp = player.skill_xp.get(sk, 0)
            needed = SKILL_XP_CURVE[min(lv, SKILL_MAX - 1)]
            bar = "●" * lv + "○" * (10 - lv)
            lines.append(f"  {sdef['name'][:24]:<24} {bar} Lv{lv} ({xp}/{needed})")
        lines.append("")
        lines.append("  ── Faction Reputation ──────────────")
        for faction, rep in player.rep.items():
            if abs(rep) > 0:
                bar = (
                    "+" * max(0, rep // 10) if rep > 0 else "-" * max(0, abs(rep) // 10)
                )
                lines.append(f"  {faction[:12]:<12} {rep:+4}  {bar[:10]}")
        lines.append("")
        lines.append("  ── Equipment ───────────────────────")
        for slot, item in player.equipment.items():
            if item:
                lines.append(f"  {slot[:8]:<8}: {item['name']}")
        lines.append("")
        lines.append("  [Esc/@ to close]")
        self._draw_modal(lines, title="CHARACTER SHEET")

    def draw_world_map(self, world, player):
        """Draw a zoomed-out world map."""
        h = min(self.term_h - 4, 50)
        w = min(self.term_w - 4, 100)
        start_y = (self.term_h - h) // 2
        start_x = (self.term_w - w) // 2

        # Draw border
        self._draw_box(start_y, start_x, h, w, "WORLD MAP — SEEN TILES")

        scale_x = WORLD_W / (w - 2)
        scale_y = WORLD_H / (h - 2)

        for sy in range(h - 2):
            for sx in range(w - 2):
                wc = int(sx * scale_x)
                wr = int(sy * scale_y)
                if 0 <= wc < WORLD_W and 0 <= wr < WORLD_H:
                    tile = world.tiles[wr][wc]
                    draw_y = start_y + 1 + sy
                    draw_x = start_x + 1 + sx

                    # Player position
                    px = int(player.col / scale_x)
                    py = int(player.row / scale_y)
                    if sx == px and sy == py:
                        self.safe_addstr(
                            self.stdscr,
                            draw_y,
                            draw_x,
                            "@",
                            curses.color_pair(10) | curses.A_BOLD,
                        )
                        continue

                    if not tile.seen:
                        self.safe_addstr(self.stdscr, draw_y, draw_x, " ")
                        continue

                    td = TERRAIN[tile.terrain]
                    self.safe_addstr(
                        self.stdscr,
                        draw_y,
                        draw_x,
                        td["ch"],
                        curses.color_pair(td["pair"]),
                    )

        # City labels
        try:
            from world import geo_to_grid

            for city in CITIES[:15]:
                gc, gr = geo_to_grid(city["lat"], city["lon"])
                sx = int(gc / scale_x)
                sy = int(gr / scale_y)
                if 1 <= sx < w - 3 and 1 <= sy < h - 2:
                    short = city["name"][:4]
                    self.safe_addstr(
                        self.stdscr,
                        start_y + 1 + sy,
                        start_x + 1 + sx,
                        short,
                        curses.color_pair(3) | curses.A_BOLD,
                    )
        except:
            pass

        self.safe_addstr(
            self.stdscr,
            start_y + h - 1,
            start_x + 2,
            " Press M or Esc to close ",
            curses.color_pair(7),
        )
        self.stdscr.refresh()

    def draw_combat_overlay(self, player, enemy, combat_mgr):
        """Draw combat UI overlay."""
        lines = [
            "",
            f"  ⚔  COMBAT: {enemy.name}",
            f"  {'=' * 38}",
            f"  Enemy HP: {self._bar(enemy.hp, enemy.max_hp, 20)} {enemy.hp}/{enemy.max_hp}",
            f"  Your HP:  {self._bar(player.hp, player.max_hp, 20)} {player.hp}/{player.max_hp}",
            f"  Your Ki:  {self._bar(player.stamina, player.max_stamina, 20)} {player.stamina}/{player.max_stamina}",
            f"  Stance: {player.stance.upper()}  |  Round: {combat_mgr.round}",
            "",
            "  ── TECHNIQUES ──────────────────────",
            "  [1] Strike        (basic attack)",
            "  [2] Feint & Strike(Ki:1, +acc)",
            "  [3] Power Strike  (Ki:2, +dmg)",
            "  [4] Parry         (Ki:1, defend)",
            "  [5] Dodge         (Ki:1, evade)",
            "  [6] Riposte       (Ki:2, counter)",
            "  [7] Throw         (Ki:2, jujutsu)",
            "  [8] Aimed Shot    (Ki:1, ranged)",
            "",
            "  [Tab] Cycle Stance  [Esc] Flee",
        ]
        self._draw_modal(lines, title=f"COMBAT vs {enemy.name[:20]}")

    def draw_debate_overlay(self, player, npc, debate_mgr):
        """Draw debate UI overlay."""
        momentum_bar = self._bar(debate_mgr.momentum, 100, 20, "▰", "▱")
        lines = [
            "",
            f"  辯  DEBATE: {npc.name}",
            f"  {'=' * 38}",
            f"  Topic: {DEBATE_TOPICS.get(debate_mgr.topic, {}).get('name', debate_mgr.topic)}",
            "",
            f"  Momentum: [{momentum_bar}] {debate_mgr.momentum}%",
            f"    Opponent   ←{' ' * 10}→   You",
            "",
            f"  Your Rhetoric: {player.skills.get('rhetoric', 1)}  Ki: {player.stamina}/{player.max_stamina}",
            f"  Argument Points: {debate_mgr.ap}  Round: {debate_mgr.round}/8",
            "",
            "  ── ARGUMENTS ───────────────────────",
            "  [1] Logical Argument    (Ki:1)",
            "  [2] Emotional Appeal    (Ki:1)",
            "  [3] Present Evidence    (Ki:2)",
            "  [4] Cite Authority      (Ki:1)",
            "  [5] Rhetorical Flourish (Ki:3)",
            "  [6] Intimidation        (Ki:0)",
            "  [7] Bribery             (20mon)",
            "  [8] Concede Point",
            "",
            "  [Esc] Withdraw from debate",
        ]
        self._draw_modal(lines, title=f"DEBATE: {npc.name[:20]}")

    def draw_dialog(self, npc, lines, topics, selected=0):
        """Draw NPC dialog overlay."""
        dialog_lines = [
            "",
            f"  Talking to: {npc.name}  ({npc.faction})",
            f"  {'-' * 38}",
        ]
        for line in lines[:3]:
            dialog_lines.append(f"  {line}")
        dialog_lines.append("")
        if topics:
            dialog_lines.append("  Ask about:")
            for i, (key, text) in enumerate(list(topics.items())[:8]):
                marker = ">" if i == selected else " "
                preview = text[:35] if isinstance(text, str) else str(text)[:35]
                dialog_lines.append(
                    f"  {marker}[{i + 1}] {key.replace('_', ' ').title()}"
                )
        dialog_lines.append("")
        dialog_lines.append("  [T]alk [D]ebate [B]uy/Sell [Esc]Leave")
        self._draw_modal(dialog_lines, title=f"DIALOG: {npc.name[:20]}")

    def draw_topic_response(self, npc, topic, response):
        """Draw a topic response popup."""
        lines = [
            "",
            f"  On the topic of '{topic.replace('_', ' ').title()}':",
            "",
        ]
        # Word-wrap the response
        words = response.split()
        line = "  "
        for word in words:
            if len(line) + len(word) + 1 > 44:
                lines.append(line)
                line = "  " + word + " "
            else:
                line += word + " "
        if line.strip():
            lines.append(line)
        lines.append("")
        lines.append(f"  — {npc.name}")
        lines.append("")
        lines.append("  [any key to continue]")
        self._draw_modal(lines, title=npc.name)

    def draw_location_info(self, world, col, row):
        """Draw popup with location info."""
        tile = world.get_tile(col, row)
        if not tile:
            return
        td = TERRAIN[tile.terrain]
        lines = [
            "",
            f"  {td['name']} ({td['jp']})",
            f"  {td['desc']}",
        ]
        if tile.feature:
            f = tile.feature
            lines.append("")
            lines.append(f"  Feature: {f.get('name', '?')}")
            if "desc" in f:
                lines.append(f"  {f['desc']}")
        if tile.items:
            lines.append("")
            lines.append(f"  Items here: {len(tile.items)}")
        lines.append("")
        lines.append("  [any key]")
        self._draw_modal(lines, title="LOCATION INFO")

    def draw_death_screen(self, player, cause):
        """Draw death screen."""
        lines = [
            "",
            "       You have perished.",
            "",
            f"  {player.name}, {CLASSES[player.cls]['name']}",
            f"  Survived {player.days_survived} days",
            f"  Kills: {player.kills}  Debates won: {player.debates_won}",
            f"  Honor: {player.honor}  Money: {player.money} mon",
            "",
            f"  Cause: {cause}",
            "",
            "  Your story ends here. The land",
            "  will not remember your name.",
            "",
            "  [Q]uit  [N]ew game",
        ]
        self._draw_modal(lines, title="✦ 死  DEATH ✦")

    def draw_rest_screen(self, hours):
        """Show rest animation."""
        self.safe_addstr(
            self.stdscr,
            self.term_h // 2,
            self.term_w // 2 - 10,
            f"  Resting... {hours}h  ",
            curses.color_pair(6) | curses.A_BOLD,
        )
        self.stdscr.refresh()

    # ─────────────────────────────────────────────────────
    # HELPERS
    # ─────────────────────────────────────────────────────
    def _draw_modal(self, lines, title=""):
        """Draw a centered modal dialog."""
        max_len = max((len(l) for l in lines), default=40)
        w = max(max_len + 4, len(title) + 6, 46)
        h = len(lines) + 4
        w = min(w, self.term_w - 2)
        h = min(h, self.term_h - 2)
        start_y = max(0, (self.term_h - h) // 2)
        start_x = max(0, (self.term_w - w) // 2)
        self._draw_box(start_y, start_x, h, w, title)

        for i, line in enumerate(lines[: h - 3]):
            self.safe_addstr(
                self.stdscr,
                start_y + 2 + i,
                start_x + 1,
                line[: w - 2],
                curses.color_pair(1),
            )
        self.stdscr.refresh()

    def _draw_box(self, y, x, h, w, title=""):
        """Draw a box with optional title."""
        attr_box = curses.color_pair(6) | curses.A_BOLD
        attr_title = curses.color_pair(3) | curses.A_BOLD

        # Fill background
        for ry in range(h):
            self.safe_addstr(
                self.stdscr, y + ry, x, " " * (w - 1), curses.color_pair(0)
            )

        # Border
        try:
            self.stdscr.addch(y, x, curses.ACS_ULCORNER, attr_box)
            self.stdscr.addch(y, x + w - 2, curses.ACS_URCORNER, attr_box)
            self.stdscr.addch(y + h - 1, x, curses.ACS_LLCORNER, attr_box)
            self.stdscr.addch(y + h - 1, x + w - 2, curses.ACS_LRCORNER, attr_box)
            for cx in range(1, w - 2):
                self.stdscr.addch(y, x + cx, curses.ACS_HLINE, attr_box)
                self.stdscr.addch(y + h - 1, x + cx, curses.ACS_HLINE, attr_box)
            for ry in range(1, h - 1):
                self.stdscr.addch(y + ry, x, curses.ACS_VLINE, attr_box)
                self.stdscr.addch(y + ry, x + w - 2, curses.ACS_VLINE, attr_box)
        except curses.error:
            pass

        if title:
            title_str = f" {title} "
            tx = x + max(1, (w - len(title_str)) // 2)
            self.safe_addstr(self.stdscr, y, tx, title_str, attr_title)

    def get_key(self):
        """Get a keypress."""
        return self.stdscr.getch()

    def prompt_string(self, prompt, max_len=20):
        """Get a string from the user."""
        curses.echo()
        curses.curs_set(1)
        y = self.term_h // 2
        x = self.term_w // 2 - len(prompt) // 2 - max_len // 2
        self.safe_addstr(
            self.stdscr,
            y,
            x,
            prompt + " " * (max_len + 2),
            curses.color_pair(3) | curses.A_BOLD,
        )
        self.stdscr.move(y, x + len(prompt) + 1)
        self.stdscr.refresh()
        try:
            result = self.stdscr.getstr(y, x + len(prompt) + 1, max_len).decode("utf-8")
        except:
            result = "Player"
        curses.noecho()
        curses.curs_set(0)
        return result.strip() or "Nameless"

    def draw_char_creation(self, selected_class, selected_region):
        """Draw character creation screen."""
        self.stdscr.clear()
        y = 2
        x = max(2, self.term_w // 2 - 38)
        attr_title = curses.color_pair(6) | curses.A_BOLD
        attr_sel = curses.color_pair(3) | curses.A_BOLD
        attr_norm = curses.color_pair(1)
        attr_desc = curses.color_pair(7)
        attr_lbl = curses.color_pair(8)

        self.safe_addstr(
            self.stdscr,
            y,
            x,
            "╔══════════════════════════════════════════════════════╗",
            attr_title,
        )
        self.safe_addstr(
            self.stdscr,
            y + 1,
            x,
            "║          縁起 ENGI — Character Creation              ║",
            attr_title,
        )
        self.safe_addstr(
            self.stdscr,
            y + 2,
            x,
            "╚══════════════════════════════════════════════════════╝",
            attr_title,
        )

        self.safe_addstr(
            self.stdscr, y + 4, x, "Choose your class:  (← → to cycle)", attr_lbl
        )
        class_keys = list(CLASSES.keys())
        for i, cls_key in enumerate(class_keys):
            cls = CLASSES[cls_key]
            marker = "►" if cls_key == selected_class else "  "
            col = attr_sel if cls_key == selected_class else attr_norm
            self.safe_addstr(
                self.stdscr, y + 5 + i, x, f"  {marker} {cls['name']}", col
            )

        # Selected class description
        if selected_class in CLASSES:
            cdef = CLASSES[selected_class]
            self.safe_addstr(self.stdscr, y + 12, x, "─" * 56, attr_lbl)
            self.safe_addstr(self.stdscr, y + 13, x, cdef["desc"][:75], attr_desc)
            self.safe_addstr(
                self.stdscr,
                y + 15,
                x,
                f"  Start HP:{cdef['hp']}  Ki:{cdef['stamina']}  Honor:{cdef['start_honor']}  Money:{cdef['start_money']}mon",
                attr_desc,
            )

            # Starting skills
            self.safe_addstr(self.stdscr, y + 16, x, "  Skills:", attr_lbl)
            sk_str = "  "
            for sk, val in cdef["skills"].items():
                if val > 0:
                    sk_str += f"{sk[:4]}:{val}  "
            self.safe_addstr(self.stdscr, y + 17, x, sk_str[:74], attr_desc)

        # Region selection
        regions = [
            ("kanto", "Kantō — Eastern plains near Edo. Tokugawa territory."),
            ("kinki", "Kansai — Capital region. Near Kyoto and Osaka."),
            ("tohoku", "Tōhoku — Rugged north. Date clan lands."),
            ("kyushu", "Kyūshū — Southern island. Firearms and foreign trade."),
        ]
        self.safe_addstr(
            self.stdscr, y + 19, x, "Starting Region:  (↑ ↓ to select)", attr_lbl
        )
        for i, (rkey, rdesc) in enumerate(regions):
            marker = "►" if rkey == selected_region else "  "
            col = attr_sel if rkey == selected_region else attr_norm
            self.safe_addstr(
                self.stdscr, y + 20 + i, x, f"  {marker} {rdesc[:70]}", col
            )

        self.safe_addstr(self.stdscr, y + 25, x, "─" * 56, attr_lbl)
        self.safe_addstr(
            self.stdscr, y + 26, x, "  [Enter] Begin your story  |  [Q] Quit", attr_sel
        )
        self.stdscr.refresh()

    def draw_splash(self):
        """Draw title/splash screen."""
        self.stdscr.clear()
        cy = self.term_h // 2 - 8
        cx = self.term_w // 2

        lines = [
            ("", 1),
            ("縁    起", 6),
            ("", 1),
            ("E  N  G  I", 3),
            ("", 1),
            ("A Roguelike Set in Feudal Japan", 7),
            ("", 1),
            ("Open world. Brutal survival.", 1),
            ("Deep combat. The art of argument.", 1),
            ("", 1),
            ("Japan — proportionally accurate.", 8),
            ("Hokkaido to Kyushu. Every province.", 8),
            ("", 1),
            ("[N]ew Game    [Q]uit", 3),
        ]
        for i, (line, pair) in enumerate(lines):
            attr = curses.color_pair(pair) | (curses.A_BOLD if pair in (3, 6) else 0)
            self.safe_addstr(self.stdscr, cy + i, cx - len(line) // 2, line, attr)
        self.stdscr.refresh()

    # ─────────────────────────────────────────────────────
    # LOCAL MAP DRAWING
    # ─────────────────────────────────────────────────────
    def draw_local(self, local_map, player_x, player_y, player_z, game_state):
        """Full redraw for local map mode (1:1 meter scale)."""
        self.stdscr.clear()
        self.recalc_layout()

        # Title bar with Z-level indicator
        if player_z == SURFACE_Z:
            z_label = "Ground"
        elif player_z < SURFACE_Z:
            z_label = "Underground"
        else:
            z_label = "Above"

        loc_name = getattr(game_state, "location_name", "Unknown")
        title = (
            f" {loc_name}  |  Z:{player_z} ({z_label})"
            f"  |  Day {game_state.day}  |  {game_state.time_str}"
            f"  |  {game_state.season}"
        )
        attr_title = curses.color_pair(6) | curses.A_BOLD
        self.safe_addstr(
            self.stdscr,
            0,
            0,
            title.center(self.term_w)[: self.term_w - 1],
            attr_title,
        )

        # Draw local map viewport centered on player
        half_w = self.map_w // 2
        half_h = self.map_h // 2
        map_win_y = 1
        map_win_x = self.map_x

        for screen_r in range(self.map_h):
            world_y = player_y - half_h + screen_r
            for screen_c in range(self.map_w):
                world_x = player_x - half_w + screen_c
                draw_y = map_win_y + screen_r
                draw_x = map_win_x + screen_c

                # Player at centre
                if world_x == player_x and world_y == player_y:
                    attr = curses.color_pair(10) | curses.A_BOLD
                    self.safe_addstr(
                        self.stdscr,
                        draw_y,
                        draw_x,
                        "@",
                        attr,
                    )
                    continue

                coord = (world_x, world_y, player_z)

                # Visibility check
                in_lit = coord in local_map.lit_tiles
                in_seen = coord in local_map.seen_tiles

                if not in_lit and not in_seen:
                    # Unseen — leave blank
                    continue

                tile = local_map.get_tile(world_x, world_y, player_z)
                if tile is None:
                    continue

                tdef = LOCAL_TERRAIN.get(tile.terrain)
                if tdef is None:
                    continue

                ch = tdef["ch"]
                pair = tdef["pair"]

                # NPC on this tile (only if lit)
                if in_lit and tile.npc_id:
                    npc = local_map.npcs.get(tile.npc_id)
                    if npc and getattr(npc, "alive", True):
                        npc_ch = getattr(npc, "char", "N")
                        npc_pair = getattr(npc, "pair", 5)
                        if getattr(npc, "hostile", False):
                            npc_attr = curses.color_pair(5) | curses.A_BOLD
                        else:
                            npc_attr = curses.color_pair(npc_pair)
                        self.safe_addstr(
                            self.stdscr,
                            draw_y,
                            draw_x,
                            npc_ch,
                            npc_attr,
                        )
                        continue

                if in_lit:
                    attr = curses.color_pair(pair)
                    if tdef.get("sight"):
                        attr |= curses.A_BOLD
                else:
                    # Seen but not currently lit — dim
                    attr = curses.color_pair(pair) | curses.A_DIM

                self.safe_addstr(
                    self.stdscr,
                    draw_y,
                    draw_x,
                    ch,
                    attr,
                )

        # Sidebar, messages, status
        self.draw_local_sidebar(
            local_map,
            player_x,
            player_y,
            player_z,
        )
        self._draw_messages()

        self.stdscr.refresh()

    def draw_local_sidebar(self, local_map, player_x, player_y, player_z):
        """Right sidebar for local map: Z-level, coords, terrain."""
        x = self.right_sidebar_x + 1
        y = 1
        w = self.sidebar_w - 2
        attr_hdr = curses.color_pair(6) | curses.A_BOLD
        attr_lbl = curses.color_pair(7)
        attr_val = curses.color_pair(1)

        def put(row, text, attr=attr_val):
            if y + row < self.term_h - self.visible_msg_lines - 2:
                self.safe_addstr(
                    self.stdscr,
                    y + row,
                    x,
                    text[:w],
                    attr,
                )

        put(0, "── LOCAL MAP ─────", attr_hdr)
        put(1, f"Z-Level: {player_z}", attr_val | curses.A_BOLD)

        if player_z == SURFACE_Z:
            z_label = "Ground"
        elif player_z < SURFACE_Z:
            z_label = "Underground"
        else:
            z_label = "Above"
        put(2, f"  ({z_label})", attr_lbl)

        put(3, "─────────────────", curses.color_pair(8))
        put(4, f"X: {player_x}", attr_lbl)
        put(5, f"Y: {player_y}", attr_lbl)

        # Terrain at player position
        put(6, "─────────────────", curses.color_pair(8))
        tile = local_map.get_tile(player_x, player_y, player_z)
        if tile is not None:
            tdef = LOCAL_TERRAIN.get(tile.terrain)
            if tdef:
                put(7, tdef["name"][:w], attr_val | curses.A_BOLD)
                put(8, tdef["desc"][:w], attr_lbl)
            else:
                put(7, "Unknown", attr_lbl)
        else:
            put(7, "Void", attr_lbl)

        # Z-level indicator
        put(10, "── DEPTH ─────────", attr_hdr)
        above = max(0, MAX_Z - player_z)
        below = max(0, player_z - MIN_Z)
        # Show arrow counts (capped for display)
        max_arrows = max(1, (w - 2))
        up_count = min(above, max_arrows)
        dn_count = min(below, max_arrows)
        if up_count > 0:
            put(11, "+" + "▲" * up_count, curses.color_pair(3))
        else:
            put(11, "(surface)", attr_lbl)
        if dn_count > 0:
            put(12, "-" + "▼" * dn_count, curses.color_pair(4))
        else:
            put(12, "(bedrock)", attr_lbl)

    def draw_transition_message(self, message):
        """Show a centred message during map transitions."""
        self.stdscr.clear()
        cy = self.term_h // 2
        cx = max(0, self.term_w // 2 - len(message) // 2)
        attr = curses.color_pair(6) | curses.A_BOLD
        self.safe_addstr(self.stdscr, cy, cx, message, attr)
        self.stdscr.refresh()
        curses.napms(800)  # brief display before auto-clear
