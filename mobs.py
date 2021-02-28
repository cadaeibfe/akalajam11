import random as rng

import pygame as pg

from assets import Assets
from items import Item
from quest import Quest
from world import Tile

class Mob(pg.sprite.Sprite):
    def __init__(self, world, factory, tile, max_hp, attack_power, defense_power):
        super().__init__()
        self.world = world
        self.factory = factory
        self.tile = tile
        self.max_hp = max_hp
        self.hp = self.max_hp
        self.attack_power = attack_power
        self.defense_power = defense_power
        self.vision = 0
        self.flip_h = False

    def move(self, mx, my):
        if mx < 0:
            self.flip_h = True
        elif mx > 0:
            self.flip_h = False
            
        newx = self.x + mx
        newy = self.y + my

        other = self.world.get_mob(newx, newy)
        if other != None:
            if other.tile != self.tile:  # mobs only attack different kinds
                self.attack(other)
            return

        if self.world.is_walkable(newx, newy):
            Assets.step_sound.play()
            self.x = newx
            self.y = newy
        else:
            Assets.bump_sound.play()

    def attack(self, defender):
        attack_power = self.get_attack_power()
        defense_power = defender.get_defense_power()
        damage = max(1, attack_power - defense_power)
        defender.take_damage(damage)
        Assets.hit_sound.play()

    def take_damage(self, damage):
        self.hp -= damage
        self.factory.new_float_text(f"-{damage}", self.x, self.y, (250, 61, 75))
        if self.hp <= 0:
            self.kill()
            self.drop_loot()

    def drop_loot(self):
        # Drop nothing by default
        pass

    def get_attack_power(self):
        return self.attack_power

    def get_defense_power(self):
        return self.defense_power

    def can_see(self, x, y):
        return (self.x - x)**2 + (self.y - y)**2 <= self.vision**2

    def wander(self):
        choices = []
        if self.world.is_walkable(self.x-1, self.y):
            choices.append((-1, 0))
        if self.world.is_walkable(self.x+1, self.y):
            choices.append((1, 0))
        if self.world.is_walkable(self.x, self.y-1):
            choices.append((0, -1))
        if self.world.is_walkable(self.x, self.y+1):
            choices.append((0, 1))

        if len(choices) > 0:
            move = rng.choice(choices)
            self.move(*move)

    def hunt(self):
        dx = self.target.x - self.x
        dy = self.target.y - self.y
        if dx < 0:
            self.move(-1, 0)
        elif dx > 0:
            self.move(1, 0)
        elif dy < 0:
            self.move(0, -1)
        elif dy > 0:
            self.move(0, 1)


class Player(Mob):
    def __init__(self, world, factory):
        super().__init__(world, factory, Tile.HERO, 30, 5, 0)
        self.vision = 5.2
        self.spent_turn = False
        self.level = 1
        self.xp = 0
        self.xp_needed = 12

    def move(self, mx, my):
        super().move(mx, my)
        self.spent_turn = True

        # try to pick up item when moving
        item = self.world.get_item(self.x, self.y)
        if item != None:
            self.world.items.remove(item)

            # check if picked item was one of the three treasures
            if item.tile == Tile.SWORD:
                Quest.has_sword = True
                self.tile = Tile.HERO_S
                Assets.powerup_sound.play()
                new_attack_power = self.attack_power + 2
                self.factory.talking_time(f"You've found the Necrosaurian Sword,\none of three legendary treasures!\nAttack power: {self.attack_power} -> {new_attack_power}", None)
                self.attack_power = new_attack_power

            elif item.tile == Tile.SHIELD:
                Quest.has_shield = True
                self.tile = Tile.HERO_SS
                Assets.powerup_sound.play()
                new_defense_power = self.defense_power + 2
                self.factory.talking_time(f"You've found the Necrosaurian Shield,\none of three legendary treasures!\nDefense power: {self.defense_power} -> {new_defense_power}", None)
                self.defense_power = new_defense_power

            elif item.tile == Tile.CROWN:
                Quest.has_crown = True
                Assets.powerup_sound.play()
                self.factory.talking_time(f"You've found the Necrosaurian Crown,\none of three legendary treasures!\nWith the crown's magic, you can escape\nthis tomb from the stairs.", None)
            
            # check if picked item is a potion
            elif item.tile == Tile.POTION:
                self.heal(int(self.max_hp / 5))

    def attack(self, defender):
        super().attack(defender)
        # override player's attack method to get xp from killed mobs
        if not defender.alive():
            self.xp += defender.xp
            while self.xp >= self.xp_needed:
                self.xp -= self.xp_needed
                self.level += 1
                self.xp_needed *= 2

                # Boost stats
                new_max_hp = self.max_hp + 3
                new_attack_power = self.attack_power + 1
                new_defense_power = self.defense_power + 1
                self.factory.talking_time(f"You reached level {self.level}!\nMax HP: {self.max_hp} -> {new_max_hp}\nAttack power: {self.attack_power} -> {new_attack_power}\nDefense power: {self.defense_power} -> {new_defense_power}", None)
                self.max_hp = new_max_hp
                self.attack_power = new_attack_power
                self.defense_power = new_defense_power

                # heal some
                self.heal(int(self.max_hp / 10))

    def heal(self, amount):
        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp
        self.factory.new_float_text(f"+{amount}", self.x, self.y, (0, 228, 48))
        Assets.heal_sound.play()


