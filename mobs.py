import random as rng

import pygame as pg

from assets import Assets
from items import Item
from quest import Quest
from world import Tile

class Mob(pg.sprite.Sprite):
    def __init__(self, world, tile, max_hp, attack_power, defense_power):
        super().__init__()
        self.world = world
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
            other.on_attack(self)
            return

        if self.world.is_walkable(newx, newy):
            Assets.step_sound.play()
            self.x = newx
            self.y = newy
        else:
            Assets.bump_sound.play()

    def on_attack(self, attacker):
        attack_power = attacker.get_attack_power()
        defense_power = self.get_defense_power()
        damage = max(1, attack_power - defense_power)
        self.hp -= damage
        if self.hp <= 0:
            self.kill()

            # lizardmen can drop the three treasures, in order
            if self.tile == Tile.LIZARD and rng.random() < 0.2:
                if not Quest.has_sword:
                    self.world.items.add(Item(Tile.SWORD, self.x, self.y))
                elif not Quest.has_shield:
                    self.world.items.add(Item(Tile.SHIELD, self.x, self.y))
                elif not Quest.has_crown:
                    self.world.items.add(Item(Tile.CROWN, self.x, self.y))

        Assets.hit_sound.play()

    def get_attack_power(self):
        return self.attack_power

    def get_defense_power(self):
        return self.defense_power

    def can_see(self, x, y):
        return (self.x - x)**2 + (self.y - y)**2 <= self.vision**2


class Player(Mob):
    def __init__(self, world):
        super().__init__(world, Tile.HERO, 30, 5, 2)
        self.vision = 5.2
        self.spent_turn = False

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
            elif item.tile == Tile.SHIELD:
                Quest.has_shield = True
                self.tile = Tile.HERO_SS
                Assets.powerup_sound.play()
            elif item.tile == Tile.CROWN:
                Quest.has_crown = True
                Assets.powerup_sound.play()

    def get_attack_power(self):
        attack_power = super().get_attack_power()
        if Quest.has_sword:
            attack_power += 5
        return attack_power

    def get_defense_power(self):
        defense_power = super().get_defense_power()
        if Quest.has_shield:
            defense_power += 5
        return defense_power


class Lizardman(Mob):
    def __init__(self, world, tile_index, max_hp, attack_power, defense_power, target):
        super().__init__(world, tile_index, max_hp, attack_power, defense_power)
        self.target = target
        self.vision = 4

    def update(self):
        if self.can_see(self.target.x, self.target.y):
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
