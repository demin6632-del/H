# Chronicles of the Abyss — V5 Architecture

## Goal
V5 is a controlled rebuild of the game architecture, not a feature dump. The target is a deeper single-player RPG inspired by the systemic breadth of large text RPGs while retaining the Abyss exploration identity.

## Non-negotiable contracts
- Player-driven room exploration remains the core loop.
- Depths 1–7 remain the initial Abyss campaign.
- A room is completed exactly once.
- New depth requires an explicit player action.
- Death clears the active expedition and stale combat state.
- Continue restores a valid saved state; New Game starts clean.
- Equipment is never auto-equipped.
- Inventory/shop/stacking rules remain explicit.
- Android WebView and web build use the same gameplay source of truth.

## Layered architecture
1. GameState — canonical persistent state.
2. RunState — current Abyss expedition.
3. CharacterSystem — stats, XP, levels, classes and skills.
4. CombatSystem — deterministic battle state and effects.
5. ExplorationSystem — rooms, events, choices and consequences.
6. LootSystem — item generation, rarity, rewards and drops.
7. EquipmentSystem — slots, equip/unequip and modifiers.
8. InventorySystem — stacks, capacity and selling.
9. EconomySystem — gold, merchants, prices and services.
10. CitySystem — hub, forge, tavern, contracts and progression.
11. EndgameSystem — arena, trials, achievements and long-term goals.
12. PersistenceSystem — versioned saves, migration and recovery.
13. Render/UI — presentation only; no authoritative game logic.

## Canonical state
All gameplay mutations must pass through one state object and one mutation/save pipeline. UI code must never maintain a second authoritative copy of depth, room, HP, inventory or equipment.

## Expansion order
### Phase A — foundation
- isolate canonical state and persistence;
- preserve current V2 Abyss behavior;
- remove duplicated legacy mutations where safe;
- add migration/version boundaries.

### Phase B — RPG progression
- XP/levels;
- attributes;
- class identity;
- skills and passive modifiers.

### Phase C — itemisation
- item instances;
- rarity;
- affixes;
- set effects;
- equipment slots;
- forge.

### Phase D — world/economy
- city services;
- merchants;
- contracts;
- resources;
- reputation.

### Phase E — Abyss content
- room families;
- elite encounters;
- bosses;
- secrets;
- depth-specific events;
- persistent consequences.

### Phase F — endgame
- Abyss Arena;
- endless trials;
- achievements;
- collections;
- seasonal/event framework.

### Phase G — optional online layer
Only after the offline core is stable: orders/guilds, asynchronous rankings, PvP and server-backed events.

## Rebuild rule
If a legacy subsystem prevents a clean single-source implementation, replace that subsystem rather than adding another wrapper around it. Existing player-facing behavior is preserved unless the new design explicitly supersedes it.

## Verification gate
Every phase must pass:
- JavaScript syntax audit;
- duplicate-ID audit;
- state-transition audit;
- save/continue/new-game audit;
- depth 1→7 progression audit;
- death/recovery audit;
- inventory/equipment audit;
- Android asset/source parity;
- signed APK verification.

## Release policy
Experimental V5 work stays isolated until the phase passes its verification gate. Main/release remains usable while the rebuild is developed.