#!/usr/bin/env python3
"""Retro terminal RPG with quests, bosses, and tactical combat."""

from __future__ import annotations

import random
import time
from dataclasses import dataclass, field

RESET = "\033[0m"
CYAN = "\033[96m"
MAGENTA = "\033[95m"
GREEN = "\033[92m"
BLUE = "\033[94m"
YELLOW = "\033[93m"
RED = "\033[91m"
DIM = "\033[2m"

BANNER = r"""
 ██████╗ ██████╗  ██████╗
 ██╔══██╗██╔══██╗██╔════╝
 ██████╔╝██████╔╝██║  ███╗
 ██╔══██╗██╔═══╝ ██║   ██║
 ██║  ██║██║     ╚██████╔╝
 ╚═╝  ╚═╝╚═╝      ╚═════╝
"""

ENEMY_SPRITES: dict[str, dict[int, str]] = {
    "Slime": {0: "(◜◟)", 1: "(oo)", 2: "()"},
    "Wolf": {0: " /\_/\\\n( o.o )\n > ^ <", 1: " /\_/\\\n( o.o )", 2: " /\\"},
    "Boar": {0: "  ,___,\n (0   0)\n /  V  \\", 1: " ,___,\n(0 0)", 2: "oo"},
    "Bandit": {0: "  O\n /|\\\n / \\", 1: " O\n/|", 2: "o"},
    "Orc": {0: " [###]\n  /|\\\n  / \\", 1: "[##]\n /|", 2: "[]"},
    "Bear": {0: " /\"\".\\\n( o.o )\n > ^ <", 1: " /\"\".\\\n( o.o )", 2: "(o)"},
    "Necromancer": {0: "  /\\\n (.. )\n /||\\", 1: " /\\\n(..)", 2: "/\\"},
    "Dragon": {0: " /\\_/\\\n( o.o )===>\n ^^ ^^", 1: " /\\_/\\\n( o.o )=>", 2: "><"},
    "Cthulhu": {0: "  .-(===)-.\n ( o   o )\n <|  ^  |>\n  /___\\", 1: " .-(=)-.\n( o o )\n  |_|", 2: "(*)"},
    "Minotaur": {0: "  /\\_/\\\n ( > < )\n /|###|\\\n  /   \\", 1: " /\\_/\\\n( > < )", 2: "M"},
    "Titan Lords": {0: " [T][T]\n  /|\\\n /_|_\\", 1: " [T]\n /|", 2: "T"},
    "Zeus": {0: "  /⚡\\\n (o o)\n /|_|\\", 1: " /⚡\\\n(o o)", 2: "⚡"},
    "Kraken": {0: "  _._\n (o o)~~\n /|_|\\", 1: " (o o)~", 2: "~K~"},
    "Sea Serpent": {0: " ~~/\\~~\n( o  o )\n ~~\\/~~", 1: " ~/\\~\n(oo)", 2: "~~"},
    "Siren": {0: "  /\\\n (o )~\n /|\\", 1: " (o)~", 2: "~s~"},
    "Leviathan": {0: " /====\\\n( o  o )\n \\____/", 1: " /==\\\n(oo)", 2: "LV"},
}

ANIMAL_SPRITES: dict[str, dict[int, str]] = {
    "Fox": {0: " /\\   /\\\n( o o )\n > ^ <", 1: " /\\ /\\\n( o o )", 2: "^^"},
    "Hawk": {0: "  __\n<(o )___\n ( ._> /", 1: " __\n<(o)", 2: "v"},
    "Wolf Pup": {0: " /\\_/\\\n( •.• )\n /   \\", 1: " /\\_/\\\n( •.• )", 2: ".."},
}

PLAYER_SPRITES: dict[int, str] = {0: "  O\n /|\\\n / \\", 1: " O\n/|", 2: "o"}

WEAPONS: dict[str, dict[str, int]] = {
    "Dagger": {"bonus": 0, "range": 1},
    "Sword": {"bonus": 2, "range": 1},
    "Axe": {"bonus": 3, "range": 1},
    "Spear": {"bonus": 2, "range": 2},
    "Bow": {"bonus": 1, "range": 3},
    "Axe of the Minotaur": {"bonus": 7, "range": 1},
}

SPELLS: dict[str, dict[str, int]] = {
    "Mana Bolt": {"cost": 8, "min": 10, "max": 17, "range": 3},
    "Arcane Burst": {"cost": 10, "min": 14, "max": 22, "range": 1},
    "Frost Lance": {"cost": 11, "min": 12, "max": 20, "range": 2},
    "Thunder Orb": {"cost": 13, "min": 16, "max": 24, "range": 3},
    "Titan Nova": {"cost": 16, "min": 20, "max": 30, "range": 3},
    "Titan Rift": {"cost": 18, "min": 22, "max": 34, "range": 2},
    "Zeus Thunderbolt": {"cost": 22, "min": 28, "max": 40, "range": 4},
}

