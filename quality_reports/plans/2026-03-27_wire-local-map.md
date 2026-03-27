# Plan: Wire Local Map Into Game Loop

**Ticket:** bug-1774621288 | **Milestone:** local | **Readiness:** 88/100
**Branch:** bug-1774621288

## Context
The local map system (100x100x64 grid, 1m scale with Z-levels) is fully implemented
across 6 files (local_map.py, local_gen.py, chunk_manager.py, region_map.py, renderer.py,
z_level.py) but never wired into the game loop. `game_world` is set to `None` on line 189,
`draw_local()` is never called, and there are no key bindings to enter/exit the local map.

## Impact Analysis
- Files affected: 1 (game.py)
- Highest risk: LOW (additive changes only)
- Existing behavior: untouched — all changes are new code paths

## Approach
Wire existing GameWorld infrastructure into game.py:
1. Instantiate GameWorld in `_init_world()`
2. Add `map_mode` switching between "travel" and "local"
3. Add local map draw path in `_game_loop()`
4. Add local map input handler with movement, FOV, and Z-level support
5. Add enter (L) and exit (Esc) key bindings

## Tasks

### Task 1: Initialize GameWorld and add local map state
- **Files:** game.py (modify)
- **Depends on:** none
- **Blocks:** Task 2
- **Description:**
  - Import `GameWorld` from `region_map`
  - Create `GameWorld` instance in `_init_world()` after world generation
  - Wire `GameWorld.region_map.world` to use the already-generated `self.world`
  - Add `location_name` attribute to `GameState`

### Task 2: Wire game loop, input handler, and movement
- **Files:** game.py (modify)
- **Depends on:** Task 1
- **Blocks:** none
- **Description:**
  - Add local map draw branch in `_game_loop()` when `map_mode == "local"`
  - Call `compute_fov()` on local map instead of world when in local mode
  - Add `_handle_local_input(k)` for local map controls (hjkl movement, Z-level, exit)
  - Add `_try_local_move(dx, dy)` for local-scale movement with walkability checks
  - Add `L` key binding in normal mode to enter local map at current position
  - Add `Esc` key binding in local mode to exit back to travel map
  - Guard `_process_turn()` terrain lookup for local mode

## File Ownership Matrix

| File | Task | Action |
|------|------|--------|
| game.py | Task 1 + Task 2 | Modify |

## Execution Waves

| Wave | Tasks | Parallel |
|------|-------|----------|
| 1 | Task 1 → Task 2 | No (same file, sequential) |

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| draw_local expects location_name on game_state | High | Low | Add to GameState |
| _process_turn reads player.col/row for terrain | Medium | Medium | Guard with map_mode |
| Edge-of-map movement in local mode | Low | Low | GameWorld.move_to_adjacent_area handles it |

## Testing Strategy
- Manual: Enter local map with L, verify render, move with hjkl, exit with Esc
- Verify: FOV computes and renders (lit vs seen tiles)
- Verify: No crash at local map boundaries
- Verify: Travel map still works normally when not in local mode

## Readiness Breakdown

| Dimension | Score | Notes |
|-----------|-------|-------|
| Requirements | 16/20 | Clear bug report, integration gap identified |
| Codebase | 20/20 | All source files explored |
| Design | 18/20 | All infrastructure exists, just needs wiring |
| Risk | 18/20 | Low risk, additive only |
| Operational | 16/20 | Branch ready |
| **Total** | **88/100** | |
