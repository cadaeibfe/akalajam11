from enum import Enum
from functools import lru_cache

import pygame as pg

from assets import Assets
from mobs import Lizardman, Player
from world import Tile, TILE_SIZE, World


class State(Enum):
    TITLE = 0
    PLAY = 1
    TALK = 2
    GAME_OVER = 3


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
        self.state = State.PLAY
        self.world = World()
        self.new_player()
        self.create_enemies()
        # self.arch = Mob(self.world, 4, 4, 11, ArchAi(self))

    def new_player(self):
        self.player = Player(self.world)
        self.world.add_mob_at(self.player, *self.world.start_pos)

    def create_enemies(self):
        for i in range(5):
            lizardman = Lizardman(self.world, 8, 10, 4, 0, self.player)
            self.world.add_mob_at_random_empty_pos(lizardman)

    def on_event(self, event):
        if self.state == State.TITLE:
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
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
                ## DEBUG
                elif event.key == pg.K_r:
                    self.new_game()
                ## ENDDEBUG

                if self.world.get_tile(self.player.x, self.player.y) == Tile.UP_STAIRS:
                    self.up_stairs()

        elif self.state == State.TALK:
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_z:
                    self.state = State.PLAY
                    if self.talk_action != None:
                        self.talk_action()

        elif self.state == State.GAME_OVER:
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                self.state = State.TITLE

    def on_update(self, dt):
        if self.state == State.PLAY:
            if self.player.spent_turn:
                for mob in self.world.mobs:
                    mob.update()
                    if not self.player.alive():
                        self.player.tile_index = 6
                        self.world.mobs.add(self.player)
                        self.state = State.GAME_OVER
                        break
                self.player.spent_turn = False

    def on_draw(self, surf):
        surf.fill((32, 32, 32))

        if self.state == State.TITLE:
            self.draw_title_screen(surf)
        else:
            self.world.draw(surf, self.player)
            self.draw_ui(surf)

            if self.state == State.TALK:
                self.draw_text_box(surf)
            elif self.state == State.GAME_OVER:
                self.draw_game_over_screen(surf)

    def draw_ui(self, surf):
        draw_text(surf, Assets.talk_font, "HP", 10, 10)
        for i in range(self.player.max_hp):
            color = (230, 41, 55) if i < self.player.hp else (245, 245, 245)
            pg.draw.rect(surf, color, (62 + i*7, 12, 5, 26))

    def draw_talk_box(self, surf):
        talk_rect = pg.Rect(20, 20, surf.get_width() - 40, 200)
        pg.draw.rect(surf, (0, 0, 0), talk_rect)
        pg.draw.rect(surf, (245, 245, 245), talk_rect, 1)

        y = 40
        for line in self.talk_lines:
            draw_text(surf, Assets.talk_font, line, 40, y)
            y += Assets.talk_font.get_linesize()

        pg.draw.rect(surf, (245, 245, 245), (talk_rect.right-30, talk_rect.bottom-30, 20, 20))

    def draw_title_screen(self, surf):
        draw_text(surf, Assets.big_font, "Tomb of the", surf.get_width()//2, surf.get_height()//2 - 150, "center")
        draw_text(surf, Assets.big_font, "Lizard King", surf.get_width()//2, surf.get_height()//2 - 40, "center")
        draw_text(surf, Assets.talk_font, "Press [Space] To Play", surf.get_width()//2, surf.get_height()//2 + 150, "center")

    def draw_game_over_screen(self, surf):
        draw_text(surf, Assets.big_font, "Game Over", surf.get_width()//2, surf.get_height()//2 - 70, "center")
        draw_text(surf, Assets.talk_font, "Press [Space]", surf.get_width()//2, surf.get_height()//2 + 60, "center")

    def talking_time(self, text, action):
        self.state = State.TALK
        self.talk_lines = text.split('\n')
        self.talk_action = action

    def up_stairs(self):
        tile = self.world.get_tile(self.player.x, self.player.y)
        if tile == Tile.UP_STAIRS:
            Assets.up_stairs_sound.play()
            self.world.new_level()
            self.world.add_mob_at(self.player, *self.world.start_pos)
            self.create_enemies()


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