"""
social_data.py - Social Hierarchy System for ENGI
Dynamic social ranks with privileges, restrictions, and mobility.
"""

# ─────────────────────────────────────────────────────────────
# SOCIAL RANKS (highest to lowest)
# ─────────────────────────────────────────────────────────────
RANK_EMPEROR = 0
RANK_SHOGUN = 1
RANK_DAIMYO = 2
RANK_SAMURAI = 3
RANK_ASHIGARU = 4
RANK_MONK = 5  # outside hierarchy but respected
RANK_MERCHANT = 6
RANK_ARTISAN = 7
RANK_FARMER = 8
RANK_ETA = 9  # outcast class
RANK_RONIN = 10  # classless warrior

SOCIAL_RANKS = {
    RANK_EMPEROR: {
        "name": "Emperor",
        "jp": "天皇",
        "tier": 0,
        "coerce_power": 10,
        "desc": "Divine ruler. Beyond mortal authority.",
    },
    RANK_SHOGUN: {
        "name": "Shogun",
        "jp": "将軍",
        "tier": 1,
        "coerce_power": 9,
        "desc": "Military ruler of all Japan.",
    },
    RANK_DAIMYO: {
        "name": "Daimyo",
        "jp": "大名",
        "tier": 2,
        "coerce_power": 8,
        "desc": "Provincial lord. Commands armies and territory.",
    },
    RANK_SAMURAI: {
        "name": "Samurai",
        "jp": "侍",
        "tier": 3,
        "coerce_power": 6,
        "desc": "Noble warrior class. Carry two swords by right.",
    },
    RANK_ASHIGARU: {
        "name": "Ashigaru",
        "jp": "足軽",
        "tier": 4,
        "coerce_power": 3,
        "desc": "Foot soldier. Common-born but armed.",
    },
    RANK_MONK: {
        "name": "Monk",
        "jp": "僧",
        "tier": 3,
        "coerce_power": 4,
        "desc": "Religious class. Respected across all ranks.",
    },
    RANK_MERCHANT: {
        "name": "Merchant",
        "jp": "商人",
        "tier": 5,
        "coerce_power": 2,
        "desc": "Traders. Wealthy but low status.",
    },
    RANK_ARTISAN: {
        "name": "Artisan",
        "jp": "職人",
        "tier": 5,
        "coerce_power": 1,
        "desc": "Craftspeople. Smiths, carpenters, potters.",
    },
    RANK_FARMER: {
        "name": "Farmer",
        "jp": "農民",
        "tier": 6,
        "coerce_power": 1,
        "desc": "The foundation. Feeds everyone, owns nothing.",
    },
    RANK_ETA: {
        "name": "Eta",
        "jp": "穢多",
        "tier": 7,
        "coerce_power": 0,
        "desc": "Outcast class. Untouchable. Handles death and leather.",
    },
    RANK_RONIN: {
        "name": "Ronin",
        "jp": "浪人",
        "tier": 4,
        "coerce_power": 4,
        "desc": "Masterless samurai. No clan, no obligations, no safety net.",
    },
}

# ─────────────────────────────────────────────────────────────
# RANK INTERACTIONS
# ─────────────────────────────────────────────────────────────
# Can a character of rank A coerce rank B?
# Coercion succeeds if coerce_power(A) > coerce_power(B) + resistance
# Resistance comes from traits (proud, brave) and relationship

# Rank-based dialog restrictions
RANK_DIALOG_RULES = {
    # rank -> list of actions available
    RANK_EMPEROR: ["command", "decree", "grant"],
    RANK_SHOGUN: ["command", "decree", "grant", "threaten"],
    RANK_DAIMYO: ["command", "threaten", "request", "negotiate"],
    RANK_SAMURAI: ["command_lower", "request", "challenge", "negotiate"],
    RANK_ASHIGARU: ["request", "obey", "negotiate"],
    RANK_MONK: ["advise", "request", "bless", "negotiate"],
    RANK_MERCHANT: ["trade", "request", "bribe", "negotiate"],
    RANK_ARTISAN: ["trade", "request", "negotiate"],
    RANK_FARMER: ["request", "plead", "obey"],
    RANK_ETA: ["plead", "obey"],
    RANK_RONIN: ["request", "threaten", "negotiate", "challenge"],
}

