import pygame as pg

from assets import Assets

class Mob(pg.sprite.Sprite):
    def __init__(self, world, glyph, max_hp, attack_power, defense_power):
        super().__init__()
        self.world = world
        self.glyph = glyph
        self.max_hp = max_hp
        self.hp = self.max_hp
        self.attack_power = attack_power
        self.defense_power = defense_power

    def move(self, mx, my):
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
        Assets.hit_sound.play()

    def get_attack_power(self):
        return self.attack_power

    def get_defense_power(self):
        return self.defense_power


class Player(Mob):
    def __init__(self, world):
        super().__init__(world, 4, 30, 5, 2)
        self.vision = 5.2

    def can_see(self, x, y):
        return (self.x - x)**2 + (self.y - y)**2 <= self.vision**2


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
