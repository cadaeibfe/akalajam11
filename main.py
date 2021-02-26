from enum import Enum
from functools import lru_cache

import pygame as pg

TILE_SIZE = 64

class World:
    def __init__(self):
        self.tiles = [[1, 1, 1, 1, 1, 1, 1, 1, 1],
                      [1, 0, 0, 0, 0, 0, 0, 0, 1],
                      [1, 0, 0, 1, 1, 1, 0, 0, 1],
                      [1, 0, 0, 1, 4, 1, 0, 0, 1],
                      [1, 0, 0, 1, 0, 1, 0, 0, 1],
                      [1, 0, 0, 0, 0, 0, 0, 0, 1],
                      [1, 0, 0, 0, 0, 0, 0, 0, 1],
                      [1, 1, 1, 0, 0, 0, 1, 1, 1],
                      [1, 1, 0, 0, 0, 0, 0, 1, 1],
                      [1, 1, 0, 1, 1, 1, 0, 1, 1],
                      [1, 1, 0, 0, 0, 0, 0, 1, 1],
                      [1, 1, 1, 1, 0, 1, 1, 1, 1],
                      [1, 1, 1, 0, 0, 0, 1, 1, 1],
                      [1, 1, 0, 0, 0, 0, 0, 1, 1],
                      [1, 1, 0, 0, 0, 0, 0, 1, 1],
                      [1, 1, 1, 0, 0, 0, 1, 1, 1],
                      [1, 1, 1, 1, 0, 1, 1, 1, 1],
                      [1, 1, 1, 1, 1, 1, 1, 1, 1]]
        self.width = len(self.tiles[0])
        self.height = len(self.tiles)

        self.mobs = {}

        self.tile_sheet = pg.Surface((384, 64))
        self.tile_sheet.set_colorkey((0, 0, 0))
        pg.draw.rect(self.tile_sheet, (255, 0, 0), (0, 0, TILE_SIZE, TILE_SIZE), 1)                 # out of bounds
        pg.draw.rect(self.tile_sheet, (48, 48, 48), (TILE_SIZE, 0, TILE_SIZE, TILE_SIZE))        # floor
        pg.draw.rect(self.tile_sheet, (156, 156, 156), (2*TILE_SIZE, 0, TILE_SIZE, TILE_SIZE))   # wall
        pg.draw.rect(self.tile_sheet, (80, 80, 80), (2*TILE_SIZE, 0, TILE_SIZE, TILE_SIZE), 2)
        pg.draw.rect(self.tile_sheet, (0, 121, 241), (3*TILE_SIZE, 0, TILE_SIZE, TILE_SIZE))        # player
        pg.draw.rect(self.tile_sheet, (0, 228, 48), (4*TILE_SIZE, 0, TILE_SIZE, TILE_SIZE))         # archaeologist
        pg.draw.rect(self.tile_sheet, (48, 48, 48), (5*TILE_SIZE, 0, TILE_SIZE, TILE_SIZE))        # down stairs
        pg.draw.line(self.tile_sheet, (245, 245, 245), (5.25*TILE_SIZE, 10), (5.75*TILE_SIZE, 0.5*TILE_SIZE), 10)
        pg.draw.line(self.tile_sheet, (245, 245, 245), (5.25*TILE_SIZE, TILE_SIZE-10), (5.75*TILE_SIZE, 0.5*TILE_SIZE), 10)


    def get_tile(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.tiles[y][x]
        else:
            return -1

    def get_mob(self, x, y):
        return self.mobs.get((x, y))

    def get_image(self, x, y):
        mob = self.get_mob(x, y)
        if mob != None:
            return self.tile_sheet.subsurface(mob.glyph*TILE_SIZE, 0, TILE_SIZE, TILE_SIZE)

        tile = self.get_tile(x, y)
        return self.tile_sheet.subsurface(((tile+1)*TILE_SIZE, 0, TILE_SIZE, TILE_SIZE))

    def is_walkable(self, x, y):
        tile = self.get_tile(x, y)
        return tile == 0 or tile == 4

    def add_mob_at(self, mob, x, y):
        self.mobs[(x, y)] = mob

    def on_mob_move(self, oldx, oldy, newx, newy):
        mob = self.mobs.pop((oldx, oldy))
        self.mobs[(newx, newy)] = mob


class Mob:
    def __init__(self, world, glyph, x, y, ai):
        self.world = world
        self.world.add_mob_at(self, x, y)
        self.glyph = glyph
        self.x = x
        self.y = y
        self.ai = ai
        if self.ai != None:
            self.ai.owner = self

    def move(self, mx, my):
        newx = self.x + mx
        newy = self.y + my

        other = self.world.get_mob(newx, newy)
        if other != None:
            other.ai.on_bump()
            return

        if self.world.is_walkable(newx, newy):
            self.world.on_mob_move(self.x, self.y, newx, newy)
            self.x = newx
            self.y = newy
        else:
            print("wall bump")


class ArchAi:
    def __init__(self, game):
        self.game = game
        self.lines = [
            ("Archaeologist:\nOh, you're here!\nThanks for helping me with my expedition.", self.move_to_stairs),
            ("Archaeologist:\nThis style of architecture looks familiar...\nWe must go deeper!", self.move_downstairs)
        ]
        self.talk_index = 0

    def on_bump(self):
        line = self.lines[self.talk_index][0]
        action = self.lines[self.talk_index][1]
        self.game.talking_time(line, action)

    def move_to_stairs(self):
        newx, newy = (4, 4)
        self.owner.world.on_mob_move(self.owner.x, self.owner.y, newx, newy)
        self.owner.x = newx
        self.owner.y = newy
        self.talk_index = 1

    def move_downstairs(self):
        # just temporarily remove from the world until I make more levels
        self.owner.world.mobs.pop((self.owner.x, self.owner.y))
        self.talk_index = 2


class State(Enum):
    PLAY = 1
    TALK = 2


class Game:
    def run(self):
        # Basic setup
        screen = pg.display.set_mode((800, 600))
        clock = pg.time.Clock()
        dt = 0

        # Load resources
        self.talk_font = pg.font.Font("freesansbold.ttf", 32)

        self.new_game()

        # Main game loop
        while True:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    return
                else:
                    self.on_event(event)

            self.on_update(dt)
            self.on_draw(screen)

            pg.display.flip()
            dt = clock.tick(60)

    def new_game(self):
        self.state = State.PLAY
        self.world = World()
        self.player = Mob(self.world, 3, 4, 15, None)
        self.arch = Mob(self.world, 4, 4, 11, ArchAi(self))

    def on_event(self, event):
        if self.state == State.PLAY:
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_LEFT:
                    self.player.move(-1, 0)
                elif event.key == pg.K_RIGHT:
                    self.player.move(1, 0)
                elif event.key == pg.K_UP:
                    self.player.move(0, -1)
                elif event.key == pg.K_DOWN:
                    self.player.move(0, 1)

        elif self.state == State.TALK:
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_z:
                    self.state = State.PLAY
                    if self.talk_action != None:
                        self.talk_action()

    def on_update(self, dt):
        pass

    def on_draw(self, surf):
        surf.fill((32, 32, 32))

        # calculat scroll so player will be in center
        scroll_x = (surf.get_width() - TILE_SIZE) // 2 - self.player.x * TILE_SIZE
        scroll_y = (surf.get_height() - TILE_SIZE) // 2 - self.player.y * TILE_SIZE

        # draw tiles
        for y in range(self.world.height):
            for x in range(self.world.width):
                rect = pg.Rect(scroll_x + x*TILE_SIZE, scroll_y + y*TILE_SIZE, TILE_SIZE, TILE_SIZE)
                if not rect.colliderect(surf.get_rect()): continue

                image = self.world.get_image(x, y)
                surf.blit(image, rect)

        if self.state == State.TALK:
            talk_rect = pg.Rect(20, 20, surf.get_width() - 40, 200)
            pg.draw.rect(surf, (0, 0, 0), talk_rect)
            pg.draw.rect(surf, (245, 245, 245), talk_rect, 1)

            y = 40
            for line in self.talk_lines:
                draw_text(surf, self.talk_font, line, 40, y)
                y += self.talk_font.get_linesize()

            pg.draw.rect(surf, (245, 245, 245), (talk_rect.right-30, talk_rect.bottom-30, 20, 20))

    def talking_time(self, text, action):
        self.state = State.TALK
        self.talk_lines = text.split('\n')
        self.talk_action = action


def draw_text(surf, font, text, x, y):
    text_surf = render_text(font, text, (245, 245, 245))
    text_rect = text_surf.get_rect(topleft = (x, y))
    surf.blit(text_surf, text_rect)

@lru_cache
def render_text(font, text, color):
    return font.render(text, True, color)

if __name__ == "__main__":
    pg.init()
    Game().run()
    pg.quit()