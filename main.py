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

        self.mobs = {}

        self.tile_sheet = pg.Surface((320, 64))
        self.tile_sheet.set_colorkey((0, 0, 0))
        pg.draw.rect(self.tile_sheet, (255, 0, 0), (0, 0, TILE_SIZE, TILE_SIZE), 1)                 # out of bounds
        pg.draw.rect(self.tile_sheet, (80, 80, 80), (TILE_SIZE, 0, TILE_SIZE, TILE_SIZE), 1)        # floor
        pg.draw.rect(self.tile_sheet, (245, 245, 245), (2*TILE_SIZE, 0, TILE_SIZE, TILE_SIZE), 1)   # wall
        pg.draw.rect(self.tile_sheet, (0, 121, 241), (3*TILE_SIZE, 0, TILE_SIZE, TILE_SIZE))        # player
        pg.draw.rect(self.tile_sheet, (0, 228, 48), (4*TILE_SIZE, 0, TILE_SIZE, TILE_SIZE))         # archaeologist


    def get_tile(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.tiles[y][x]
        else:
            return -1

    def get_mob(self, x, y):
        return self.mobs.get((x, y))

    def get_image(self, x, y):
        mob = self.get_mob(x, y)
        if mob != None:
            return self.tile_sheet.subsurface(mob.glyph*TILE_SIZE, 0, TILE_SIZE, TILE_SIZE)

        tile = self.get_tile(x, y)
        return self.tile_sheet.subsurface(((tile+1)*TILE_SIZE, 0, TILE_SIZE, TILE_SIZE))

    def is_walkable(self, x, y):
        tile = self.get_tile(x, y)
        return tile == 0

    def add_mob_at(self, mob, x, y):
        self.mobs[(x, y)] = mob

    def on_mob_move(self, oldx, oldy, newx, newy):
        mob = self.mobs.pop((oldx, oldy))
        self.mobs[(newx, newy)] = mob


class Mob:
    def __init__(self, world, glyph, x, y):
        self.world = world
        self.world.add_mob_at(self, x, y)
        self.glyph = glyph
        self.x = x
        self.y = y

    def move(self, mx, my):
        newx = self.x + mx
        newy = self.y + my

        other = self.world.get_mob(newx, newy)
        if other != None:
            print("mob bump")
            return

        if self.world.is_walkable(newx, newy):
            self.world.on_mob_move(self.x, self.y, newx, newy)
            self.x = newx
            self.y = newy
        else:
            print("wall bump")


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
        self.player = Mob(self.world, 3, 1, 1)
        self.arch = Mob(self.world, 4, 3, 1)

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

        # calculat scroll so player will be in center
        scroll_x = (surf.get_width() - TILE_SIZE) // 2 - self.player.x * TILE_SIZE
        scroll_y = (surf.get_height() - TILE_SIZE) // 2 - self.player.y * TILE_SIZE

        # draw tiles
        for y in range(self.world.height):
            for x in range(self.world.width):
                rect = pg.Rect(scroll_x + x*TILE_SIZE, scroll_y + y*TILE_SIZE, TILE_SIZE, TILE_SIZE)
                if not rect.colliderect(surf.get_rect()): continue

                image = self.world.get_image(x, y)
                surf.blit(image, rect)


if __name__ == "__main__":
    pg.init()
    Game().run()
    pg.quit()