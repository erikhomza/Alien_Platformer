import pygame
import pickle
from pygame.locals import *
from pygame import mixer
from os import path


pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()
pygame.init()

clock = pygame.time.Clock()
fps = 60

screen_width = 1400
screen_height = 800
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("game")


font = pygame.font.SysFont("comicsans", 80)
font_score = pygame.font.SysFont("comicsans", 30)


tile_size = 50
game_over = 0
main_menu = True
level = 1
max_levels = 4
score = 0
magic_power = False

white = (255, 255, 255)
red = (255, 0, 0)


start_img = pygame.image.load("Base pack/liquidLava.png")
exit_img = pygame.image.load("Base pack/flyDead.png")
restart_img = pygame.image.load("Base pack/liquidLavaTop_mid.png")

if level > 1:
    bg = pygame.image.load("Base pack/bg_castle.png")
else:
    bg = pygame.image.load("Base pack/bg.png")
background = pygame.transform.scale(bg, (1400, 800))


coin_sound = pygame.mixer.Sound("Base pack/coinsound.mp3")
jump_sound = pygame.mixer.Sound("Base pack/jumpsound.mp3")
jump_sound.set_volume(0.5)
death_sound = pygame.mixer.Sound("Base pack/deathsound.mp3")
death_sound.set_volume(0.5)


def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


def reset_level(level):
    player.reset(100, screen_height - 130)
    fly_group.empty()
    platform_group.empty()
    lava_group.empty()
    exit_group.empty()
    magic_group.empty()
    magic_power = False
    if path.exists(f"world_data{level}.pkl"):
        pickle_in = open(f"world_data{level}.pkl", "rb")
        world_data = pickle.load(pickle_in)
    world = World(world_data)
    return world


class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.clicked = False

    def draw(self):
        action = False
        pos = pygame.mouse.get_pos()

        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                action = True
                self.clicked = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False


        screen.blit(self.image, self.rect)

        return action



