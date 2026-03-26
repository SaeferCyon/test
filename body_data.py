"""
body_data.py - Realistic Body Zone System for ENGI
20+ body zones with injury types, permanent effects, and healing.
"""

# ─────────────────────────────────────────────────────────────
# BODY ZONES (20+ zones organized by region)
# ─────────────────────────────────────────────────────────────
ZONE_HEAD = "head"
ZONE_FACE = "face"
ZONE_LEFT_EYE = "left_eye"
ZONE_RIGHT_EYE = "right_eye"
ZONE_LEFT_EAR = "left_ear"
ZONE_RIGHT_EAR = "right_ear"
ZONE_JAW = "jaw"
ZONE_NECK = "neck"
ZONE_CHEST = "chest"
ZONE_ABDOMEN = "abdomen"
ZONE_BACK = "back"
ZONE_LEFT_UPPER_ARM = "left_upper_arm"
ZONE_RIGHT_UPPER_ARM = "right_upper_arm"
ZONE_LEFT_FOREARM = "left_forearm"
ZONE_RIGHT_FOREARM = "right_forearm"
ZONE_LEFT_HAND = "left_hand"
ZONE_RIGHT_HAND = "right_hand"
ZONE_LEFT_THIGH = "left_thigh"
ZONE_RIGHT_THIGH = "right_thigh"
ZONE_LEFT_SHIN = "left_shin"
ZONE_RIGHT_SHIN = "right_shin"
ZONE_LEFT_FOOT = "left_foot"
ZONE_RIGHT_FOOT = "right_foot"
# Internal (only damaged by deep wounds)
ZONE_LUNGS = "lungs"
ZONE_HEART = "heart"
ZONE_STOMACH = "stomach"
ZONE_LIVER = "liver"

