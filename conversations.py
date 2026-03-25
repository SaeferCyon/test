"""
conversations.py - Morrowind-style Topic-Based Conversation System for ENGI
Players discover topics through conversation and can ask NPCs about them.
Response quality depends on NPC knowledge, relationship trust, and personality.
"""

from topic_data import (
    TOPICS,
    TOPIC_DISCOVER_BASE_CHANCE,
    KNOWLEDGE_NONE,
    KNOWLEDGE_VAGUE,
    KNOWLEDGE_BASIC,
    KNOWLEDGE_GOOD,
    KNOWLEDGE_EXPERT,
    KNOWLEDGE_MASTER,
    DIALOG_TRUST_THRESHOLDS,
)

# ─────────────────────────────────────────────────────────────
# RESPONSE TEMPLATES
# Keyed by topic -> knowledge tier -> list of template strings.
# Placeholders: {npc_name}, {location}, {faction}
# ─────────────────────────────────────────────────────────────

_VAGUE_GENERIC = [
    "I've heard something about that, but I can't say much.",
    "Hmm... I may have heard a rumor once, but I can't recall the details.",
    "I know little of such things, traveler.",
]

_NONE_GENERIC = [
    "I don't know anything about that.",
    "You're asking the wrong person.",
    "I have nothing to say on that matter.",
]

