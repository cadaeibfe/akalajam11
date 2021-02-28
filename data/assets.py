import pygame as pg

TILE_SIZE = 60

class Assets:
    @staticmethod
    def load_assets():
        # fonts
        Assets.big_font = pg.font.Font("freesansbold.ttf", 100)
        Assets.damage_font = pg.font.Font("freesansbold.ttf", 44)
        Assets.small_font = pg.font.Font("freesansbold.ttf", 20)

        # images
        Assets.tile_sheet_small = pg.image.load("data/images/tile_sheet.png").convert()   # save original size image for ui icons
        Assets.tile_sheet = pg.transform.scale(Assets.tile_sheet_small, (Assets.tile_sheet_small.get_width()*3, Assets.tile_sheet_small.get_height()*3))
        Assets.tile_sheet_flipped = pg.transform.flip(Assets.tile_sheet, True, False)

        Assets.title_image = pg.image.load("data/images/title.png").convert()
        Assets.title_image = pg.transform.scale(Assets.title_image, (Assets.title_image.get_width()*5, Assets.title_image.get_height()*5))

        # sounds
        Assets.step_sound = Assets.load_sound("data/sounds/Hit_Hurt5.wav")
        Assets.bump_sound = Assets.load_sound("data/sounds/Hit_Hurt4.wav")
        Assets.hit_sound = Assets.load_sound("data/sounds/Hit_Hurt22.wav")
        Assets.up_stairs_sound = Assets.load_sound("data/sounds/Hit_Hurt3.wav")
        Assets.powerup_sound = Assets.load_sound("data/sounds/Powerup6.wav")
        Assets.heal_sound = Assets.load_sound("data/sounds/Powerup12.wav")
        Assets.select_sound = Assets.load_sound("data/sounds/Blip_Select6.wav")
        Assets.game_over_sound = Assets.load_sound("data/sounds/Randomize39.wav")
        Assets.win_sound = Assets.load_sound("data/sounds/Powerup19.wav")

    @staticmethod
    def load_sound(filepath, volume=0.4):
        # helper method to set the volume of all sounds as they are loaded
        sound = pg.mixer.Sound(filepath)
        sound.set_volume(volume)
        return sound

    @staticmethod
    def get_tile_image(tile, flip_h=False):
        if flip_h:
            return Assets.tile_sheet_flipped.subsurface((Assets.tile_sheet_flipped.get_width() - (tile.value+1)*TILE_SIZE, 0, TILE_SIZE, TILE_SIZE))
        else:
            return Assets.tile_sheet.subsurface((tile.value*TILE_SIZE, 0, TILE_SIZE, TILE_SIZE))
