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
pygame.display.set_caption("Alien Platformer")


font = pygame.font.SysFont("comicsans", 80)
font_score = pygame.font.SysFont("comicsans", 30)


tile_size = 50
game_over = 0
main_menu = True
level = 1
max_levels = 30
score = 0
level_score = 0
magic_power = False
button_used = False
game_paused = False
save_cooldown = 0

transparent_white = (245, 245, 245, 0)
white = (255, 255, 255)
red = (255, 0, 0)
black = (0, 0, 0)


start_img = pygame.image.load("Base pack/button_start.png").convert_alpha()
exit_img = pygame.image.load("Base pack/button_quit.png").convert_alpha()
restart_img = pygame.image.load("Base pack/button_restart.png").convert_alpha()
continue_img = pygame.image.load("Base pack/button_continue.png").convert_alpha()


if level > 25:
    bg = pygame.image.load("Base pack/bg.png").convert_alpha()
elif level > 20:
    bg = pygame.image.load("Base pack/bg_shroom.png").convert_alpha()
elif level > 15:
    bg = pygame.image.load("Base pack/bg.png").convert_alpha()
elif level > 10:
    bg = pygame.image.load("Base pack/bg_desert.png").convert_alpha()
elif level > 5:
    bg = pygame.image.load("Base pack/bg_castle.png").convert_alpha()
else:
    bg = pygame.image.load("Base pack/bg_grasslands.png").convert_alpha()
background = pygame.transform.scale(bg, (1400, 800))


coin_sound = pygame.mixer.Sound("Base pack/coinsound.mp3")
jump_sound = pygame.mixer.Sound("Base pack/jumpsound.mp3")
jump_sound.set_volume(0.5)
death_sound = pygame.mixer.Sound("Base pack/deathsound.mp3")
death_sound.set_volume(0.5)


