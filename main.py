import pygame as pg

from data.game import Game

if __name__ == "__main__":
    pg.init()
    Game().run()
    pg.quit()