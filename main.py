from enum import Enum
from functools import lru_cache

import pygame as pg

from assets import Assets
from mobs import Lizardman, Player
from world import Tile, TILE_SIZE, World


class State(Enum):
    PLAY = 1
    TALK = 2


class Game:
    def run(self):
        # Basic setup
        screen = pg.display.set_mode((800, 600))
        clock = pg.time.Clock()
        dt = 0

        # Load resources
        Assets.load_assets()

        self.new_game()

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
            lizardman = Lizardman(self.world, 6, 10, 4, 0, self.player)
            self.world.add_mob_at_random_empty_pos(lizardman)

    def on_event(self, event):
        if self.state == State.PLAY:
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

    def on_update(self, dt):
        if self.player.spent_turn:
            self.world.mobs.update()
            self.player.spent_turn = False

    def on_draw(self, surf):
        surf.fill((32, 32, 32))

        # calculat scroll so player will be in center
        scroll_x = (surf.get_width() - TILE_SIZE) // 2 - self.player.x * TILE_SIZE
        scroll_y = (surf.get_height() - TILE_SIZE) // 2 - self.player.y * TILE_SIZE

        # draw tiles
        for y in range(self.world.height):
            for x in range(self.world.width):
                rect = pg.Rect(scroll_x + x*TILE_SIZE, scroll_y + y*TILE_SIZE, TILE_SIZE, TILE_SIZE)
                if rect.colliderect(surf.get_rect()) and self.player.can_see(x, y):
                    image = self.world.get_image(x, y)
                    surf.blit(image, rect)

        # draw mobs
        for mob in self.world.mobs:
            rect = pg.Rect(scroll_x + mob.x*TILE_SIZE, scroll_y + mob.y*TILE_SIZE, TILE_SIZE, TILE_SIZE)
            if rect.colliderect(surf.get_rect()) and self.player.can_see(mob.x, mob.y):
                image = self.world.tile_sheet.subsurface((mob.tile_index*TILE_SIZE, 0, TILE_SIZE, TILE_SIZE))
                surf.blit(image, rect)

        # draw ui
        draw_text(surf, Assets.talk_font, "HP", 10, 10)
        for i in range(self.player.max_hp):
            color = (230, 41, 55) if i < self.player.hp else (245, 245, 245)
            pg.draw.rect(surf, color, (62 + i*7, 12, 5, 26))

        if self.state == State.TALK:
            talk_rect = pg.Rect(20, 20, surf.get_width() - 40, 200)
            pg.draw.rect(surf, (0, 0, 0), talk_rect)
            pg.draw.rect(surf, (245, 245, 245), talk_rect, 1)

            y = 40
            for line in self.talk_lines:
                draw_text(surf, Assets.talk_font, line, 40, y)
                y += Assets.talk_font.get_linesize()

            pg.draw.rect(surf, (245, 245, 245), (talk_rect.right-30, talk_rect.bottom-30, 20, 20))

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


def draw_text(surf, font, text, x, y):
    text_surf = render_text(font, text, (245, 245, 245))
    text_rect = text_surf.get_rect(topleft = (x, y))
    surf.blit(text_surf, text_rect)

@lru_cache
def render_text(font, text, color):
    return font.render(text, True, color)

if __name__ == "__main__":
    pg.init()
    Game().run()
    pg.quit()