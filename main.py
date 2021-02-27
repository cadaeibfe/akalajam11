from enum import Enum
from functools import lru_cache
import random as rng

import pygame as pg

TILE_SIZE = 32

class Tile(Enum):
    OUT_OF_BOUNDS = -1
    FLOOR = 0
    WALL = 1
    DOWN_STAIRS = 2
    UP_STAIRS = 3

class MazeGenerator:
    def generate(self, width, height):
        self.tiles = [[Tile.WALL for x in range(width)] for y in range(height)]
        rooms = []

        # make empty rooms
        for i in range(5):
            for j in range(100):
                r = pg.Rect(0, 0, 0, 0)
                r.w = rng.randrange(4, 9)
                r.h = rng.randrange(4, 9)
                r.x = rng.randrange(1, width - r.w)
                r.y = rng.randrange(1, height - r.h)
                if not self.collide_any(r, rooms):
                    self.dig_room(r)
                    rooms.append(r)
                    break

        # connect the rooms
        connected = [rooms[0]]
        unconnected = rooms[1:]

        while len(unconnected) > 0:
            start_room = rng.choice(connected)
            end_room = rng.choice(unconnected)
            start_pos = self.random_room_pos(start_room)
            end_pos = self.random_room_pos(end_room)
            self.dig_hall(start_pos, end_pos)
            unconnected.remove(end_room)
            connected.append(end_room)

        # put stairs
        up_stairs_room = rng.choice(rooms)
        up_stairs_pos = self.random_room_pos(up_stairs_room)
        self.tiles[up_stairs_pos[1]][up_stairs_pos[0]] = Tile.UP_STAIRS

        rooms.remove(up_stairs_room)
        down_stairs_room = rng.choice(rooms)
        down_stairs_pos = self.random_room_pos(down_stairs_room)
        self.tiles[down_stairs_pos[1]][down_stairs_pos[0]] = Tile.DOWN_STAIRS

        return self.tiles, up_stairs_pos, down_stairs_pos

    def random_room_pos(self, r):
        return (rng.randrange(r.left, r.right), rng.randrange(r.top, r.bottom))

    def dig_room(self, r):
        for y in range(r.top, r.bottom):
            for x in range(r.left, r.right):
                self.tiles[y][x] = Tile.FLOOR

    def dig_hall(self, p1, p2):
        xmin = min(p1[0], p2[0])
        xmax = max(p1[0], p2[0])
        ymin = min(p1[1], p2[1])
        ymax = max(p1[1], p2[1])
        for x in range(xmin, xmax):
            self.tiles[p1[1]][x] = Tile.FLOOR
        for y in range(ymin, ymax+1):
            self.tiles[y][p2[0]] = Tile.FLOOR

    def collide_room(self, r1, r2):
        return (r1.right >= r2.left and r1.left <= r2.right and r1.bottom >= r2.top and r1.top <= r2.bottom)

    def collide_any(self, r, others):
        for other in others:
            if self.collide_room(r, other):
                return True
        return False