# ─────────────────────────────────────────────────────────────
# SOCIAL MOBILITY PATHS
# How a character can change rank
# ─────────────────────────────────────────────────────────────
MOBILITY_PATHS = {
    "farmer_to_ashigaru": {
        "from": RANK_FARMER,
        "to": RANK_ASHIGARU,
        "requirement": "recruited by daimyo or joins army",
        "honor_change": 5,
        "money_cost": 0,
    },
    "ashigaru_to_samurai": {
        "from": RANK_ASHIGARU,
        "to": RANK_SAMURAI,
        "requirement": "distinguished military service or daimyo grant",
        "honor_change": 20,
        "money_cost": 0,
    },
    "merchant_to_samurai": {
        "from": RANK_MERCHANT,
        "to": RANK_SAMURAI,
        "requirement": "purchase samurai status from daimyo",
        "honor_change": 10,
        "money_cost": 500,
    },
    "ronin_to_samurai": {
        "from": RANK_RONIN,
        "to": RANK_SAMURAI,
        "requirement": "pledge fealty to a daimyo",
        "honor_change": 15,
        "money_cost": 0,
    },
    "samurai_to_ronin": {
        "from": RANK_SAMURAI,
        "to": RANK_RONIN,
        "requirement": "lord dies, betrayal, or voluntary departure",
        "honor_change": -20,
        "money_cost": 0,
    },
    "monk_entry": {
        "from": None,
        "to": RANK_MONK,
        "requirement": "take vows at a temple",
        "honor_change": 10,
        "money_cost": 0,
    },
    "samurai_to_daimyo": {
        "from": RANK_SAMURAI,
        "to": RANK_DAIMYO,
        "requirement": "conquer territory or inherit domain",
        "honor_change": 30,
        "money_cost": 0,
    },
}

# ─────────────────────────────────────────────────────────────
# RANK PRIVILEGES AND RESTRICTIONS
# ─────────────────────────────────────────────────────────────
RANK_PRIVILEGES = {
    RANK_SAMURAI: {
        "can_carry_swords": True,
        "castle_access": True,
        "checkpoint_pass": True,
        "tax_exempt": True,
        "can_execute_commoners": True,
    },
    RANK_DAIMYO: {
        "can_carry_swords": True,
        "castle_access": True,
        "checkpoint_pass": True,
        "tax_exempt": True,
        "can_execute_commoners": True,
        "can_command_army": True,
        "can_grant_rank": True,
    },
    RANK_MERCHANT: {
        "can_carry_swords": False,
        "castle_access": False,
        "checkpoint_pass": True,  # with papers
        "trade_bonus": True,
    },
    RANK_FARMER: {
        "can_carry_swords": False,
        "castle_access": False,
        "checkpoint_pass": True,  # with papers
    },
    RANK_ETA: {
        "can_carry_swords": False,
        "castle_access": False,
        "checkpoint_pass": False,  # often denied
        "settlement_restricted": True,
    },
    RANK_RONIN: {
        "can_carry_swords": True,
        "castle_access": False,
        "checkpoint_pass": True,  # but suspicious
        "watched_by_guards": True,
    },
}

# ─────────────────────────────────────────────────────────────
# DISGUISE SYSTEM
# ─────────────────────────────────────────────────────────────
DISGUISE_DETECTION_BASE = 0.3  # base chance of being detected per checkpoint

# Items that enable disguise
DISGUISE_ITEMS = {
    "samurai_disguise": {
        "fake_rank": RANK_SAMURAI,
        "detection_mod": 0.5,
        "requires": ["katana", "do_armor"],
        "desc": "Dress as a samurai. Convincing with the right armor.",
    },
    "merchant_disguise": {
        "fake_rank": RANK_MERCHANT,
        "detection_mod": 0.3,
        "requires": [],
        "desc": "Travel as a merchant. Common and unremarkable.",
    },
    "monk_disguise": {
        "fake_rank": RANK_MONK,
        "detection_mod": 0.4,
        "requires": ["prayer_beads"],
        "desc": "Shave head and don robes. Pilgrims are everywhere.",
    },
    "farmer_disguise": {
        "fake_rank": RANK_FARMER,
        "detection_mod": 0.2,
        "requires": [],
        "desc": "Dirty clothes and a straw hat. Invisible.",
    },
}

# ─────────────────────────────────────────────────────────────
# NPC TYPE TO DEFAULT RANK MAPPING
# ─────────────────────────────────────────────────────────────
NPC_DEFAULT_RANK = {
    "farmer": RANK_FARMER,
    "elder": RANK_FARMER,
    "samurai": RANK_SAMURAI,
    "ronin": RANK_RONIN,
    "bandit": RANK_ETA,
    "bandit_chief": RANK_ETA,
    "monk": RANK_MONK,
    "pilgrim": RANK_FARMER,
    "merchant": RANK_MERCHANT,
    "guard": RANK_ASHIGARU,
    "lord": RANK_DAIMYO,
    "hunter": RANK_FARMER,
    "ninja": RANK_RONIN,
    "yamabushi": RANK_MONK,
    "innkeeper": RANK_MERCHANT,
    "blacksmith": RANK_ARTISAN,
    "captain": RANK_SAMURAI,
}

# Player class to starting rank
PLAYER_CLASS_RANK = {
    "ronin": RANK_RONIN,
    "samurai": RANK_SAMURAI,
    "ninja": RANK_RONIN,
    "monk": RANK_MONK,
    "merchant": RANK_MERCHANT,
    "hunter": RANK_FARMER,
}