RESPONSE_TEMPLATES = {
    "greetings": {
        "vague": [
            "Hmph. What do you want?",
            "...Yes?",
        ],
        "basic": [
            "Good day, traveler. What brings you here?",
            "Welcome. I hope you find what you seek.",
        ],
        "good": [
            "Ah, a visitor! Welcome to {location}. How may I help you?",
            "Greetings, friend. {location} is glad to receive travelers.",
        ],
        "expert": [
            "Welcome, welcome! It is not often we see new faces in {location}. Let me know if there is anything you need.",
            "A fine day to you! I am always pleased to meet those who travel these roads.",
        ],
        "master": [
            "You honor us with your presence. {location} remembers its friends. Speak freely, and know you are among allies.",
            "Ah, I have been expecting someone like you. Please, sit. Let us talk as friends.",
        ],
    },
    "directions": {
        "vague": [
            "There are roads... but I forget where they lead.",
            "I think there's a path somewhere to the east? Or was it west...",
        ],
        "basic": [
            "The main road heads north toward the mountains. That's all I know.",
            "Follow the river and you'll reach the next village eventually.",
        ],
        "good": [
            "If you head north from {location}, the road forks. Take the left path for the mountain pass.",
            "The merchant road runs east to west through {location}. Most travelers follow it.",
        ],
        "expert": [
            "From {location}, three roads branch out. North leads to the castle town, east to the port, and the forest trail south is a shortcut if you know it.",
            "I know every path within a day's walk of {location}. Tell me where you wish to go and I'll set you right.",
        ],
        "master": [
            "I have walked every trail in this province. There are hidden paths through the mountains that even the {faction} patrols don't know. Let me draw you a map.",
            "Ah, directions! I could guide you blindfolded. There are old hunter's trails that cut travel time in half, if you know the markers.",
        ],
    },
    "local_news": {
        "vague": [
            "Things happen around here, but I pay little attention.",
            "Something happened recently... I can't remember what.",
        ],
        "basic": [
            "The harvest has been fair this season. That's about all there is to say.",
            "A few travelers passed through {location} recently. Unusual for this time of year.",
        ],
        "good": [
            "There's been some trouble on the roads near {location}. Bandits, they say. The {faction} has been slow to respond.",
            "The lord's tax collectors came through last week. People are grumbling, but what can you do?",
        ],
        "expert": [
            "Let me tell you what's really going on in {location}. The {faction} is pulling soldiers from the garrison, and the bandits know it. Three caravans have been hit this month alone.",
            "There's more happening than meets the eye. The elder has been meeting with {faction} envoys in secret. Something is brewing.",
        ],
        "master": [
            "I know everything that happens in {location} and beyond. The {faction} is repositioning for a campaign, and our village is caught in the middle. I can tell you exactly who to trust and who to avoid.",
            "You want the real news? Not the rumors the farmers trade? Very well. But this stays between us.",
        ],
    },
    "trade": {
        "vague": [
            "I've seen merchants on the road, but I don't deal in trade myself.",
            "Buying and selling... not really my concern.",
        ],
        "basic": [
            "You can buy basic supplies at the market in {location}.",
            "Prices have been going up lately. Hard times for everyone.",
        ],
        "good": [
            "The market in {location} is well-stocked. Rice, tools, and cloth are the main goods. For weapons, you'll want to visit the blacksmith.",
            "If you're looking to trade, the merchants here deal fairly. Just don't try to haggle too aggressively.",
        ],
        "expert": [
            "I know every merchant in {location} and their specialties. Tell me what you need and I'll point you to the best deal.",
            "Trade has been good this season. The {faction} has kept the roads safe, which means more caravans and lower prices. Buy rice now before winter drives the price up.",
        ],
        "master": [
            "I can arrange introductions with the most influential merchants in the region. Some deals aren't made at the market stall, if you understand my meaning. The {faction} has certain... needs... that pay very well.",
            "You want to make real money? Forget the local market. I know the trade routes, the suppliers, the demand. With the right goods, you could triple your investment.",
        ],
    },
    "local_danger": {
        "vague": [
            "I've heard there's danger out there. Be careful.",
            "Dangerous? I suppose everywhere is, if you're not careful.",
        ],
        "basic": [
            "Bandits sometimes lurk on the roads outside {location}. Travel in daylight.",
            "Wolves have been spotted in the hills. Stay on the main paths.",
        ],
        "good": [
            "The forest east of {location} is home to a band of outlaws. They prey on lone travelers. The {faction} has posted bounties but no one dares go after them.",
            "Wild boar and bear roam the mountains. And worse things come out at night. I'd avoid the old shrine path after dark if I were you.",
        ],
        "expert": [
            "Let me tell you exactly what threatens {location}. The bandit camp is three hours east in the ravine. They number about a dozen, led by a ronin who deserted the {faction}. The mountain pass has wolves, but they avoid fire.",
            "I've survived every danger this land has to offer. The real threat isn't the wildlife; it's the masterless samurai who've turned to banditry. I can tell you their patrol routes.",
        ],
        "master": [
            "I know every threat within a week's march. The bandits, the beasts, the hidden traps left from the last war. There are also things in the deep forest that people don't like to talk about. I'll tell you everything, but heed my warnings.",
            "You want to know about the dangers? I'll give you the complete picture. But some of this knowledge is... unsettling. The {faction} doesn't want people knowing about the caves beneath the old fortress.",
        ],
    },
    "clan_politics": {
        "vague": [
            "Lords and their games... I try to stay out of it.",
            "Politics? I'm just trying to get by.",
        ],
        "basic": [
            "The {faction} controls this region. That's all most people need to know.",
            "There are several clans vying for power. Best not to take sides openly.",
        ],
        "good": [
            "The {faction} has held this province for three generations, but their grip is weakening. The neighboring clans sense opportunity.",
            "There's a power struggle within the {faction}. Two heirs, and the lord hasn't named his successor. It's making everyone nervous.",
        ],
        "expert": [
            "I follow the politics closely. The {faction} is allied with two minor clans to the north, but those alliances are fragile. The southern lords are forming their own coalition. War could come within the year.",
            "Let me explain the situation. The {faction} lord owes debts to three different daimyo. His vassal network is fraying. The retainers are already choosing sides for what comes next.",
        ],
        "master": [
            "I know the true power structure behind the {faction}. The public alliances are theater. The real decisions are made by a council of elders who control the treasury. I can tell you who really holds the strings.",
            "You want to understand clan politics? I've spent my life watching these games. Every marriage, every favor, every betrayal, I remember them all. The {faction} is not what it appears to be.",
        ],
    },
    "bushido": {
        "vague": [
            "The way of the warrior... I know the word, but little else.",
            "Bushido? That's for samurai to worry about.",
        ],
        "basic": [
            "Bushido demands honor, loyalty, and courage. At least that's what they say.",
            "A samurai must serve his lord faithfully. That is the core of bushido.",
        ],
        "good": [
            "Bushido is more than just fighting. It encompasses loyalty, honor, self-discipline, and respect. A true warrior masters himself before he masters the sword.",
            "The code of bushido has evolved over generations. Different schools emphasize different virtues, but loyalty to one's lord remains paramount.",
        ],
        "expert": [
            "Let me speak plainly about bushido. The ideal is noble: righteousness, courage, benevolence, respect, honesty, honor, and loyalty. But in practice, lords use it to control their samurai. The code is a tool as much as a philosophy.",
            "I have studied bushido deeply. The tension between duty and morality is its central challenge. What does a samurai do when his lord orders something dishonorable? That question has no easy answer.",
        ],
        "master": [
            "Bushido is a living philosophy, not a rigid code. I have seen it interpreted a hundred different ways. The greatest warriors I've known understood that true bushido means thinking for yourself while serving something greater. The {faction} teaches a simplified version; the truth is far more nuanced.",
            "After a lifetime of practice, I'll tell you what bushido really means. It's not about blind obedience or glorious death. It's about finding meaning in service while maintaining your humanity. Most people never grasp this.",
        ],
    },
    "buddhism": {
        "vague": [
            "The monks chant at the temple. That's about all I know.",
            "Buddhism? I see the pilgrims pass through sometimes.",
        ],
        "basic": [
            "The Buddha teaches that suffering comes from desire. The monks at the temple can tell you more.",
            "There are several temples in the region. The faithful make pilgrimages regularly.",
        ],
        "good": [
            "Buddhism teaches the Four Noble Truths and the Eightfold Path. The temple in {location} follows the Pure Land tradition, which emphasizes faith in Amida Buddha.",
            "The monks here practice meditation and study the sutras. Some sects believe enlightenment comes through discipline, others through devotion. Both paths have merit.",
        ],
        "expert": [
            "The Buddhist traditions in this region are complex. Zen emphasizes direct experience of awakening through meditation. Pure Land seeks rebirth in the Western Paradise. Shingon uses esoteric practices. Each has its place.",
            "I have studied the dharma extensively. The concept of impermanence is central: nothing lasts, not joy, not suffering. Understanding this deeply changes how you see the world and the conflicts around you.",
        ],
        "master": [
            "I have spent decades contemplating the dharma. Let me share what I've learned: the boundaries between Buddhist sects are less rigid than they appear. The {faction}'s temple politics are worldly concerns wrapped in spiritual language. True practice transcends all that.",
            "You seek knowledge of the Buddha's teachings? I can offer you something rare: understanding that bridges the gap between doctrine and lived experience. But be warned, true insight changes you in ways you cannot predict.",
        ],
    },
}

