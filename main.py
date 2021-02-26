import pygame as pg

TILE_SIZE = 64

class World:
    def __init__(self):
        self.tiles = [[1, 1, 1, 1, 1, 1, 1, 1, 1],
                      [1, 0, 0, 0, 0, 0, 0, 0, 1],
                      [1, 0, 0, 0, 0, 0, 0, 0, 1],
                      [1, 0, 0, 0, 0, 0, 0, 0, 1],
                      [1, 0, 0, 0, 0, 0, 0, 0, 1],
                      [1, 0, 0, 0, 0, 0, 0, 0, 1],
                      [1, 0, 0, 0, 0, 0, 0, 0, 1],
                      [1, 1, 1, 1, 1, 1, 1, 1, 1]]
        self.width = len(self.tiles[0])
        self.height = len(self.tiles)

    def get_tile(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.tiles[y][x]
        else:
            return -1

    def get_color(self, x, y):
        tile = self.get_tile(x, y)
        if tile == 0:
            return (80, 80, 80)
        elif tile == 1:
            return (245, 245, 245)
        else:
            return (255, 0, 0)

    def is_walkable(self, x, y):
        tile = self.get_tile(x, y)
        return tile == 0


class Mob:
    def __init__(self, x, y, world):
        self.x = x
        self.y = y
        self.world = world

    def move(self, mx, my):
        newx = self.x + mx
        newy = self.y + my

        if self.world.is_walkable(newx, newy):
            self.x = newx
            self.y = newy
        else:
            print("bump sound")


class Game:
    def run(self):
        screen = pg.display.set_mode((800, 600))
        clock = pg.time.Clock()
        dt = 0

        self.new_game()

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
        self.world = World()
        self.player = Mob(1, 1, self.world)
        self.arch = Mob(3, 1, self.world)

    def on_event(self, event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_LEFT:
                self.player.move(-1, 0)
            elif event.key == pg.K_RIGHT:
                self.player.move(1, 0)
            elif event.key == pg.K_UP:
                self.player.move(0, -1)
            elif event.key == pg.K_DOWN:
                self.player.move(0, 1)

    def on_update(self, dt):
        pass

    def on_draw(self, surf):
        surf.fill((32, 32, 32))

        scroll_x = (surf.get_width() - TILE_SIZE) // 2 - self.player.x * TILE_SIZE
        scroll_y = (surf.get_height() - TILE_SIZE) // 2 - self.player.y * TILE_SIZE

        # draw tiles
        for y in range(self.world.height):
            for x in range(self.world.width):
                rect = pg.Rect(scroll_x + x*TILE_SIZE, scroll_y + y*TILE_SIZE, TILE_SIZE, TILE_SIZE)
                if not rect.colliderect(surf.get_rect()): continue

                color = self.world.get_color(x, y)
                pg.draw.rect(surf, color, rect, 1)

        # draw player in center
        pg.draw.rect(surf, (0, 121, 241), (scroll_x + self.player.x*TILE_SIZE, scroll_y + self.player.y*TILE_SIZE, TILE_SIZE, TILE_SIZE))


if __name__ == "__main__":
    pg.init()
    Game().run()
    pg.quit()