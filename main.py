from lib2to3.refactor import MultiprocessRefactoringTool
from pygame import mixer
import pygame
import os
import time
import random
pygame.font.init()
mixer.init()

WIDTH, HEIGHT = 750, 750
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space HERO")

#Load images
RED_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_red_small.png"))
GREEN_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_green_small.png"))
BLUE_SPACE_SHIP = pygame.image.load(os.path.join("assets", "space2.png"))
BLUESHIP = pygame.transform.scale(BLUE_SPACE_SHIP,(100,100))
VIOLET = pygame.image.load(os.path.join("assets", "space3.png"))
VIOLET1 = pygame.transform.scale(VIOLET,(100,100))
BLACK = pygame.image.load(os.path.join("assets", "space4.png"))
BLACK1 = pygame.transform.scale(BLUE_SPACE_SHIP,(100,100))


#Player player
YELLOW_SPACE_SHIP = pygame.image.load(os.path.join("assets", "space1.png"))
SPACESHIP = pygame.transform.scale(YELLOW_SPACE_SHIP,(120,120))

#Lasers
RED_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
GREEN_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))
BLUE_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
YELLOW_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png"))

#Background
BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "Space_Background.png")), (WIDTH, HEIGHT))

#laser sound
laser = pygame.mixer.Sound("laser2.wav")
laser.set_volume(0.2)

#blast sound
blast = pygame.mixer.Sound("boom.mp3")
blast.set_volume(0.2)

#Background Music
music = pygame.mixer.music.load(os.path.join('assets', "background2.mp3"))
pygame.mixer.music.play(-1)
mixer.music.set_volume(0.7)


########################################################################################################################################

class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))                        #laser Shooting System 

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not(self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)

########################################################################################################################################

class Ship:
    COOLDOWN = 30

    def __init__(self, x, y, health=200):
        self.x = x
        self.y = y                                             #defining variables
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):                                      #Ship machanism
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:                                  #cooldown for laser so that enemise should not spamm laser
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()

########################################################################################################################################

class Player(Ship):
    def __init__(self, x, y, health=500):
        super().__init__(x, y, health)
        self.ship_img = SPACESHIP
        self.laser_img = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health                                        #player movement and laser shooting machanism

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:                                                         #player laser shooting system so that when player shoot laser will not change direction while player shoot
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        blast.play()
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)
                                                       #healt System
    def healthbar(self, window):
        pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 10))


########################################################################################################################################


class Enemy(Ship):
    COLOR_MAP = {
                "red": (RED_SPACE_SHIP, RED_LASER),                            #enemy spawn system 
                "green": (GREEN_SPACE_SHIP, GREEN_LASER),
                "blue": (BLUESHIP, BLUE_LASER),
                "violet": (VIOLET1, RED_LASER),
                "black": (BLACK1, GREEN_LASER)
                
                }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)                                   #Enemy system include movement laser shooting  
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.y += vel                                                    #Movement of Enemy 

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x-10, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1


def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None 
    

########################################################################################################################################

def main():
    run = True
    FPS = 60
    level = 0
    lives = 10
    main_font = pygame.font.SysFont("roboto", 50)
    lost_font = pygame.font.SysFont("roboto", 60)

    enemies = []
    wave_length = 4
    enemy_vel = 1
                                                                                  #definig variable 
    player_vel = 4                         #speed of player 
    laser_vel = 5                          #speed of laser 

    player = Player(300, 630)              #spawn poit of player

    clock = pygame.time.Clock()

    lost = False
    lost_count = 0                         #End screen

    ###############################################################################################################################

    def redraw_window():
        WIN.blit(BG, (0,0))
        # draw text
        lives_label = main_font.render(f"Lives: {lives}", 1, (255,255,255))
        level_label = main_font.render(f"Level: {level}", 1, (255,255,255))

        WIN.blit(lives_label, (10, 10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))

        for enemy in enemies:
            enemy.draw(WIN)

        player.draw(WIN)

        if lost:
            lost_label = lost_font.render("You Lost!!", 1, (255,255,255))
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350))

        pygame.display.update()

    while run:
        clock.tick(FPS)
        redraw_window()

        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 3:
                run = False
            else:
                continue

        if len(enemies) == 0:                               #Spawn Enemy
            level += 1
            wave_length += 5
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-1500, -100), random.choice(["red", "blue", "green",]))
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:                  #quit system that right hand corner cut Butten (x)
                quit()

 #############################################################################################################3#####################333

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x - player_vel > 0:                                          # left
            player.x -= player_vel

        if keys[pygame.K_d] and player.x + player_vel + player.get_width() < WIDTH:                 # right
            player.x += player_vel

        if keys[pygame.K_w] and player.y - player_vel > 0:                                          # up
            player.y -= player_vel

        if keys[pygame.K_s] and player.y + player_vel + player.get_height() + 15 < HEIGHT:          # down
            player.y += player_vel

        if keys[pygame.K_SPACE]: 
            laser.play()                                                                  # laser shooting butten                             
            player.shoot()

        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)

            if random.randrange(0, 2*60) == 1:
                enemy.shoot()

            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)
            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)

        player.move_lasers(-laser_vel, enemies)

#####################################################################################################################################

def main_menu():
    title_font = pygame.font.SysFont("roboto", 50)
    run = True
    while run:
        WIN.blit(BG, (0,0))
        title_label = title_font.render("Press the mouse to begin...", 1, (255,255,255))          #starting streen
        WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 350))
        pygame.display.update()

        for event in pygame.event.get():                                          #move laser method 
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    pygame.quit()


main_menu()