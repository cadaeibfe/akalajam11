import pygame as pg

class Item(pg.sprite.Sprite):
    def __init__(self, tile, x, y):
        super().__init__()
        self.tile = tile
        self.x = x
        self.y = y