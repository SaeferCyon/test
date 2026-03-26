"""
topic_data.py - Morrowind-style Conversation Topic System for ENGI
Global topic registry with knowledge requirements and unlock chains.
"""

# ─────────────────────────────────────────────────────────────
# TOPIC CATEGORIES
# ─────────────────────────────────────────────────────────────
TCAT_GENERAL = "general"
TCAT_LOCAL = "local"
TCAT_POLITICS = "politics"
TCAT_MILITARY = "military"
TCAT_RELIGION = "religion"
TCAT_TRADE = "trade"
TCAT_SURVIVAL = "survival"
TCAT_PERSONAL = "personal"
TCAT_RUMORS = "rumors"
TCAT_SKILLS = "skills"

# ─────────────────────────────────────────────────────────────
# TOPIC DEFINITIONS
# Each topic has:
#   name: display name shown in dialog menu
#   category: topic category for organization
#   starting: if True, all characters know this topic from the start
#   unlock_from: list of topic keys that can reveal this one
#   skill_gate: skill + min level required to use this topic (None = anyone)
#   knowledge_by_type: dict of NPC type -> knowledge score (0-100)
#   desc: brief description for the player
# ─────────────────────────────────────────────────────────────
TOPICS = {
    # ── GENERAL (everyone starts with these) ──────────────
    "greetings": {
        "name": "Greetings",
        "category": TCAT_GENERAL,
        "starting": True,
        "unlock_from": [],
        "skill_gate": None,
        "knowledge_by_type": {
            "farmer": 80,
            "samurai": 90,
            "merchant": 85,
            "monk": 95,
            "ronin": 70,
            "bandit": 50,
            "lord": 95,
            "hunter": 60,
            "pilgrim": 85,
            "guard": 80,
            "elder": 90,
            "innkeeper": 90,
            "blacksmith": 70,
            "yamabushi": 80,
            "ninja": 60,
        },
        "desc": "Basic pleasantries and introductions.",
    },
    "directions": {
        "name": "Directions",
        "category": TCAT_GENERAL,
        "starting": True,
        "unlock_from": [],
        "skill_gate": None,
        "knowledge_by_type": {
            "farmer": 70,
            "samurai": 60,
            "merchant": 90,
            "monk": 50,
            "ronin": 80,
            "bandit": 40,
            "lord": 30,
            "hunter": 85,
            "pilgrim": 75,
            "guard": 70,
            "elder": 90,
            "innkeeper": 85,
            "blacksmith": 60,
            "yamabushi": 80,
            "ninja": 70,
        },
        "desc": "Ask about nearby locations and how to reach them.",
    },
    "weather": {
        "name": "Weather",
        "category": TCAT_GENERAL,
        "starting": True,
        "unlock_from": [],
        "skill_gate": None,
        "knowledge_by_type": {
            "farmer": 95,
            "samurai": 40,
            "merchant": 60,
            "monk": 50,
            "ronin": 60,
            "hunter": 95,
            "pilgrim": 70,
            "elder": 80,
            "yamabushi": 90,
        },
        "desc": "Discuss current and coming weather.",
    },
    "local_news": {
        "name": "Local News",
        "category": TCAT_LOCAL,
        "starting": True,
        "unlock_from": [],
        "skill_gate": None,
        "knowledge_by_type": {
            "farmer": 80,
            "samurai": 60,
            "merchant": 85,
            "monk": 50,
            "ronin": 50,
            "guard": 75,
            "elder": 95,
            "innkeeper": 95,
            "blacksmith": 70,
        },
        "desc": "What's happening in the area.",
    },
    "trade": {
        "name": "Trade",
        "category": TCAT_TRADE,
        "starting": True,
        "unlock_from": [],
        "skill_gate": None,
        "knowledge_by_type": {
            "farmer": 40,
            "merchant": 100,
            "monk": 20,
            "ronin": 30,
            "innkeeper": 80,
            "blacksmith": 70,
            "guard": 30,
        },
        "desc": "Buy, sell, and barter goods.",
    },
    # ── UNLOCKABLE TOPICS ─────────────────────────────────
    "local_danger": {
        "name": "Local Dangers",
        "category": TCAT_LOCAL,
        "starting": False,
        "unlock_from": ["local_news", "directions"],
        "skill_gate": None,
        "knowledge_by_type": {
            "farmer": 75,
            "hunter": 95,
            "ronin": 70,
            "bandit": 80,
            "guard": 85,
            "elder": 80,
            "yamabushi": 70,
            "ninja": 60,
        },
        "desc": "Bandits, animals, and hazards in the area.",
    },
    "clan_politics": {
        "name": "Clan Politics",
        "category": TCAT_POLITICS,
        "starting": False,
        "unlock_from": ["local_news"],
        "skill_gate": None,
        "knowledge_by_type": {
            "farmer": 30,
            "samurai": 85,
            "merchant": 60,
            "lord": 100,
            "ronin": 50,
            "guard": 60,
            "elder": 70,
            "monk": 40,
        },
        "desc": "Who rules, who schemes, who is at war.",
    },
    "war_rumors": {
        "name": "War Rumors",
        "category": TCAT_MILITARY,
        "starting": False,
        "unlock_from": ["clan_politics"],
        "skill_gate": None,
        "knowledge_by_type": {
            "samurai": 90,
            "merchant": 50,
            "lord": 95,
            "ronin": 70,
            "guard": 80,
            "ashigaru": 75,
        },
        "desc": "Troop movements, battles, and campaigns.",
    },
    "bushido": {
        "name": "Bushido",
        "category": TCAT_MILITARY,
        "starting": False,
        "unlock_from": ["clan_politics", "greetings"],
        "skill_gate": None,
        "knowledge_by_type": {
            "samurai": 95,
            "lord": 90,
            "ronin": 80,
            "monk": 60,
            "guard": 50,
            "farmer": 20,
        },
        "desc": "The way of the warrior. Honor, duty, and death.",
    },
    "buddhism": {
        "name": "Buddhism",
        "category": TCAT_RELIGION,
        "starting": False,
        "unlock_from": ["greetings"],
        "skill_gate": None,
        "knowledge_by_type": {
            "monk": 100,
            "pilgrim": 85,
            "yamabushi": 80,
            "elder": 60,
            "farmer": 30,
            "samurai": 40,
            "lord": 50,
        },
        "desc": "The dharma, temples, and spiritual practice.",
    },
    "shinto": {
        "name": "Shinto",
        "category": TCAT_RELIGION,
        "starting": False,
        "unlock_from": ["greetings"],
        "skill_gate": None,
        "knowledge_by_type": {
            "yamabushi": 100,
            "monk": 70,
            "pilgrim": 75,
            "elder": 80,
            "farmer": 60,
            "samurai": 40,
        },
        "desc": "The kami, shrines, and the old ways.",
    },
    "medicine": {
        "name": "Medicine",
        "category": TCAT_SKILLS,
        "starting": False,
        "unlock_from": ["greetings"],
        "skill_gate": ("medicine", 2),
        "knowledge_by_type": {
            "monk": 80,
            "yamabushi": 90,
            "elder": 50,
            "healer": 100,
            "merchant": 30,
        },
        "desc": "Herbs, treatments, and healing arts.",
    },
    "swordsmanship": {
        "name": "Swordsmanship",
        "category": TCAT_SKILLS,
        "starting": False,
        "unlock_from": ["bushido"],
        "skill_gate": ("kenjutsu", 3),
        "knowledge_by_type": {
            "samurai": 90,
            "ronin": 85,
            "lord": 70,
            "guard": 60,
            "blacksmith": 50,
            "ninja": 70,
        },
        "desc": "Techniques, schools, and blade philosophy.",
    },
    "survival_tips": {
        "name": "Survival",
        "category": TCAT_SURVIVAL,
        "starting": False,
        "unlock_from": ["directions", "weather"],
        "skill_gate": None,
        "knowledge_by_type": {
            "hunter": 100,
            "yamabushi": 90,
            "farmer": 70,
            "ronin": 60,
            "pilgrim": 50,
            "bandit": 65,
        },
        "desc": "Living off the land. Food, water, shelter.",
    },
    "trade_routes": {
        "name": "Trade Routes",
        "category": TCAT_TRADE,
        "starting": False,
        "unlock_from": ["trade", "directions"],
        "skill_gate": None,
        "knowledge_by_type": {
            "merchant": 100,
            "innkeeper": 80,
            "guard": 50,
            "pilgrim": 60,
            "farmer": 30,
        },
        "desc": "Roads, ports, and profitable routes.",
    },
    "foreign_goods": {
        "name": "Foreign Goods",
        "category": TCAT_TRADE,
        "starting": False,
        "unlock_from": ["trade_routes"],
        "skill_gate": None,
        "knowledge_by_type": {"merchant": 90, "lord": 50, "monk": 30},
        "desc": "Portuguese imports, Chinese silk, and exotic wares.",
    },
    "firearms": {
        "name": "Firearms",
        "category": TCAT_MILITARY,
        "starting": False,
        "unlock_from": ["foreign_goods", "war_rumors"],
        "skill_gate": None,
        "knowledge_by_type": {
            "merchant": 60,
            "samurai": 50,
            "lord": 70,
            "blacksmith": 80,
        },
        "desc": "Teppo muskets and the revolution they bring.",
    },
    "assassination": {
        "name": "Dark Arts",
        "category": TCAT_MILITARY,
        "starting": False,
        "unlock_from": ["local_danger"],
        "skill_gate": ("stealth", 4),
        "knowledge_by_type": {"ninja": 100, "bandit_chief": 60, "ronin": 40},
        "desc": "Poisons, infiltration, and the shinobi way.",
    },
    "philosophy": {
        "name": "Philosophy",
        "category": TCAT_RELIGION,
        "starting": False,
        "unlock_from": ["buddhism", "bushido"],
        "skill_gate": ("rhetoric", 3),
        "knowledge_by_type": {
            "monk": 90,
            "elder": 80,
            "lord": 60,
            "samurai": 50,
            "scholar": 95,
            "yamabushi": 75,
        },
        "desc": "The nature of existence, duty, and meaning.",
    },
    "family": {
        "name": "Family",
        "category": TCAT_PERSONAL,
        "starting": False,
        "unlock_from": ["greetings"],
        "skill_gate": None,
        "knowledge_by_type": {
            "farmer": 90,
            "elder": 95,
            "innkeeper": 80,
            "merchant": 60,
            "samurai": 70,
            "monk": 30,
        },
        "desc": "Ask about family, marriage, and children.",
    },
    "rumors": {
        "name": "Rumors",
        "category": TCAT_RUMORS,
        "starting": False,
        "unlock_from": ["local_news"],
        "skill_gate": None,
        "knowledge_by_type": {
            "innkeeper": 100,
            "merchant": 85,
            "farmer": 70,
            "guard": 60,
            "pilgrim": 75,
            "elder": 80,
        },
        "desc": "Gossip, whispers, and unverified tales.",
    },
    "hire": {
        "name": "Hire Services",
        "category": TCAT_TRADE,
        "starting": False,
        "unlock_from": ["trade"],
        "skill_gate": ("rhetoric", 2),
        "knowledge_by_type": {
            "ronin": 90,
            "ninja": 70,
            "merchant": 50,
            "blacksmith": 60,
        },
        "desc": "Recruit companions or hire services.",
    },
    "history": {
        "name": "History",
        "category": TCAT_GENERAL,
        "starting": False,
        "unlock_from": ["clan_politics", "buddhism"],
        "skill_gate": None,
        "knowledge_by_type": {
            "elder": 100,
            "monk": 80,
            "lord": 75,
            "samurai": 60,
            "scholar": 95,
            "pilgrim": 50,
        },
        "desc": "The past of Japan, clans, and great battles.",
    },
    "crafting": {
        "name": "Crafting",
        "category": TCAT_SKILLS,
        "starting": False,
        "unlock_from": ["trade"],
        "skill_gate": None,
        "knowledge_by_type": {
            "blacksmith": 100,
            "artisan": 90,
            "farmer": 40,
            "merchant": 50,
        },
        "desc": "Forging, building, and making things.",
    },
}

