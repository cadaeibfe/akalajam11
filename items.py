import pygame as pg

class Item(pg.sprite.Sprite):
    def __init__(self, tile):
        super().__init__()
        self.tile = tile
        self.x = None
        self.y = None