def pause(run):
    game_paused = True
    draw_text("GAME PAUSED", font, white, (screen_width // 2) - 280, (screen_height // 2) - 80)
    pygame.display.update()
    while game_paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_paused = False
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    game_paused = False
    return run


def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


def reset_level(level):
    player.reset(100, screen_height - 130)
    fly_group.empty()
    enemy2_group.empty()
    enemy3_group.empty()
    enemy4_group.empty()
    ghost_group.empty()
    coin_group.empty()
    platform_group.empty()
    lava_group.empty()
    exit_group.empty()
    magic_group.empty()
    decoration_group.empty()
    fake_block_group.empty()
    coin_group.add(score_coin)
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
                if magic_power == True:
                    dx -= 2
                else:
                    dx -= 5
                self.counter += 1
                self.direction = -1
            if key[pygame.K_RIGHT]:
                if magic_power == True:
                    dx += 2
                else:
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

            if magic_power == False:
                if pygame.sprite.spritecollide(self, fly_group, False):
                    death_sound.play()
                    game_over = -1

            if magic_power == False:
                if pygame.sprite.spritecollide(self, enemy2_group, False):
                    death_sound.play()
                    game_over = -1

            if magic_power == False:
                if pygame.sprite.spritecollide(self, enemy3_group, False):
                    death_sound.play()
                    game_over = -1

            if magic_power == False:
                if pygame.sprite.spritecollide(self, enemy4_group, False):
                    death_sound.play()
                    game_over = -1

            if pygame.sprite.spritecollide(self, lava_group, False):
                death_sound.play()
                game_over = -1

            if pygame.sprite.spritecollide(self, exit_group, False):
                game_over = 1

            if magic_power == False:
                if pygame.sprite.spritecollide(self, ghost_group, False):
                    death_sound.play()
                    game_over = -1

            if pygame.sprite.spritecollide(self, fake_block_group, True):
                death_sound.play()



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
                img_right = pygame.image.load(f"Base pack/p1_walk0{num}.png").convert_alpha()
            else:
                img_right = pygame.image.load(f"Base pack/p3_walk0{num}.png").convert_alpha()
            img_right = pygame.transform.scale(img_right, (40, 80))
            img_left = pygame.transform.flip(img_right, True, False)
            self.images_right.append(img_right)
            self.images_left.append(img_left)
        self.dead_image = pygame.image.load("Base pack/cloud2.png").convert_alpha()
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

        if level > 25:
            dirt_img = pygame.image.load("Base pack/cakeCenter.png").convert_alpha()
            grass_img = pygame.image.load("Base pack/cake.png").convert_alpha()
        elif level > 20:
            dirt_img = pygame.image.load("Base pack/dirtCenter.png").convert_alpha()
            grass_img = pygame.image.load("Base pack/dirt.png").convert_alpha()
        elif level > 15:
            dirt_img = pygame.image.load("Base pack/iceWaterDeepStars.png").convert_alpha()
            grass_img = pygame.image.load("Base pack/iceBlock.png").convert_alpha()
        elif level > 10:
            dirt_img = pygame.image.load("Base pack/grassCenter.png").convert_alpha()
            grass_img = pygame.image.load("Base pack/sand.png").convert_alpha()
        elif level > 5:
            dirt_img = pygame.image.load("Base pack/castleCenter.png").convert_alpha()
            grass_img = pygame.image.load("Base pack/castle.png").convert_alpha()
        else:
            dirt_img = pygame.image.load("Base pack/grassCenter.png").convert_alpha()
            grass_img = pygame.image.load("Base pack/grass.png").convert_alpha()

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
                    if level > 20 and level < 26:
                        fly = Enemy(col_count * tile_size, row_count * tile_size + 10)
                    elif level > 25:
                        fly = Enemy(col_count * tile_size, row_count * tile_size + 30)
                    else:
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
                if tile == 10:
                    ghost = Ghost(col_count * tile_size, row_count * tile_size)
                    ghost_group.add(ghost)
                if tile == 11:
                    decoration = Decoration(col_count * tile_size, row_count * tile_size)
                    decoration_group.add(decoration)
                if tile == 12:
                    if level > 10 and level < 16:
                        enemy2 = Enemy2(col_count * tile_size, row_count * tile_size - 15)
                    elif level > 15 and level < 21:
                        enemy2 = Enemy2(col_count * tile_size, row_count * tile_size - 20)
                    else:
                        enemy2 = Enemy2(col_count * tile_size, row_count * tile_size)
                    enemy2_group.add(enemy2)
                if tile == 13:
                    enemy3 = Enemy3(col_count * tile_size, row_count * tile_size)
                    enemy3_group.add(enemy3)
                if tile == 14:
                    if level > 10 and level < 16:
                        enemy4 = Enemy4(col_count * tile_size, row_count * tile_size + 10)
                    elif level > 15 and level < 21:
                        enemy4 = Enemy4(col_count * tile_size, row_count * tile_size + 40)
                    elif level > 20 and level < 26:
                        enemy4 = Enemy4(col_count * tile_size, row_count * tile_size + 15)
                    elif level > 25:
                        enemy4 = Enemy4(col_count * tile_size, row_count * tile_size + 40)
                    else:
                        enemy4 = Enemy4(col_count * tile_size, row_count * tile_size)
                    enemy4_group.add(enemy4)
                if tile == 15:
                    fake_block = Fake_block(col_count * tile_size, row_count * tile_size)
                    fake_block_group.add(fake_block)
                col_count += 1
            row_count += 1

    def draw(self):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        if level > 25:
            self.image = pygame.image.load("Base pack/worm.png").convert_alpha()
        elif level > 20:
            self.image = pygame.image.load("Base pack/snail.png").convert_alpha()
        elif level > 15:
            self.image = pygame.image.load("Base pack/fishPink.png").convert_alpha()
        elif level > 10:
            self.image = pygame.image.load("Base pack/bee.png").convert_alpha()
        elif level > 5:
            self.image = pygame.image.load("Base pack/bat.png").convert_alpha()
        else:
            self.image = pygame.image.load("Base pack/flyFly1.png").convert_alpha()
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
            if level > 25:
                self.image = pygame.image.load("Base pack/worm_walk.png").convert_alpha()
            elif level > 20:
                self.image = pygame.image.load("Base pack/snail_walk.png").convert_alpha()
            elif level > 15:
                self.image = pygame.image.load("Base pack/fishPink_swim.png").convert_alpha()
            elif level > 10:
                self.image = pygame.image.load("Base pack/bee_fly.png").convert_alpha()
            elif level > 5:
                self.image = pygame.image.load("Base pack/bat_fly.png").convert_alpha()
            else:
                self.image = pygame.image.load("Base pack/flyFly2.png").convert_alpha()


class Enemy2(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        if level > 20:
            self.image = pygame.image.load("Base pack/barnacle.png").convert_alpha()
        elif level > 15:
            self.image = pygame.image.load("Base pack/spikesBottomAlt.png").convert_alpha()
        elif level > 10:
            self.image = pygame.image.load("Base pack/spikes.png").convert_alpha()
        elif level > 5:
            self.image = pygame.image.load("Base pack/spinner.png").convert_alpha()
        else:
            self.image = pygame.image.load("Base pack/blockerMad.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.flipped = pygame.transform.flip(self.image, True, False)
        self.rect.x = x
        self.rect.y = y
        self.move_direction = 1
        self.move_counter = 0
        self.width = self.image.get_width()
        self.height = self.image.get_height()


    def update(self):
        if (self.rect.y - player.rect.y) < 50 and (self.rect.y - player.rect.y) > 0 or (player.rect.y - self.rect.y) < 50 and (player.rect.y - self.rect.y) >0:
            if self.move_counter > -100:
                if (self.rect.x - player.rect.x) < 150 and (self.rect.x - player.rect.x) > 0:
                    self.rect.x -= 2
                    self.move_counter -= 2
            if self.move_counter < 100:
                if (player.rect.x - self.rect.x) < 150 and (player.rect.x - self.rect.x) > 0:
                    self.rect.x += 2
                    self.move_counter += 2


class Enemy4(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        if level > 25:
            self.image = pygame.image.load("Base pack/slimeGreen_squashed.png").convert_alpha()
        elif level > 20:
            self.image = pygame.image.load("Base pack/frog.png").convert_alpha()
        elif level > 15:
            self.image = pygame.image.load("Base pack/slimeBlue_squashed.png").convert_alpha()
        elif level > 10:
            self.image = pygame.image.load("Base pack/spider.png").convert_alpha()
        elif level > 5:
            self.image = pygame.image.load("Base pack/spinner.png").convert_alpha()
        else:
            self.image = pygame.image.load("Base pack/blockerMad.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.flipped = pygame.transform.flip(self.image, True, False)
        self.rect.x = x
        self.rect.y = y
        self.move = 0
        self.move_counter = 0
        self.position_counter = True
        self.width = self.image.get_width()
        self.height = self.image.get_height()


    def update(self):
        if (self.rect.x - player.rect.x) < 50 and (self.rect.x - player.rect.x) > 0 or (player.rect.x - self.rect.x) < 50 and (player.rect.x - self.rect.x) >0:
            if self.move <= 220:
                if (self.rect.y - player.rect.y) < 220 and (self.rect.y - player.rect.y) > 0:
                    if self.position_counter == True:
                        if self.move <= 220:
                            self.rect.y -= 6
                            self.move_counter -= 6
                            self.move += 6
        if self.move > 0:
            self.rect.y += 2
            self.move_counter += 2
            self.move -= 2
            if level > 25:
                self.image = pygame.image.load("Base pack/slimeGreen.png").convert_alpha()
            elif level > 20:
                self.image = pygame.image.load("Base pack/frog_leap.png").convert_alpha()
            elif level > 15:
                self.image = pygame.image.load("Base pack/slimeBlue.png").convert_alpha()
            elif level > 10:
                self.image = pygame.image.load("Base pack/spider_walk2.png").convert_alpha()
            elif level > 5:
                self.image = pygame.image.load("Base pack/spinner_spin.png").convert_alpha()
            else:
                self.image = pygame.image.load("Base pack/blockerMad.png").convert_alpha()

        if self.move == 220:
            self.position_counter = False
        if self.move == 0:
            self.position_counter = True
            if level > 25:
                self.image = pygame.image.load("Base pack/slimeGreen_squashed.png").convert_alpha()
            elif level > 20:
                self.image = pygame.image.load("Base pack/frog.png").convert_alpha()
            elif level > 15:
                self.image = pygame.image.load("Base pack/slimeBlue_squashed.png").convert_alpha()
            elif level > 10:
                self.image = pygame.image.load("Base pack/spider.png").convert_alpha()
            elif level > 5:
                self.image = pygame.image.load("Base pack/spinner.png").convert_alpha()
            else:
                self.image = pygame.image.load("Base pack/blockerMad.png").convert_alpha()


class Enemy3(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        if level > 25:
            self.image = pygame.image.load("Base pack/slime_walk.png").convert_alpha()
        elif level > 20:
            self.image = pygame.image.load("Base pack/ladyBug.png").convert_alpha()
        elif level > 15:
            self.image = pygame.image.load("Base pack/piranha_down.png").convert_alpha()
        elif level > 10:
            self.image = pygame.image.load("Base pack/bee.png").convert_alpha()
        elif level > 5:
            self.image = pygame.image.load("Base pack/bat.png").convert_alpha()
        else:
            self.image = pygame.image.load("Base pack/flyFly1.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.flipped = pygame.transform.flip(self.image, True, False)
        self.rect.x = x
        self.rect.y = y
        self.move_direction = 1
        self.move_counter = 0

    def update(self):
        self.rect.y += self.move_direction
        self.move_counter += 1
        if abs(self.move_counter) > 50:
            self.move_direction *= -1
            self.move_counter *= -1
        if self.move_direction == 1:
            self.image = self.flipped
        else:
            if level > 25:
                self.image = pygame.image.load("Base pack/slime.png").convert_alpha()
            elif level > 20:
                self.image = pygame.image.load("Base pack/ladyBug_fly.png").convert_alpha()
            elif level > 15:
                self.image = pygame.image.load("Base pack/piranha.png").convert_alpha()
            elif level > 10:
                self.image = pygame.image.load("Base pack/bee_fly.png").convert_alpha()
            elif level > 5:
                self.image = pygame.image.load("Base pack/bat_fly.png").convert_alpha()
            else:
                self.image = pygame.image.load("Base pack/flyFly2.png").convert_alpha()


class Ghost(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("Base pack/ghost.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.flipped = pygame.transform.flip(self.image, True, False)
        self.rect.x = x
        self.rect.y = y


    def update(self):
        if (self.rect.y - player.rect.y) < 150 and (self.rect.y - player.rect.y) > 0 or (player.rect.y - self.rect.y) < 150 and (player.rect.y - self.rect.y) >0:
            if (self.rect.x - player.rect.x) < 150 and (self.rect.x - player.rect.x) > 0:
                self.rect.x -= 2
            elif (player.rect.x - self.rect.x) < 150 and (player.rect.x - self.rect.x) > 0:
                self.rect.x += 2

        if (self.rect.x - player.rect.x) < 150 and (self.rect.x - player.rect.x) > 0 or (player.rect.x - self.rect.x) < 150 and (player.rect.x - self.rect.x) >0:
            if (self.rect.y - player.rect.y) < 150 and (self.rect.y - player.rect.y) > 0:
                self.rect.y -= 2
            elif (player.rect.y - self.rect.y) < 150 and (player.rect.y - self.rect.y) > 0:
                self.rect.y += 2


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, move_x, move_y):
        pygame.sprite.Sprite.__init__(self)
        if level > 25:
            img = pygame.image.load("Base pack/cakeHalfAlt.png").convert_alpha()
        elif level > 20:
            img = pygame.image.load("Base pack/dirtHalf.png").convert_alpha()
        elif level > 15:
            img = pygame.image.load("Base pack/iceBlockHalf.png").convert_alpha()
        elif level > 10:
            img = pygame.image.load("Base pack/sandHalf.png").convert_alpha()
        elif level > 5:
            img = pygame.image.load("Base pack/castleHalf.png").convert_alpha()
        else:
            img = pygame.image.load("Base pack/grassHalf.png").convert_alpha()
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
        if level > 15 and level < 26:
            img = pygame.image.load("Base pack/iceWater.png").convert_alpha()
        else:
            img = pygame.image.load("Base pack/liquidLavaTop_mid.png").convert_alpha()
        self.image = pygame.transform.scale(img, (tile_size, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Fake_block(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        if level > 25:
            img = pygame.image.load("Base pack/cake.png").convert_alpha()
        elif level > 20:
            img = pygame.image.load("Base pack/dirt.png").convert_alpha()
        elif level > 15:
            img = pygame.image.load("Base pack/iceBlock.png").convert_alpha()
        elif level > 10:
            img = pygame.image.load("Base pack/sand.png").convert_alpha()
        elif level > 5:
            img = pygame.image.load("Base pack/castle.png").convert_alpha()
        else:
            img = pygame.image.load("Base pack/grass.png").convert_alpha()
        self.image = pygame.transform.scale(img, (tile_size, tile_size))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Decoration(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        if level > 25:
            img = pygame.image.load("Base pack/creamChoco.png").convert_alpha()
        elif level > 20:
            img = pygame.image.load("Base pack/tallShroom_red.png").convert_alpha()
        elif level > 15:
            img = pygame.image.load("Base pack/deadTree.png").convert_alpha()
        elif level > 10:
            img = pygame.image.load("Base pack/cactus.png").convert_alpha()
        elif level > 5:
            img = pygame.image.load("Base pack/tochLit.png").convert_alpha()
        else:
            img = pygame.image.load("Base pack/plant.png").convert_alpha()
        self.image = pygame.transform.scale(img, (tile_size, tile_size))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Magic(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        magic_img = pygame.image.load("Base pack/buttonRed.png").convert_alpha()

        self.image = pygame.transform.scale(magic_img, (tile_size, tile_size))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


    def change_image(self, x, y):
        magic_img = pygame.image.load("Base pack/buttonRed_pressed.png").convert_alpha()
        self.image = pygame.transform.scale(magic_img, (tile_size, tile_size))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load("Base pack/coinGold.png").convert_alpha()
        self.image = pygame.transform.scale(img, (tile_size // 2, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)



class Exit(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load("Base pack/signExit.png").convert_alpha()
        self.image = pygame.transform.scale(img, (tile_size, int(tile_size * 1.5)))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


player = Player(100, screen_height - 130)
fly_group = pygame.sprite.Group()
platform_group = pygame.sprite.Group()
lava_group = pygame.sprite.Group()
coin_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()
magic_group = pygame.sprite.Group()
ghost_group = pygame.sprite.Group()
decoration_group = pygame.sprite.Group()
enemy2_group = pygame.sprite.Group()
enemy3_group = pygame.sprite.Group()
enemy4_group = pygame.sprite.Group()
fake_block_group = pygame.sprite.Group()

score_coin = Coin(tile_size // 2, tile_size // 2)
coin_group.add(score_coin)

if path.exists(f"world_data{level}.pkl"):
    pickle_in = open(f"world_data{level}.pkl", "rb")
    world_data = pickle.load(pickle_in)
world = World(world_data)


restart_button = Button(screen_width // 2 - 100, screen_height // 2 + 50, restart_img)
start_button = Button(screen_width // 2 - 300, screen_height // 2 - 50, start_img)
exit_button = Button(screen_width // 2 + 150, screen_height // 2 - 50, exit_img)
continue_button = Button(screen_width // 2 - 76, screen_height // 2 - 50, continue_img)


run = True
while run:

    clock.tick(fps)
    screen.blit(background, (0, 0))

    if level > 25:
        bg = pygame.image.load("Base pack/bg.png").convert_alpha()
    elif level > 20:
        bg = pygame.image.load("Base pack/bg_shroom.png").convert_alpha()
    elif level > 15:
        bg = pygame.image.load("Base pack/bg.png").convert_alpha()
    elif level > 10:
        bg = pygame.image.load("Base pack/bg_desert.png").convert_alpha()
    elif level > 5:
        bg = pygame.image.load("Base pack/bg_castle.png").convert_alpha()
    else:
        bg = pygame.image.load("Base pack/bg_grasslands.png").convert_alpha()
    background = pygame.transform.scale(bg, (1400, 800))


    if main_menu == True:
        pygame.draw.rect(screen, transparent_white, pygame.Rect(360, 100, 700, 120), 0, 15)
        draw_text("Alien Platformer", font, black, (screen_width // 2) - 300, (screen_height // 2) - 300)
        draw_text("ulo??enie hry: i", font_score, black, (screen_width // 2) - 300, (screen_height // 2) + 100)
        draw_text("zastavenie hry: p", font_score, black, (screen_width // 2) - 300, (screen_height // 2) + 150)
        draw_text("1.0.", font_score, white, (screen_width - 50), (screen_height - 50))
        if exit_button.draw():
            run = False
        if start_button.draw():
            main_menu = False
        if continue_button.draw():
            if path.exists("saved_level.dat") and path.exists("saved_score.dat"):
                level = pickle.load(open("saved_level.dat", "rb"))
                score = pickle.load(open("saved_score.dat", "rb"))
                world_data = []
                world = reset_level(level)
            main_menu = False
    else:
        world.draw()

        if game_over == 0:

            fly_group.update()
            enemy2_group.update()
            enemy3_group.update()
            enemy4_group.update()
            ghost_group.update()
            platform_group.update()
            magic_group.update()
            fake_block_group.update()
            if pygame.sprite.spritecollide(player, coin_group, True):
                coin_sound.play()
                score += 1
                level_score += 1
            draw_text("X " + str(score), font_score, white, tile_size - 10, 5)
            draw_text("level " + str(level), font_score, white, 1270, 5)


            if button_used == False:
                if pygame.sprite.spritecollide(player, magic_group, False):
                    button_used = True
                    magic_power = True
                    for magic in magic_group:
                        magic.change_image(magic.rect.x, magic.rect.y)

                    player.images_right = []
                    player.images_left = []
                    player.index = 0
                    player.counter = 0
                    for num in range(1, 11):
                        if magic_power == False:
                            img_right = pygame.image.load(f"Base pack/p1_walk0{num}.png").convert_alpha()
                        else:
                            img_right = pygame.image.load(f"Base pack/p3_walk0{num}.png").convert_alpha()
                        img_right = pygame.transform.scale(img_right, (40, 80))
                        img_left = pygame.transform.flip(img_right, True, False)
                        player.images_right.append(img_right)
                        player.images_left.append(img_left)

        if pygame.key.get_pressed()[pygame.K_SPACE]:
            magic_power = False
            player.images_right = []
            player.images_left = []
            player.index = 0
            player.counter = 0
            for num in range(1, 11):
                img_right = pygame.image.load(f"Base pack/p1_walk0{num}.png").convert_alpha()
                img_right = pygame.transform.scale(img_right, (40, 80))
                img_left = pygame.transform.flip(img_right, True, False)
                player.images_right.append(img_right)
                player.images_left.append(img_left)


        fly_group.draw(screen)
        enemy2_group.draw(screen)
        enemy3_group.draw(screen)
        enemy4_group.draw(screen)
        ghost_group.draw(screen)
        platform_group.draw(screen)
        decoration_group.draw(screen)
        lava_group.draw(screen)
        coin_group.draw(screen)
        exit_group.draw(screen)
        magic_group.draw(screen)
        fake_block_group.draw(screen)
        draw_text("1.0.", font_score, white, (screen_width - 50), (screen_height - 50))

        if save_cooldown > 0:
            draw_text("GAME SAVED", font_score, white, (screen_width - 220), (screen_height - 100))
            save_cooldown -= 1

        game_over = player.update(game_over)


        if game_over == -1:
            button_used = False
            magic_power = False
            death_sound.play()
            if restart_button.draw():
                world_data = []
                world = reset_level(level)
                game_over = 0
                score -= level_score
                level_score = 0


        if game_over == 1:
            button_used = False
            level += 1
            if level <= max_levels:
                world_data = []
                world = reset_level(level)
                game_over = 0
                level_score = 0
                magic_power = False
                player.images_right = []
                player.images_left = []
                player.index = 0
                player.counter = 0
                for num in range(1, 11):
                    img_right = pygame.image.load(f"Base pack/p1_walk0{num}.png").convert_alpha()
                    img_right = pygame.transform.scale(img_right, (40, 80))
                    img_left = pygame.transform.flip(img_right, True, False)
                    player.images_right.append(img_right)
                    player.images_left.append(img_left)
            else:
                draw_text("VYHRAL SI!", font, red, (screen_width // 2) - 230, 300)
                if restart_button.draw():
                    level = 1
                    world_data = []
                    world = reset_level(level)
                    game_over = 0
                    score = 0


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                run = pause(run)
            if event.key == pygame.K_i:
                if save_cooldown == 0:
                    pickle.dump(level, open("saved_level.dat", "wb"))
                    pickle.dump(score - level_score, open("saved_score.dat", "wb"))
                    save_cooldown = 100


    pygame.display.update()

pygame.quit()