ARROW_TYPES = ["normal", "poison", "frost", "fire"]
ARROW_EFFECT_KEYS = {"normal": "arrows", "poison": "poison_arrows", "frost": "frost_arrows", "fire": "fire_arrows"}

CTHULHU = ("Cthulhu", 180, 20, 220)
ZEUS_TRIAL_BOSSES = [
    ("Minotaur", 130, 16, 140),
    ("Titan Lords", 170, 19, 200),
    ("Zeus", 220, 24, 300),
]

AQUATIC_ENEMIES: list[tuple[str, int, int, int]] = [
    ("Siren", 58, 12, 48),
    ("Sea Serpent", 72, 14, 62),
    ("Kraken", 95, 16, 88),
    ("Leviathan", 130, 19, 120),
]

GROWABLE_FOODS: dict[str, int] = {
    "berries": 8,
    "leafy_greens": 10,
    "mushrooms": 12,
    "carrots": 14,
    "melons": 16,
}

HOME_STRUCTURES: dict[str, dict[str, object]] = {
    "campfire": {"cost": {"food": 2}, "bonus": "max_hp", "amount": 4, "label": "Campfire"},
    "workbench": {"cost": {"arrows": 3}, "bonus": "attack_power", "amount": 1, "label": "Workbench"},
    "library": {"cost": {"ethers": 1}, "bonus": "max_mana", "amount": 4, "label": "Library"},
    "watchtower": {"cost": {"relic_shards": 1}, "bonus": "armor_rating", "amount": 1, "label": "Watchtower"},
}


BOSS_PLAQUE_ORDER = ["Cthulhu", "Minotaur", "Titan Lords", "Zeus"]

@dataclass
class Character:
    name: str
    max_hp: int
    attack_power: int
    hp: int | None = None
    status_effects: dict[str, int] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.hp is None:
            self.hp = self.max_hp

    @property
    def is_alive(self) -> bool:
        return self.hp > 0

    def strike(self, target: "Character", bonus: int = 0) -> int:
        power = self.attack_power + bonus
        raw = random.uniform(max(1, power - 3), power + 3)
        armor = getattr(target, "effective_armor", getattr(target, "armor_rating", 0))
        damage = max(1, int(round(raw - armor)))
        target.hp = max(0, target.hp - damage)
        return damage

    def heal(self, amount: int) -> int:
        before = self.hp
        self.hp = min(self.max_hp, self.hp + amount)
        return self.hp - before


@dataclass
class AnimalCompanion:
    name: str
    attack_power: int

    def strike(self, target: Character, distance_gap: int) -> int:
        penalty = max(0, distance_gap - 1)
        low = max(1, self.attack_power - 1 - penalty)
        high = max(1, self.attack_power + 1 - penalty)
        damage = random.randint(low, high)
        target.hp = max(0, target.hp - damage)
        return damage


@dataclass
class Player(Character):
    level: int = 1
    xp: int = 0
    max_mana: int = 25
    mana: int = 25
    armor_name: str = "Traveler Garb"
    armor_rating: int = 0
    location: str = "Mainland"
    inventory: dict[str, int] = field(default_factory=lambda: {
        "potions": 5,
        "food": 4,
        "arrows": 8,
        "poison_arrows": 2,
        "frost_arrows": 2,
        "fire_arrows": 2,
        "ethers": 2,
        "relic_shards": 0,
    })
    known_spells: list[str] = field(default_factory=lambda: ["Mana Bolt", "Arcane Burst"])
    weapon: str = "Sword"
    arrow_mode: str = "normal"
    companion: AnimalCompanion | None = None
    pos_x: int = 1
    pos_y: int = 0
    quests: dict[str, bool] = field(default_factory=lambda: {"hunter_trial": False, "spell_mastery": False, "relic_hunt": False})
    quest_progress: dict[str, int] = field(default_factory=lambda: {"beasts_down": 0, "spells_cast": 0, "relic_shards": 0})
    cthulhu_unlocked: bool = False
    cthulhu_defeated: bool = False
    tafity_unlocked: bool = False
    zeus_trial_stage: int = 0
    zeus_trial_complete: bool = False
    mob_bonuses: dict[str, float] = field(default_factory=lambda: {"might": 0.0, "ward": 0.0, "focus": 0.0, "vitality": 0.0})
    farm_food: dict[str, int] = field(default_factory=lambda: {name: 0 for name in GROWABLE_FOODS})
    home_base: dict[str, bool] = field(default_factory=lambda: {key: False for key in HOME_STRUCTURES})
    boss_plaques: dict[str, bool] = field(default_factory=lambda: {name: False for name in BOSS_PLAQUE_ORDER})

    @property
    def effective_armor(self) -> float:
        return self.armor_rating + self.mob_bonuses["ward"]

    def gain_xp(self, amount: int) -> bool:
        self.xp += amount
        threshold = self.level * 25
        if self.xp < threshold:
            return False
        self.xp -= threshold
        self.level += 1
        self.max_hp += 8
        self.attack_power += 2
        self.max_mana += 6
        self.hp = self.max_hp
        self.mana = self.max_mana
        return True

    def spend_mana(self, cost: int) -> bool:
        if self.mana < cost:
            return False
        self.mana -= cost
        return True

    def restore_mana(self, amount: int) -> int:
        old = self.mana
        self.mana = min(self.max_mana, self.mana + amount)
        return self.mana - old


