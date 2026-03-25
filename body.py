"""
body.py - BodyMap class for realistic body zone system.
Manages injuries, healing, treatments, hit locations, and combat modifiers.
"""

import random as _random_module

from body_data import (
    BODY_ZONES,
    INJURY_TYPES,
    PERMANENT_EFFECTS,
    HIT_TABLE_NORMAL,
    INTERNAL_HIT_CHANCE,
    TREATMENTS,
    INJ_SEVERED,
    INJ_DEEP_WOUND,
    INJ_FRACTURE,
    INJ_CRUSHED,
    INJ_INFECTED,
)


class Injury:
    """A single injury on a body zone."""

    __slots__ = (
        "zone",
        "injury_type",
        "severity",
        "days_remaining",
        "treated",
        "infected",
    )

    def __init__(
        self, zone, injury_type, severity, days_remaining, treated=False, infected=False
    ):
        self.zone = zone
        self.injury_type = injury_type
        self.severity = severity
        self.days_remaining = days_remaining
        self.treated = treated
        self.infected = infected

    def __repr__(self):
        return (
            f"Injury({self.zone!r}, {self.injury_type!r}, "
            f"sev={self.severity}, days={self.days_remaining})"
        )


def _weighted_choice(table, rng=None):
    """Pick a zone from a weighted table using the given RNG."""
    rng = rng or _random_module
    zones, weights = zip(*table)
    total = sum(weights)
    roll = rng.random() * total
    cumulative = 0
    for zone, weight in zip(zones, weights):
        cumulative += weight
        if roll < cumulative:
            return zone
    return zones[-1]


def roll_hit_location(rng=None):
    """Return a random zone key from HIT_TABLE_NORMAL."""
    return _weighted_choice(HIT_TABLE_NORMAL, rng)


def injury_to_trait(zone, injury_type):
    """Return permanent trait key or None from PERMANENT_EFFECTS."""
    effect = PERMANENT_EFFECTS.get((zone, injury_type))
    if effect is not None:
        return effect.get("trait")
    return None


