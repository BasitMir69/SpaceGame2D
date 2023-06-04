import pygame
import random
import os
import time

pygame.font.init()
pygame.mixer.init()

WIDTH, HEIGHT = 800, 800
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Game")

# Loading background and transforming it to fill the screen
BG = pygame.transform.scale(pygame.image.load(os.path.join("gameproj", "background-black.png")), (WIDTH, HEIGHT))

# Asteroids
user_asteroids = pygame.image.load(os.path.join("gameproj", "asteroid2_proj.png"))
user_asteroids = pygame.transform.scale(user_asteroids, (80, 80))

# Laser
user_laser = pygame.image.load(os.path.join("gameproj", "pixel_laser_red.png"))

# User space
space_ship = pygame.image.load(os.path.join("gameproj", "spaceship.png"))

#sounds
laser_sound = pygame.mixer.Sound(os.path.join("gameproj","laser_sound.mp3"))
explosion_sound = pygame.mixer.Sound(os.path.join("gameproj","explosion_sound.wav"))

# Load background music
pygame.mixer.music.load(os.path.join("gameproj","backgroundmusic.mp3"))


# High score counter
high_score = 0

# Function to update high score
def update_high_score(score):
    global high_score
    if score > high_score:
        high_score = score
        print("New high score:", high_score)

class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not (self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)


class Ship:  # abstract class
    COOLDOWN = 15

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window):
        # pygame.draw.rect(window,(255,255,255), (self.x,self.y, 50, 50)) #draws a rectangle in the window, color white and location self.x and self.y by scale of 50x50
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_laser(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 15
                self.lasers.remove(laser)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):  # creates a new laser, starts counting the lasers and stores them in a list
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()


class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = space_ship
        self.laser_img = user_laser
        self.mask = pygame.mask.from_surface(self.ship_img)  # tells us where the pixels are, used for collision
        self.max_health = health

    def move_laser(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)  # removes object when colliding with laser
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        self.lasers.remove(laser)

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (255, 0, 0),
                         (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0, 255, 0), (self.x, self.y + self.ship_img.get_height() + 10,
                                                self.ship_img.get_width() * (self.health / self.max_health), 10))


class Enemy(Ship):
    asteroid = user_asteroids

    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = Enemy.asteroid
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.y += vel


def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x  # distance from object 1 to object 2
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None  # hitting the mask of the distance of the object


def main():
    global high_score
    run = True
    FPS = 60
    level = 0
    lives = 3
    main_font = pygame.font.SysFont("Arial", 45)  # font of text
    lost_font = pygame.font.SysFont("Arial", 100)

    enemies = []
    wave_length = 5
    enemy_vel = 3  # 1 pixel movement from enemy
    player_vel = 7  # pixels to move
    laser_vel = 9

    player = Player(400, 700)

    clock = pygame.time.Clock()  # refresh rate
    lost = False
    lost_count = 0

    def redraw_window():
        WIN.blit(BG, (0, 0))

        lives_text = main_font.render(f"Lives: {lives}", 1, (255, 255, 255))
        level_text = main_font.render(f"Level: {level}", 1, (255, 255, 255))
        high_score_text = main_font.render(f"High score: {high_score}", 1, (255, 255, 255))

        WIN.blit(lives_text, (10, 10))
        WIN.blit(level_text, (WIDTH - level_text.get_width() - 10, 10))
        WIN.blit(high_score_text, (10, 50))

        for enemy in enemies:
            enemy.draw(WIN)

        player.draw(WIN)

        if lost:
            lost_label = lost_font.render("WASTED", 1, (255, 255, 255))
            WIN.blit(lost_label, (WIDTH / 2 - lost_label.get_width() / 2, 350))

        pygame.display.update()

    while run:
        clock.tick(FPS)
        redraw_window()
        # Start playing background music
        pygame.mixer.music.play(-1)  # -1 plays the music in a loop

        if lives <= 0 or player.health <= 0:
            lost = True
            if level > high_score:
                high_score = level
            lost_count += 1

        if lost:
            if lost_count > FPS * 3:
                run = False
            else:
                continue

        if len(enemies) == 0:
            level += 1
            wave_length += 5
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, WIDTH - 100), random.randrange(-1500, -100))
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player.x - player_vel > 0:
            player.x -= player_vel

        if keys[pygame.K_RIGHT] and player.x + player_vel + player.get_width() < WIDTH:
            player.x += player_vel

        if keys[pygame.K_UP] and player.y - player_vel > 0:
            player.y -= player_vel

        if keys[pygame.K_DOWN] and player.y + player_vel + player.get_height() + 15 < HEIGHT:
            player.y += player_vel

        if keys[pygame.K_SPACE]:
            player.shoot()
            laser_sound.play()

        for enemy in enemies:
            enemy.move(enemy_vel)
            enemy.move_laser(laser_vel, player)

            if collide(enemy, player):
                player.health -= 15
                enemies.remove(enemy)
                explosion_sound.play()

            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)

        player.move_laser(-laser_vel, enemies)


def main_menu():
    run = True
    while run:
        WIN.blit(BG, (0, 0))
        title_label = pygame.font.SysFont("Arial", 55).render("Press the mouse button to begin.", 1, (255, 255, 255))
        WIN.blit(title_label, (WIDTH / 2 - title_label.get_width() / 2, 350))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    pygame.quit()


main_menu()