ENEMIES: list[tuple[str, int, int, int]] = [
    ("Slime", 20, 5, 10),
    ("Wolf", 28, 7, 15),
    ("Boar", 32, 8, 18),
    ("Bandit", 35, 8, 20),
    ("Skeleton", 34, 9, 22),
    ("Orc", 45, 10, 30),
    ("Cave Troll", 54, 11, 36),
    ("Bear", 55, 11, 38),
    ("Wraith", 62, 13, 46),
    ("Necromancer", 60, 12, 45),
    ("Gorgon", 72, 14, 55),
    ("Lich", 84, 15, 65),
    ("Dragon", 90, 15, 80),
]

WILD_ANIMALS = [AnimalCompanion("Fox", 3), AnimalCompanion("Hawk", 4), AnimalCompanion("Wolf Pup", 5)]

MOB_STAT_BOOSTS: dict[str, tuple[str, float]] = {
    "Slime": ("vitality", 0.5),
    "Wolf": ("might", 0.5),
    "Boar": ("vitality", 1.0),
    "Bandit": ("might", 1.0),
    "Skeleton": ("ward", 0.5),
    "Orc": ("might", 1.0),
    "Cave Troll": ("ward", 1.0),
    "Bear": ("vitality", 1.0),
    "Wraith": ("focus", 0.5),
    "Necromancer": ("focus", 1.0),
    "Gorgon": ("ward", 1.0),
    "Lich": ("focus", 1.0),
    "Dragon": ("might", 1.0),
    "Cthulhu": ("ward", 1.0),
    "Minotaur": ("might", 1.0),
    "Titan Lords": ("focus", 1.0),
    "Zeus": ("focus", 1.0),
    "Siren": ("focus", 0.5),
    "Sea Serpent": ("might", 1.0),
    "Kraken": ("ward", 1.0),
    "Leviathan": ("vitality", 1.0),
}


def consecutive_hours(start_time: float) -> float:
    return max(0.0, (time.time() - start_time) / 3600)


def hp_bar(current: int, maximum: int, width: int = 20) -> str:
    filled = round((current / maximum) * width) if maximum else 0
    return f"{'█' * filled}{'░' * (width - filled)}"


def panel(title: str, lines: list[str]) -> str:
    width = max(len(title), *(len(line) for line in lines))
    top = f"┌─[{title}]" + "─" * (width - len(title) + 2) + "┐"
    body = [f"│ {line.ljust(width)} │" for line in lines]
    return "\n".join([top, *body, "└" + "─" * (width + 2) + "┘"])


def sprite_for(name: str, depth: int, table: dict[str, dict[int, str]]) -> str:
    return table.get(name, {0: "???", 1: "??", 2: "?"}).get(depth, "?")


def distance(player: Player, ex: int, ey: int) -> int:
    return abs(player.pos_x - ex) + abs(player.pos_y - ey)


def cast_spell(player: Player, enemy: Character, spacing: int, spell_name: str) -> str:
    if spell_name not in player.known_spells:
        return "You do not know that spell."
    info = SPELLS[spell_name]
    if spacing > info["range"]:
        return f"{spell_name} fizzles: out of range."
    if not player.spend_mana(info["cost"]):
        return "Not enough mana for that spell."
    damage = int(round(random.uniform(info["min"], info["max"]) + player.mob_bonuses["focus"]))
    enemy.hp = max(0, enemy.hp - damage)
    player.quest_progress["spells_cast"] += 1
    return f"{BLUE}{spell_name}{RESET} hits {enemy.name} for {damage}."


def apply_arrow_status(enemy: Character, mode: str) -> str:
    if mode == "poison" and random.random() < 0.75:
        enemy.status_effects["poison"] = max(enemy.status_effects.get("poison", 0), 3)
        return " Poisoned!"
    if mode == "frost" and random.random() < 0.7:
        enemy.status_effects["frost"] = 1
        return " Frozen!"
    if mode == "fire" and random.random() < 0.75:
        enemy.status_effects["burn"] = max(enemy.status_effects.get("burn", 0), 2)
        return " Burning!"
    return ""


