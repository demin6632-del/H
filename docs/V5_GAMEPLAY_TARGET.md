# V5 Gameplay Target — WellDungeon-like breadth, original implementation

## Target
Expand Chronicles of the Abyss toward the breadth of a mature text RPG such as Подземелья Колодца, while keeping original text, art, names, balance, code, and game identity.

## Systems to implement
- Character: level, XP, attributes, class, skills, passive effects.
- Equipment: weapon, armor, accessories, rarity, affixes, upgrades, explicit equip/unequip.
- Inventory: stackable consumables/resources, capacity, selling, sorting.
- Combat: turn-based encounters, enemy intents, statuses, skills, elites, bosses.
- Abyss: 7 depths initially, 5 rooms each, room families, branching choices, secrets, traps, ambushes, treasure, crossroads, elites and bosses.
- Progression: depth difficulty scaling, permanent character progression, run rewards and death consequences.
- City: tavern, merchant, forge, contracts, training, healing and preparation.
- Economy: gold, resources, merchant reputation, buy/sell, rare merchants.
- Endgame: arena/trials, achievements, collections and repeatable high-level challenges.
- Events: rotating modifiers and special encounters can be added after the offline core is stable.

## Interaction model
The player explicitly chooses actions. No automatic room resolution, automatic equipment, automatic depth transition, or hidden reward mutation.

## Originality boundary
Similarity is limited to documented genre/system concepts and interaction breadth. Do not copy source code, text, artwork, exact item/enemy names, proprietary UI, maps, narrative, or distinctive presentation from another game.

## Implementation order
1. Character + combat + status effects.
2. Equipment + inventory + affixes + forge.
3. Abyss room families + encounters + bosses.
4. City + contracts + economy.
5. Arena/trials + achievements/collections.
6. UI integration.
7. Full save migration, audit and Android release build.
