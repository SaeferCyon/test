"""
clan_sim.py - Sengoku Period Clan Simulation Engine for ENGI
Handles clan AI, diplomacy, warfare, and territory changes.
"""

import random
from typing import Optional

from clan_data import (
    CLANS,
    CLAN_TRAITS,
    PROVINCES,
    RELATION_ALLIED,
    RELATION_FRIENDLY,
    RELATION_HOSTILE,
    RELATION_NEUTRAL,
    RELATION_TRUCE,
    RELATION_WAR,
    BATTLE_RANDOM_FACTOR,
    TRUCE_DURATION_DAYS,
    WAR_DECLARATION_THRESHOLD,
)

# ---------------------------------------------------------------------------
# Province adjacency graph (computed from geographic proximity)
# Two provinces are neighbors if their centers are within ~1.8 degrees apart.
# This threshold captures historically adjacent provinces without false links.
# ---------------------------------------------------------------------------
_ADJACENCY_THRESHOLD = 1.8


def _build_adjacency() -> dict[str, set[str]]:
    """Build a province adjacency graph from lat/lon proximity."""
    adj: dict[str, set[str]] = {k: set() for k in PROVINCES}
    keys = list(PROVINCES.keys())
    for i, k1 in enumerate(keys):
        p1 = PROVINCES[k1]
        for k2 in keys[i + 1 :]:
            p2 = PROVINCES[k2]
            dist = ((p1["lat"] - p2["lat"]) ** 2 + (p1["lon"] - p2["lon"]) ** 2) ** 0.5
            if dist <= _ADJACENCY_THRESHOLD:
                adj[k1].add(k2)
                adj[k2].add(k1)
    return adj


PROVINCE_ADJACENCY = _build_adjacency()