def weapon_attack(player: Player, enemy: Character, spacing: int) -> str:
    info = WEAPONS[player.weapon]
    if spacing > info["range"]:
        return f"Your {player.weapon} cannot reach from here."

    suffix = ""
    if player.weapon == "Bow":
        key = ARROW_EFFECT_KEYS[player.arrow_mode]
        if player.inventory[key] <= 0:
            return f"No {player.arrow_mode} arrows left."
        player.inventory[key] -= 1
        suffix = f" ({player.arrow_mode}:{player.inventory[key]})"

    damage = player.strike(enemy, info["bonus"] + player.mob_bonuses["might"])
    msg = f"You hit {enemy.name} with {player.weapon} for {damage}.{suffix}"
    if player.weapon == "Bow" and enemy.is_alive:
        msg += apply_arrow_status(enemy, player.arrow_mode)
    return msg


def tick_status_effects(enemy: Character) -> tuple[str, bool]:
    notes: list[str] = []
    skip = False
    if enemy.status_effects.get("poison", 0) > 0:
        dmg = random.randint(3, 6)
        enemy.hp = max(0, enemy.hp - dmg)
        enemy.status_effects["poison"] -= 1
        notes.append(f"Poison {dmg}")
    if enemy.status_effects.get("burn", 0) > 0:
        dmg = random.randint(4, 7)
        enemy.hp = max(0, enemy.hp - dmg)
        enemy.status_effects["burn"] -= 1
        notes.append(f"Burn {dmg}")
    if enemy.status_effects.get("frost", 0) > 0:
        enemy.status_effects["frost"] -= 1
        skip = True
        notes.append("Frozen")
    for key in ("poison", "burn", "frost"):
        if enemy.status_effects.get(key, 0) <= 0:
            enemy.status_effects.pop(key, None)
    return (", ".join(notes), skip)


def render_arena(player: Player, enemy: Character, ex: int, ey: int) -> str:
    rows: list[str] = []
    for depth in (2, 1, 0):
        indent = " " * (depth * 5)
        lane = ["   "] * 3
        if ey == depth:
            lane[ex] = f"{RED}E{RESET}"
        if player.pos_y == depth:
            lane[player.pos_x] = f"{GREEN}P{RESET}"
        rows.append(f"{indent}{'   '.join(lane)}")

    depth_view = max(player.pos_y, ey)
    p_art = PLAYER_SPRITES[depth_view].splitlines()
    e_art = sprite_for(enemy.name, depth_view, ENEMY_SPRITES).splitlines()
    while len(p_art) < len(e_art):
        p_art.append("")
    while len(e_art) < len(p_art):
        e_art.append("")

    rows.append("")
    rows.append(f"{GREEN}You{RESET}".ljust(16) + f"{RED}{enemy.name}{RESET}")
    for left, right in zip(p_art, e_art):
        rows.append(left.ljust(16) + right)
    rows.append("")
    rows.append(f"Distance: {distance(player, ex, ey)}")
    return "\n".join(rows)


def spawn_enemy(stage: int, player: Player, hours_played: float) -> tuple[Character, int, int, int]:
    if player.location == "Tafity" and not player.zeus_trial_complete:
        name, hp, attack, reward = ZEUS_TRIAL_BOSSES[min(player.zeus_trial_stage, len(ZEUS_TRIAL_BOSSES) - 1)]
        return Character(name=name, max_hp=hp, attack_power=attack), reward, 1, 2

    if player.cthulhu_unlocked and not player.cthulhu_defeated and stage >= len(ENEMIES):
        name, hp, attack, reward = CTHULHU
        return Character(name=name, max_hp=hp, attack_power=attack), reward, 1, 2

    max_index = min(len(ENEMIES) - 1, stage + 2 + int(hours_played * 2))
    min_index = max(0, max_index - 3 - int(hours_played))
    pool = ENEMIES[min_index : max_index + 1]
    weights = [1 + i + int(hours_played) for i in range(len(pool))]
    name, hp, attack, reward = random.choices(pool, weights=weights, k=1)[0]
    return Character(name=name, max_hp=hp, attack_power=attack), reward, random.randint(0, 2), random.randint(1, 2)


def spawn_aquatic_enemy(hours_played: float) -> tuple[Character, int, int, int]:
    bias = min(len(AQUATIC_ENEMIES) - 1, int(hours_played))
    pool = AQUATIC_ENEMIES[: bias + 2]
    name, hp, attack, reward = random.choice(pool)
    return Character(name=name, max_hp=hp, attack_power=attack), reward, random.randint(0, 2), random.randint(1, 2)


