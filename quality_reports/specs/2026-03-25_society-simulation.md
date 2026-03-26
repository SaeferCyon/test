## Requirements Summary

**Domain**: Game Engine (NPC AI, dialog, social simulation, life cycle)
**Goal**: Transform ENGI from a survival roguelike into a society simulation roguelike with Morrowind-style conversations, CK-inspired traits, full relationship/memory networks, dynasty simulation, realistic body system, dynamic social hierarchy, and emergent NPC encounters.
**Complexity**: Complex (7+ new modules, 4+ modified files)
**Approach**: A — Modular Systems with event bus coordination

### Functional Requirements

- [FR-1]: **Trait System (CK-style, 50+ traits)**
  - Categories: education, personality, lifestyle, congenital, physical
  - Conflict rules: certain traits mutually exclusive (brave/cowardly, honest/deceitful)
  - Complement rules: some traits synergize (strategic + patient)
  - Trait inheritance for children (genetic + environmental)
  - Mix of visible and hidden traits (hidden until discovered via conversation/observation)
  - Player can choose or randomly assign traits at character creation
  - NPCs assigned traits at spawn based on type, faction, background
  - Acceptance: 50+ defined traits with conflict/complement matrix, visible in character sheet

- [FR-2]: **Morrowind-style Conversation System**
  - Global topic list grows as player discovers topics through conversation
  - Every NPC can be asked any known topic
  - NPC response varies by: knowledge (0-100 per topic), personality traits, faction, relationship with player, social class
  - Talking about topic X can unlock new topic Y
  - Skills affect conversation options (rhetoric unlocks persuasion topics, survival unlocks nature topics)
  - NPC knowledge based on: profession, location, faction, personal experience
  - Replace current static dialog system
  - Acceptance: Topic list visible in dialog UI, responses contextual, new topics discoverable

- [FR-3]: **Relationship System**
  - Relationship types: stranger, acquaintance, friend, close friend, rival, enemy, lover, spouse, family
  - Familial ties: parent, child, sibling, in-law, clan member
  - Relationship score (-100 to 100) with named thresholds
  - Factors: shared traits (complement/conflict), social class compatibility, faction alignment, shared memories, gifts, time spent
  - NPC-to-NPC relationships: NPCs form/break relationships autonomously
  - Gossip system: information and opinions spread through social networks
  - Player actions affecting one NPC ripple to connected NPCs
  - Blood feuds: conflicts between families that span generations
  - Acceptance: Relationship visible in NPC info, changes based on player actions

- [FR-4]: **Memory System**
  - Characters remember specific interactions (helped, harmed, insulted, protected, stole from, etc.)
  - Memory types: witnessed events, personal interactions, heard gossip
  - Memories have: event type, participants, location, time, emotional impact
  - Memories decay over time but never fully disappear ("forgiven but not forgotten")
  - Memories influence: relationship score, dialog options, NPC behavior
  - NPCs share memories through gossip
  - Acceptance: NPC references past interactions in dialog, relationship affected by history

- [FR-5]: **Life Simulation (Dynasty)**
  - Aging: characters age over game time, stats change with age
  - Courtship and marriage: requires relationship threshold + compatible traits
  - Children: born from marriages, inherit traits (genetic + environmental)
  - Children grow up: become playable NPCs or the player's heir
  - Death: old age, combat, illness, execution
  - Play as heir on death (dynasty continuation)
  - Illness: disease model with contagion, treatment, recovery/death
  - Family tree tracking visible to player
  - Acceptance: Player can marry, have children, die of old age, continue as heir

- [FR-6]: **Body Part System (Realistic, 20+ zones)**
  - Zones: head (skull, face, eyes L/R, ears L/R, jaw), neck, chest, abdomen, back
  - Arms: upper arm L/R, forearm L/R, hand L/R (individual fingers)
  - Legs: thigh L/R, shin L/R, foot L/R
  - Internal: lungs, heart, stomach, liver (for deep wounds)
  - Injury types: bruise, cut, deep wound, fracture, severed, crushed
  - Permanent effects: lost limb, scarring, blindness, deafness, limp
  - Medical treatment: bandaging, surgery, herbal medicine, time
  - Wound infection model
  - Combat targets body parts (aimed attacks, random hit location)
  - Acceptance: Injuries visible on character sheet, permanent effects on gameplay

- [FR-7]: **Social Hierarchy (Dynamic)**
  - Ranks: Emperor > Shogun > Daimyo > Samurai > Ashigaru > Merchant > Artisan > Farmer > Eta
  - Higher rank can intimidate/coerce lower rank in conversation
  - Lower rank shows deference (affects dialog options)
  - Social mobility: achievements can raise status (merchant buys samurai status, farmer becomes ashigaru)
  - Disguises: can fake status (checked at checkpoints, risk of discovery)
  - Rank affects: where you can go, who talks to you, prices, quest availability
  - Acceptance: Rank visible, affects all social interactions

- [FR-8]: **Random Encounters (Fully Dynamic)**
  - NPCs actually travel between locations on the region map
  - Armies on campaign move between territories
  - Refugees flee from wars
  - Merchants follow trade routes
  - Pilgrims walk temple circuits
  - Encounters are real NPCs met on the road, not templates
  - Encounter type varies by: terrain, season, faction territory, time of day, current wars
  - Some encounters become recurring characters
  - Acceptance: Travel map has moving NPCs, encounter them naturally

- [FR-9]: **Recruitment and Trading**
  - Skill-based: rhetoric and relationship affect success
  - Recruit NPCs as companions (requires relationship + compatible traits)
  - Trading system: barter and money, prices affected by relationship and social class
  - Acceptance: Can recruit NPCs and trade with contextual prices

### Non-Functional Requirements

- [NFR-1]: NPC relationship/memory processing should not cause noticeable frame lag
- [NFR-2]: Gossip propagation should be lazy (not every NPC every tick)
- [NFR-3]: Save/load must capture all new state (traits, relationships, memories, family trees)

### Constraints

- Pure Python, curses renderer
- Must integrate with existing combat, debate, survival systems
- This branch is off main (no dual-map system from feature-1774377928)
- Existing NPC types and data preserved, extended with new attributes

### Scope Boundary

**IN scope**: Trait system, conversation overhaul, relationships, memories, life simulation, body parts, social hierarchy, dynamic encounters, recruitment, trading, README update, keybinding additions

**OUT of scope**: Graphical UI, multiplayer, mod system, voice acting, procedural quest generation

### Assumptions

- Current dialog system (DIALOGS dict in data.py) will be replaced, not extended
- Existing NPC spawn system continues to work with new trait/relationship data added at spawn
- Event bus is a simple observer pattern, not a distributed system

### Implementation Strategy (Architecture-first)

1. Core data: trait definitions, body zones, social ranks, topic registry
2. Trait engine + body part system
3. Memory system + relationship manager
4. Conversation system (Morrowind-style topic replacement)
5. Life simulation (aging, marriage, children, dynasty)
6. Social hierarchy + coercion mechanics
7. Dynamic encounters on travel map
8. Entity integration (Player + NPC extensions)
9. Game loop + renderer wiring
10. README and keybinding updates