class Player():
    def __init__(self, x, y):
        self.reset(x, y)


    def update(self, game_over):
        dx = 0
        dy = 0
        walk_cooldown = 5
        col_thresh = 20


        if game_over == 0:
            key = pygame.key.get_pressed()
            if key[pygame.K_UP] and self.jumped == False and self.in_air == False:
                jump_sound.play()
                self.vel_y = -20
                self.jumped = True
            if key[pygame.K_UP] == False:
                self.jumped = False
            if key[pygame.K_LEFT]:
                dx -= 5
                self.counter += 1
                self.direction = -1
            if key[pygame.K_RIGHT]:
                dx += 5
                self.counter += 1
                self.direction = 1
            if key[pygame.K_LEFT] == False and key[pygame.K_RIGHT] == False:
                self.counter = 0
                self.index = 0
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                if self.direction == -1:
                    self.image = self.images_left[self.index]


            if self.counter > walk_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images_right):
                    self.index = 0
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                if self.direction == -1:
                    self.image = self.images_left[self.index]



            self.vel_y += 1
            if self.vel_y > 10:
                self.vel_y = 10
            dy += self.vel_y



            self.in_air = True
            for tile in world.tile_list:
                if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0
                if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    if self.vel_y < 0:
                        dy = tile[1].bottom - self.rect.top
                        self.vel_y = 0
                    elif self.vel_y >= 0:
                        dy = tile[1].top - self.rect.bottom
                        self.vel_y = 0
                        self.in_air = False

            if pygame.sprite.spritecollide(self, fly_group, False):
                death_sound.play()
                game_over = -1

            if pygame.sprite.spritecollide(self, lava_group, False):
                death_sound.play()
                game_over = -1

            if pygame.sprite.spritecollide(self, exit_group, False):
                game_over = 1

            if pygame.sprite.spritecollide(self, magic_group, False):
                magic_power = True


            for platform in platform_group:
                if platform.rect.colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0
                if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    if abs((self.rect.top + dy) - platform.rect.bottom) < col_thresh:
                        self.vel_y = 0
                        dy = platform.rect.bottom - self.rect.top
                    elif abs((self.rect.bottom + dy) - platform.rect.top) < col_thresh:
                        self.rect.bottom = platform.rect.top - 1
                        self.in_air = False
                        dy = 0
                    if platform.move_X != 0:
                        self.rect.x += platform.move_direction



            self.rect.x += dx
            self.rect.y += dy

        elif game_over == -1:
            self.image = self.dead_image
            draw_text("ZAHYNUL SI V BOLESTIACH!", font, red, (screen_width // 2) - 570, (screen_height //2) - 100)
            self.rect.y -= 5

        screen.blit(self.image, self.rect)

        return game_over


    def reset(self, x, y):
        self.images_right = []
        self.images_left = []
        self.index = 0
        self.counter = 0
        for num in range(1, 11):
            if magic_power == False:
                img_right = pygame.image.load(f"Base pack/p1_walk0{num}.png")
            else:
                img_right = pygame.image.load(f"Base pack/p3_walk0{num}.png")
            img_right = pygame.transform.scale(img_right, (40, 80))
            img_left = pygame.transform.flip(img_right, True, False)
            self.images_right.append(img_right)
            self.images_left.append(img_left)
        self.dead_image = pygame.image.load("Base pack/cloud2.png")
        self.image = self.images_right[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.vel_y = 0
        self.jumped = False
        self.direction = 0
        self.in_air = True



class World():
    def __init__(self, data):
        self.tile_list = []


        if level > 1:
            dirt_img = pygame.image.load("Tiles/castleCenter.png")
            grass_img = pygame.image.load("Tiles/castle.png")
        else:
            dirt_img = pygame.image.load("Tiles/grassCenter.png")
            grass_img = pygame.image.load("Tiles/grass.png")

        row_count = 0
        for row in data:
            col_count = 0
            for tile in row:
                if tile == 1:
                    img = pygame.transform.scale(dirt_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 2:
                    img = pygame.transform.scale(grass_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 3:
                    fly = Enemy(col_count * tile_size, row_count * tile_size)
                    fly_group.add(fly)
                if tile == 4:
                    platform = Platform(col_count * tile_size, row_count * tile_size, 1, 0)
                    platform_group.add(platform)
                if tile == 5:
                    platform = Platform(col_count * tile_size, row_count * tile_size, 0, 1)
                    platform_group.add(platform)
                if tile == 6:
                    lava = Lava(col_count * tile_size, row_count * tile_size + (tile_size // 2))
                    lava_group.add(lava)
                if tile == 7:
                    coin = Coin(col_count * tile_size + (tile_size // 2), row_count * tile_size + (tile_size // 2))
                    coin_group.add(coin)
                if tile == 8:
                    exit = Exit(col_count * tile_size, row_count * tile_size - (tile_size // 2))
                    exit_group.add(exit)
                if tile == 9:
                    magic = Magic(col_count * tile_size, row_count * tile_size)
                    magic_group.add(magic)
                col_count += 1
            row_count += 1

    def draw(self):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("Base pack/flyFly1.png")
        self.rect = self.image.get_rect()
        self.flipped = pygame.transform.flip(self.image, True, False)
        self.rect.x = x
        self.rect.y = y
        self.move_direction = 1
        self.move_counter = 0

    def update(self):
        self.rect.x += self.move_direction
        self.move_counter += 1
        if abs(self.move_counter) > 50:
            self.move_direction *= -1
            self.move_counter *= -1
        if self.move_direction == 1:
            self.image = self.flipped
        else:
            self.image = pygame.image.load(f"Base pack/flyFly1.png")



class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, move_x, move_y):
        pygame.sprite.Sprite.__init__(self)
        if level > 1:
            img = pygame.image.load("Base pack/castleHalf.png")
        else:
            img = pygame.image.load("Base pack/grassHalf.png")
        self.image = pygame.transform.scale(img, (tile_size, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_counter = 0
        self.move_direction = 1
        self.move_X = move_x
        self.move_y = move_y


    def update(self):
        self.rect.x += self.move_direction * self.move_X
        self.rect.y += self.move_direction * self.move_y
        self.move_counter += 1
        if abs(self.move_counter) > 50:
            self.move_counter *= -1
            self.move_direction *= -1




class Lava(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load("Base pack/liquidLavaTop_mid.png")
        self.image = pygame.transform.scale(img, (tile_size, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_direction = 1
        self.move_counter = 0


class Magic(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load("Base pack/buttonYellow.png")
        self.image = pygame.transform.scale(img, (tile_size, tile_size))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y



class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load("Base pack/coinGold.png")
        self.image = pygame.transform.scale(img, (tile_size // 2, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.move_direction = 1
        self.move_counter = 0



class Exit(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load("Base pack/signExit.png")
        self.image = pygame.transform.scale(img, (tile_size, int(tile_size * 1.5)))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_direction = 1
        self.move_counter = 0






player = Player(100, screen_height - 130)
fly_group = pygame.sprite.Group()
platform_group = pygame.sprite.Group()
lava_group = pygame.sprite.Group()
coin_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()
magic_group = pygame.sprite.Group()

score_coin = Coin(tile_size // 2, tile_size // 2)
coin_group.add(score_coin)

if path.exists(f"world_data{level}.pkl"):
    pickle_in = open(f"world_data{level}.pkl", "rb")
    world_data = pickle.load(pickle_in)
world = World(world_data)


restart_buttom = Button(screen_width // 2 - 50, screen_height // 2 + 100, restart_img)
start_buttom = Button(screen_width // 2 - 200, screen_height // 2, start_img)
exit_button = Button(screen_width // 2 + 150, screen_height // 2, exit_img)

run = True
while run:

    clock.tick(fps)
    screen.blit(background, (0, 0))

    if level > 1:
        bg = pygame.image.load("Base pack/bg_castle.png")
    else:
        bg = pygame.image.load("Base pack/bg.png")
    background = pygame.transform.scale(bg, (1400, 800))


    if main_menu == True:
        if exit_button.draw():
            run = False
        if start_buttom.draw():
            main_menu = False
    else:
        world.draw()


        if game_over == 0:
            fly_group.update()
            platform_group.update()
            magic_group.update()
            if pygame.sprite.spritecollide(player, coin_group, True):
                coin_sound.play()
                score += 1
            draw_text("X " + str(score), font_score, white, tile_size - 10, 10)
            



        fly_group.draw(screen)
        platform_group.draw(screen)
        lava_group.draw(screen)
        coin_group.draw(screen)
        exit_group.draw(screen)
        magic_group.draw(screen)
        game_over = player.update(game_over)


        if game_over == -1:
           if restart_buttom.draw():
                world_data = []
                world = reset_level(level)
                game_over = 0
                score = 0


        if game_over == 1:
            level += 1
            if level <= max_levels:
                world_data = []
                world = reset_level(level)
                game_over = 0
            else:
                draw_text("VYHRAL SI!", font, red, (screen_width // 2) - 200, screen_height // 2)
                if restart_buttom.draw():
                    level = 1
                    world_data = []
                    world = reset_level(level)
                    game_over = 0
                    score = 0





    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()

pygame.quit()