# Fallback templates for topics not in the detailed dict above
_FALLBACK_TEMPLATES = {
    "vague": [
        "I've heard a little about that, but I'm no expert.",
        "That's not something I know much about, I'm afraid.",
    ],
    "basic": [
        "I know the basics. Let me tell you what I can.",
        "Here's what I know, though it isn't much.",
    ],
    "good": [
        "I can tell you a fair bit about that. Listen closely.",
        "I know this subject reasonably well. Here is what I can share.",
    ],
    "expert": [
        "I know a great deal about this. Let me share my knowledge.",
        "You've come to the right person. I have studied this extensively.",
    ],
    "master": [
        "Few know as much as I do about this. Let me tell you everything.",
        "I am among the foremost authorities on this matter. Ask freely.",
    ],
}


# ─────────────────────────────────────────────────────────────
# TRUST HELPERS
# ─────────────────────────────────────────────────────────────


def _get_trust_tier(relationship_score):
    """Return the trust tier dict for the given relationship score."""
    for tier in DIALOG_TRUST_THRESHOLDS.values():
        if tier["min_rel"] <= relationship_score < tier["max_rel"]:
            return tier
    # Default to neutral if score is exactly at a boundary
    return DIALOG_TRUST_THRESHOLDS["neutral"]


def _get_trust_modifier(relationship_score):
    """Return the knowledge modifier for the given relationship score."""
    tier = _get_trust_tier(relationship_score)
    return tier["knowledge_mod"]