def move_unit(x: int, y: int, tx: int, ty: int) -> tuple[int, int]:
    if x < tx:
        x += 1
    elif x > tx:
        x -= 1
    elif y > ty:
        y -= 1
    elif y < ty:
        y += 1
    return max(0, min(2, x)), max(0, min(2, y))


def cycle_weapon(player: Player) -> str:
    names = list(WEAPONS)
    player.weapon = names[(names.index(player.weapon) + 1) % len(names)]
    return f"Weapon swapped to {player.weapon}."


def cycle_arrow_mode(player: Player) -> str:
    player.arrow_mode = ARROW_TYPES[(ARROW_TYPES.index(player.arrow_mode) + 1) % len(ARROW_TYPES)]
    key = ARROW_EFFECT_KEYS[player.arrow_mode]
    return f"Arrow type: {player.arrow_mode} ({player.inventory[key]} left)."


def total_food_supply(player: Player) -> int:
    return player.inventory["food"] + sum(player.farm_food.values())


def plant_and_harvest(player: Player) -> str:
    crop = random.choice(list(GROWABLE_FOODS))
    amount = random.randint(1, 2)
    player.farm_food[crop] += amount
    return f"You tend your farm and harvest {amount} {crop}."


def forage_food(player: Player) -> str:
    source = random.choice(["grass", "leafs"])
    crop = random.choice(list(GROWABLE_FOODS))
    amount = random.randint(1, 2)
    player.farm_food[crop] += amount
    return f"You forage through {source} and find {amount} {crop}."


def travel_home_base(player: Player) -> str:
    if player.location not in {"Mainland", "Home Base"}:
        return "You can only reach your home base from the mainland."
    player.location = "Home Base" if player.location == "Mainland" else "Mainland"
    return f"You travel to {player.location}."


def build_home_base(player: Player) -> str:
    if player.location != "Home Base":
        return "You need to be at Home Base to build."

    options = [name for name, done in player.home_base.items() if not done]
    if not options:
        return "Your home base is fully built."

    key = random.choice(options)
    spec = HOME_STRUCTURES[key]
    costs = spec["cost"]
    for resource, amount in costs.items():
        if resource == "food":
            if total_food_supply(player) < amount:
                return f"Not enough total food to build {spec['label']}."
        elif player.inventory.get(resource, 0) < amount:
            return f"Not enough {resource} to build {spec['label']}."

    for resource, amount in costs.items():
        if resource == "food":
            use = min(player.inventory["food"], amount)
            player.inventory["food"] -= use
            remaining = amount - use
            while remaining > 0:
                crop = next((name for name, count in player.farm_food.items() if count > 0), None)
                if crop is None:
                    break
                player.farm_food[crop] -= 1
                remaining -= 1
        else:
            player.inventory[resource] -= amount

    player.home_base[key] = True
    bonus = spec["bonus"]
    amount = int(spec["amount"])
    if bonus == "max_hp":
        player.max_hp += amount
        player.hp = min(player.max_hp, player.hp + amount)
    elif bonus == "attack_power":
        player.attack_power += amount
    elif bonus == "max_mana":
        player.max_mana += amount
        player.mana = min(player.max_mana, player.mana + amount)
    elif bonus == "armor_rating":
        player.armor_rating += amount

    return f"Built {spec['label']} at Home Base! {bonus.replace('_', ' ').title()} +{amount}."


def plaque_status_line(player: Player) -> str:
    return ", ".join(f"{name}:{'✓' if player.boss_plaques[name] else '…'}" for name in BOSS_PLAQUE_ORDER)


def award_boss_plaque(player: Player, enemy_name: str) -> str:
    if enemy_name not in player.boss_plaques:
        return ""
    if player.boss_plaques[enemy_name]:
        return ""
    player.boss_plaques[enemy_name] = True
    return f"Plaque added to Home Base: {enemy_name}."


def eat_food(player: Player) -> str:
    if player.inventory["food"] > 0:
        player.inventory["food"] -= 1
        heal_amt = int(round(12 + player.mob_bonuses["vitality"]))
        return f"Food healed {player.heal(heal_amt)} HP."

    available = [name for name, count in player.farm_food.items() if count > 0]
    if not available:
        return "No food left."
    crop = max(available, key=lambda name: GROWABLE_FOODS[name])
    player.farm_food[crop] -= 1
    heal_amt = int(round(GROWABLE_FOODS[crop] + player.mob_bonuses["vitality"]))
    return f"You eat {crop} and heal {player.heal(heal_amt)} HP."


