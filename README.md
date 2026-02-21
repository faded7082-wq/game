# Basic RPG Game (8-bit Terminal Edition)

A tiny command-line RPG in Python with a retro 8-bit inspired interface:
- Pixel-style title banner
- Framed HUD panels
- Pseudo-3D battle arena with depth lanes
- Expanded dungeon-crawling roster with more hostile mobs (Skeletons, Cave Trolls, Wraiths, Gorgons, Liches)
- Mob essence boons: each defeated mob grants a single small permanent stat bonus (+0.5 or +1.0)
- Inventory system for potions, food, arrows, relics, and ethers
- Multiple weapon types, including bows and the Axe of the Minotaur
- Special arrows with status effects (poison, frost, fire)
- Cthulhu questline and boss unlock
- **Zeus's Trial** on the remote island of **Tafity**
- Aquatic ambush mobs can appear while sailing between islands
- Encounter pressure scales upward with consecutive hours played in a session
- Farming and world-foraging system for all growable foods
- Home Base building mode with structure upgrades
- Automatic boss plaques added to Home Base when bosses are defeated

## Run

```bash
python3 game.py
```

## Controls

- `A` weapon attack
- `1/2/3/4` cast spell slot 1-4
- `R` restore mana
- `H` potion
- `F` food
- `G` farm (grow/harvest crops)
- `Z` forage through grass and leafs
- `N` travel between mainland and home base
- `B` build a home base structure
- `E` ether
- `W` cycle weapon
- `T` cycle arrow type
- `X` quest progress
- `O` sail between mainland and Tafity (after unlocking route)
- `V` inventory
- `I/J/K/L` movement
- `Q` quit

## Mob Essence Bonuses

Each mob boosts one stat by a small amount when defeated (only +0.5 or +1.0 per enemy):
- **Might**: increases weapon damage
- **Ward**: increases effective armor
- **Focus**: increases spell damage
- **Vitality**: increases potion/food healing

Current boon totals are shown in the HUD as `Mob Boons`.

## Ocean Travel Encounters

When you sail (`O`), aquatic mobs can randomly ambush you: **Siren**, **Sea Serpent**, **Kraken**, and **Leviathan**.

The longer you play in one continuous session, the more frequent and dangerous encounters become across all mobs.

## Farming and Foraging

You can grow and obtain food from the world:
- `G` to farm and harvest crops.
- `Z` to forage through grass and leafs.

All growable foods can be obtained by foraging: **berries**, **leafy_greens**, **mushrooms**, **carrots**, and **melons**.

Using `F` consumes standard food first, then automatically consumes farmed food types.

## Home Base Building Mode

Use `N` to travel between **Mainland** and **Home Base**.

At Home Base, use `B` to construct structures. Each structure costs resources and grants a permanent bonus:
- **Campfire**: boosts max HP
- **Workbench**: boosts attack power
- **Library**: boosts max mana
- **Watchtower**: boosts armor rating

When a major boss is defeated (**Cthulhu**, **Minotaur**, **Titan Lords**, **Zeus**), a matching plaque is automatically added to your Home Base display.

## Cthulhu Path

Complete all 3 quests while surviving the deeper hostile dungeon packs:
- Hunter's Trial: defeat 2 major beasts
- Spell Mastery: cast 5 spells
- Relic Hunt: gather 2 relic shards

Then defeat Cthulhu to gain Eldritch Aegis armor and unlock travel to Tafity.

## Zeus's Trial on Tafity

On Tafity you face a boss gauntlet:
1. **Minotaur** → reward: **Axe of the Minotaur**
2. **Titan Lords** → reward: advanced titan magic (`Titan Nova`, `Titan Rift`)
3. **Zeus** → reward: **Zeus Thunderbolt** magic and Zeus's thunderbolts

You must defeat each boss in order to complete Zeus's Trial.