# ─────────────────────────────────────────────────────────────
# ZONE DEFINITIONS
# ─────────────────────────────────────────────────────────────
BODY_ZONES = {
    ZONE_HEAD: {
        "name": "Head (Skull)",
        "region": "head",
        "vital": True,
        "armor_slot": "head",
        "hit_weight": 5,
        "sever": False,
        "internal": False,
        "desc": "Protected by the skull. Blows here cause dizziness or death.",
    },
    ZONE_FACE: {
        "name": "Face",
        "region": "head",
        "vital": False,
        "armor_slot": "head",
        "hit_weight": 3,
        "sever": False,
        "internal": False,
        "desc": "Exposed skin. Scars here are visible to all.",
    },
    ZONE_LEFT_EYE: {
        "name": "Left Eye",
        "region": "head",
        "vital": False,
        "armor_slot": "head",
        "hit_weight": 1,
        "sever": False,
        "internal": False,
        "desc": "Losing an eye halves ranged accuracy.",
    },
    ZONE_RIGHT_EYE: {
        "name": "Right Eye",
        "region": "head",
        "vital": False,
        "armor_slot": "head",
        "hit_weight": 1,
        "sever": False,
        "internal": False,
        "desc": "Losing an eye halves ranged accuracy.",
    },
    ZONE_LEFT_EAR: {
        "name": "Left Ear",
        "region": "head",
        "vital": False,
        "armor_slot": "head",
        "hit_weight": 1,
        "sever": True,
        "internal": False,
        "desc": "Losing an ear reduces hearing and awareness.",
    },
    ZONE_RIGHT_EAR: {
        "name": "Right Ear",
        "region": "head",
        "vital": False,
        "armor_slot": "head",
        "hit_weight": 1,
        "sever": True,
        "internal": False,
        "desc": "Losing an ear reduces hearing and awareness.",
    },
    ZONE_JAW: {
        "name": "Jaw",
        "region": "head",
        "vital": False,
        "armor_slot": "head",
        "hit_weight": 2,
        "sever": False,
        "internal": False,
        "desc": "Broken jaw impairs speech and eating.",
    },
    ZONE_NECK: {
        "name": "Neck",
        "region": "head",
        "vital": True,
        "armor_slot": "body",
        "hit_weight": 2,
        "sever": True,
        "internal": False,
        "desc": "Extremely vulnerable. Cuts here are often fatal.",
    },
    ZONE_CHEST: {
        "name": "Chest",
        "region": "torso",
        "vital": True,
        "armor_slot": "body",
        "hit_weight": 12,
        "sever": False,
        "internal": False,
        "desc": "Ribcage protects the heart and lungs.",
    },
    ZONE_ABDOMEN: {
        "name": "Abdomen",
        "region": "torso",
        "vital": True,
        "armor_slot": "body",
        "hit_weight": 8,
        "sever": False,
        "internal": False,
        "desc": "Gut wounds are slow killers. Infection is near-certain.",
    },
    ZONE_BACK: {
        "name": "Back",
        "region": "torso",
        "vital": False,
        "armor_slot": "body",
        "hit_weight": 6,
        "sever": False,
        "internal": False,
        "desc": "Spine damage can paralyze.",
    },
    ZONE_LEFT_UPPER_ARM: {
        "name": "Left Upper Arm",
        "region": "left_arm",
        "vital": False,
        "armor_slot": "body",
        "hit_weight": 4,
        "sever": True,
        "internal": False,
        "desc": "Major blood vessels here. Severing disables the arm.",
    },
    ZONE_RIGHT_UPPER_ARM: {
        "name": "Right Upper Arm",
        "region": "right_arm",
        "vital": False,
        "armor_slot": "body",
        "hit_weight": 4,
        "sever": True,
        "internal": False,
        "desc": "Major blood vessels here. Severing disables the arm.",
    },
    ZONE_LEFT_FOREARM: {
        "name": "Left Forearm",
        "region": "left_arm",
        "vital": False,
        "armor_slot": "hands",
        "hit_weight": 4,
        "sever": True,
        "internal": False,
        "desc": "Defensive wounds are common here.",
    },
    ZONE_RIGHT_FOREARM: {
        "name": "Right Forearm",
        "region": "right_arm",
        "vital": False,
        "armor_slot": "hands",
        "hit_weight": 4,
        "sever": True,
        "internal": False,
        "desc": "Defensive wounds are common here.",
    },
    ZONE_LEFT_HAND: {
        "name": "Left Hand",
        "region": "left_arm",
        "vital": False,
        "armor_slot": "hands",
        "hit_weight": 3,
        "sever": True,
        "internal": False,
        "desc": "Losing fingers impairs grip. Losing the hand ends weapon use.",
    },
    ZONE_RIGHT_HAND: {
        "name": "Right Hand",
        "region": "right_arm",
        "vital": False,
        "armor_slot": "hands",
        "hit_weight": 3,
        "sever": True,
        "internal": False,
        "desc": "The weapon hand. Losing it is devastating for a warrior.",
    },
    ZONE_LEFT_THIGH: {
        "name": "Left Thigh",
        "region": "left_leg",
        "vital": False,
        "armor_slot": "legs",
        "hit_weight": 5,
        "sever": True,
        "internal": False,
        "desc": "Femoral artery. Deep cuts here bleed fast.",
    },
    ZONE_RIGHT_THIGH: {
        "name": "Right Thigh",
        "region": "right_leg",
        "vital": False,
        "armor_slot": "legs",
        "hit_weight": 5,
        "sever": True,
        "internal": False,
        "desc": "Femoral artery. Deep cuts here bleed fast.",
    },
    ZONE_LEFT_SHIN: {
        "name": "Left Shin",
        "region": "left_leg",
        "vital": False,
        "armor_slot": "legs",
        "hit_weight": 4,
        "sever": True,
        "internal": False,
        "desc": "Shin guards exist for a reason.",
    },
    ZONE_RIGHT_SHIN: {
        "name": "Right Shin",
        "region": "right_leg",
        "vital": False,
        "armor_slot": "legs",
        "hit_weight": 4,
        "sever": True,
        "internal": False,
        "desc": "Shin guards exist for a reason.",
    },
    ZONE_LEFT_FOOT: {
        "name": "Left Foot",
        "region": "left_leg",
        "vital": False,
        "armor_slot": "legs",
        "hit_weight": 2,
        "sever": True,
        "internal": False,
        "desc": "Losing a foot means crutches or a peg.",
    },
    ZONE_RIGHT_FOOT: {
        "name": "Right Foot",
        "region": "right_leg",
        "vital": False,
        "armor_slot": "legs",
        "hit_weight": 2,
        "sever": True,
        "internal": False,
        "desc": "Losing a foot means crutches or a peg.",
    },
    # Internal organs (only from deep wounds to torso)
    ZONE_LUNGS: {
        "name": "Lungs",
        "region": "internal",
        "vital": True,
        "armor_slot": "body",
        "hit_weight": 0,
        "sever": False,
        "internal": True,
        "desc": "Punctured lung. Drowning in air.",
    },
    ZONE_HEART: {
        "name": "Heart",
        "region": "internal",
        "vital": True,
        "armor_slot": "body",
        "hit_weight": 0,
        "sever": False,
        "internal": True,
        "desc": "Heart wound. Death in moments.",
    },
    ZONE_STOMACH: {
        "name": "Stomach",
        "region": "internal",
        "vital": True,
        "armor_slot": "body",
        "hit_weight": 0,
        "sever": False,
        "internal": True,
        "desc": "Stomach acid leaks. Slow, agonizing death without treatment.",
    },
    ZONE_LIVER: {
        "name": "Liver",
        "region": "internal",
        "vital": True,
        "armor_slot": "body",
        "hit_weight": 0,
        "sever": False,
        "internal": True,
        "desc": "Bleeds profusely. Fatal without immediate surgery.",
    },
}