# ---------------------------------------------------------------------------
# ClanState
# ---------------------------------------------------------------------------
class ClanState:
    """Mutable runtime state for a single clan."""

    def __init__(self, clan_id: str) -> None:
        data = CLANS[clan_id]
        self.clan_id: str = clan_id
        self.military: int = data["military"]
        self.treasury: int = data["treasury"]
        self.provinces: list[str] = list(data["provinces"])
        self.allies: set[str] = set(data["allies"])
        self.enemies: set[str] = set(data["enemies"])
        self.truces: dict[str, int] = {}  # clan_id -> days remaining
        self.at_war_with: set[str] = set()
        self.daimyo_alive: bool = True

    # -- serialisation helpers ------------------------------------------------
    def to_dict(self) -> dict:
        return {
            "clan_id": self.clan_id,
            "military": self.military,
            "treasury": self.treasury,
            "provinces": self.provinces,
            "allies": sorted(self.allies),
            "enemies": sorted(self.enemies),
            "truces": self.truces,
            "at_war_with": sorted(self.at_war_with),
            "daimyo_alive": self.daimyo_alive,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ClanState":
        state = cls.__new__(cls)
        state.clan_id = data["clan_id"]
        state.military = data["military"]
        state.treasury = data["treasury"]
        state.provinces = list(data["provinces"])
        state.allies = set(data["allies"])
        state.enemies = set(data["enemies"])
        state.truces = {k: int(v) for k, v in data["truces"].items()}
        state.at_war_with = set(data["at_war_with"])
        state.daimyo_alive = data["daimyo_alive"]
        return state


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _trait_value(clan_id: str, key: str, default: float = 1.0) -> float:
    """Aggregate a trait bonus for *clan_id*."""
    traits = CLANS[clan_id].get("traits", [])
    value = default
    for t in traits:
        td = CLAN_TRAITS.get(t, {})
        if key in td:
            v = td[key]
            if isinstance(v, (int, float)):
                value *= v
    return value


def _defense_bonus(clan_id: str) -> float:
    """Combined defense multiplier for a clan."""
    return _trait_value(clan_id, "defense_bonus")


def _war_tendency(clan_id: str) -> float:
    """How eager a clan is to declare war (higher = more eager)."""
    return _trait_value(clan_id, "war_tendency")


# ---------------------------------------------------------------------------
# ClanSimulation
# ---------------------------------------------------------------------------
class ClanSimulation:
    """Top-level simulation engine for all clan interactions."""

    def __init__(self) -> None:
        self.states: dict[str, ClanState] = {cid: ClanState(cid) for cid in CLANS}
        self.relations: dict[tuple[str, str], str] = {}
        self.events: list[dict] = []
        self.day: int = 0

        self._init_relations()

    # -- initialisation -------------------------------------------------------
    def _init_relations(self) -> None:
        """Seed bilateral relations from static clan data."""
        for cid, data in CLANS.items():
            for ally in data.get("allies", []):
                if ally in CLANS:
                    self.set_relation(cid, ally, RELATION_ALLIED)
            for enemy in data.get("enemies", []):
                if enemy in CLANS:
                    self.set_relation(cid, enemy, RELATION_HOSTILE)

    # -- relation helpers -----------------------------------------------------
    @staticmethod
    def _rel_key(a: str, b: str) -> tuple[str, str]:
        return (min(a, b), max(a, b))

    def get_relation(self, clan_a: str, clan_b: str) -> str:
        return self.relations.get(self._rel_key(clan_a, clan_b), RELATION_NEUTRAL)

    def set_relation(self, clan_a: str, clan_b: str, relation: str) -> None:
        self.relations[self._rel_key(clan_a, clan_b)] = relation

    # -- state access ---------------------------------------------------------
    def get_state(self, clan_id: str) -> Optional[ClanState]:
        return self.states.get(clan_id)

    def get_clan_at_province(self, province_key: str) -> Optional[str]:
        for cid, st in self.states.items():
            if province_key in st.provinces:
                return cid
        return None

    def get_border_clans(self, clan_id: str) -> set[str]:
        """Return clan ids whose provinces neighbour *clan_id*'s."""
        st = self.states.get(clan_id)
        if st is None:
            return set()
        neighbours: set[str] = set()
        for prov in st.provinces:
            for adj_prov in PROVINCE_ADJACENCY.get(prov, set()):
                owner = self.get_clan_at_province(adj_prov)
                if owner is not None and owner != clan_id:
                    neighbours.add(owner)
        return neighbours

    def get_recent_events(self, count: int = 10) -> list[dict]:
        return self.events[-count:]

    # -- diplomacy actions ----------------------------------------------------
    def declare_war(self, attacker_id: str, defender_id: str) -> None:
        a_st = self.states[attacker_id]
        d_st = self.states[defender_id]
        a_st.at_war_with.add(defender_id)
        d_st.at_war_with.add(attacker_id)
        a_st.enemies.add(defender_id)
        d_st.enemies.add(attacker_id)
        a_st.allies.discard(defender_id)
        d_st.allies.discard(attacker_id)
        self.set_relation(attacker_id, defender_id, RELATION_WAR)
        self.events.append(
            {
                "day": self.day,
                "type": "war_declared",
                "attacker": attacker_id,
                "defender": defender_id,
            }
        )

    def make_peace(self, clan_a: str, clan_b: str) -> None:
        sa = self.states[clan_a]
        sb = self.states[clan_b]
        sa.at_war_with.discard(clan_b)
        sb.at_war_with.discard(clan_a)
        sa.truces[clan_b] = TRUCE_DURATION_DAYS
        sb.truces[clan_a] = TRUCE_DURATION_DAYS
        self.set_relation(clan_a, clan_b, RELATION_TRUCE)
        self.events.append(
            {
                "day": self.day,
                "type": "peace",
                "parties": sorted([clan_a, clan_b]),
            }
        )

    def form_alliance(self, clan_a: str, clan_b: str) -> None:
        sa = self.states[clan_a]
        sb = self.states[clan_b]
        sa.allies.add(clan_b)
        sb.allies.add(clan_a)
        sa.enemies.discard(clan_b)
        sb.enemies.discard(clan_a)
        self.set_relation(clan_a, clan_b, RELATION_ALLIED)
        self.events.append(
            {
                "day": self.day,
                "type": "alliance_formed",
                "parties": sorted([clan_a, clan_b]),
            }
        )

    def break_alliance(self, clan_a: str, clan_b: str) -> None:
        sa = self.states[clan_a]
        sb = self.states[clan_b]
        sa.allies.discard(clan_b)
        sb.allies.discard(clan_a)
        self.set_relation(clan_a, clan_b, RELATION_NEUTRAL)
        self.events.append(
            {
                "day": self.day,
                "type": "alliance_broken",
                "parties": sorted([clan_a, clan_b]),
            }
        )

    # -- tick -----------------------------------------------------------------
    def tick(self, rng: Optional[random.Random] = None) -> None:
        """Advance the simulation by one day."""
        if rng is None:
            rng = random.Random()
        self.day += 1
        self._decay_truces()
        self._check_war_declarations(rng)
        self._resolve_battles(rng)
        self._process_income()
        self._check_alliances(rng)

    # -- tick sub-phases ------------------------------------------------------
    def _decay_truces(self) -> None:
        for st in self.states.values():
            expired = []
            for other, days in st.truces.items():
                st.truces[other] = days - 1
                if st.truces[other] <= 0:
                    expired.append(other)
            for other in expired:
                del st.truces[other]
                # If this is the canonical pair, reset to neutral
                if other > st.clan_id:
                    rel = self.get_relation(st.clan_id, other)
                    if rel == RELATION_TRUCE:
                        self.set_relation(st.clan_id, other, RELATION_NEUTRAL)

    def _check_war_declarations(self, rng: random.Random) -> None:
        clans = list(self.states.keys())
        for cid in clans:
            st = self.states[cid]
            if not st.daimyo_alive or st.military <= 0:
                continue
            # Don't start too many wars
            if len(st.at_war_with) >= 2:
                continue

            borders = self.get_border_clans(cid)
            for target in borders:
                tgt_st = self.states[target]
                if target in st.allies:
                    continue
                if target in st.at_war_with:
                    continue
                if target in st.truces:
                    continue
                if tgt_st.military <= 0:
                    continue

                ratio = st.military / max(tgt_st.military, 1)
                threshold = WAR_DECLARATION_THRESHOLD / _war_tendency(cid)
                # Small random chance even below threshold if hostile
                is_hostile = target in st.enemies
                roll = rng.random()
                if ratio >= threshold and roll < 0.15:
                    self.declare_war(cid, target)
                elif is_hostile and ratio >= threshold * 0.8 and roll < 0.05:
                    self.declare_war(cid, target)

    def _resolve_battles(self, rng: random.Random) -> None:
        """Resolve one battle per active war per day."""
        processed: set[tuple[str, str]] = set()
        for cid in list(self.states.keys()):
            st = self.states[cid]
            for enemy_id in list(st.at_war_with):
                key = self._rel_key(cid, enemy_id)
                if key in processed:
                    continue
                processed.add(key)
                self._fight_battle(cid, enemy_id, rng)

    def _fight_battle(self, clan_a: str, clan_b: str, rng: random.Random) -> None:
        sa = self.states[clan_a]
        sb = self.states[clan_b]
        if sa.military <= 0 or sb.military <= 0:
            self.make_peace(clan_a, clan_b)
            return

        rf = BATTLE_RANDOM_FACTOR  # 0.3 -> range [0.7, 1.3]
        a_rand = 1.0 - rf + rng.random() * 2 * rf
        b_rand = 1.0 - rf + rng.random() * 2 * rf

        a_str = sa.military * _trait_value(clan_a, "attack_bonus") * a_rand
        b_str = (
            sb.military
            * _defense_bonus(clan_b)
            * _trait_value(clan_b, "attack_bonus")
            * b_rand
        )

        if a_str > b_str * 1.2:
            # Attacker wins — take a border province
            province = self._find_border_province(clan_a, clan_b, rng)
            if province:
                sb.provinces.remove(province)
                sa.provinces.append(province)
                self.events.append(
                    {
                        "day": self.day,
                        "type": "province_captured",
                        "attacker": clan_a,
                        "defender": clan_b,
                        "province": province,
                    }
                )
            loss_a = max(1, int(sa.military * rng.uniform(0.02, 0.05)))
            loss_b = max(1, int(sb.military * rng.uniform(0.05, 0.12)))
            sa.military = max(0, sa.military - loss_a)
            sb.military = max(0, sb.military - loss_b)
            # If defender lost all provinces, war ends
            if not sb.provinces:
                self.make_peace(clan_a, clan_b)
        elif b_str > a_str * 1.2:
            # Defender wins — attacker loses military
            loss_a = max(1, int(sa.military * rng.uniform(0.05, 0.12)))
            loss_b = max(1, int(sb.military * rng.uniform(0.02, 0.05)))
            sa.military = max(0, sa.military - loss_a)
            sb.military = max(0, sb.military - loss_b)
            self.events.append(
                {
                    "day": self.day,
                    "type": "battle_defender_wins",
                    "attacker": clan_a,
                    "defender": clan_b,
                }
            )
        else:
            # Stalemate
            loss = max(1, int(min(sa.military, sb.military) * rng.uniform(0.02, 0.05)))
            sa.military = max(0, sa.military - loss)
            sb.military = max(0, sb.military - loss)
            self.events.append(
                {
                    "day": self.day,
                    "type": "battle_stalemate",
                    "parties": sorted([clan_a, clan_b]),
                }
            )

    def _find_border_province(
        self, attacker: str, defender: str, rng: random.Random
    ) -> Optional[str]:
        """Find a defender province adjacent to attacker territory."""
        sa = self.states[attacker]
        sb = self.states[defender]
        candidates = []
        for d_prov in sb.provinces:
            for adj in PROVINCE_ADJACENCY.get(d_prov, set()):
                if adj in sa.provinces:
                    candidates.append(d_prov)
                    break
        if candidates:
            return rng.choice(candidates)
        # Fallback: any defender province (e.g. naval invasion)
        if sb.provinces:
            return rng.choice(sb.provinces)
        return None

    def _process_income(self) -> None:
        """Generate daily income from provinces and traits."""
        for cid, st in self.states.items():
            base_income = len(st.provinces) * 10
            rate = _trait_value(cid, "treasury_rate")
            st.treasury += int(base_income * rate)
            # Wartime costs
            war_cost = len(st.at_war_with) * 5
            st.treasury = max(0, st.treasury - war_cost)

    def _check_alliances(self, rng: random.Random) -> None:
        """Occasionally form or dissolve alliances."""
        clans = list(self.states.keys())
        for cid in clans:
            st = self.states[cid]
            if not st.daimyo_alive:
                continue
            # Chance to form alliance with a shared-enemy neighbour
            if rng.random() < 0.01:
                borders = self.get_border_clans(cid)
                for other in borders:
                    if other in st.allies or other in st.enemies:
                        continue
                    if other in st.at_war_with or other in st.truces:
                        continue
                    ost = self.states[other]
                    shared_enemies = st.enemies & ost.enemies
                    if shared_enemies:
                        alliance_rate = _trait_value(cid, "alliance_rate")
                        if rng.random() < 0.3 * alliance_rate:
                            self.form_alliance(cid, other)
                            break

    # -- serialisation --------------------------------------------------------
    def to_save_data(self) -> dict:
        return {
            "day": self.day,
            "states": {cid: st.to_dict() for cid, st in self.states.items()},
            "relations": {f"{a}|{b}": rel for (a, b), rel in self.relations.items()},
            "events": self.events,
        }

    @classmethod
    def from_save_data(cls, data: dict) -> "ClanSimulation":
        sim = cls.__new__(cls)
        sim.day = data["day"]
        sim.states = {
            cid: ClanState.from_dict(sd) for cid, sd in data["states"].items()
        }
        sim.relations = {}
        for key_str, rel in data["relations"].items():
            a, b = key_str.split("|")
            sim.relations[(a, b)] = rel
        sim.events = list(data["events"])
        return sim
