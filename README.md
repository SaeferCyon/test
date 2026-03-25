# 縁起 ENGI — A Feudal Japan Society Simulation Roguelike

A mechanically dense, geographically accurate open-world society simulation
roguelike set in Sengoku-era (1467–1615) Japan. Inspired by Nethack, Cataclysm:
Dark Days Ahead, Morrowind, and Crusader Kings.

---

## REQUIREMENTS

- Python 3.7+
- Terminal: minimum 120×40, recommended 140×45+
- `curses` (built-in on macOS/Linux; Windows needs `pip install windows-curses`)

---

## RUNNING THE GAME

```bash
cd engi/
python3 engi.py
```

Or directly:
```bash
python3 game.py
```

---

## THE WORLD

Japan's entire main island chain is represented on a 240×130 grid:
- **Hokkaido** — Northern wilderness, Ainu borderlands, Matsumae clan
- **Honshu** — The main island. Tohoku, Kanto, Chubu, Kinki, Chugoku
- **Shikoku** — Chosokabe territory, 88-temple pilgrimage route
- **Kyushu** — Shimazu, Portuguese firearms, foreign trade at Nagasaki
- **Smaller islands** — Tsushima, Iki, Sado, Awaji, Oshima

**Geographic accuracy:**
- Proportionally correct island shapes from real lat/lon polygon outlines
- 38 historical cities placed at real coordinates (Edo, Kyoto, Osaka, Sendai…)
- Mountain ranges at accurate positions (Northern Alps, Ou Range, Daisetsuzan…)
- 13 major rivers (Shinano, Tone, Mogami, Yodo, Ishikari…)
- Elevation-based terrain (T_HIGH_PEAK near Mt. Fuji at 35.36°N 138.73°E)
- Hot springs near volcanic zones (Fuji, Aso, Zao, Hakone, Akan)

---

## MECHANICS

### SURVIVAL
Every turn matters. Track **Hunger**, **Thirst**, **Fatigue**, and **Warmth**.
- Forage [F], Fish [f], Hunt [H], or set Traps [t]
- Start fires in cold weather with flint + wood
- Sleep quality depends on terrain and shelter
- Conditions: Bleeding, Poisoned, Fever, Hypothermia, Exhaustion, and more
- Seasons change. Winter in Tohoku will kill the unprepared.

### COMBAT
Turn-based with stances and techniques:
- **Stances:** Balanced / Aggressive / Defensive / Mobile
- **Techniques:** Strike, Feint, Power Strike, Riposte, Parry, Dodge, Throw, Aimed Shot
- **Skills:** Kenjutsu, Kyujutsu (archery), Jujutsu (grappling), Naginata, Teppo (firearms)
- Wounds cause Bleeding, Dizziness, and morale penalties
- Enemy AI uses morale — battered foes may flee

### DEBATE (辯論)
Japan's political and social landscape runs on rhetoric as much as steel.
- Debate any NPC with [D] — win to change attitudes, gain honor, improve faction rep
- **8 argument types:** Logical, Emotional, Evidence, Authority, Rhetoric, Intimidation, Bribery, Concede
- Momentum bar shifts with each exchange. Hit 80+ to win; fall to 20 and you lose.
- Counter-argument relationships matter — emotional appeals fail against cold logic
- High honor amplifies authority arguments; high combat skill backs intimidation

### SKILLS (1–10)
Kenjutsu · Kyujutsu · Jujutsu · Naginata · Stealth · Rhetoric · Survival · Medicine · Teppo

Skills improve through use. Use your sword — it improves. Win debates — Rhetoric grows.

### FACTIONS & HONOR
- **Honor** (0–100) affects dialog options, argument power, and NPC reactions
- **Faction reputation** with Tokugawa, Imperial, Temple, Merchant, Bandits, and more
- Kill civilians → lose honor. Win debates → gain it. Flee from battle → lose it.