def quest_status(player: Player) -> str:
    c = f"Cthulhu[{ '✓' if all(player.quests.values()) else '…'}]"
    z = f"Zeus[{player.zeus_trial_stage}/3{'✓' if player.zeus_trial_complete else ''}]"
    return f"{c} {z}"


def update_quests(player: Player, enemy_name: str) -> str:
    notes: list[str] = []
    if enemy_name in {"Wolf", "Bear", "Dragon"}:
        player.quest_progress["beasts_down"] += 1
    if enemy_name in {"Necromancer", "Dragon", "Cthulhu"}:
        player.inventory["relic_shards"] += 1
        player.quest_progress["relic_shards"] = player.inventory["relic_shards"]

    if player.quest_progress["beasts_down"] >= 2 and not player.quests["hunter_trial"]:
        player.quests["hunter_trial"] = True
        notes.append("Hunter's Trial complete")
    if player.quest_progress["spells_cast"] >= 5 and not player.quests["spell_mastery"]:
        player.quests["spell_mastery"] = True
        notes.append("Spell Mastery complete")
    if player.quest_progress["relic_shards"] >= 2 and not player.quests["relic_hunt"]:
        player.quests["relic_hunt"] = True
        notes.append("Relic Hunt complete")

    if all(player.quests.values()) and not player.cthulhu_unlocked:
        player.cthulhu_unlocked = True
        notes.append("Cthulhu gateway unlocked")
    if player.cthulhu_defeated and not player.tafity_unlocked:
        player.tafity_unlocked = True
        notes.append("Tafity island route is now open")
    return ". ".join(notes)


def cthulhu_reward(player: Player) -> str:
    player.cthulhu_defeated = True
    player.armor_name = "Eldritch Aegis"
    player.armor_rating = 4
    player.max_hp += 25
    player.hp = player.max_hp
    player.tafity_unlocked = True
    return "You forged Eldritch Aegis! DR +4, +25 max HP. Tafity can now be reached."


def zeus_trial_reward(player: Player, boss_name: str) -> str:
    if boss_name == "Minotaur":
        player.zeus_trial_stage = 1
        player.weapon = "Axe of the Minotaur"
        return "Trial 1 complete: Axe of the Minotaur claimed."
    if boss_name == "Titan Lords":
        player.zeus_trial_stage = 2
        for spell in ("Titan Nova", "Titan Rift"):
            if spell not in player.known_spells:
                player.known_spells.append(spell)
        return "Trial 2 complete: Titan advanced magic learned."
    if boss_name == "Zeus":
        player.zeus_trial_stage = 3
        player.zeus_trial_complete = True
        if "Zeus Thunderbolt" not in player.known_spells:
            player.known_spells.append("Zeus Thunderbolt")
        player.inventory["fire_arrows"] += 12
        return "Trial 3 complete: Zeus's thunderbolts bestowed."
    return ""


def sail_tafity(player: Player) -> str:
    if not player.tafity_unlocked:
        return "The Tafity route is hidden. Defeat Cthulhu first."
    player.location = "Tafity" if player.location == "Mainland" else "Mainland"
    return f"You sail to {player.location}."


def apply_mob_bonus(player: Player, enemy_name: str) -> str:
    bonus = MOB_STAT_BOOSTS.get(enemy_name)
    if not bonus:
        return ""
    stat, amount = bonus
    player.mob_bonuses[stat] += amount
    return f"{enemy_name} essence: {stat.title()} +{amount:g}."