def _get_blocked_categories(relationship_score):
    """Return the list of topic categories blocked at this trust level."""
    tier = _get_trust_tier(relationship_score)
    return tier.get("topic_block", [])


# ─────────────────────────────────────────────────────────────
# KNOWLEDGE TIER HELPERS
# ─────────────────────────────────────────────────────────────


def _knowledge_tier_label(effective_knowledge):
    """Map effective knowledge to a tier label string."""
    if effective_knowledge < KNOWLEDGE_VAGUE:
        return "none"
    elif effective_knowledge < KNOWLEDGE_BASIC:
        return "vague"
    elif effective_knowledge < KNOWLEDGE_GOOD:
        return "basic"
    elif effective_knowledge < KNOWLEDGE_EXPERT:
        return "good"
    elif effective_knowledge < KNOWLEDGE_MASTER:
        return "expert"
    else:
        return "master"


# ─────────────────────────────────────────────────────────────
# TRAIT-BASED RESPONSE MODIFIERS
# ─────────────────────────────────────────────────────────────


def _apply_trait_modifiers(text, npc_traits):
    """Modify response text based on NPC personality traits."""
    trait_set = set(npc_traits) if npc_traits else set()

    if "deceitful" in trait_set:
        text = (
            "Well... " + text + " Or so I've been told. Who can say what's really true?"
        )
    elif "honest" in trait_set:
        text = "I'll be straight with you. " + text

    if "shy" in trait_set:
        # Truncate to first sentence for shy NPCs
        first_period = text.find(".")
        if first_period > 0 and first_period < len(text) - 1:
            text = text[: first_period + 1]

    if "gregarious" in trait_set:
        text = text + " But there's more to it than that, if you have time to listen!"

    return text


# ─────────────────────────────────────────────────────────────
# CONVERSATION SYSTEM
# ─────────────────────────────────────────────────────────────