class Lizardman(Mob):
    def __init__(self, world, factory, tile, max_hp, attack_power, defense_power, target):
        super().__init__(world, factory, tile, max_hp, attack_power, defense_power)
        self.target = target
        self.vision = 4
        self.xp = 12

    def update(self):
        if self.can_see(self.target.x, self.target.y):
            self.hunt()

    def drop_loot(self):
        r = rng.random()

        # lizardmen can drop the three treasures, in order
        if r < 0.2:
            if not Quest.has_sword:
                self.world.items.add(Item(Tile.SWORD, self.x, self.y))
            elif not Quest.has_shield:
                self.world.items.add(Item(Tile.SHIELD, self.x, self.y))
            elif not Quest.has_crown:
                self.world.items.add(Item(Tile.CROWN, self.x, self.y))
            else:  # no more treasures, just drop a potion
                self.world.items.add(Item(Tile.POTION, self.x, self.y))
        elif r < 0.6:
            self.world.items.add(Item(Tile.POTION, self.x, self.y))


class Slime(Mob):
    def __init__(self, world, factory, tile, max_hp, attack_power, defense_power, target):
        super().__init__(world, factory, tile, max_hp, attack_power, defense_power)
        self.target = target
        self.vision = 2
        self.xp = 4

    def update(self):
        num_turns = rng.randrange(0, 2)  # slime is slow, sometimes doesn't move
        for i in range(num_turns):
            if self.can_see(self.target.x, self.target.y):
                self.hunt()
            else:
                self.wander()

    def drop_loot(self):
        if rng.random() < 0.35:
            self.world.items.add(Item(Tile.POTION, self.x, self.y))


class Bat(Mob):
    def __init__(self, world, factory, tile, max_hp, attack_power, defense_power, target):
        super().__init__(world, factory, tile, max_hp, attack_power, defense_power)
        self.target = target
        self.vision = 2
        self.xp = 6

    def update(self):
        if self.can_see(self.target.x, self.target.y):
            self.hunt()
        else:
            num_turns = rng.randrange(1, 3)
            for i in range(num_turns):
                self.wander()

    def drop_loot(self):
        # Bats are harder so have higher chance to drop a potion
        if rng.random() < 0.7:
            self.world.items.add(Item(Tile.POTION, self.x, self.y))


# class ArchAi:
#     def __init__(self, game):
#         self.game = game
#         self.lines = [
#             ("Archaeologist:\nOh, you're here!\nThanks for helping me with my expedition.", self.move_to_stairs),
#             ("Archaeologist:\nThis style of architecture looks familiar...\nWe must go deeper!", self.move_downstairs)
#         ]
#         self.talk_index = 0

#     def on_bump(self):
#         line = self.lines[self.talk_index][0]
#         action = self.lines[self.talk_index][1]
#         self.game.talking_time(line, action)

#     def move_to_stairs(self):
#         newx, newy = (4, 4)
#         self.owner.world.on_mob_move(self.owner.x, self.owner.y, newx, newy)
#         self.owner.x = newx
#         self.owner.y = newy
#         self.talk_index = 1

#     def move_downstairs(self):
#         # just temporarily remove from the world until I make more levels
#         self.owner.world.mobs.pop((self.owner.x, self.owner.y))
#         self.talk_index = 2
