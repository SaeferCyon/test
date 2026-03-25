"""
traits.py - CK-style Trait Engine for ENGI
Manages trait assignment, conflicts, inheritance, and effect aggregation.
"""

from trait_data import (
    TRAITS,
    TRAIT_CONFLICTS,
    TRAIT_COMPLEMENTS,
    INHERITANCE_CHANCE,
    ENVIRONMENTAL_TRAIT_CHANCE,
    MAX_TRAITS,
    CAT_CONGENITAL,
    CAT_PERSONALITY,
)


class TraitManager:
    """Manages trait operations: assignment, conflicts, inheritance, effects."""

    def __init__(self):
        # Build conflict lookup: trait_key -> set of conflicting trait_keys
        self._conflicts = {}
        for a, b in TRAIT_CONFLICTS:
            self._conflicts.setdefault(a, set()).add(b)
            self._conflicts.setdefault(b, set()).add(a)

        # Build complement lookup: trait_key -> set of complementary trait_keys
        self._complements = {}
        for a, b in TRAIT_COMPLEMENTS:
            self._complements.setdefault(a, set()).add(b)
            self._complements.setdefault(b, set()).add(a)

    def assign_trait(self, character_traits, trait_key):
        """Add a trait if valid. Returns (success, message)."""
        if trait_key not in TRAITS:
            return False, f"Unknown trait: {trait_key}"

        if trait_key in character_traits:
            return False, f"Already has trait: {trait_key}"

        if len(character_traits) >= MAX_TRAITS:
            return False, f"At max traits ({MAX_TRAITS})"

        if self.has_conflict(character_traits, trait_key):
            conflicting = self._conflicts.get(trait_key, set())
            found = conflicting & set(character_traits)
            return False, f"Conflicts with: {', '.join(sorted(found))}"

        character_traits.append(trait_key)
        return True, f"Gained trait: {TRAITS[trait_key]['name']}"

    def remove_trait(self, character_traits, trait_key):
        """Remove a trait. Returns (success, message)."""
        if trait_key not in character_traits:
            return False, f"Does not have trait: {trait_key}"

        character_traits.remove(trait_key)
        return True, f"Lost trait: {TRAITS[trait_key]['name']}"

    def has_conflict(self, character_traits, trait_key):
        """Check if trait_key conflicts with any existing trait."""
        conflicting = self._conflicts.get(trait_key, set())
        return bool(conflicting & set(character_traits))

    def get_conflicting(self, trait_key):
        """Return the set of trait keys that conflict with trait_key."""
        return set(self._conflicts.get(trait_key, set()))

    def get_compatibility_score(self, traits_a, traits_b):
        """Score compatibility between two trait lists.

        Positive = compatible, negative = incompatible.
        +1 per shared trait, +0.5 per complement pair across lists,
        -1 per conflict pair across lists.
        """
        set_a = set(traits_a)
        set_b = set(traits_b)
        score = 0.0

        # Shared traits boost compatibility
        score += len(set_a & set_b)

        # Complement pairs across the two lists
        for a_trait in set_a:
            complements = self._complements.get(a_trait, set())
            score += 0.5 * len(complements & set_b)

        # Conflict pairs across the two lists
        for a_trait in set_a:
            conflicts = self._conflicts.get(a_trait, set())
            score -= len(conflicts & set_b)

        return score

    def inherit_traits(self, parent_a_traits, parent_b_traits, rng):
        """Generate child traits from two parents.

        Congenital traits use INHERITANCE_CHANCE per parent who has the trait.
        Personality traits use ENVIRONMENTAL_TRAIT_CHANCE per parent trait.
        Returns a list of non-conflicting inherited traits.
        """
        child_traits = []
        all_parent_traits = set(parent_a_traits) | set(parent_b_traits)

        # Pass 1: congenital inheritance
        for trait_key in list(all_parent_traits):
            trait_info = TRAITS.get(trait_key)
            if trait_info is None:
                continue
            if trait_info["category"] != CAT_CONGENITAL:
                continue

            chance = INHERITANCE_CHANCE.get(trait_key, 0.0)
            # Both parents having trait increases chance
            parent_count = (1 if trait_key in parent_a_traits else 0) + (
                1 if trait_key in parent_b_traits else 0
            )
            effective_chance = 1.0 - (1.0 - chance) ** parent_count

            if rng.random() < effective_chance:
                ok, _ = self.assign_trait(child_traits, trait_key)
                if not ok:
                    continue

        # Pass 2: environmental / personality influence
        for trait_key in list(all_parent_traits):
            trait_info = TRAITS.get(trait_key)
            if trait_info is None:
                continue
            if trait_info["category"] == CAT_CONGENITAL:
                continue  # already handled

            parent_count = (1 if trait_key in parent_a_traits else 0) + (
                1 if trait_key in parent_b_traits else 0
            )
            effective_chance = 1.0 - (1.0 - ENVIRONMENTAL_TRAIT_CHANCE) ** parent_count

            if rng.random() < effective_chance:
                ok, _ = self.assign_trait(child_traits, trait_key)
                if not ok:
                    continue

        return child_traits

    def random_traits(self, count, rng, category_filter=None):
        """Pick random non-conflicting traits.

        Args:
            count: number of traits to pick
            rng: random.Random instance
            category_filter: optional category string to restrict selection
        """
        pool = list(TRAITS.keys())
        if category_filter is not None:
            pool = [k for k in pool if TRAITS[k]["category"] == category_filter]

        rng.shuffle(pool)
        picked = []
        for trait_key in pool:
            if len(picked) >= count:
                break
            if not self.has_conflict(picked, trait_key):
                picked.append(trait_key)

        return picked

    def get_trait_effects(self, character_traits):
        """Aggregate all effects from a trait list.

        Floats are multiplied together, bools are OR'd.
        """
        combined = {}
        for trait_key in character_traits:
            trait_info = TRAITS.get(trait_key)
            if trait_info is None:
                continue
            for effect_key, value in trait_info["effects"].items():
                if isinstance(value, bool):
                    combined[effect_key] = combined.get(effect_key, False) or value
                elif isinstance(value, (int, float)):
                    combined[effect_key] = combined.get(effect_key, 1.0) * value
                else:
                    combined[effect_key] = value
        return combined

    def discover_trait(self, trait_key):
        """Return trait data if it was hidden, marking it visible.

        Returns the trait dict (with hidden set to False) or None if
        the trait doesn't exist or wasn't hidden.
        """
        trait_info = TRAITS.get(trait_key)
        if trait_info is None:
            return None
        if not trait_info["hidden"]:
            return None

        trait_info["hidden"] = False
        return dict(trait_info)


# ─────────────────────────────────────────────────────────────
# Module-level helpers
# ─────────────────────────────────────────────────────────────


def get_trait(key):
    """Return trait dict or None."""
    return TRAITS.get(key)


def is_hidden(key):
    """Return whether a trait is hidden."""
    trait = TRAITS.get(key)
    if trait is None:
        return False
    return trait["hidden"]


def get_category_traits(category):
    """Return list of trait keys in the given category."""
    return [k for k, v in TRAITS.items() if v["category"] == category]
