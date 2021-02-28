""" This module runs the game Tomb of the Lizard King, my entry for the 11th Alakajam. """

import pygame as pg

from data.game import Game

if __name__ == "__main__":
    pg.init()
    Game().run()
    pg.quit()