class World:
    def __init__(self):
        # self.tiles = [[1, 1, 1, 1, 1, 1, 1, 1, 1],
        #               [1, 0, 0, 0, 0, 0, 0, 0, 1],
        #               [1, 0, 0, 1, 1, 1, 0, 0, 1],
        #               [1, 0, 0, 1, 4, 1, 0, 0, 1],
        #               [1, 0, 0, 1, 0, 1, 0, 0, 1],
        #               [1, 0, 0, 0, 0, 0, 0, 0, 1],
        #               [1, 0, 0, 0, 0, 0, 0, 0, 1],
        #               [1, 1, 1, 0, 0, 0, 1, 1, 1],
        #               [1, 1, 0, 0, 0, 0, 0, 1, 1],
        #               [1, 1, 0, 1, 1, 1, 0, 1, 1],
        #               [1, 1, 0, 0, 0, 0, 0, 1, 1],
        #               [1, 1, 1, 1, 0, 1, 1, 1, 1],
        #               [1, 1, 1, 0, 0, 0, 1, 1, 1],
        #               [1, 1, 0, 0, 0, 0, 0, 1, 1],
        #               [1, 1, 0, 0, 0, 0, 0, 1, 1],
        #               [1, 1, 1, 0, 0, 0, 1, 1, 1],
        #               [1, 1, 1, 1, 0, 1, 1, 1, 1],
        #               [1, 1, 1, 1, 1, 1, 1, 1, 1]]
        self.generator = MazeGenerator()
        self.tiles, self.up_stairs_pos, self.down_stairs_pos = self.generator.generate(20, 20)
        self.width = len(self.tiles[0])
        self.height = len(self.tiles)

        self.mobs = {}

        self.tile_sheet = pg.Surface((384, 64))
        self.tile_sheet.set_colorkey((0, 0, 0))
        pg.draw.rect(self.tile_sheet, (255, 0, 0), (0, 0, TILE_SIZE, TILE_SIZE), 1)                 # out of bounds
        pg.draw.rect(self.tile_sheet, (48, 48, 48), (TILE_SIZE, 0, TILE_SIZE, TILE_SIZE))           # floor
        pg.draw.rect(self.tile_sheet, (156, 156, 156), (2*TILE_SIZE, 0, TILE_SIZE, TILE_SIZE))      # wall
        pg.draw.rect(self.tile_sheet, (80, 80, 80), (2*TILE_SIZE, 0, TILE_SIZE, TILE_SIZE), 2)
        pg.draw.rect(self.tile_sheet, (48, 48, 48), (3*TILE_SIZE, 0, TILE_SIZE, TILE_SIZE))         # down stairs
        pg.draw.line(self.tile_sheet, (245, 245, 245), (3.25*TILE_SIZE, 10), (3.75*TILE_SIZE, 0.5*TILE_SIZE), 5)
        pg.draw.line(self.tile_sheet, (245, 245, 245), (3.25*TILE_SIZE, TILE_SIZE-10), (3.75*TILE_SIZE, 0.5*TILE_SIZE), 5)
        pg.draw.rect(self.tile_sheet, (48, 48, 48), (4*TILE_SIZE, 0, TILE_SIZE, TILE_SIZE))         # up stairs
        pg.draw.line(self.tile_sheet, (245, 245, 245), (4.75*TILE_SIZE, 10), (4.25*TILE_SIZE, 0.5*TILE_SIZE), 5)
        pg.draw.line(self.tile_sheet, (245, 245, 245), (4.75*TILE_SIZE, TILE_SIZE-10), (4.25*TILE_SIZE, 0.5*TILE_SIZE), 5)
        pg.draw.rect(self.tile_sheet, (0, 121, 241), (5*TILE_SIZE, 0, TILE_SIZE, TILE_SIZE))        # player
        pg.draw.rect(self.tile_sheet, (0, 228, 48), (6*TILE_SIZE, 0, TILE_SIZE, TILE_SIZE))         # archaeologist


    def get_tile(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.tiles[y][x]
        else:
            return Tile.OUT_OF_BOUNDS

    def get_mob(self, x, y):
        return self.mobs.get((x, y))

    def get_image(self, x, y):
        mob = self.get_mob(x, y)
        if mob != None:
            return self.tile_sheet.subsurface(mob.glyph*TILE_SIZE, 0, TILE_SIZE, TILE_SIZE)

        tile = self.get_tile(x, y)
        return self.tile_sheet.subsurface(((tile.value+1)*TILE_SIZE, 0, TILE_SIZE, TILE_SIZE))

    def is_walkable(self, x, y):
        tile = self.get_tile(x, y)
        return tile == Tile.FLOOR or tile == Tile.UP_STAIRS or tile == Tile.DOWN_STAIRS

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

    def down_stairs(self):
        tile = self.world.get_tile(self.x, self.y)
        if tile == Tile.DOWN_STAIRS:
            self.world.tiles, self.world.up_stairs_pos, self.world.down_stairs_pos = self.world.generator.generate(20, 20)
            self.world.on_mob_move(self.x, self.y, self.world.up_stairs_pos[0], self.world.up_stairs_pos[1])
            self.x = self.world.up_stairs_pos[0]
            self.y = self.world.up_stairs_pos[1]

    def up_stairs(self):
        tile = self.world.get_tile(self.x, self.y)
        if tile == Tile.UP_STAIRS:
            self.world.tiles, self.world.down_stairs_pos, self.world.down_stairs_pos = self.world.generator.generate(20, 20)
            self.world.on_mob_move(self.x, self.y, self.world.down_stairs_pos[0], self.world.down_stairs_pos[1])
            self.x = self.world.down_stairs_pos[0]
            self.y = self.world.down_stairs_pos[1]


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
        # self.player = Mob(self.world, 3, 4, 15, None)
        self.player = Mob(self.world, 5, self.world.up_stairs_pos[0], self.world.up_stairs_pos[1], None)
        # self.arch = Mob(self.world, 4, 4, 11, ArchAi(self))

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
                elif event.unicode == ">":
                    self.player.down_stairs()
                elif event.unicode == "<":
                    self.player.up_stairs()
                ## DEBUG
                elif event.key == pg.K_r:
                    self.new_game()
                ## ENDDEBUG

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