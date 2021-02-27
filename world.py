from enum import Enum
import random as rng

import pygame as pg

TILE_SIZE = 32


class Tile(Enum):
    OUT_OF_BOUNDS = -1
    FLOOR = 0
    WALL = 1
    UP_STAIRS = 2


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

        # put up stairs
        up_stairs_room = rng.choice(rooms)
        up_stairs_pos = self.random_room_pos(up_stairs_room)
        self.tiles[up_stairs_pos[1]][up_stairs_pos[0]] = Tile.UP_STAIRS

        # player starts in random room that is not the up stairs room
        rooms.remove(up_stairs_room)
        start_room = rng.choice(rooms)
        start_pos = self.random_room_pos(start_room)

        return self.tiles, start_pos

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
        self.new_level()

        self.tile_sheet = pg.Surface((384, 64))
        self.tile_sheet.set_colorkey((0, 0, 0))
        pg.draw.rect(self.tile_sheet, (255, 0, 0), (0, 0, TILE_SIZE, TILE_SIZE), 1)                 # out of bounds
        pg.draw.rect(self.tile_sheet, (48, 48, 48), (TILE_SIZE, 0, TILE_SIZE, TILE_SIZE))           # floor
        pg.draw.rect(self.tile_sheet, (156, 156, 156), (2*TILE_SIZE, 0, TILE_SIZE, TILE_SIZE))      # wall
        pg.draw.rect(self.tile_sheet, (80, 80, 80), (2*TILE_SIZE, 0, TILE_SIZE, TILE_SIZE), 2)
        pg.draw.rect(self.tile_sheet, (48, 48, 48), (3*TILE_SIZE, 0, TILE_SIZE, TILE_SIZE))         # up stairs
        pg.draw.line(self.tile_sheet, (235, 235, 235), (3.75*TILE_SIZE, 10), (3.25*TILE_SIZE, 0.5*TILE_SIZE), 5)
        pg.draw.line(self.tile_sheet, (235, 235, 235), (3.75*TILE_SIZE, TILE_SIZE-10), (3.25*TILE_SIZE, 0.5*TILE_SIZE), 5)
        pg.draw.rect(self.tile_sheet, (0, 121, 241), (4*TILE_SIZE, 0, TILE_SIZE, TILE_SIZE))        # player
        pg.draw.rect(self.tile_sheet, (0, 228, 48), (5*TILE_SIZE, 0, TILE_SIZE, TILE_SIZE))         # archaeologist
        pg.draw.rect(self.tile_sheet, (230, 41, 55), (6*TILE_SIZE, 0, TILE_SIZE, TILE_SIZE))        # lizardman

    def new_level(self):
        self.tiles, self.start_pos = self.generator.generate(20, 20)
        self.width = len(self.tiles[0])
        self.height = len(self.tiles)
        self.mobs = pg.sprite.Group()

    def get_tile(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.tiles[y][x]
        else:
            return Tile.OUT_OF_BOUNDS

    def get_mob(self, x, y):
        for mob in self.mobs:
            if mob.x == x and mob.y == y:
                return mob
        return None

    def get_image(self, x, y):
        tile = self.get_tile(x, y)
        return self.tile_sheet.subsurface(((tile.value+1)*TILE_SIZE, 0, TILE_SIZE, TILE_SIZE))

    def is_walkable(self, x, y):
        tile = self.get_tile(x, y)
        return tile == Tile.FLOOR or tile == Tile.UP_STAIRS

    def add_mob_at_random_empty_pos(self, mob):
        for i in range(100):
            x = rng.randrange(0, self.width)
            y = rng.randrange(0, self.height)
            if (x, y) != self.start_pos and self.is_walkable(x, y) and self.get_mob(x, y) == None:
                self.add_mob_at(mob, x, y)
                break

    def add_mob_at(self, mob, x, y):
        self.mobs.add(mob)
        mob.x = x
        mob.y = y
