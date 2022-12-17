import time

import pygame
import sys
import random
from game_objects import Ship, Bullet, Alien, Bunker_Block, MysteryShip

# TODO: разные уровни, экран победы и проигрыша, таблица рекордов
#  TODO: ADDITIONAL: Стрельба в разные стороны (бонус),
#   редактор уровней, SAVE & LOAD, музыка,
#   пасхалки, бонусы


class Game:
    def __init__(self):
        self.screen = pygame.display.get_surface()
        self.screen_width, self.screen_height = self.screen.get_size()
        ship = Ship(self.screen_width // 2, self.screen_height - 100)
        self.ship = pygame.sprite.GroupSingle(ship)

        self.lives = 2
        self.live_img = pygame.image.load(
            'textures/ship.png').convert()
        self.live_x_start_pos = self.screen_width - (
                self.live_img.get_size()[0] * 2 + 20)
        self.score = 0
        self.font = pygame.font.SysFont('pixeled', 40)

        self.aliens = pygame.sprite.Group()
        self.alien_bullets = pygame.sprite.Group()
        self.create_aliens(5, 11)
        self.aliens_direction = 1
        self.aliens_speed = 1
        self.mystery_spawn_time = random.randint(500, 1000)
        self.mystery = pygame.sprite.GroupSingle()

        with open('textures/BunkerShape.txt') as f:
            self.shape = f.readlines()
        self.block_size = 15
        self.blocks = pygame.sprite.Group()
        self.bunker_amount = 4
        self.bunker_x_positions = [
            num * (self.screen_width / self.bunker_amount) for num in
            range(self.bunker_amount)]
        self.create_bunkers(*self.bunker_x_positions,
                            x_start=self.screen_width / 15,
                            y_start=self.screen_height - 250)

        self.is_finished = False
        self.is_paused = False

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
                if event.type == ALIENSHOOT and not self.is_paused:
                    self.aliens_shoot()
            self.update()

    def gameplay_draw(self):
        self.blocks.draw(self.screen)
        self.mystery.draw(self.screen)
        self.ship.sprite.bullets.draw(self.screen)
        self.ship.draw(self.screen)
        self.aliens.draw(self.screen)
        self.alien_bullets.draw(self.screen)
        self.display_score()
        self.display_lives()
        self.victory_message()

    def gameplay_update(self):
        self.ship.update()
        self.ship.sprite.bullets.update()

        self.collision_check()

        self.extra_alien_timer()
        self.mystery.update()

        self.aliens_position_check()
        self.alien_bullets.update()
        self.aliens.update(self.aliens_direction, self.aliens_speed)

    def update(self):
        self.screen.fill((0, 0, 0))
        key = pygame.key.get_pressed()
        if key[pygame.K_ESCAPE]:
            self.is_paused = not self.is_paused
            time.sleep(0.2)
        if not self.is_paused and not self.is_finished:
            self.gameplay_update()
        self.gameplay_draw()
        pygame.display.update()

    def collision_check(self):
        for bullet in self.ship.sprite.bullets:
            hit_aliens = pygame.sprite.spritecollide(bullet, self.aliens, True)
            for alien in hit_aliens:
                bullet.kill()
                self.score += alien.price
                self.aliens_speed += 0.1
            bunker_blocks = pygame.sprite.spritecollide(bullet, self.blocks,
                                                        False)
            for block in bunker_blocks:
                if not block.is_translucent:
                    block.kill()
                    bullet.kill()

            if pygame.sprite.spritecollide(bullet, self.mystery, True):
                bullet.kill()
                self.score += 500

        for bullet in self.alien_bullets:
            if pygame.sprite.spritecollide(bullet, self.blocks, True):
                bullet.kill()
            if pygame.sprite.spritecollide(bullet, self.ship, True):
                bullet.kill()
                self.lives -= 1
                if self.lives < 0:
                    pygame.quit()
                    sys.exit()
                ship = Ship(self.screen_width // 2, self.screen_height - 100)
                self.ship = pygame.sprite.GroupSingle(ship)

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
            laser_sprite = Bullet(alien.rect.centerx, alien.rect.bottom, 5,
                                  True)
            self.alien_bullets.add(laser_sprite)

    def create_aliens(self, rows_count, columns_count,
                      x_distance=80, y_distance=48, x_offset=70, y_offset=100):
        for row in range(rows_count):
            for col in range(columns_count):
                x = col * x_distance + x_offset
                y = row * y_distance + y_offset
                self.aliens.add(Alien(x, y, "blue"))

    def create_bunker(self, x_start, y_start, offset_x):
        for row_index, row in enumerate(self.shape):
            for col_index, col in enumerate(row):
                if col == 'x':
                    x = x_start + col_index * self.block_size + offset_x
                    y = y_start + row_index * self.block_size
                    block = Bunker_Block(self.block_size, x, y, True)
                    self.blocks.add(block)

    def create_bunkers(self, *offset, x_start, y_start):
        for offset_x in offset:
            self.create_bunker(x_start, y_start, offset_x)

    def extra_alien_timer(self):
        self.mystery_spawn_time -= 1
        if self.mystery_spawn_time <= 0:
            self.mystery.add(MysteryShip(random.choice([-1, 1])))
            self.mystery_spawn_time = random.randint(500, 1000)

    def display_lives(self):
        for live in range(self.lives):
            x = self.live_x_start_pos + (
                        live * (self.live_img.get_size()[0] + 10))
            self.screen.blit(self.live_img, (x, 8))

    def display_score(self):
        score_surf = self.font.render(f'Score: {self.score}', True, 'white')
        score_rect = score_surf.get_rect(topleft=(20, 10))
        self.screen.blit(score_surf, score_rect)

    def victory_message(self):
        if not self.aliens.sprites():
            victory_surf = self.font.render('Win!', True, 'white')
            victory_rect = victory_surf.get_rect(
                center=(self.screen_width / 2, self.screen_height / 2))
            self.screen.blit(victory_surf, victory_rect)
            self.is_paused = True


def main():
    pygame.init()
    size = 1920, 1080
    pygame.display.set_mode(size)
    pygame.display.set_caption('Space Invaders | By Denis and Isa')
    game = Game()
    game.run()


if __name__ == '__main__':
    main()
