"""
trait_data.py - CK-inspired Trait System Data for ENGI
50+ traits across 5 categories with conflict/complement matrices.
"""

# ─────────────────────────────────────────────────────────────
# TRAIT CATEGORIES
# ─────────────────────────────────────────────────────────────
CAT_PERSONALITY = "personality"
CAT_EDUCATION = "education"
CAT_LIFESTYLE = "lifestyle"
CAT_CONGENITAL = "congenital"
CAT_PHYSICAL = "physical"

TRAIT_CATEGORIES = {
    CAT_PERSONALITY: {
        "name": "Personality",
        "desc": "Core character traits that define behavior.",
    },
    CAT_EDUCATION: {
        "name": "Education",
        "desc": "Learned skills and intellectual traits.",
    },
    CAT_LIFESTYLE: {"name": "Lifestyle", "desc": "Habits and way of living."},
    CAT_CONGENITAL: {
        "name": "Congenital",
        "desc": "Inborn traits, inherited from parents.",
    },
    CAT_PHYSICAL: {"name": "Physical", "desc": "Body and appearance traits."},
}

# ─────────────────────────────────────────────────────────────
# TRAIT DEFINITIONS
# Each trait has:
#   name: display name
#   category: one of the categories above
#   hidden: if True, not visible until discovered
#   inheritable: if True, can pass to children (congenital always True)
#   effects: dict of stat modifiers and special flags
#   desc: flavor text
# ─────────────────────────────────────────────────────────────
TRAITS = {
    # ── PERSONALITY (20 traits) ───────────────────────────
    "brave": {
        "name": "Brave",
        "category": CAT_PERSONALITY,
        "hidden": False,
        "inheritable": False,
        "effects": {
            "morale_bonus": 1.2,
            "intimidate_resist": 1.3,
            "flee_penalty": True,
        },
        "desc": "Faces danger without flinching. Others take heart from your courage.",
    },
    "cowardly": {
        "name": "Cowardly",
        "category": CAT_PERSONALITY,
        "hidden": False,
        "inheritable": False,
        "effects": {"morale_bonus": 0.7, "flee_bonus": 1.3, "intimidate_resist": 0.5},
        "desc": "Fear rules the heart. Quick to run, slow to fight.",
    },
    "honest": {
        "name": "Honest",
        "category": CAT_PERSONALITY,
        "hidden": False,
        "inheritable": False,
        "effects": {"trust_bonus": 1.3, "bribe_resist": 1.5, "deception_penalty": True},
        "desc": "Speaks truth even when it hurts. Trusted but predictable.",
    },
    "deceitful": {
        "name": "Deceitful",
        "category": CAT_PERSONALITY,
        "hidden": True,
        "inheritable": False,
        "effects": {"deception_bonus": 1.5, "trust_bonus": 0.5, "bribe_bonus": 1.2},
        "desc": "Lies flow like water. Never trust the smile.",
    },
    "compassionate": {
        "name": "Compassionate",
        "category": CAT_PERSONALITY,
        "hidden": False,
        "inheritable": False,
        "effects": {
            "relationship_gain": 1.3,
            "honor_gain": 1.2,
            "cruelty_penalty": True,
        },
        "desc": "Feels the suffering of others. Cannot ignore those in need.",
    },
    "cruel": {
        "name": "Cruel",
        "category": CAT_PERSONALITY,
        "hidden": True,
        "inheritable": False,
        "effects": {
            "intimidate_bonus": 1.5,
            "morale_drain": 1.3,
            "relationship_gain": 0.6,
        },
        "desc": "Takes pleasure in the pain of others. Feared, not loved.",
    },
    "patient": {
        "name": "Patient",
        "category": CAT_PERSONALITY,
        "hidden": False,
        "inheritable": False,
        "effects": {"skill_xp_bonus": 1.2, "ambush_bonus": 1.2, "crafting_bonus": 1.2},
        "desc": "Waits for the right moment. Mastery comes to those who endure.",
    },
    "impulsive": {
        "name": "Impulsive",
        "category": CAT_PERSONALITY,
        "hidden": False,
        "inheritable": False,
        "effects": {
            "initiative_bonus": 1.3,
            "skill_xp_bonus": 0.8,
            "surprise_resist": 1.2,
        },
        "desc": "Acts first, thinks later. Sometimes that's exactly right.",
    },
    "ambitious": {
        "name": "Ambitious",
        "category": CAT_PERSONALITY,
        "hidden": False,
        "inheritable": False,
        "effects": {"social_climb_bonus": 1.5, "rivalry_tendency": 1.3},
        "desc": "Hungry for power and status. Will not be content with less.",
    },
    "content": {
        "name": "Content",
        "category": CAT_PERSONALITY,
        "hidden": False,
        "inheritable": False,
        "effects": {
            "morale_bonus": 1.2,
            "stress_resist": 1.3,
            "social_climb_bonus": 0.5,
        },
        "desc": "At peace with what is. The bamboo bends but does not break.",
    },
    "gregarious": {
        "name": "Gregarious",
        "category": CAT_PERSONALITY,
        "hidden": False,
        "inheritable": False,
        "effects": {
            "relationship_gain": 1.4,
            "gossip_range": 1.5,
            "loneliness_resist": 1.3,
        },
        "desc": "Draws people in. Never met a stranger.",
    },
    "shy": {
        "name": "Shy",
        "category": CAT_PERSONALITY,
        "hidden": False,
        "inheritable": False,
        "effects": {
            "relationship_gain": 0.7,
            "stealth_bonus": 1.2,
            "observation_bonus": 1.2,
        },
        "desc": "Shrinks from attention. Sees much, says little.",
    },
    "wrathful": {
        "name": "Wrathful",
        "category": CAT_PERSONALITY,
        "hidden": False,
        "inheritable": False,
        "effects": {
            "attack_bonus": 1.2,
            "relationship_loss": 1.3,
            "feud_tendency": 1.5,
        },
        "desc": "Anger burns hot and long. Grudges last forever.",
    },
    "calm": {
        "name": "Calm",
        "category": CAT_PERSONALITY,
        "hidden": False,
        "inheritable": False,
        "effects": {"stress_resist": 1.4, "debate_bonus": 1.2, "feud_tendency": 0.5},
        "desc": "Still waters. Nothing rattles the composed mind.",
    },
    "proud": {
        "name": "Proud",
        "category": CAT_PERSONALITY,
        "hidden": False,
        "inheritable": False,
        "effects": {
            "honor_sensitivity": 1.5,
            "coercion_resist": 1.3,
            "apology_penalty": True,
        },
        "desc": "Will not bend the knee. Honor above all.",
    },
    "humble": {
        "name": "Humble",
        "category": CAT_PERSONALITY,
        "hidden": False,
        "inheritable": False,
        "effects": {
            "relationship_gain": 1.2,
            "clergy_bonus": 1.3,
            "leadership_penalty": 0.8,
        },
        "desc": "Knows their place. The kami favor the modest.",
    },
    "loyal": {
        "name": "Loyal",
        "category": CAT_PERSONALITY,
        "hidden": False,
        "inheritable": False,
        "effects": {"betrayal_resist": 2.0, "ally_bonus": 1.3, "faction_lock": True},
        "desc": "Once given, loyalty is absolute. Betrayal is unthinkable.",
    },
    "treacherous": {
        "name": "Treacherous",
        "category": CAT_PERSONALITY,
        "hidden": True,
        "inheritable": False,
        "effects": {
            "betrayal_bonus": 1.5,
            "trust_bonus": 0.3,
            "assassination_bonus": 1.3,
        },
        "desc": "Allegiance is a tool, not a chain. Switches sides without remorse.",
    },
    "just": {
        "name": "Just",
        "category": CAT_PERSONALITY,
        "hidden": False,
        "inheritable": False,
        "effects": {"peasant_opinion": 1.3, "law_bonus": 1.2, "mercy_penalty": 0.8},
        "desc": "Fairness above all. Even enemies receive just treatment.",
    },
    "arbitrary": {
        "name": "Arbitrary",
        "category": CAT_PERSONALITY,
        "hidden": False,
        "inheritable": False,
        "effects": {"peasant_opinion": 0.6, "unpredictability": 1.5, "fear_bonus": 1.2},
        "desc": "Rules on whim. Subjects never know what to expect.",
    },
    # ── EDUCATION (10 traits) ─────────────────────────────
    "scholar": {
        "name": "Scholar",
        "category": CAT_EDUCATION,
        "hidden": False,
        "inheritable": False,
        "effects": {"rhetoric_bonus": 2, "medicine_bonus": 1, "topic_discovery": 1.3},
        "desc": "Read the classics. Knowledge is the sharpest blade.",
    },
    "strategist": {
        "name": "Strategist",
        "category": CAT_EDUCATION,
        "hidden": False,
        "inheritable": False,
        "effects": {"battle_tactics": 1.4, "ambush_bonus": 1.3, "planning_bonus": 1.3},
        "desc": "Studied the art of war. Sees three moves ahead.",
    },
    "diplomat": {
        "name": "Diplomat",
        "category": CAT_EDUCATION,
        "hidden": False,
        "inheritable": False,
        "effects": {
            "rhetoric_bonus": 3,
            "relationship_gain": 1.3,
            "alliance_bonus": 1.4,
        },
        "desc": "Words are weapons. Trained in the art of negotiation.",
    },
    "artisan": {
        "name": "Artisan",
        "category": CAT_EDUCATION,
        "hidden": False,
        "inheritable": False,
        "effects": {
            "crafting_bonus": 1.5,
            "repair_bonus": 1.3,
            "merchant_opinion": 1.2,
        },
        "desc": "Skilled hands. Can craft, repair, and build.",
    },
    "illiterate": {
        "name": "Illiterate",
        "category": CAT_EDUCATION,
        "hidden": False,
        "inheritable": False,
        "effects": {
            "rhetoric_bonus": -2,
            "scroll_penalty": True,
            "peasant_relate": 1.2,
        },
        "desc": "Cannot read. Common among farmers and laborers.",
    },
    "martial": {
        "name": "Martial",
        "category": CAT_EDUCATION,
        "hidden": False,
        "inheritable": False,
        "effects": {
            "combat_xp_bonus": 1.3,
            "kenjutsu_bonus": 2,
            "weapon_maintenance": 1.2,
        },
        "desc": "Trained in the warrior arts from youth.",
    },
    "spiritual": {
        "name": "Spiritual",
        "category": CAT_EDUCATION,
        "hidden": False,
        "inheritable": False,
        "effects": {"morale_bonus": 1.2, "temple_opinion": 1.4, "undead_resist": 1.3},
        "desc": "Deep connection to the kami and Buddha. The unseen world speaks.",
    },
    "worldly": {
        "name": "Worldly",
        "category": CAT_EDUCATION,
        "hidden": False,
        "inheritable": False,
        "effects": {"trade_bonus": 1.3, "foreign_opinion": 1.3, "topic_discovery": 1.2},
        "desc": "Has traveled far. Knows foreign customs and trade routes.",
    },
    "healer": {
        "name": "Healer",
        "category": CAT_EDUCATION,
        "hidden": False,
        "inheritable": False,
        "effects": {"medicine_bonus": 3, "surgery_bonus": 1.5, "herb_bonus": 1.3},
        "desc": "Trained in medicine. Hands that mend, not break.",
    },
    "hunter_trained": {
        "name": "Woodsman",
        "category": CAT_EDUCATION,
        "hidden": False,
        "inheritable": False,
        "effects": {"survival_bonus": 3, "tracking_bonus": 1.5, "animal_bonus": 1.3},
        "desc": "Raised in the wild. Reads tracks like others read scrolls.",
    },
    # ── LIFESTYLE (10 traits) ─────────────────────────────
    "ascetic": {
        "name": "Ascetic",
        "category": CAT_LIFESTYLE,
        "hidden": False,
        "inheritable": False,
        "effects": {
            "hunger_resist": 1.5,
            "luxury_penalty": True,
            "temple_opinion": 1.3,
        },
        "desc": "Denies the body's cravings. Strength through deprivation.",
    },
    "hedonist": {
        "name": "Hedonist",
        "category": CAT_LIFESTYLE,
        "hidden": False,
        "inheritable": False,
        "effects": {
            "morale_from_food": 1.5,
            "morale_from_sake": 1.5,
            "discipline_penalty": 0.7,
        },
        "desc": "Lives for pleasure. Sake, food, and comfort above all.",
    },
    "devout": {
        "name": "Devout",
        "category": CAT_LIFESTYLE,
        "hidden": False,
        "inheritable": False,
        "effects": {
            "temple_opinion": 1.5,
            "prayer_bonus": True,
            "heresy_penalty": True,
        },
        "desc": "Deep faith. Prays daily. The kami listen.",
    },
    "cynical": {
        "name": "Cynical",
        "category": CAT_LIFESTYLE,
        "hidden": False,
        "inheritable": False,
        "effects": {"deception_resist": 1.3, "temple_opinion": 0.6, "trust_bonus": 0.7},
        "desc": "Trusts nothing. Sees manipulation everywhere.",
    },
    "drunkard": {
        "name": "Drunkard",
        "category": CAT_LIFESTYLE,
        "hidden": False,
        "inheritable": False,
        "effects": {
            "sake_dependency": True,
            "social_bonus": 1.2,
            "combat_penalty": 0.8,
        },
        "desc": "The bottle is a demanding master.",
    },
    "temperate": {
        "name": "Temperate",
        "category": CAT_LIFESTYLE,
        "hidden": False,
        "inheritable": False,
        "effects": {
            "health_bonus": 1.2,
            "disease_resist": 1.2,
            "morale_stability": 1.3,
        },
        "desc": "Moderation in all things. The body stays strong.",
    },
    "paranoid": {
        "name": "Paranoid",
        "category": CAT_LIFESTYLE,
        "hidden": True,
        "inheritable": False,
        "effects": {
            "ambush_resist": 1.5,
            "assassination_resist": 1.5,
            "trust_bonus": 0.3,
        },
        "desc": "Sees enemies in every shadow. Sometimes correctly.",
    },
    "trusting": {
        "name": "Trusting",
        "category": CAT_LIFESTYLE,
        "hidden": False,
        "inheritable": False,
        "effects": {
            "relationship_gain": 1.3,
            "betrayal_vulnerability": 1.5,
            "merchant_bonus": 1.2,
        },
        "desc": "Takes people at their word. A refreshing — and dangerous — quality.",
    },
    "wanderer": {
        "name": "Wanderer",
        "category": CAT_LIFESTYLE,
        "hidden": False,
        "inheritable": False,
        "effects": {
            "travel_speed": 1.2,
            "fatigue_resist": 1.2,
            "settlement_penalty": 0.8,
        },
        "desc": "The road is home. Cannot stay in one place long.",
    },
    "homebody": {
        "name": "Homebody",
        "category": CAT_LIFESTYLE,
        "hidden": False,
        "inheritable": False,
        "effects": {
            "settlement_bonus": 1.3,
            "travel_penalty": 0.8,
            "family_bonus": 1.3,
        },
        "desc": "Roots run deep. Happiest within familiar walls.",
    },
    # ── CONGENITAL (8 traits, inheritable) ────────────────
    "genius": {
        "name": "Genius",
        "category": CAT_CONGENITAL,
        "hidden": False,
        "inheritable": True,
        "effects": {"skill_xp_bonus": 1.5, "rhetoric_bonus": 3, "topic_discovery": 1.5},
        "desc": "A mind of extraordinary power. Sees what others cannot.",
    },
    "quick": {
        "name": "Quick-witted",
        "category": CAT_CONGENITAL,
        "hidden": False,
        "inheritable": True,
        "effects": {"skill_xp_bonus": 1.2, "initiative_bonus": 1.2},
        "desc": "Sharp mind, fast reactions. Not genius, but close.",
    },
    "slow": {
        "name": "Slow-witted",
        "category": CAT_CONGENITAL,
        "hidden": False,
        "inheritable": True,
        "effects": {"skill_xp_bonus": 0.7, "rhetoric_bonus": -2},
        "desc": "The world moves too fast. Understanding comes slowly.",
    },
    "strong": {
        "name": "Strong",
        "category": CAT_CONGENITAL,
        "hidden": False,
        "inheritable": True,
        "effects": {"attack_bonus": 1.3, "carry_weight": 1.3, "intimidate_bonus": 1.2},
        "desc": "Born with the strength of an ox. Muscles like knotted rope.",
    },
    "weak": {
        "name": "Weak",
        "category": CAT_CONGENITAL,
        "hidden": False,
        "inheritable": True,
        "effects": {"attack_bonus": 0.7, "carry_weight": 0.7, "stamina_penalty": 0.8},
        "desc": "Frail body. Must rely on wits rather than force.",
    },
    "beautiful": {
        "name": "Beautiful",
        "category": CAT_CONGENITAL,
        "hidden": False,
        "inheritable": True,
        "effects": {
            "relationship_gain": 1.4,
            "attraction_bonus": 1.5,
            "noble_opinion": 1.2,
        },
        "desc": "Striking appearance. Doors open for the beautiful.",
    },
    "ugly": {
        "name": "Ugly",
        "category": CAT_CONGENITAL,
        "hidden": False,
        "inheritable": True,
        "effects": {
            "relationship_gain": 0.7,
            "intimidate_bonus": 1.2,
            "attraction_penalty": 0.5,
        },
        "desc": "A face only a mother could love. Judges by appearance are legion.",
    },
    "robust": {
        "name": "Robust",
        "category": CAT_CONGENITAL,
        "hidden": False,
        "inheritable": True,
        "effects": {"disease_resist": 1.5, "hp_bonus": 1.2, "wound_resist": 1.2},
        "desc": "Iron constitution. Shrugs off what kills others.",
    },
    # ── PHYSICAL (7 traits, acquired through events) ──────
    "scarred": {
        "name": "Scarred",
        "category": CAT_PHYSICAL,
        "hidden": False,
        "inheritable": False,
        "effects": {
            "intimidate_bonus": 1.2,
            "beauty_penalty": 0.8,
            "veteran_opinion": 1.2,
        },
        "desc": "Battle-marked skin tells a story of survival.",
    },
    "maimed": {
        "name": "Maimed",
        "category": CAT_PHYSICAL,
        "hidden": False,
        "inheritable": False,
        "effects": {"combat_penalty": 0.6, "pity_bonus": 1.3, "pain_resist": 1.2},
        "desc": "A limb lost. The body adapts, but never forgets.",
    },
    "one_eyed": {
        "name": "One-Eyed",
        "category": CAT_PHYSICAL,
        "hidden": False,
        "inheritable": False,
        "effects": {
            "ranged_penalty": 0.6,
            "depth_penalty": True,
            "intimidate_bonus": 1.3,
        },
        "desc": "Lost an eye. Like Date Masamune, sees the world differently.",
    },
    "blind": {
        "name": "Blind",
        "category": CAT_PHYSICAL,
        "hidden": False,
        "inheritable": False,
        "effects": {"fov_penalty": 0.0, "hearing_bonus": 1.5, "combat_penalty": 0.3},
        "desc": "The world is darkness. Other senses sharpen to compensate.",
    },
    "deaf": {
        "name": "Deaf",
        "category": CAT_PHYSICAL,
        "hidden": False,
        "inheritable": False,
        "effects": {
            "conversation_penalty": 0.5,
            "ambush_vulnerability": 1.5,
            "focus_bonus": 1.3,
        },
        "desc": "Silence is permanent. Reads lips and gestures.",
    },
    "limping": {
        "name": "Limping",
        "category": CAT_PHYSICAL,
        "hidden": False,
        "inheritable": False,
        "effects": {"move_speed": 0.7, "flee_penalty": 0.5, "endurance_penalty": 0.8},
        "desc": "A leg that never healed right. Every step reminds.",
    },
    "disfigured": {
        "name": "Disfigured",
        "category": CAT_PHYSICAL,
        "hidden": False,
        "inheritable": False,
        "effects": {"beauty_penalty": 0.3, "fear_bonus": 1.5, "relationship_gain": 0.6},
        "desc": "Face tells a tale of violence. Children look away.",
    },
}

