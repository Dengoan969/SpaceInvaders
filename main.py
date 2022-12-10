import pygame
import random
from game_objects import Ship, Bullet, Alien


class Game:
    def __init__(self):
        self.screen = pygame.display.get_surface()
        self.screen_width, self.screen_height = self.screen.get_size()
        ship = Ship(self.screen_width // 2, self.screen_height - 100)
        self.ship = pygame.sprite.GroupSingle(ship)

        self.aliens = pygame.sprite.Group()
        self.alien_bullets = pygame.sprite.Group()
        self.create_aliens(3, 8)
        self.aliens_direction = 1

        self.is_finished = False

    def run(self):
        run = True
        clock = pygame.time.Clock()
        ALIENSHOOT = pygame.USEREVENT + 0
        pygame.time.set_timer(ALIENSHOOT, 1000)
        while run:
            clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                if event.type == ALIENSHOOT:
                    self.aliens_shoot()
            self.update()

    def update(self):
        self.screen.fill((0, 0, 0))
        self.ship.update()
        self.ship.sprite.bullets.update()

        self.collision_check()

        self.aliens_position_check()
        self.alien_bullets.update()
        self.aliens.update(self.aliens_direction)

        self.ship.sprite.bullets.draw(self.screen)
        self.ship.draw(self.screen)
        self.aliens.draw(self.screen)
        self.alien_bullets.draw(self.screen)

        pygame.display.update()

    def collision_check(self):
        for bullet in self.ship.sprite.bullets:
            if pygame.sprite.spritecollide(bullet, self.aliens, True):
                bullet.kill()

    def aliens_position_check(self):
        for alien in self.aliens:
            if alien.rect.right >= self.screen_width:
                self.move_aliens_down(5)
                self.aliens_direction = -1
                break
            if alien.rect.left <= 0:
                self.move_aliens_down(5)
                self.aliens_direction = 1
                break

    def move_aliens_down(self, distance):
        for alien in self.aliens:
            alien.rect.y += distance

    def aliens_shoot(self):
        if self.aliens.sprites():
            alien = random.choice(self.aliens.sprites())
            laser_sprite = Bullet(alien.rect.centerx, alien.rect.bottom, 5)
            self.alien_bullets.add(laser_sprite)

    def create_aliens(self, rows_count, columns_count,
                      x_distance=60, y_distance=48, x_offset=70, y_offset=100):
        for row in range(rows_count):
            for col in range(columns_count):
                x = col * x_distance + x_offset
                y = row * y_distance + y_offset
                self.aliens.add(Alien(x, y))


def main():
    pygame.init()
    size = 600, 800
    pygame.display.set_mode(size, pygame.RESIZABLE)
    pygame.display.set_caption('Space Invaders | By Denis and Isa')
    game = Game()
    game.run()


if __name__ == '__main__':
    main()