def render_screen(player: Player, enemy: Character, stage: int, ex: int, ey: int, message: str) -> None:
    print("\033[2J\033[H", end="")
    print(f"{MAGENTA}{BANNER}{RESET}")
    print(f"{DIM}Stage {stage + 1} - {player.location}{RESET}\n")

    status = ", ".join(f"{k}:{v}" for k, v in enemy.status_effects.items()) or "None"
    player_lines = [
        f"Name   : {player.name}",
        f"Level  : {player.level}",
        f"Armor  : {player.armor_name} (DR {player.armor_rating})",
        f"Quest  : {quest_status(player)}",
        (
            f"Mob Boons: Might {player.mob_bonuses['might']:.1f} | Ward {player.mob_bonuses['ward']:.1f} | "
            f"Focus {player.mob_bonuses['focus']:.1f} | Vitality {player.mob_bonuses['vitality']:.1f}"
        ),
        f"HP     : {GREEN}{hp_bar(player.hp, player.max_hp)}{RESET} {player.hp}/{player.max_hp}",
        f"Mana   : {BLUE}{hp_bar(player.mana, player.max_mana)}{RESET} {player.mana}/{player.max_mana}",
        f"Weapon : {player.weapon}",
        f"Arrows : {player.arrow_mode}",
        f"Potions: {player.inventory['potions']} Food: {total_food_supply(player)} Ethers: {player.inventory['ethers']}",
        "Farm  : " + ", ".join(f"{k}:{v}" for k, v in player.farm_food.items()),
        f"N:{player.inventory['arrows']} P:{player.inventory['poison_arrows']} F:{player.inventory['frost_arrows']} Fire:{player.inventory['fire_arrows']}",
        f"Relics : {player.inventory['relic_shards']}",
        "Base  : " + ", ".join(f"{HOME_STRUCTURES[k]['label']}={'✓' if v else '…'}" for k, v in player.home_base.items()),
        "Plaques: " + plaque_status_line(player),
    ]
    enemy_lines = [
        f"Type   : {enemy.name}",
        f"HP     : {RED}{hp_bar(enemy.hp, enemy.max_hp)}{RESET} {enemy.hp}/{enemy.max_hp}",
        f"Pos    : x{ex} y{ey}",
        f"Range  : {distance(player, ex, ey)}",
        f"Status : {status}",
    ]

    print(panel(f"{CYAN}HERO{RESET}", player_lines))
    print(panel(f"{YELLOW}ENEMY{RESET}", enemy_lines))
    print(panel("ARENA", render_arena(player, enemy, ex, ey).splitlines()))
    print(panel("LOG", [
        message or "Prepare for battle!",
        "",
        "[A]ttack [1..4] spells [R]estore [H]eal [F]ood [E]ther [W]eapon [T]arrow [X]quests [O]sail [G]farm [Z]forage [B]uild [N]home [I/J/K/L] move",
        "[V]inventory [Q]quit",
    ]))


def choose_action() -> str:
    return input("\n> ").strip().lower()


def apply_player_move(player: Player, action: str) -> bool:
    before = (player.pos_x, player.pos_y)
    if action == "i":
        player.pos_y = min(2, player.pos_y + 1)
    elif action == "k":
        player.pos_y = max(0, player.pos_y - 1)
    elif action == "j":
        player.pos_x = max(0, player.pos_x - 1)
    elif action == "l":
        player.pos_x = min(2, player.pos_x + 1)
    return before != (player.pos_x, player.pos_y)