# ─────────────────────────────────────────────────────────────
# INJURY TYPES
# ─────────────────────────────────────────────────────────────
INJ_BRUISE = "bruise"
INJ_CUT = "cut"
INJ_DEEP_WOUND = "deep_wound"
INJ_FRACTURE = "fracture"
INJ_SEVERED = "severed"
INJ_CRUSHED = "crushed"
INJ_BURNED = "burned"
INJ_INFECTED = "infected"

INJURY_TYPES = {
    INJ_BRUISE: {
        "name": "Bruise",
        "severity": 1,
        "bleed": False,
        "heal_days": 3,
        "pain": 1,
        "infection_chance": 0.0,
        "desc": "Painful but not dangerous. Discolored skin.",
    },
    INJ_CUT: {
        "name": "Cut",
        "severity": 2,
        "bleed": True,
        "heal_days": 7,
        "pain": 2,
        "infection_chance": 0.1,
        "desc": "Open wound. Needs bandaging to stop bleeding.",
    },
    INJ_DEEP_WOUND: {
        "name": "Deep Wound",
        "severity": 4,
        "bleed": True,
        "heal_days": 21,
        "pain": 4,
        "infection_chance": 0.3,
        "desc": "Penetrating wound. Risk of organ damage and infection.",
    },
    INJ_FRACTURE: {
        "name": "Fracture",
        "severity": 3,
        "bleed": False,
        "heal_days": 30,
        "pain": 5,
        "infection_chance": 0.05,
        "desc": "Broken bone. Immobilizes the area until healed.",
    },
    INJ_SEVERED: {
        "name": "Severed",
        "severity": 5,
        "bleed": True,
        "heal_days": -1,
        "pain": 6,
        "infection_chance": 0.5,
        "desc": "Permanently removed. Cannot be healed, only treated.",
    },
    INJ_CRUSHED: {
        "name": "Crushed",
        "severity": 4,
        "bleed": False,
        "heal_days": 30,
        "pain": 5,
        "infection_chance": 0.2,
        "desc": "Tissue destruction. May require amputation.",
    },
    INJ_BURNED: {
        "name": "Burned",
        "severity": 3,
        "bleed": False,
        "heal_days": 14,
        "pain": 5,
        "infection_chance": 0.4,
        "desc": "Fire damage. High infection risk, permanent scarring.",
    },
    INJ_INFECTED: {
        "name": "Infected",
        "severity": 3,
        "bleed": False,
        "heal_days": 14,
        "pain": 3,
        "infection_chance": 0.0,
        "desc": "Wound infection. Fever, pus, spreading redness. Needs medicine.",
    },
}

