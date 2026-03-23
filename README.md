# 縁起 ENGI — A Feudal Japan Roguelike

A mechanically dense, geographically accurate open-world roguelike set in
Sengoku-era (1467–1615) Japan. Inspired by Nethack and Cataclysm: Dark Days Ahead.

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
  T / Enter   Talk to adjacent NPC
  D           Challenge to debate
  B           Trade/Bribe

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

INTERFACE
  M   World map         @   Character sheet
  ?   Help              Q   Quit
  Tab Cycle stance (outside combat)
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
├── entities.py   — Player, NPC, item entities
├── mechanics.py  — Combat, debate, survival systems
├── data.py       — All static game data
└── README.md     — This file
```

---

*"The bamboo that bends in the storm does not break."*