# ─────────────────────────────────────────────────────────────
# CONFLICT MATRIX — mutually exclusive trait pairs
# If a character has trait A, they cannot also have trait B.
# ─────────────────────────────────────────────────────────────
TRAIT_CONFLICTS = [
    ("brave", "cowardly"),
    ("honest", "deceitful"),
    ("compassionate", "cruel"),
    ("patient", "impulsive"),
    ("ambitious", "content"),
    ("gregarious", "shy"),
    ("wrathful", "calm"),
    ("proud", "humble"),
    ("loyal", "treacherous"),
    ("just", "arbitrary"),
    ("ascetic", "hedonist"),
    ("devout", "cynical"),
    ("drunkard", "temperate"),
    ("paranoid", "trusting"),
    ("wanderer", "homebody"),
    ("genius", "slow"),
    ("quick", "slow"),
    ("strong", "weak"),
    ("beautiful", "ugly"),
    ("blind", "one_eyed"),
]

# ─────────────────────────────────────────────────────────────
# COMPLEMENT MATRIX — traits that synergize well
# Having both grants a small bonus to relationship with like-minded.
# ─────────────────────────────────────────────────────────────
TRAIT_COMPLEMENTS = [
    ("brave", "martial"),
    ("honest", "just"),
    ("compassionate", "healer"),
    ("patient", "strategist"),
    ("ambitious", "strategist"),
    ("gregarious", "diplomat"),
    ("calm", "strategist"),
    ("proud", "martial"),
    ("loyal", "brave"),
    ("devout", "spiritual"),
    ("ascetic", "spiritual"),
    ("scholar", "patient"),
    ("worldly", "diplomat"),
    ("hunter_trained", "wanderer"),
    ("strong", "martial"),
    ("robust", "temperate"),
    ("genius", "scholar"),
]

# ─────────────────────────────────────────────────────────────
# TRAIT INHERITANCE WEIGHTS
# Congenital traits have a chance to pass from parent to child.
# ─────────────────────────────────────────────────────────────
INHERITANCE_CHANCE = {
    "genius": 0.25,
    "quick": 0.40,
    "slow": 0.30,
    "strong": 0.40,
    "weak": 0.30,
    "beautiful": 0.35,
    "ugly": 0.30,
    "robust": 0.40,
}

# Personality traits can develop in children based on parent influence
ENVIRONMENTAL_TRAIT_CHANCE = 0.15  # chance per parent trait to influence child

# Maximum traits per character
MAX_TRAITS = 8

# Number of traits assigned at character creation
CREATION_TRAITS = 3