### CONVERSATIONS (Morrowind-style)
Talk to NPCs by selecting from a growing list of **topics** you've discovered.
- Start with 5 basic topics (Greetings, Directions, Weather, Local News, Trade)
- Discover new topics through conversation — asking about trade might reveal Trade Routes
- Every NPC can be asked any known topic — responses vary by their knowledge, personality, and relationship with you
- NPC knowledge depends on their profession, location, and faction
- Some topics are skill-gated — need Medicine 2+ to discuss healing arts
- Trust matters: hostile NPCs won't share personal topics or rumors

### TRAITS (Crusader Kings-style)
Every character has personality traits that define how they interact with the world.
- **55 traits** across 5 categories: Personality, Education, Lifestyle, Congenital, Physical
- Conflicting traits can't coexist (Brave vs Cowardly, Honest vs Deceitful)
- Complementary traits synergize (Brave + Loyal, Scholar + Patient)
- Some traits are hidden until discovered through conversation or observation
- Congenital traits (Genius, Strong, Beautiful) can be inherited by children
- Physical traits (Scarred, Maimed, One-Eyed) acquired through combat injuries
- Traits affect: combat, dialog, relationships, skill learning, social interactions

### RELATIONSHIPS & MEMORIES
Characters remember how you treat them.
- Relationship score (-100 to 100): Stranger → Acquaintance → Friend → Close Friend / Rival → Enemy
- Family ties: parent, child, sibling, spouse
- **Memories**: NPCs remember if you helped them, stole from them, or insulted their family
- Memories decay over time but never fully disappear — "forgiven but not forgotten"
- **Gossip**: NPCs share memories with each other, spreading your reputation
- **Blood feuds**: harm one family member and the whole family may turn against you
- NPC-to-NPC relationships form and break autonomously

### SOCIAL HIERARCHY
Sengoku Japan has a strict class system. Your rank determines what you can do.
- **Ranks**: Emperor > Shogun > Daimyo > Samurai > Ashigaru > Merchant > Artisan > Farmer > Eta
- Higher ranks can coerce lower ranks in conversation
- Rank affects: where you can go, who talks to you, prices, available actions
- **Social mobility**: a farmer can become an ashigaru, a merchant can buy samurai status
- **Disguises**: fake your rank with the right equipment — but checkpoints may catch you