# ─────────────────────────────────────────────────────────────
# PERMANENT EFFECTS from injuries
# Maps (zone, injury_type) patterns to permanent trait/condition
# ─────────────────────────────────────────────────────────────
PERMANENT_EFFECTS = {
    # Eyes
    (ZONE_LEFT_EYE, INJ_SEVERED): {
        "trait": "one_eyed",
        "condition": "half_vision",
        "desc": "Lost the left eye.",
    },
    (ZONE_RIGHT_EYE, INJ_SEVERED): {
        "trait": "one_eyed",
        "condition": "half_vision",
        "desc": "Lost the right eye.",
    },
    # Both eyes gone = blind
    # Ears
    (ZONE_LEFT_EAR, INJ_SEVERED): {
        "trait": None,
        "condition": "reduced_hearing",
        "desc": "Left ear severed.",
    },
    (ZONE_RIGHT_EAR, INJ_SEVERED): {
        "trait": None,
        "condition": "reduced_hearing",
        "desc": "Right ear severed.",
    },
    # Hands
    (ZONE_LEFT_HAND, INJ_SEVERED): {
        "trait": "maimed",
        "condition": "no_left_hand",
        "desc": "Lost the left hand.",
    },
    (ZONE_RIGHT_HAND, INJ_SEVERED): {
        "trait": "maimed",
        "condition": "no_right_hand",
        "desc": "Lost the right hand. Cannot wield weapons normally.",
    },
    # Arms
    (ZONE_LEFT_UPPER_ARM, INJ_SEVERED): {
        "trait": "maimed",
        "condition": "no_left_arm",
        "desc": "Lost the left arm.",
    },
    (ZONE_RIGHT_UPPER_ARM, INJ_SEVERED): {
        "trait": "maimed",
        "condition": "no_right_arm",
        "desc": "Lost the right arm.",
    },
    # Legs
    (ZONE_LEFT_THIGH, INJ_SEVERED): {
        "trait": "maimed",
        "condition": "no_left_leg",
        "desc": "Lost the left leg.",
    },
    (ZONE_RIGHT_THIGH, INJ_SEVERED): {
        "trait": "maimed",
        "condition": "no_right_leg",
        "desc": "Lost the right leg.",
    },
    # Feet
    (ZONE_LEFT_FOOT, INJ_SEVERED): {
        "trait": "limping",
        "condition": "no_left_foot",
        "desc": "Lost the left foot.",
    },
    (ZONE_RIGHT_FOOT, INJ_SEVERED): {
        "trait": "limping",
        "condition": "no_right_foot",
        "desc": "Lost the right foot.",
    },
    # Face scarring
    (ZONE_FACE, INJ_DEEP_WOUND): {
        "trait": "scarred",
        "condition": None,
        "desc": "Deep facial scar.",
    },
    (ZONE_FACE, INJ_BURNED): {
        "trait": "disfigured",
        "condition": None,
        "desc": "Face burned beyond recognition.",
    },
    # Jaw
    (ZONE_JAW, INJ_FRACTURE): {
        "trait": None,
        "condition": "broken_jaw",
        "desc": "Broken jaw. Speech impaired.",
    },
    # Internal
    (ZONE_LUNGS, INJ_DEEP_WOUND): {
        "trait": None,
        "condition": "punctured_lung",
        "desc": "Lung punctured. Breathing labored.",
    },
    (ZONE_HEART, INJ_DEEP_WOUND): {
        "trait": None,
        "condition": "instant_death",
        "desc": "Heart pierced. Death.",
    },
}

# ─────────────────────────────────────────────────────────────
# HIT LOCATION TABLES
# Weighted random selection for combat hit locations.
# "aimed" tables used when player targets a specific region.
# ─────────────────────────────────────────────────────────────
HIT_TABLE_NORMAL = [
    # (zone, weight) — higher weight = more likely to be hit
    (ZONE_CHEST, 15),
    (ZONE_ABDOMEN, 10),
    (ZONE_LEFT_UPPER_ARM, 6),
    (ZONE_RIGHT_UPPER_ARM, 6),
    (ZONE_LEFT_FOREARM, 5),
    (ZONE_RIGHT_FOREARM, 5),
    (ZONE_LEFT_THIGH, 5),
    (ZONE_RIGHT_THIGH, 5),
    (ZONE_LEFT_SHIN, 4),
    (ZONE_RIGHT_SHIN, 4),
    (ZONE_HEAD, 4),
    (ZONE_FACE, 3),
    (ZONE_LEFT_HAND, 3),
    (ZONE_RIGHT_HAND, 3),
    (ZONE_BACK, 5),
    (ZONE_NECK, 2),
    (ZONE_LEFT_FOOT, 2),
    (ZONE_RIGHT_FOOT, 2),
    (ZONE_JAW, 1),
    (ZONE_LEFT_EYE, 1),
    (ZONE_RIGHT_EYE, 1),
    (ZONE_LEFT_EAR, 1),
    (ZONE_RIGHT_EAR, 1),
]

# Internal organ hit chance when torso takes a deep wound
INTERNAL_HIT_CHANCE = {
    ZONE_CHEST: [(ZONE_LUNGS, 0.20), (ZONE_HEART, 0.05)],
    ZONE_ABDOMEN: [(ZONE_STOMACH, 0.15), (ZONE_LIVER, 0.10)],
    ZONE_BACK: [(ZONE_LUNGS, 0.10), (ZONE_LIVER, 0.05)],
}