def play() -> None:
    random.seed()
    session_start = time.time()
    print(f"{MAGENTA}{BANNER}{RESET}")
    name = input("Enter hero name: ").strip() or "Hero"
    player = Player(name=name, max_hp=50, attack_power=9)
    stage = 0

    while player.is_alive:
        enemy, xp_reward, ex, ey = spawn_enemy(stage, player, consecutive_hours(session_start))
        player.pos_x, player.pos_y = 1, 0
        message = f"A wild {enemy.name} appears!"

        while player.is_alive and enemy.is_alive:
            render_screen(player, enemy, stage, ex, ey, message)
            action = choose_action()
            spacing = distance(player, ex, ey)

            if action in {"i", "j", "k", "l"}:
                message = "You move." if apply_player_move(player, action) else "Cannot move further."
            elif action in {"a", "attack"}:
                message = weapon_attack(player, enemy, spacing)
            elif action in {"1", "2", "3", "4"}:
                slot = int(action) - 1
                if slot >= len(player.known_spells):
                    message = "No spell in that slot."
                else:
                    message = cast_spell(player, enemy, spacing, player.known_spells[slot])
            elif action in {"r", "restore"}:
                message = f"Restored {player.restore_mana(random.randint(7, 13))} mana."
            elif action in {"h", "heal", "potion"}:
                if player.inventory["potions"] <= 0:
                    message = "No potions left."; continue
                player.inventory["potions"] -= 1
                heal_amt = int(round(20 + player.mob_bonuses["vitality"]))
                message = f"Potion healed {player.heal(heal_amt)} HP."
            elif action in {"f", "food", "eat"}:
                message = eat_food(player)
            elif action in {"e", "ether"}:
                if player.inventory["ethers"] <= 0:
                    message = "No ethers left."; continue
                player.inventory["ethers"] -= 1
                message = f"Ether restored {player.restore_mana(15)} mana."
            elif action in {"w", "weapon"}:
                message = cycle_weapon(player)
            elif action in {"t", "arrow"}:
                message = cycle_arrow_mode(player)
            elif action in {"g", "farm"}:
                message = plant_and_harvest(player)
                continue
            elif action in {"z", "forage"}:
                message = forage_food(player)
                continue
            elif action in {"n", "home", "base"}:
                message = travel_home_base(player)
                continue
            elif action in {"b", "build"}:
                message = build_home_base(player)
                continue
            elif action in {"o", "sail"}:
                message = sail_tafity(player)
                if message.startswith("The Tafity route is hidden"):
                    continue
                sea_chance = min(0.2 + consecutive_hours(session_start) * 0.15, 0.9)
                if random.random() < sea_chance:
                    enemy, xp_reward, ex, ey = spawn_aquatic_enemy(consecutive_hours(session_start))
                    player.pos_x, player.pos_y = 1, 0
                    message += f" {BLUE}Sea ambush!{RESET} {enemy.name} emerges from the waves."
                else:
                    continue
            elif action in {"x", "quest", "quests"}:
                message = (
                    f"Cthulhu quests | Beasts {player.quest_progress['beasts_down']}/2 | "
                    f"Spells {player.quest_progress['spells_cast']}/5 | Relics {player.quest_progress['relic_shards']}/2. "
                    f"Zeus Trials stage: {player.zeus_trial_stage}/3"
                )
                continue
            elif action in {"v", "inventory"}:
                message = (
                    f"Inv Ptn:{player.inventory['potions']} Food:{total_food_supply(player)} Eth:{player.inventory['ethers']} "
                    f"N:{player.inventory['arrows']} P:{player.inventory['poison_arrows']} "
                    f"F:{player.inventory['frost_arrows']} Fire:{player.inventory['fire_arrows']} | "
                    f"Farm(B:{player.farm_food['berries']} L:{player.farm_food['leafy_greens']} M:{player.farm_food['mushrooms']} C:{player.farm_food['carrots']} Me:{player.farm_food['melons']})"
                )
                continue
            elif action in {"q", "quit"}:
                print("\nYou retreat from the dungeon.\n")
                return
            else:
                message = "Unknown command."
                continue

            if enemy.is_alive:
                tick_note, skip = tick_status_effects(enemy)
                if tick_note:
                    message += f" {enemy.name}: {tick_note}."
                if not enemy.is_alive:
                    continue
                if not skip:
                    ex, ey = move_unit(ex, ey, player.pos_x, player.pos_y)
                    spacing = distance(player, ex, ey)
                    if player.companion and spacing <= 2:
                        comp = player.companion.strike(enemy, spacing)
                        message += f" {player.companion.name} hits for {comp}!"
                    if enemy.is_alive:
                        if spacing <= 1:
                            message += f" {enemy.name} hits for {enemy.strike(player)}!"
                        else:
                            message += f" {enemy.name} closes in."
                else:
                    message += f" {enemy.name} is frozen."

            regen = player.restore_mana(2)
            if regen:
                message += f" (+{regen} mana)"

        if not player.is_alive:
            break

        message = f"{enemy.name} defeated! +{xp_reward} XP."
        if enemy.name == "Cthulhu":
            message += " " + cthulhu_reward(player)
        elif player.location == "Tafity" and enemy.name in {"Minotaur", "Titan Lords", "Zeus"}:
            message += " " + zeus_trial_reward(player, enemy.name)
        else:
            q = update_quests(player, enemy.name)
            if q:
                message += " " + q

        mob_note = apply_mob_bonus(player, enemy.name)
        if mob_note:
            message += " " + mob_note

        plaque_note = award_boss_plaque(player, enemy.name)
        if plaque_note:
            message += " " + plaque_note

        if player.gain_xp(xp_reward):
            message += f" LEVEL UP! You are now level {player.level}."

        if random.random() < 0.45:
            player.inventory["potions"] += random.randint(1, 3)
        if random.random() < 0.5:
            player.inventory["food"] += random.randint(1, 2)
        if random.random() < 0.55:
            player.inventory["arrows"] += random.randint(2, 5)
        if random.random() < 0.35:
            player.inventory["poison_arrows"] += random.randint(1, 2)
        if random.random() < 0.35:
            player.inventory["frost_arrows"] += random.randint(1, 2)
        if random.random() < 0.35:
            player.inventory["fire_arrows"] += random.randint(1, 2)
        if random.random() < 0.4:
            player.inventory["ethers"] += random.randint(1, 2)
        if random.random() < 0.35:
            learnable = [s for s in ("Frost Lance", "Thunder Orb") if s not in player.known_spells]
            if learnable:
                player.known_spells.append(random.choice(learnable))

        if random.random() < 0.35 and player.inventory["food"] > 0:
            wild = random.choice(WILD_ANIMALS)
            player.inventory["food"] -= 1
            player.companion = AnimalCompanion(wild.name, wild.attack_power)
            message += f" A wild {wild.name} joins you."

        if player.location == "Mainland":
            stage += 1

        render_screen(player, enemy, max(stage - 1, 0), ex, ey, message)
        rush_chance = min(0.1 + consecutive_hours(session_start) * 0.2, 0.85)
        if random.random() < rush_chance:
            message += " The longer you push on, mobs close in faster."
        else:
            input("\nPress Enter for next battle...")

    print(f"\n{RED}GAME OVER{RESET} - The dungeon claims another hero.")


if __name__ == "__main__":
    play()
