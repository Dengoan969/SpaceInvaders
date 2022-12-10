import pygame


class Ship(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load('textures/ship.png').convert()
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 5
        self.bullets = pygame.sprite.Group()
        self.last_shot = pygame.time.get_ticks()
        self.cooldown = 500
        self.screen_width = pygame.display.get_surface().get_width()

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
            bullet = Bullet(self.rect.centerx, self.rect.top, -5, False)
            self.bullets.add(bullet)
            self.last_shot = time_now


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, speed, is_alien):
        super().__init__()
        self.screen_height = pygame.display.get_surface().get_height()
        if is_alien:
            self.image = pygame.image.load("textures/alien_bullet.png")
        else:
            self.image = pygame.image.load("textures/bullet.png")
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = speed

    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom <= 0 or self.rect.top >= self.screen_height:
            self.kill()


class Alien(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("textures/alien1.png")
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 1

    def update(self, direction):
        self.rect.x += self.speed * direction


class Bunker_Block(pygame.sprite.Sprite):
    def __init__(self, size, color, x, y):
        super().__init__()
        self.image = pygame.Surface((size, size))
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=(x, y))