### BODY & INJURIES
Combat wounds target specific body parts with lasting consequences.
- **27 body zones**: head, face, eyes, ears, neck, chest, abdomen, arms, hands, legs, feet, internal organs
- **Injury types**: bruises, cuts, deep wounds, fractures, severed limbs, burns
- **Permanent effects**: lose an eye (halved ranged accuracy), lose a hand (can't dual wield), lose a leg (movement penalty)
- Wound infection model — untreated wounds can become infected and kill
- Medical treatment: bandaging, herbal medicine, surgery, amputation
- **6 diseases**: plague, dysentery, fever, smallpox, malaria, tetanus

### LIFE & DYNASTY
Live a full life in Sengoku Japan. Grow old. Start a family. Die. Continue as your heir.
- **Aging**: stats change across 6 life stages (child → young adult → prime → middle age → old → elderly)
- **Courtship & Marriage**: requires relationship threshold + compatible traits
- **Children**: inherit traits from parents (congenital by genetics, personality by upbringing)
- **Death**: old age, combat, illness, execution
- **Play as your heir**: when you die, continue as your oldest living child
- **Family tree**: track your lineage across generations

### RANDOM ENCOUNTERS
The travel map is alive with people going about their business.
- Merchants follow trade routes, pilgrims walk temple circuits, armies march to war
- Encounter type varies by terrain, season, time of day, and active wars
- Night travel is more dangerous — higher chance of hostile encounters
- Some encounters become recurring characters you meet again later

---

## CLASSES

| Class | Strength | Weakness | Starting Region |
|-------|----------|----------|-----------------|
| 浪人 Ronin | Swordsmanship | Low honor, no clan | Anywhere |
| 侍 Samurai | Balanced warrior | Clan obligations | Kanto/Kinki |
| 忍者 Ninja | Stealth, medicine | Terrible in open combat | Any |
| 僧 Warrior Monk | Naginata, healing, rhetoric | No money | Temple areas |
| 商人 Merchant | Rhetoric, money, contacts | Frail | Kinki/Kyushu |
| 狩人 Hunter | Archery, survival, stealth | Social skills | Tohoku/Kyushu |

---

## KEY CONTROLS

```
MOVEMENT   h j k l  (←↓↑→)   y u b n  (diagonals)
           Arrow keys or numpad also work

ACTIONS
  .   Wait            ,   Pick up item        i   Inventory
  e   Eat/Drink       a   Apply/Use item      d   Drop item
  w   Equip           r   Rest (10 turns)     R   Sleep till dawn
  s   Sneak toggle    F   Forage              H   Hunt
  f   Fish            t   Set trap            x   Examine location

SOCIAL
  T / Enter   Talk to adjacent NPC (topic-based conversation)
  D           Challenge to debate
  B           Trade/Bribe
  G           Gift item to NPC
  P           View relationship with adjacent NPC

COMBAT (when in combat overlay)
  1   Strike            2   Feint & Strike
  3   Power Strike      4   Parry
  5   Dodge             6   Riposte
  7   Throw             8   Aimed Shot
  Tab Cycle stance      Esc Flee

DEBATE (when in debate overlay)
  1   Logical           2   Emotional
  3   Present Evidence  4   Cite Authority
  5   Rhetorical        6   Intimidation
  7   Bribery           8   Concede
  Esc Withdraw

CONVERSATION (when talking to NPC)
  j/k         Scroll topic list
  Enter       Ask about selected topic
  Esc         End conversation

INTERFACE
  M   World map         @   Character sheet
  ?   Help              Q   Quit
  Tab Cycle stance (outside combat)
  V   View family tree
  R   Relationship list (known NPCs)
```

---

## TERRAIN

```
.  Plains / Beach      "  Farmland / Rice Paddy    T  Forest / Pine / Bamboo
^  Mountain / Peak     ~  River / Sea              ≈  Deep Sea / Swamp
#  Town                ♦  Castle Town              ☆  Temple
Δ  Village             ⚓  Port Town               ♨  Hot Spring
%  Ruins               ·  Road
```

---

## TIPS

1. **Eat before you're hungry.** Survival stats degrade faster than you expect.
2. **Roads are fast.** Off-road in mountains costs 3-4× move points.
3. **Monks and Yamabushi know medicine.** Talk to them; their advice is free.
4. **Ronin will work for coin.** A skilled ronin as an ally changes everything.
5. **Debates avoid bloodshed.** Winning a debate costs nothing but Ki.
6. **Hot springs heal.** If you find one, camp nearby.
7. **Night reduces FOV.** Light a lantern or stay on the road.
8. **Bandits on mountain passes.** The eastern Tokaido road is safer than the Nakasendo.
9. **Kagoshima Shimazu are the strongest.** Don't pick a fight until you're ready.
10. **The merchant in Sakai sells Portuguese goods.** Teppo and Nanban medicine. Worth the trip.

---

## FILE STRUCTURE

```
engi/
├── engi.py       — Launcher
├── game.py       — Main game loop & input handling
├── renderer.py   — Curses terminal renderer
├── world.py      — World generation & geography
├── entities.py      — Player, NPC, item entities (with traits, body, family)
├── mechanics.py     — Combat, debate, survival systems
├── data.py          — All static game data
├── trait_data.py    — 55 CK-style traits with conflict/complement matrices
├── body_data.py     — 27 body zones, injury types, diseases, treatments
├── social_data.py   — Social hierarchy ranks, privileges, mobility paths
├── topic_data.py    — 24 Morrowind-style conversation topics
├── traits.py        — Trait engine (assignment, inheritance, compatibility)
├── body.py          — Body/injury system (hit locations, dismemberment)
├── memories.py      — Memory system (recall, gossip, decay)
├── relationships.py — Relationship graph (NPC-NPC, feuds, family ties)
├── conversations.py — Topic-based conversation system
├── life_sim.py      — Dynasty simulation (aging, marriage, children, heir)
├── encounters.py    — Dynamic random encounters on travel map
├── event_bus.py     — Observer pattern event coordination
├── design_doc.md    — Game design document
└── README.md        — This file
```

---

*"The bamboo that bends in the storm does not break."*
