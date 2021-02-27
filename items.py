import pygame as pg

class Item(pg.sprite.Sprite):
    def __init__(self, tile_index, x, y):
        super().__init__()
        self.tile_index = tile_index
        self.x = x
        self.y = y