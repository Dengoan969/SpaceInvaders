import pygame


class Ship(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load('textures/ship.png').convert()
        self.laser_sound = pygame.mixer.Sound("audio/shoot_sound.wav")
        self.laser_sound.set_volume(0.3)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 5
        self.bullets = pygame.sprite.Group()
        self.last_shot = pygame.time.get_ticks()
        self.cooldown = 500
        self.screen_width = pygame.display.get_surface().get_width()
        self.is_diagonal_shoot = False

    def update(self):
        self.handle_input()

    def handle_input(self):
        key = pygame.key.get_pressed()
        if key[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if key[pygame.K_RIGHT] and self.rect.right < self.screen_width:
            self.rect.x += self.speed

        time_now = pygame.time.get_ticks()
        if (key[pygame.K_SPACE] or key[pygame.K_UP]) and \
                time_now - self.last_shot > self.cooldown:
            self.laser_sound.play()
            if self.is_diagonal_shoot:
                bullet = Bullet(self.rect.centerx, self.rect.top, -1, -5, False)
                self.bullets.add(bullet)
                bullet = Bullet(self.rect.centerx, self.rect.top, 1, -5, False)
                self.bullets.add(bullet)
            bullet = Bullet(self.rect.centerx, self.rect.top, 0, -5, False)
            self.bullets.add(bullet)
            self.last_shot = time_now


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, speed_x, speed_y, is_alien):
        super().__init__()
        self.screen_height = pygame.display.get_surface().get_height()
        if is_alien:
            self.image = pygame.image.load("textures/alien_bullet.png")
        elif speed_x != 0:
            self.image = pygame.image.load("textures/bullet_diagonal.jpg")
        else:
            self.image = pygame.image.load("textures/bullet.png")
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = (speed_x, speed_y)

    def update(self):
        self.rect.x += self.speed[0]
        self.rect.y += self.speed[1]
        if self.rect.bottom <= 0 or self.rect.top >= self.screen_height:
            self.kill()


class Alien(pygame.sprite.Sprite):
    aliens_prices = {"blue": 100, "skin": 150, "yellow": 200, "red": 250,
                     "green": 300, "purple": 400}

    def __init__(self, x, y, color):
        super().__init__()
        self.image = pygame.image.load(f"textures/alien_{color}.png")
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.price = Alien.aliens_prices[color]

    def update(self, direction, speed):
        self.rect.x += speed * direction


class Bunker_Block(pygame.sprite.Sprite):
    def __init__(self, size, x, y, is_translucent):
        super().__init__()
        self.image = pygame.Surface((size, size))
        if is_translucent:
            color = (128, 128, 128)
        else:
            color = (255, 255, 255)
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.is_translucent = is_translucent


class MysteryShip(pygame.sprite.Sprite):
    def __init__(self, direction):
        super().__init__()
        self.screen_width = pygame.display.get_surface().get_width()
        self.image = pygame.image.load("textures/MysteryShip.png")
        self.rect = self.image.get_rect()
        if direction == 1:
            x = -80
        else:
            x = self.screen_width + 80
        self.rect.center = (x, 50)
        self.speed = 3 * direction

    def update(self):
        self.rect.x += self.speed
        if self.speed > 0 and self.rect.left > self.screen_width or \
                self.speed < 0 and self.rect.right <= 0:
            self.kill()


class Bonus(pygame.sprite.Sprite):
    def __init__(self, x, y, bonus_type):
        super().__init__()
        self.bonus_type = bonus_type
        self.buffer = None
        self.time = 500
        self.screen_height = pygame.display.get_surface().get_height()
        self.image = pygame.image.load(f"textures/bonus_{bonus_type}.jpg")
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self):
        self.rect.y += 2
        if self.rect.top >= self.screen_height:
            self.kill()

    def effect(self, game):
        if self.bonus_type == "freeze":
            self.buffer = game.aliens_speed
            game.aliens_speed = 0
            game.is_freeze = True
        elif self.bonus_type == "life":
            game.lives += 1
        elif self.bonus_type == "fast":
            self.buffer = game.ship.sprite.cooldown
            game.ship.sprite.cooldown /= 2
        elif self.bonus_type == "bullets":
            game.ship.sprite.is_diagonal_shoot = True

    def effect_undo(self, game):
        if self.bonus_type == "freeze":
            game.aliens_speed += self.buffer
            game.is_freeze = False
        elif self.bonus_type == "fast":
            game.ship.sprite.cooldown = self.buffer
        elif self.bonus_type == "bullets":
            game.ship.sprite.is_diagonal_shoot = False

    def timer(self, game):
        self.time -= 1
        if self.time < 0:
            self.effect_undo(game)
            self.kill()
