from enum import Enum
from functools import lru_cache
import random as rng

import pygame as pg

from assets import Assets, TILE_SIZE
from items import Item
from mobs import Bat, Lizardman, Player, Slime
from quest import Quest
from world import Tile, World


class State(Enum):
    TITLE = 0
    PLAY = 1
    TALK = 2
    GAME_OVER = 3
    WIN = 4


class Game:
    def run(self):
        # Basic setup
        screen = pg.display.set_mode((800, 600))
        clock = pg.time.Clock()
        dt = 0

        # Load resources
        Assets.load_assets()

        # Show title screen when program starts
        # self.state = State.TITLE
        self.new_game() ##DEBUG

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
        Quest.reset()
        self.float_group = pg.sprite.Group()  # used to draw floating damage numbers
        self.state = State.PLAY
        self.world = World()
        self.new_player()
        self.create_enemies_and_items()

    def new_player(self):
        self.player = Player(self.world, self)
        self.world.add_mob_at(self.player, *self.world.start_pos)

    def create_enemies_and_items(self):
        num_enemies = 5 + self.player.level  # more enemies as player levels up
        for i in range(num_enemies):
            # choose an enemy type
            if self.player.level == 1:
                t = rng.randrange(0, 2)  # only slimes and bats at level 1
            elif self.player.level < 6 and not Quest.has_shield:
                t = rng.randrange(0, 3)  # lizardmen can spawn at low levels
            else:
                t = rng.randrange(0, 4)  # lizard knights can spawn

            # spawn enemy of the chosen type
            if t == 0:
                slime = Slime(self.world, self, Tile.SLIME, 6, 2, 0, self.player)
                self.world.add_mob_at_random_empty_pos(slime)
            elif t == 1:
                bat = Bat(self.world, self, Tile.BAT, 10, 4, 0, self.player)
                self.world.add_mob_at_random_empty_pos(bat)
            elif t == 2:
                lizardman = Lizardman(self.world, self, Tile.LIZARD, 20, 6, 2, self.player)
                self.world.add_mob_at_random_empty_pos(lizardman)
            elif t == 3:
                lizardknight = Lizardman(self.world, self, Tile.LIZARDKNIGHT, 30, 10, 4, self.player)
                lizardknight.vision += 1
                lizardknight.treasure_drop_rate *= 3
                lizardknight.xp *= 4
                self.world.add_mob_at_random_empty_pos(lizardknight)

        num_items = num_enemies // 3
        for i in range(num_items):
            self.world.add_item_at_random_empty_pos(Item(Tile.POTION))

    def new_float_text(self, text, x, y, color):
        self.float_group.add(FloatText(text, x, y, color))

    def on_event(self, event):
        if self.state == State.TITLE:
            if event.type == pg.KEYDOWN and (event.key == pg.K_SPACE or event.key == pg.K_RETURN):
                Assets.select_sound.play()
                self.new_game()

        elif self.state == State.PLAY:
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_LEFT:
                    self.player.move(-1, 0)
                elif event.key == pg.K_RIGHT:
                    self.player.move(1, 0)
                elif event.key == pg.K_UP:
                    self.player.move(0, -1)
                elif event.key == pg.K_DOWN:
                    self.player.move(0, 1)
                elif event.key == pg.K_SPACE or event.key == pg.K_RETURN:
                    self.player.spent_turn = True
                ## DEBUG
                elif event.key == pg.K_r:
                    self.new_game()
                ## ENDDEBUG

                if self.world.get_tile(self.player.x, self.player.y) == Tile.UP_STAIRS:
                    self.up_stairs()

        elif self.state == State.TALK:
            if event.type == pg.KEYDOWN and (event.key == pg.K_SPACE or event.key == pg.K_RETURN):
                self.state = State.PLAY
                if self.talk_action != None:
                    self.talk_action()

        elif self.state == State.GAME_OVER:
            if event.type == pg.KEYDOWN and (event.key == pg.K_SPACE or event.key == pg.K_RETURN):
                Assets.select_sound.play()
                self.state = State.TITLE

        elif self.state == State.WIN:
            if event.type == pg.KEYDOWN and (event.key == pg.K_SPACE or event.key == pg.K_RETURN):
                Assets.select_sound.play()
                self.state = State.TITLE

    def on_update(self, dt):
        if self.state == State.PLAY:
            self.float_group.update(dt)  # make damage text disappear after a moment

            if self.player.spent_turn:
                for mob in self.world.mobs:
                    mob.update()

                    # check if player was killed by last mob action
                    if not self.player.alive():
                        self.player.tile = Tile.SKULL
                        self.world.mobs.add(self.player)
                        self.state = State.GAME_OVER
                        Assets.game_over_sound.play()
                        break

                self.player.spent_turn = False

    def on_draw(self, surf):
        ui_size = 40
        surf.fill((0, 0, 0))

        if self.state == State.TITLE:
            self.draw_title_screen(surf)
        else:
            self.world.draw(surf, self.player, ui_size)
            self.draw_ui(surf, ui_size)
            self.draw_damage_text(surf)

            if self.state == State.TALK:
                self.draw_talk_box(surf)
            elif self.state == State.GAME_OVER:
                self.draw_game_over_screen(surf)
            elif self.state == State.WIN:
                self.draw_win_screen(surf)

    def draw_ui(self, surf, ui_size):
        pg.draw.rect(surf, (32, 32, 32), (0, 0, surf.get_width(), ui_size))

        # draw health bar
        draw_text(surf, Assets.small_font, "HP:", 10, 11)
        for i in range(self.player.max_hp):
            color = (230, 41, 55) if i < self.player.hp else (245, 245, 245)
            pg.draw.rect(surf, color, (50 + i*7, 10, 5, 20))

        # draw quest items collected
        draw_text(surf, Assets.small_font, f"Treasures: {Quest.num_found()}/3", 420, 11)

        # draw xp and level
        draw_text(surf, Assets.small_font, f"Level: {self.player.level}  XP: {self.player.xp}/{self.player.xp_needed}", surf.get_width() - 10, 10, "topright")

        pg.draw.line(surf, (245, 245, 245), (0, ui_size), (surf.get_width(), ui_size))

    def draw_damage_text(self, surf):
        scroll_x = (surf.get_width() - TILE_SIZE) // 2 - self.player.x * TILE_SIZE
        scroll_y = (surf.get_height() - TILE_SIZE) // 2 - self.player.y * TILE_SIZE
        for float_text in self.float_group:
            rect = float_text.image.get_rect()
            rect.center = (scroll_x + float_text.x*TILE_SIZE + TILE_SIZE/2, scroll_y + float_text.y*TILE_SIZE + TILE_SIZE/2 + float_text.y_offset)
            surf.blit(float_text.image, rect)

    def draw_talk_box(self, surf):
        talk_rect = pg.Rect(20, 20, surf.get_width() - 40, 200)
        pg.draw.rect(surf, (0, 0, 0), talk_rect)
        pg.draw.rect(surf, (245, 245, 245), talk_rect, 1)

        y = 40
        for line in self.talk_lines:
            draw_text(surf, Assets.talk_font, line, 40, y)
            y += Assets.talk_font.get_linesize() + 1

        pg.draw.rect(surf, (245, 245, 245), (talk_rect.right-30, talk_rect.bottom-30, 20, 20))

    def draw_title_screen(self, surf):
        draw_text(surf, Assets.big_font, "Tomb of the", surf.get_width()//2, surf.get_height()//2 - 150, "center")
        draw_text(surf, Assets.big_font, "Lizard King", surf.get_width()//2, surf.get_height()//2 - 40, "center")
        draw_text(surf, Assets.talk_font, "Press [Space] To Play", surf.get_width()//2, surf.get_height()//2 + 150, "center")

    def draw_game_over_screen(self, surf):
        draw_text(surf, Assets.big_font, "Game Over", surf.get_width()//2, surf.get_height()//2 - 70, "center")
        draw_text(surf, Assets.talk_font, "Press [Space] To Return To Title", surf.get_width()//2, surf.get_height()//2 + 60, "center")

    def draw_win_screen(self, surf):
        draw_text(surf, Assets.big_font, "You Win!", surf.get_width()//2, surf.get_height()//2 - 70, "center")
        draw_text(surf, Assets.talk_font, "Thanks for playing!", surf.get_width()//2, surf.get_height()//2 + 60, "center")
        draw_text(surf, Assets.talk_font, "Press [Space] To Return To Title", surf.get_width()//2, surf.get_height()//2 + 100, "center")

    def talking_time(self, text, action):
        self.state = State.TALK
        self.talk_lines = text.split('\n')
        self.talk_action = action

    def up_stairs(self):
        tile = self.world.get_tile(self.player.x, self.player.y)
        if tile == Tile.UP_STAIRS:
            Assets.up_stairs_sound.play()

            # check if player is able to escape the tomb
            if Quest.can_escape():
                self.player.kill()  # make player sprite disappear so it looks like they went up the stairs
                Assets.win_sound.play()
                self.state = State.WIN
            else:
                # if not, just generate another level
                self.world.new_level()
                self.world.add_mob_at(self.player, *self.world.start_pos)
                self.create_enemies_and_items()
                Quest.treasure_dropped_this_level = False  # reset flag so treasure can drop again
                self.player.spent_turn = False  # don't spend a turn climbinb stairs, otherwise enemies get a free attack


class FloatText(pg.sprite.Sprite):
    """ Displays some floating text in the play field. """
    def __init__(self, text, x, y, color):
        super().__init__()
        self.image = render_text(Assets.damage_font, text, color)
        self.x = x
        self.y = y
        self.duration = 300
        self.y_offset = 0

    def update(self, dt):
        self.y_offset -= 1  # rising animation

        self.duration -= dt
        if self.duration <= 0:
            self.kill()


def draw_text(surf, font, text, x, y, anchor="topleft"):
    text_surf = render_text(font, text, (245, 245, 245))
    text_rect = text_surf.get_rect(**{anchor: (x, y)})
    surf.blit(text_surf, text_rect)

@lru_cache
def render_text(font, text, color):
    return font.render(text, True, color)

if __name__ == "__main__":
    pg.init()
    Game().run()
    pg.quit()