# ─────────────────────────────────────────────────────────────
# TOPIC UNLOCK CHANCE
# When talking about a topic, chance to discover a linked topic.
# Base chance modified by NPC knowledge and player traits.
# ─────────────────────────────────────────────────────────────
TOPIC_DISCOVER_BASE_CHANCE = 0.25

# ─────────────────────────────────────────────────────────────
# RESPONSE QUALITY THRESHOLDS
# NPC knowledge score determines response detail.
# ─────────────────────────────────────────────────────────────
KNOWLEDGE_NONE = 0  # "I don't know anything about that."
KNOWLEDGE_VAGUE = 20  # "I've heard something about that..."
KNOWLEDGE_BASIC = 40  # Gives basic information
KNOWLEDGE_GOOD = 60  # Gives useful, specific information
KNOWLEDGE_EXPERT = 80  # Gives detailed, expert information
KNOWLEDGE_MASTER = 95  # Gives comprehensive, insider knowledge

# ─────────────────────────────────────────────────────────────
# RELATIONSHIP-BASED DIALOG MODIFIERS
# How relationship score affects what an NPC will share.
# ─────────────────────────────────────────────────────────────
DIALOG_TRUST_THRESHOLDS = {
    "hostile": {
        "min_rel": -100,
        "max_rel": -50,
        "knowledge_mod": 0.3,
        "topic_block": ["personal", "rumors", "hire"],
    },
    "unfriendly": {
        "min_rel": -50,
        "max_rel": -10,
        "knowledge_mod": 0.6,
        "topic_block": ["personal", "hire"],
    },
    "neutral": {"min_rel": -10, "max_rel": 20, "knowledge_mod": 1.0, "topic_block": []},
    "friendly": {"min_rel": 20, "max_rel": 50, "knowledge_mod": 1.2, "topic_block": []},
    "trusted": {"min_rel": 50, "max_rel": 100, "knowledge_mod": 1.5, "topic_block": []},
}

# ─────────────────────────────────────────────────────────────
# EVENT BUS CONSTANTS
# ─────────────────────────────────────────────────────────────
EVT_TOPIC_DISCOVERED = "topic_discovered"
EVT_CONVERSATION_END = "conversation_end"
EVT_RELATIONSHIP_CHANGE = "relationship_change"
EVT_MEMORY_CREATED = "memory_created"
EVT_TRAIT_DISCOVERED = "trait_discovered"
EVT_COMBAT_HIT = "combat_hit"
EVT_COMBAT_KILL = "combat_kill"
EVT_NPC_DEATH = "npc_death"
EVT_PLAYER_DEATH = "player_death"
EVT_MARRIAGE = "marriage"
EVT_CHILD_BORN = "child_born"
EVT_RANK_CHANGE = "rank_change"
EVT_CRIME_WITNESSED = "crime_witnessed"
EVT_GIFT_GIVEN = "gift_given"
EVT_THEFT = "theft"
EVT_INSULT = "insult"
EVT_COMPLIMENT = "compliment"
EVT_BETRAYAL = "betrayal"
EVT_RESCUE = "rescue"
