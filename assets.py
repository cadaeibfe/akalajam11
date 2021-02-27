import pygame as pg

class Assets:
    @staticmethod
    def load_assets():
        # fonts
        Assets.big_font = pg.font.Font("freesansbold.ttf", 100)
        Assets.talk_font = pg.font.Font("freesansbold.ttf", 32)

        # sounds
        Assets.step_sound = pg.mixer.Sound("sounds/Hit_Hurt5.wav")
        Assets.bump_sound = pg.mixer.Sound("sounds/Hit_Hurt4.wav")
        Assets.hit_sound = pg.mixer.Sound("sounds/Hit_Hurt22.wav")
        Assets.up_stairs_sound = pg.mixer.Sound("sounds/Hit_Hurt3.wav")