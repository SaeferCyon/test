# Plan: Society Simulation Systems

**Ticket:** FR-1774474529 | **Milestone:** local | **Readiness:** 76/100
**Branch:** feature-request-1774474529

## Context

Transform ENGI from a survival roguelike into a society simulation roguelike per
design_doc.md. Add Morrowind-style conversations (global topic discovery), CK-inspired
trait system (50+ traits with inheritance), full relationship/memory networks with gossip,
dynasty simulation (marriage, children, play-as-heir), realistic body part system (20+
zones with dismemberment), dynamic social hierarchy, and emergent NPC encounters on the
travel map.

## Impact Analysis
- Files affected: 7 new + 4 modified = 11 total
- Highest risk: HIGH (entities.py extensions, game.py dialog replacement)
- This replaces the current dialog system entirely

## Approach
Modular Systems (Approach A): standalone module per system with event bus coordination.

## Tasks

### Task 1: Core Data — Traits, Body Zones, Social Ranks, Topics
- **Files:** trait_data.py, body_data.py, social_data.py, topic_data.py (all create)
- **Depends on:** none
- **Blocks:** 2, 3, 4, 5, 6, 7, 8
- **Size:** L
- **Description:** Define 50+ traits with categories (education, personality, lifestyle,
  congenital, physical), conflict/complement matrix. 20+ body zones with injury types
  and permanent effects. Social hierarchy ranks (Emperor→Eta) with privileges. Initial
  global topic registry with knowledge requirements.

### Task 2: Trait Engine
- **Files:** traits.py (create)
- **Depends on:** 1
- **Blocks:** 5, 6, 8
- **Size:** M
- **Description:** TraitManager with assign/remove/check_conflict/get_compatibility.
  Trait inheritance logic for parent→child. Trait discovery (hidden→visible). Trait
  effects on stats and social interactions.

### Task 3: Body Part System
- **Files:** body.py (create)
- **Depends on:** 1
- **Blocks:** 8
- **Size:** L
- **Description:** BodyMap with 20+ zones. Injury application with hit location and
  severity. Permanent effects (lost limb, blindness, scarring). Wound healing, infection,
  medical treatment. Combat integration for targeted attacks.

### Task 4: Memory System
- **Files:** memories.py (create)
- **Depends on:** 1
- **Blocks:** 5, 6, 8
- **Size:** M
- **Description:** Memory class (event_type, participants, location, time, impact).
  MemoryManager: add/recall/decay/share. Lazy gossip propagation. Memory influence
  on relationship scores and dialog.

### Task 5: Relationship Manager
- **Files:** relationships.py (create)
- **Depends on:** 1, 2, 4
- **Blocks:** 6, 8
- **Size:** L
- **Description:** Relationship graph (NPC↔NPC, NPC↔Player). Types: stranger→spouse/enemy.
  Score -100 to 100. Factors: traits, class, faction, memories. Autonomous NPC
  relationships. Blood feud tracking. Gossip-driven opinion spread.

### Task 6: Conversation System (Morrowind-style)
- **Files:** conversations.py (create)
- **Depends on:** 1, 2, 4, 5
- **Blocks:** 8, 9
- **Size:** L
- **Description:** Replace DIALOGS system. TopicRegistry: growing global topic list.
  NPCKnowledge: per-NPC knowledge scores. Response generation from knowledge + traits
  + relationship + class. Topic unlock chains. Skill-gated topics.

### Task 7: Life Simulation (Dynasty)
- **Files:** life_sim.py (create)
- **Depends on:** 1, 2, 3
- **Blocks:** 8
- **Size:** L
- **Description:** Aging with stat changes. Courtship (relationship + traits). Marriage,
  children with trait inheritance. Child growth. Death (age, combat, illness). Play-as-heir
  dynasty continuation. Family tree. Disease model with contagion.

### Task 8: Entity Extensions
- **Files:** entities.py (modify)
- **Depends on:** 1, 2, 3, 4, 5, 6, 7
- **Blocks:** 9, 10, 11
- **Size:** L
- **Description:** Extend Player: traits, body_map, family, social_rank, known_topics,
  age, memories_ref. Extend NPC: same + travel_destination, knowledge dict. Update
  character creation for trait selection. Social hierarchy coercion.