class BodyMap:
    """Tracks all injuries on a character's body."""

    def __init__(self):
        self.injuries = []
        self.severed_zones = set()

    # ------------------------------------------------------------------
    # Injury application
    # ------------------------------------------------------------------

    def apply_injury(self, zone, injury_type, rng=None):
        """Apply an injury to a zone.

        Returns (Injury, list_of_messages).
        """
        rng = rng or _random_module
        messages = []
        itype = INJURY_TYPES.get(injury_type)
        if itype is None:
            return None, [f"Unknown injury type: {injury_type}"]

        zone_data = BODY_ZONES.get(zone)
        if zone_data is None:
            return None, [f"Unknown zone: {zone}"]

        # If zone already severed, nothing more to damage
        if zone in self.severed_zones:
            messages.append(f"{zone_data['name']} is already severed.")
            return None, messages

        severity = itype["severity"]
        days = itype["heal_days"]

        inj = Injury(
            zone=zone,
            injury_type=injury_type,
            severity=severity,
            days_remaining=days,
        )
        self.injuries.append(inj)

        zone_name = zone_data["name"]
        inj_name = itype["name"]
        messages.append(f"{inj_name} to {zone_name}.")

        # Handle severed
        if injury_type == INJ_SEVERED:
            if zone_data.get("sever"):
                self.severed_zones.add(zone)
                messages.append(f"{zone_name} has been severed!")
            else:
                messages.append(f"{zone_name} cannot be severed.")

        # Permanent effects
        effect = PERMANENT_EFFECTS.get((zone, injury_type))
        if effect is not None:
            messages.append(f"Permanent effect: {effect['desc']}")

        # Internal organ damage for deep torso wounds
        if injury_type == INJ_DEEP_WOUND and zone in INTERNAL_HIT_CHANCE:
            for organ_zone, chance in INTERNAL_HIT_CHANCE[zone]:
                if rng.random() < chance:
                    organ_inj, organ_msgs = self.apply_injury(
                        organ_zone, INJ_DEEP_WOUND, rng
                    )
                    messages.extend(organ_msgs)

        return inj, messages

    # ------------------------------------------------------------------
    # Query methods
    # ------------------------------------------------------------------

    def get_zone_injuries(self, zone):
        """Return list of Injury objects at the given zone."""
        return [i for i in self.injuries if i.zone == zone]

    def get_all_injuries(self):
        """Return list of all active injuries."""
        return list(self.injuries)

    def is_zone_functional(self, zone):
        """False if severed or has an immobilizing injury."""
        if zone in self.severed_zones:
            return False
        for inj in self.injuries:
            if inj.zone == zone and inj.injury_type in (
                INJ_FRACTURE,
                INJ_CRUSHED,
                INJ_SEVERED,
            ):
                return False
        return True

    # ------------------------------------------------------------------
    # Healing
    # ------------------------------------------------------------------

    def tick_healing(self, rng=None):
        """Advance one day of healing. Returns list of messages."""
        rng = rng or _random_module
        messages = []
        healed = []

        for inj in self.injuries:
            # Permanent injuries don't heal
            if inj.days_remaining < 0:
                continue

            # Infection check on untreated wounds
            if not inj.treated and not inj.infected:
                itype = INJURY_TYPES.get(inj.injury_type)
                if itype and rng.random() < itype["infection_chance"]:
                    inj.infected = True
                    zone_data = BODY_ZONES.get(inj.zone, {})
                    messages.append(
                        f"{zone_data.get('name', inj.zone)} "
                        f"{itype['name']} has become infected!"
                    )

            # Infected wounds don't heal and get worse
            if inj.infected:
                inj.days_remaining += 1
                continue

            # Advance healing
            inj.days_remaining -= 1
            if inj.days_remaining <= 0:
                zone_data = BODY_ZONES.get(inj.zone, {})
                itype = INJURY_TYPES.get(inj.injury_type, {})
                messages.append(
                    f"{zone_data.get('name', inj.zone)} "
                    f"{itype.get('name', inj.injury_type)} has healed."
                )
                healed.append(inj)

        for inj in healed:
            self.injuries.remove(inj)

        return messages

    # ------------------------------------------------------------------
    # Treatment
    # ------------------------------------------------------------------

    def apply_treatment(self, injury, treatment_type, skill_level):
        """Attempt to treat an injury.

        Returns (success: bool, messages: list).
        """
        messages = []
        treatment = TREATMENTS.get(treatment_type)
        if treatment is None:
            return False, [f"Unknown treatment: {treatment_type}"]

        if skill_level < treatment["min_skill"]:
            messages.append(
                f"Skill too low for {treatment['name']} "
                f"(need {treatment['min_skill']}, have {skill_level})."
            )
            return False, messages

        if injury.injury_type not in treatment["treats"]:
            messages.append(
                f"{treatment['name']} cannot treat "
                f"{INJURY_TYPES.get(injury.injury_type, {}).get('name', injury.injury_type)}."
            )
            return False, messages

        # Apply treatment
        injury.treated = True

        # Heal bonus reduces remaining days
        if injury.days_remaining > 0 and treatment["heal_bonus"] > 0:
            injury.days_remaining = max(
                1, int(injury.days_remaining / treatment["heal_bonus"])
            )

        # Clear infection
        if injury.infected and injury.injury_type in treatment["treats"]:
            injury.infected = False
            messages.append("Infection cleared.")

        zone_data = BODY_ZONES.get(injury.zone, {})
        messages.append(
            f"{treatment['name']} applied to {zone_data.get('name', injury.zone)}."
        )
        return True, messages

    # ------------------------------------------------------------------
    # Hit location
    # ------------------------------------------------------------------

    def get_hit_zone(self, rng=None, aimed_region=None):
        """Get a hit zone via weighted random, or aimed region."""
        rng = rng or _random_module

        if aimed_region is not None:
            # Filter hit table to zones in the aimed region
            region_table = [
                (z, w)
                for z, w in HIT_TABLE_NORMAL
                if BODY_ZONES.get(z, {}).get("region") == aimed_region
            ]
            if region_table:
                return _weighted_choice(region_table, rng)

        return _weighted_choice(HIT_TABLE_NORMAL, rng)

    # ------------------------------------------------------------------
    # Combat modifiers
    # ------------------------------------------------------------------

    def get_combat_modifiers(self):
        """Return dict of combat penalty modifiers from injuries."""
        mods = {
            "attack_mod": 0,
            "defense_mod": 0,
            "move_mod": 0,
            "accuracy_mod": 0,
        }

        for inj in self.injuries:
            zone_data = BODY_ZONES.get(inj.zone, {})
            region = zone_data.get("region", "")
            severity = inj.severity

            # Pain penalty applies to everything
            pain = INJURY_TYPES.get(inj.injury_type, {}).get("pain", 0)
            mods["defense_mod"] -= pain

            # Arm injuries affect attack
            if region in ("left_arm", "right_arm"):
                mods["attack_mod"] -= severity

            # Leg injuries affect movement
            if region in ("left_leg", "right_leg"):
                mods["move_mod"] -= severity

            # Eye/head injuries affect accuracy
            if region == "head":
                mods["accuracy_mod"] -= severity

            # Severed zones compound
            if inj.zone in self.severed_zones:
                if region in ("left_arm", "right_arm"):
                    mods["attack_mod"] -= 5
                if region in ("left_leg", "right_leg"):
                    mods["move_mod"] -= 5

        return mods

    # ------------------------------------------------------------------
    # Status summary
    # ------------------------------------------------------------------

    def get_status_summary(self):
        """Return human-readable list of injury descriptions."""
        lines = []

        for inj in self.injuries:
            zone_data = BODY_ZONES.get(inj.zone, {})
            itype = INJURY_TYPES.get(inj.injury_type, {})
            zone_name = zone_data.get("name", inj.zone)
            inj_name = itype.get("name", inj.injury_type)

            parts = [f"{zone_name}: {inj_name} (severity {inj.severity})"]
            if inj.infected:
                parts.append("INFECTED")
            if inj.treated:
                parts.append("treated")
            if inj.days_remaining < 0:
                parts.append("permanent")
            else:
                parts.append(f"{inj.days_remaining}d remaining")

            lines.append(" - ".join(parts))

        for zone in sorted(self.severed_zones):
            zone_data = BODY_ZONES.get(zone, {})
            zone_name = zone_data.get("name", zone)
            if not any(i.zone == zone for i in self.injuries):
                lines.append(f"{zone_name}: SEVERED")

        return lines