# ─────────────────────────────────────────────────────────────
# MEDICAL TREATMENT
# ─────────────────────────────────────────────────────────────
TREATMENT_BANDAGE = "bandage"
TREATMENT_SURGERY = "surgery"
TREATMENT_HERBAL = "herbal"
TREATMENT_REST = "rest"
TREATMENT_AMPUTATION = "amputation"

TREATMENTS = {
    TREATMENT_BANDAGE: {
        "name": "Bandaging",
        "skill": "medicine",
        "min_skill": 1,
        "treats": [INJ_CUT, INJ_DEEP_WOUND, INJ_BURNED],
        "heal_bonus": 1.5,
        "bleed_stop": True,
        "desc": "Clean and bind the wound. Stops bleeding.",
    },
    TREATMENT_SURGERY: {
        "name": "Surgery",
        "skill": "medicine",
        "min_skill": 5,
        "treats": [INJ_DEEP_WOUND, INJ_FRACTURE, INJ_CRUSHED, INJ_INFECTED],
        "heal_bonus": 2.0,
        "bleed_stop": True,
        "desc": "Invasive treatment. High skill required.",
    },
    TREATMENT_HERBAL: {
        "name": "Herbal Medicine",
        "skill": "medicine",
        "min_skill": 2,
        "treats": [INJ_BRUISE, INJ_CUT, INJ_BURNED, INJ_INFECTED],
        "heal_bonus": 1.3,
        "bleed_stop": False,
        "desc": "Poultice and herb application. Reduces infection.",
    },
    TREATMENT_REST: {
        "name": "Rest",
        "skill": "medicine",
        "min_skill": 0,
        "treats": [INJ_BRUISE, INJ_FRACTURE],
        "heal_bonus": 1.0,
        "bleed_stop": False,
        "desc": "Time heals most wounds. Sleep and eat well.",
    },
    TREATMENT_AMPUTATION: {
        "name": "Amputation",
        "skill": "medicine",
        "min_skill": 4,
        "treats": [INJ_CRUSHED, INJ_INFECTED],
        "heal_bonus": 0.0,
        "bleed_stop": True,
        "desc": "Remove the damaged part to save the whole. Last resort.",
    },
}

# ─────────────────────────────────────────────────────────────
# DISEASE MODEL
# ─────────────────────────────────────────────────────────────
DISEASES = {
    "plague": {
        "name": "Plague",
        "contagion": 0.3,
        "severity": 5,
        "duration_days": 14,
        "mortality": 0.4,
        "symptoms": ["fever", "weakness", "pain"],
        "treatment": "herbal",
        "desc": "The great sickness. Kills villages.",
    },
    "dysentery": {
        "name": "Dysentery",
        "contagion": 0.2,
        "severity": 3,
        "duration_days": 10,
        "mortality": 0.15,
        "symptoms": ["thirst", "weakness", "pain"],
        "treatment": "herbal",
        "desc": "Bad water. Dehydration kills.",
    },
    "fever": {
        "name": "Fever",
        "contagion": 0.1,
        "severity": 2,
        "duration_days": 5,
        "mortality": 0.05,
        "symptoms": ["fever", "fatigue"],
        "treatment": "rest",
        "desc": "Common illness. Rest cures most.",
    },
    "smallpox": {
        "name": "Smallpox",
        "contagion": 0.4,
        "severity": 4,
        "duration_days": 21,
        "mortality": 0.3,
        "symptoms": ["fever", "disfigurement", "pain"],
        "treatment": "herbal",
        "desc": "Leaves permanent scars. Often fatal.",
    },
    "malaria": {
        "name": "Malaria",
        "contagion": 0.0,
        "severity": 3,
        "duration_days": 7,
        "mortality": 0.1,
        "symptoms": ["fever", "chills", "fatigue"],
        "treatment": "herbal",
        "desc": "Swamp sickness. Recurring bouts.",
    },
    "tetanus": {
        "name": "Tetanus",
        "contagion": 0.0,
        "severity": 4,
        "duration_days": 14,
        "mortality": 0.25,
        "symptoms": ["jaw_lock", "spasms", "pain"],
        "treatment": "surgery",
        "desc": "Lockjaw from dirty wounds. Deadly.",
    },
}