### Task 9: Dynamic Encounters
- **Files:** encounters.py (create)
- **Depends on:** 6, 8
- **Blocks:** 10
- **Size:** L
- **Description:** NPCs traveling between locations. Armies, refugees, merchants, pilgrims
  with real destinations. Encounter from simulation. Context: terrain, season, faction,
  time. Recurring characters.

### Task 10: Event Bus + Game Loop Integration
- **Files:** event_bus.py (create), game.py (modify), mechanics.py (modify)
- **Depends on:** 2, 3, 4, 5, 6, 7, 8, 9
- **Blocks:** 11
- **Size:** L
- **Description:** Event bus (observer pattern). Wire all systems into game loop: trait
  checks, relationship updates, memory creation, life sim tick, encounter checks,
  body part targeting in combat. Replace dialog handler.

### Task 11: Renderer + UI + README
- **Files:** renderer.py (modify), README.md (modify)
- **Depends on:** 8, 10
- **Blocks:** none
- **Size:** L
- **Description:** Morrowind-style topic list UI. Body status on character sheet.
  Relationship view. Family tree view. New keybindings. Updated README.

## File Ownership Matrix

| File | Task | Action |
|------|------|--------|
| trait_data.py | Task 1 | Create |
| body_data.py | Task 1 | Create |
| social_data.py | Task 1 | Create |
| topic_data.py | Task 1 | Create |
| traits.py | Task 2 | Create |
| body.py | Task 3 | Create |
| memories.py | Task 4 | Create |
| relationships.py | Task 5 | Create |
| conversations.py | Task 6 | Create |
| life_sim.py | Task 7 | Create |
| entities.py | Task 8 | Modify |
| encounters.py | Task 9 | Create |
| event_bus.py | Task 10 | Create |
| game.py | Task 10 | Modify |
| mechanics.py | Task 10 | Modify |
| renderer.py | Task 11 | Modify |
| README.md | Task 11 | Modify |

## Execution Waves

| Wave | Tasks | Parallel | Description |
|------|-------|----------|-------------|
| 1 | Task 1 | No | Core data definitions |
| 2 | Task 2, 3, 4 | Yes | Trait engine, body system, memory system |
| 3 | Task 5 | No | Relationship manager |
| 4 | Task 6, 7 | Yes | Conversations, life simulation |
| 5 | Task 8 | No | Entity extensions |
| 6 | Task 9 | No | Dynamic encounters |
| 7 | Task 10 | No | Event bus + game loop wiring |
| 8 | Task 11 | No | Renderer + README |

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Dialog replacement breaks NPC interactions | High | High | Keep DIALOGS as fallback data source |
| NPC relationship processing lag | Medium | Medium | Lazy gossip (1 hop per tick) |
| entities.py too large | Medium | Medium | Composition (refs to managers) |
| Body system makes combat too lethal | Medium | High | Tune injury thresholds |
| Dynasty play-as-heir state transfer | Medium | High | Fresh Player, copy family/rep |
| Trait inheritance degenerate | Low | Medium | Cap trait count, validate |

## Testing Strategy
- Unit: trait conflicts, relationship scoring, memory decay, body targeting, topic knowledge
- Integration: conversation flow, combat→injury→healing, marriage→child→heir
- Edge cases: all-conflict traits, no-knowledge NPC, zero-relationship gossip, orphan heir
- Regression: combat, debate, movement, survival

## Readiness Breakdown

| Dimension | Score | Notes |
|-----------|-------|-------|
| Requirements | 17/20 | LISA spec comprehensive |
| Codebase | 18/20 | Full codebase knowledge from prior work |
| Design | 14/20 | Modular approach clear; conversation replacement needs care |
| Risk | 12/20 | Dialog replacement and entity bloat are real risks |
| Operational | 15/20 | Branch ready, no blockers |
| **Total** | **76/100** | Proceed |
