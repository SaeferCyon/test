"""
life_sim.py - Dynasty Simulation for ENGI
Aging, marriage, children, death, heir selection, and disease.
"""

from body_data import DISEASES


# ─────────────────────────────────────────────────────────────
# FAMILY MEMBER
# ─────────────────────────────────────────────────────────────
class FamilyMember:
    """A single member of a dynasty family tree."""

    __slots__ = (
        "char_id",
        "name",
        "birth_turn",
        "death_turn",
        "age",
        "gender",
        "traits",
        "parent_a_id",
        "parent_b_id",
        "spouse_id",
        "children_ids",
    )

    def __init__(
        self,
        char_id,
        name,
        birth_turn=0,
        death_turn=-1,
        age=0,
        gender="male",
        traits=None,
        parent_a_id=None,
        parent_b_id=None,
        spouse_id=None,
        children_ids=None,
    ):
        self.char_id = char_id
        self.name = name
        self.birth_turn = birth_turn
        self.death_turn = death_turn
        self.age = age
        self.gender = gender
        self.traits = traits if traits is not None else []
        self.parent_a_id = parent_a_id
        self.parent_b_id = parent_b_id
        self.spouse_id = spouse_id
        self.children_ids = children_ids if children_ids is not None else []

    def is_alive(self):
        """Return True if character has not died."""
        return self.death_turn == -1

    def to_dict(self):
        """Serialize to a plain dict."""
        return {
            "char_id": self.char_id,
            "name": self.name,
            "birth_turn": self.birth_turn,
            "death_turn": self.death_turn,
            "age": self.age,
            "gender": self.gender,
            "traits": list(self.traits),
            "parent_a_id": self.parent_a_id,
            "parent_b_id": self.parent_b_id,
            "spouse_id": self.spouse_id,
            "children_ids": list(self.children_ids),
        }

    @classmethod
    def from_dict(cls, data):
        """Restore from a plain dict."""
        return cls(
            char_id=data["char_id"],
            name=data["name"],
            birth_turn=data.get("birth_turn", 0),
            death_turn=data.get("death_turn", -1),
            age=data.get("age", 0),
            gender=data.get("gender", "male"),
            traits=data.get("traits", []),
            parent_a_id=data.get("parent_a_id"),
            parent_b_id=data.get("parent_b_id"),
            spouse_id=data.get("spouse_id"),
            children_ids=data.get("children_ids", []),
        )


# ─────────────────────────────────────────────────────────────
# AGE BRACKET CONSTANTS
# ─────────────────────────────────────────────────────────────
_AGE_BRACKETS = [
    # (min_age, max_age, label, stat_modifiers)
    (
        0,
        15,
        "child",
        {
            "strength": 0.4,
            "stamina": 0.5,
            "combat": 0.0,
            "speed": 0.6,
            "charisma": 0.7,
        },
    ),
    (
        16,
        19,
        "young_adult",
        {
            "strength": 0.8,
            "stamina": 0.85,
            "combat": 0.7,
            "speed": 0.9,
            "charisma": 0.9,
        },
    ),
    (
        20,
        39,
        "prime",
        {
            "strength": 1.0,
            "stamina": 1.0,
            "combat": 1.0,
            "speed": 1.0,
            "charisma": 1.0,
        },
    ),
    (
        40,
        49,
        "middle_age",
        {
            "strength": 0.95,
            "stamina": 0.85,
            "combat": 0.95,
            "speed": 0.9,
            "charisma": 1.0,
        },
    ),
    (
        50,
        59,
        "old",
        {
            "strength": 0.75,
            "stamina": 0.65,
            "combat": 0.7,
            "speed": 0.7,
            "charisma": 0.9,
        },
    ),
    (
        60,
        999,
        "elderly",
        {
            "strength": 0.5,
            "stamina": 0.4,
            "combat": 0.4,
            "speed": 0.5,
            "charisma": 0.8,
        },
    ),
]

# Minimum marriage age
_MIN_MARRIAGE_AGE = 16