class ConversationSystem:
    """Morrowind-style topic-based conversation system.

    Tracks which topics each character has discovered, manages topic unlocking
    through conversation, and generates NPC responses based on knowledge,
    trust, and personality.
    """

    def __init__(self, relationship_manager=None):
        self._relationship_manager = relationship_manager
        self._known_topics = {}  # character_id -> set of topic keys

    def init_starting_topics(self, character_id):
        """Add all topics marked as starting=True to the character's known set."""
        if character_id not in self._known_topics:
            self._known_topics[character_id] = set()
        for topic_key, topic_data in TOPICS.items():
            if topic_data.get("starting", False):
                self._known_topics[character_id].add(topic_key)

    def get_known_topics(self, character_id):
        """Return a sorted list of topic keys the character knows."""
        topics = self._known_topics.get(character_id, set())
        return sorted(topics)

    def discover_topic(self, character_id, topic_key):
        """Add a topic to the character's known set.

        Returns True if the topic was newly discovered, False if already known.
        """
        if topic_key not in TOPICS:
            return False
        if character_id not in self._known_topics:
            self._known_topics[character_id] = set()
        if topic_key in self._known_topics[character_id]:
            return False
        self._known_topics[character_id].add(topic_key)
        return True

    def can_ask_topic(self, character_id, topic_key, player_skills):
        """Check if the character knows the topic and meets the skill gate.

        Args:
            character_id: the character asking
            topic_key: the topic to ask about
            player_skills: dict of skill_name -> skill_level

        Returns True if the topic is known and any skill gate is met.
        """
        known = self._known_topics.get(character_id, set())
        if topic_key not in known:
            return False

        topic_data = TOPICS.get(topic_key)
        if topic_data is None:
            return False

        skill_gate = topic_data.get("skill_gate")
        if skill_gate is not None:
            skill_name, min_level = skill_gate
            if player_skills.get(skill_name, 0) < min_level:
                return False

        return True

    def get_available_topics(
        self, character_id, npc_type, player_skills, relationship_score
    ):
        """Return list of topic keys the player can ask this NPC about.

        A topic is available if:
        - The character knows it (discovered)
        - The player meets the skill gate
        - The topic category is not blocked by the current trust level
        - The NPC has knowledge about it (knowledge > 0)

        Args:
            character_id: the character asking
            npc_type: NPC archetype string (e.g. "farmer", "samurai")
            player_skills: dict of skill_name -> skill_level
            relationship_score: int relationship score with this NPC

        Returns sorted list of available topic keys.
        """
        blocked_cats = _get_blocked_categories(relationship_score)
        available = []

        for topic_key in self.get_known_topics(character_id):
            if not self.can_ask_topic(character_id, topic_key, player_skills):
                continue

            topic_data = TOPICS.get(topic_key)
            if topic_data is None:
                continue

            # Check category block from trust level
            if topic_data.get("category") in blocked_cats:
                continue

            # Check NPC has knowledge
            knowledge = self.get_npc_knowledge(topic_key, npc_type)
            if knowledge <= 0:
                continue

            available.append(topic_key)

        return sorted(available)

    def get_npc_knowledge(self, topic_key, npc_type):
        """Look up knowledge score for an NPC type on a topic.

        Returns 0 if topic or NPC type not found.
        """
        topic_data = TOPICS.get(topic_key)
        if topic_data is None:
            return 0
        return topic_data["knowledge_by_type"].get(npc_type, 0)

    def get_response(
        self, topic_key, npc_id, npc_type, npc_traits, relationship_score, rng
    ):
        """Generate a response for an NPC on a topic.

        Args:
            topic_key: the topic being asked about
            npc_id: the NPC's character id
            npc_type: NPC archetype string
            npc_traits: list of trait keys for this NPC
            relationship_score: int relationship score with the player
            rng: random.Random instance for selecting templates

        Returns:
            (response_text, effective_knowledge_level) tuple
        """
        base_knowledge = self.get_npc_knowledge(topic_key, npc_type)
        trust_mod = _get_trust_modifier(relationship_score)
        effective_knowledge = base_knowledge * trust_mod

        tier_label = _knowledge_tier_label(effective_knowledge)

        # Select response template
        if tier_label == "none":
            templates = _NONE_GENERIC
        else:
            topic_templates = RESPONSE_TEMPLATES.get(topic_key, _FALLBACK_TEMPLATES)
            templates = topic_templates.get(
                tier_label, _FALLBACK_TEMPLATES.get(tier_label, _VAGUE_GENERIC)
            )

        text = rng.choice(templates)

        # Fill placeholders with defaults
        text = text.replace("{npc_name}", str(npc_id))
        text = text.replace("{location}", "this area")
        text = text.replace("{faction}", "the local clan")

        # Apply trait-based modifiers
        text = _apply_trait_modifiers(text, npc_traits)

        return text, int(effective_knowledge)

    def check_topic_unlock(self, character_id, topic_key, npc_knowledge, rng):
        """After asking about a topic, check if linked topics are discovered.

        For each topic that lists topic_key in its unlock_from, roll a chance
        to discover it. Chance = TOPIC_DISCOVER_BASE_CHANCE * (npc_knowledge / 100).

        Args:
            character_id: the character who asked
            topic_key: the topic that was discussed
            npc_knowledge: the NPC's knowledge score on the topic (0-100)
            rng: random.Random instance

        Returns list of newly discovered topic keys.
        """
        newly_discovered = []
        discover_chance = TOPIC_DISCOVER_BASE_CHANCE * (npc_knowledge / 100)

        for candidate_key, candidate_data in TOPICS.items():
            if topic_key not in candidate_data.get("unlock_from", []):
                continue

            # Already known?
            known = self._known_topics.get(character_id, set())
            if candidate_key in known:
                continue

            if rng.random() < discover_chance:
                if self.discover_topic(character_id, candidate_key):
                    newly_discovered.append(candidate_key)

        return newly_discovered

    def to_save_data(self):
        """Serialize conversation state for saving."""
        data = {}
        for char_id, topics in self._known_topics.items():
            data[str(char_id)] = sorted(topics)
        return {"known_topics": data}

    @classmethod
    def from_save_data(cls, data, relationship_manager=None):
        """Restore a ConversationSystem from serialized data."""
        system = cls(relationship_manager=relationship_manager)
        known = data.get("known_topics", {})
        for char_id, topic_list in known.items():
            system._known_topics[char_id] = set(topic_list)
        return system
