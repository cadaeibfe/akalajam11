import pygame as pg

class Assets:
    @staticmethod
    def load_assets():
        # fonts
        Assets.big_font = pg.font.Font("freesansbold.ttf", 100)
        Assets.talk_font = pg.font.Font("freesansbold.ttf", 32)

        # images
        Assets.tile_sheet = pg.image.load("images/tile_sheet.png").convert()
        Assets.tile_sheet = pg.transform.scale(Assets.tile_sheet, (Assets.tile_sheet.get_width()*3, Assets.tile_sheet.get_height()*3))

        # sounds
        Assets.step_sound = pg.mixer.Sound("sounds/Hit_Hurt5.wav")
        Assets.bump_sound = pg.mixer.Sound("sounds/Hit_Hurt4.wav")
        Assets.hit_sound = pg.mixer.Sound("sounds/Hit_Hurt22.wav")
        Assets.up_stairs_sound = pg.mixer.Sound("sounds/Hit_Hurt3.wav")
        Assets.powerup_sound = pg.mixer.Sound("sounds/Powerup6.wav")