# ─────────────────────────────────────────────────────────────
# LIFE SIMULATION
# ─────────────────────────────────────────────────────────────
class LifeSimulation:
    """Manages dynasty lifecycle: aging, marriage, children, death, heirs."""

    def __init__(self, trait_manager=None, relationship_manager=None):
        self._trait_manager = trait_manager
        self._relationship_manager = relationship_manager
        self._family_tree = {}  # char_id -> FamilyMember
        self._diseases = {}  # char_id -> list of {disease_key, remaining_days}

    # ── Registration ─────────────────────────────────────────

    def register_character(
        self,
        char_id,
        name,
        age,
        gender,
        traits,
        parent_a=None,
        parent_b=None,
    ):
        """Register a character in the family tree.

        Returns the created FamilyMember.
        """
        fm = FamilyMember(
            char_id=char_id,
            name=name,
            age=age,
            gender=gender,
            traits=list(traits),
            parent_a_id=parent_a,
            parent_b_id=parent_b,
        )
        self._family_tree[char_id] = fm
        self._diseases.setdefault(char_id, [])
        return fm

    # ── Aging ────────────────────────────────────────────────

    def tick_aging(self, char_id, turns_per_year):
        """Age a character by one turn.

        Returns a list of event messages.
        """
        messages = []
        fm = self._family_tree.get(char_id)
        if fm is None or not fm.is_alive():
            return messages

        old_age = fm.age
        # Fractional year tracking: increment age when enough turns pass
        fm.birth_turn += 1
        if fm.birth_turn % turns_per_year == 0:
            fm.age += 1
            messages.append(f"{fm.name} is now {fm.age} years old.")

            # Check for old-age death
            if fm.age >= 60:
                # Increasing death chance: 5% base + 3% per year over 60
                death_chance = 0.05 + 0.03 * (fm.age - 60)
                messages.append(
                    f"{fm.name} faces mortality (age {fm.age}, "
                    f"chance {death_chance:.0%})."
                )

            # Age bracket transition
            old_bracket = self._get_age_bracket(old_age)
            new_bracket = self._get_age_bracket(fm.age)
            if old_bracket != new_bracket:
                messages.append(f"{fm.name} enters {new_bracket} stage.")

        return messages

    def _get_age_bracket(self, age):
        """Return the bracket label for an age."""
        for min_age, max_age, label, _ in _AGE_BRACKETS:
            if min_age <= age <= max_age:
                return label
        return "elderly"

    def get_age_stat_modifiers(self, age):
        """Return stat modifier dict for a given age.

        Modifiers are multipliers: 1.0 = full, 0.5 = halved.
        """
        for min_age, max_age, _label, mods in _AGE_BRACKETS:
            if min_age <= age <= max_age:
                return dict(mods)
        # Default to elderly for very old characters
        return dict(_AGE_BRACKETS[-1][3])

    # ── Marriage ─────────────────────────────────────────────

    def can_marry(self, id_a, id_b):
        """Check whether two characters can marry.

        Returns (bool, reason_string).
        """
        fm_a = self._family_tree.get(id_a)
        fm_b = self._family_tree.get(id_b)

        if fm_a is None or fm_b is None:
            return False, "Character not found."

        if not fm_a.is_alive() or not fm_b.is_alive():
            return False, "One or both characters are dead."

        if fm_a.age < _MIN_MARRIAGE_AGE or fm_b.age < _MIN_MARRIAGE_AGE:
            return False, "Both characters must be at least 16."

        if fm_a.spouse_id is not None:
            return False, f"{fm_a.name} is already married."
        if fm_b.spouse_id is not None:
            return False, f"{fm_b.name} is already married."

        # Family check: cannot marry parent, child, or sibling
        if self._are_close_family(id_a, id_b):
            return False, "Cannot marry close family members."

        # Relationship score check
        if self._relationship_manager is not None:
            score = self._relationship_manager.get_score(id_a, id_b)
            if score <= 50:
                return False, (f"Relationship score too low ({score}). Need > 50.")

        return True, "Can marry."

    def _are_close_family(self, id_a, id_b):
        """Check if two characters are parent/child or siblings."""
        fm_a = self._family_tree.get(id_a)
        fm_b = self._family_tree.get(id_b)
        if fm_a is None or fm_b is None:
            return False

        # Parent-child
        if fm_a.parent_a_id == id_b or fm_a.parent_b_id == id_b:
            return True
        if fm_b.parent_a_id == id_a or fm_b.parent_b_id == id_a:
            return True

        # Siblings (share at least one parent)
        a_parents = {p for p in (fm_a.parent_a_id, fm_a.parent_b_id) if p is not None}
        b_parents = {p for p in (fm_b.parent_a_id, fm_b.parent_b_id) if p is not None}
        if a_parents and b_parents and a_parents & b_parents:
            return True

        return False

    def marry(self, id_a, id_b):
        """Marry two characters.

        Returns a list of event messages.
        """
        messages = []
        fm_a = self._family_tree[id_a]
        fm_b = self._family_tree[id_b]

        fm_a.spouse_id = id_b
        fm_b.spouse_id = id_a

        messages.append(f"{fm_a.name} and {fm_b.name} are now married.")

        # Update relationship manager
        if self._relationship_manager is not None:
            self._relationship_manager.modify_score(id_a, id_b, 20, reason="marriage")
            self._relationship_manager.set_family(id_a, id_b, "spouse")

        return messages

    # ── Children ─────────────────────────────────────────────

    def can_have_child(self, parent_a_id, parent_b_id):
        """Check whether two characters can have a child.

        Returns (bool, reason_string).
        """
        fm_a = self._family_tree.get(parent_a_id)
        fm_b = self._family_tree.get(parent_b_id)

        if fm_a is None or fm_b is None:
            return False, "Parent not found."

        if not fm_a.is_alive() or not fm_b.is_alive():
            return False, "One or both parents are dead."

        if fm_a.spouse_id != parent_b_id:
            return False, "Parents must be married."

        return True, "Can have child."

    def birth_child(
        self,
        parent_a_id,
        parent_b_id,
        child_name,
        child_gender,
        rng,
    ):
        """Create a child from two parents.

        Inherits traits via TraitManager. Registers the child in the
        family tree and sets family relationships.

        Returns the new FamilyMember.
        """
        fm_a = self._family_tree[parent_a_id]
        fm_b = self._family_tree[parent_b_id]

        # Generate child ID
        child_id = f"child_{parent_a_id}_{parent_b_id}_{child_name.lower()}"

        # Inherit traits
        child_traits = []
        if self._trait_manager is not None:
            child_traits = self._trait_manager.inherit_traits(
                fm_a.traits, fm_b.traits, rng
            )

        # Register child
        child = self.register_character(
            char_id=child_id,
            name=child_name,
            age=0,
            gender=child_gender,
            traits=child_traits,
            parent_a=parent_a_id,
            parent_b=parent_b_id,
        )

        # Update parent records
        fm_a.children_ids.append(child_id)
        fm_b.children_ids.append(child_id)

        # Set family relationships
        if self._relationship_manager is not None:
            self._relationship_manager.set_family(parent_a_id, child_id, "parent_child")
            self._relationship_manager.set_family(parent_b_id, child_id, "parent_child")
            # Sibling relationships
            for sib_id in fm_a.children_ids:
                if sib_id != child_id:
                    self._relationship_manager.set_family(child_id, sib_id, "sibling")

        return child

    # ── Death ────────────────────────────────────────────────

    def kill_character(self, char_id, cause):
        """Mark a character as dead.

        Returns a list of event messages.
        """
        messages = []
        fm = self._family_tree.get(char_id)
        if fm is None or not fm.is_alive():
            return messages

        fm.death_turn = fm.birth_turn
        messages.append(f"{fm.name} has died. Cause: {cause}.")

        # Notify spouse
        if fm.spouse_id is not None:
            spouse = self._family_tree.get(fm.spouse_id)
            if spouse is not None and spouse.is_alive():
                messages.append(f"{spouse.name} mourns the death of {fm.name}.")
                spouse.spouse_id = None  # widowed
                if self._relationship_manager is not None:
                    self._relationship_manager.modify_score(
                        fm.spouse_id, char_id, -30, reason="death_of_spouse"
                    )

        # Notify children
        for child_id in fm.children_ids:
            child = self._family_tree.get(child_id)
            if child is not None and child.is_alive():
                messages.append(f"{child.name} mourns the death of parent {fm.name}.")

        return messages

    # ── Heir Selection ───────────────────────────────────────

    def get_heir(self, char_id):
        """Find the best heir for a character.

        Priority: oldest living child, then sibling, then spouse.
        Returns char_id of heir or None.
        """
        fm = self._family_tree.get(char_id)
        if fm is None:
            return None

        # 1. Oldest living child
        living_children = []
        for cid in fm.children_ids:
            child = self._family_tree.get(cid)
            if child is not None and child.is_alive():
                living_children.append(child)

        if living_children:
            living_children.sort(key=lambda c: c.age, reverse=True)
            return living_children[0].char_id

        # 2. Sibling (shares a parent)
        siblings = self._get_siblings(char_id)
        living_siblings = [
            s
            for s in siblings
            if self._family_tree.get(s) is not None and self._family_tree[s].is_alive()
        ]
        if living_siblings:
            living_siblings.sort(key=lambda s: self._family_tree[s].age, reverse=True)
            return living_siblings[0]

        # 3. Spouse
        if fm.spouse_id is not None:
            spouse = self._family_tree.get(fm.spouse_id)
            if spouse is not None and spouse.is_alive():
                return fm.spouse_id

        return None

    def _get_siblings(self, char_id):
        """Return list of sibling char_ids (share at least one parent)."""
        fm = self._family_tree.get(char_id)
        if fm is None:
            return []

        siblings = set()
        for parent_id in (fm.parent_a_id, fm.parent_b_id):
            if parent_id is None:
                continue
            parent = self._family_tree.get(parent_id)
            if parent is None:
                continue
            for cid in parent.children_ids:
                if cid != char_id:
                    siblings.add(cid)

        return list(siblings)

    # ── Family Tree Display ──────────────────────────────────

    def get_family_tree(self, char_id):
        """Return a dict tree structure for display.

        Keys: character info, parents, spouse, children.
        """
        fm = self._family_tree.get(char_id)
        if fm is None:
            return {}

        tree = {
            "char_id": fm.char_id,
            "name": fm.name,
            "age": fm.age,
            "gender": fm.gender,
            "alive": fm.is_alive(),
            "traits": list(fm.traits),
            "parents": [],
            "spouse": None,
            "children": [],
        }

        # Parents
        for pid in (fm.parent_a_id, fm.parent_b_id):
            if pid is not None:
                parent = self._family_tree.get(pid)
                if parent is not None:
                    tree["parents"].append(
                        {
                            "char_id": parent.char_id,
                            "name": parent.name,
                            "alive": parent.is_alive(),
                        }
                    )

        # Spouse
        if fm.spouse_id is not None:
            spouse = self._family_tree.get(fm.spouse_id)
            if spouse is not None:
                tree["spouse"] = {
                    "char_id": spouse.char_id,
                    "name": spouse.name,
                    "alive": spouse.is_alive(),
                }

        # Children
        for cid in fm.children_ids:
            child = self._family_tree.get(cid)
            if child is not None:
                tree["children"].append(
                    {
                        "char_id": child.char_id,
                        "name": child.name,
                        "age": child.age,
                        "alive": child.is_alive(),
                    }
                )

        return tree

    # ── Disease System ───────────────────────────────────────

    def contract_disease(self, char_id, disease_key, rng):
        """Attempt to contract a disease.

        Chance based on disease contagion stat.
        Returns (bool_contracted, list_of_messages).
        """
        messages = []
        fm = self._family_tree.get(char_id)
        if fm is None or not fm.is_alive():
            return False, messages

        disease = DISEASES.get(disease_key)
        if disease is None:
            return False, [f"Unknown disease: {disease_key}"]

        # Check if already has this disease
        active = self._diseases.get(char_id, [])
        for d in active:
            if d["disease_key"] == disease_key:
                return False, [f"{fm.name} already has {disease['name']}."]

        # Roll contagion chance
        contagion = disease["contagion"]
        if rng.random() >= contagion:
            return False, []

        # Contract the disease
        active.append(
            {
                "disease_key": disease_key,
                "remaining_days": disease["duration_days"],
            }
        )
        self._diseases[char_id] = active
        messages.append(f"{fm.name} has contracted {disease['name']}!")

        return True, messages

    def tick_diseases(self, rng):
        """Progress all active diseases by one day.

        Checks for recovery and mortality.
        Returns a list of event messages.
        """
        messages = []

        for char_id in list(self._diseases.keys()):
            fm = self._family_tree.get(char_id)
            if fm is None or not fm.is_alive():
                continue

            active = self._diseases.get(char_id, [])
            remaining = []

            for entry in active:
                disease_key = entry["disease_key"]
                disease = DISEASES.get(disease_key)
                if disease is None:
                    continue

                entry["remaining_days"] -= 1

                if entry["remaining_days"] <= 0:
                    # Disease runs its course — recovery
                    messages.append(f"{fm.name} has recovered from {disease['name']}.")
                    continue

                # Daily mortality check
                daily_mortality = disease["mortality"] / max(
                    disease["duration_days"], 1
                )
                if rng.random() < daily_mortality:
                    death_msgs = self.kill_character(char_id, cause=disease["name"])
                    messages.extend(death_msgs)
                    remaining = []
                    break

                remaining.append(entry)

            self._diseases[char_id] = remaining

        return messages

    # ── Serialization ────────────────────────────────────────

    def to_save_data(self):
        """Serialize the entire life simulation state."""
        tree_data = {}
        for cid, fm in self._family_tree.items():
            tree_data[cid] = fm.to_dict()

        disease_data = {}
        for cid, diseases in self._diseases.items():
            disease_data[cid] = [dict(d) for d in diseases]

        return {
            "family_tree": tree_data,
            "diseases": disease_data,
        }

    @classmethod
    def from_save_data(
        cls,
        data,
        trait_manager=None,
        relationship_manager=None,
    ):
        """Restore a LifeSimulation from serialized data."""
        sim = cls(
            trait_manager=trait_manager,
            relationship_manager=relationship_manager,
        )

        for cid, fm_data in data.get("family_tree", {}).items():
            sim._family_tree[cid] = FamilyMember.from_dict(fm_data)

        for cid, disease_list in data.get("diseases", {}).items():
            sim._diseases[cid] = [dict(d) for d in disease_list]

        return sim
