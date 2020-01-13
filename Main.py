import os
import sys

import pygame


FPS = 60


pygame.init()
size = WIDTH, HEIGHT = 1024, 576
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()
GRAVITY = 5


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    image = pygame.image.load(fullname)
    if colorkey:
        print(colorkey)
        if colorkey == -1:
            colorkey = image.get_at((1, 1))
        print(colorkey)
        image.set_colorkey(colorkey)
    image = image.convert_alpha()
    return image


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    intro_text = ["                               Приветствую вас", "",
                  "                               Для начала игры нажмите",
                  "                               ENTER"]

    fon = pygame.transform.scale(load_image('fon.jpeg'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
                if event.key == 13:
                    return
        pygame.display.flip()
        clock.tick(FPS)


def load_level(filename):
    filename = "data/" + filename
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    max_width = max(map(len, level_map))

    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


tile_images = {'wall': load_image('grow.png')}
player_image = load_image('trump.png')

tile_width = tile_height = 39


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, sheet, columns, rows):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame_right = 0
        self.cur_frame_left = 0
        self.pos_x = tile_width * pos_x + 15
        self.pos_y = tile_height * pos_y + 5
        self.rect = self.image.get_rect().move(tile_width * pos_x + 15, tile_height * pos_y + 5)

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update_right(self):
        self.cur_frame_right = 6 + ((self.cur_frame_right + 1) % 6)
        self.image = self.frames[self.cur_frame_left]

    def update_left(self):
        self.cur_frame_left = 18 + ((self.cur_frame_left + 1) % 6)
        self.image = self.frames[self.cur_frame_right]

    def update(self):
        self.image = player_image


player = None

all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()


def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == '@':
                new_player = Player(x, y, load_image('trump_run.png'), 6, 4)
    return new_player, x, y


class Camera:
    def __init__(self):
        self.dx = 0
        self.dy = 0

    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - WIDTH // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - HEIGHT // 2)


def play():
    x = 0
    y = 0
    camera = Camera()
    f = False
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or event.key == \
                        pygame.K_DOWN or event.key == pygame.K_RIGHT or event.key == pygame.K_LEFT:
                    q = event.key
                    f = True
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE or event.key == \
                        pygame.K_DOWN or event.key == pygame.K_RIGHT or event.key == pygame.K_LEFT:
                    q = event.key
                    f = False
        if f:
            if q == pygame.K_SPACE and y == 0 and pygame.sprite.spritecollideany(player, tiles_group):
                y = 25
            if q == pygame.K_RIGHT:
                x += 5
            if q == pygame.K_LEFT:
                x = -5
        if not pygame.sprite.spritecollideany(player, tiles_group):
            player.rect.y += GRAVITY
        screen.fill((0, 0, 0))
        # if x < 0:
        #     player.update_right()
        # elif x > 0:
        #     player.update_left()
        # else:
        #     player.update()
        player.rect.x += x
        player.rect.y -= y
        if x < 0:
            player.update_right()
        if x > 0:
            player.update_left()
        if x == 0:
            player.update()
        print(player.cur_frame_right, player.cur_frame_left)

        y -= 1
        if y < 20:
            y = 0
        x = 0
        camera.update(player)
        for sprite in all_sprites:
            camera.apply(sprite)
        player_group.draw(screen)
        all_sprites.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)


player, level_x, level_y = generate_level(load_level('map.txt'))


start_screen()
play()
