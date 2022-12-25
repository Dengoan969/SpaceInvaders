import time

import pygame
import pygame_menu
import sys
import random
import pickle

from pygame_menu import Theme

from game_objects import Ship, Bullet, Alien, Bunker_Block, MysteryShip, Bonus


# TODO: таблица рекордов


class Game:
    def __init__(self, level):
        self.screen = pygame.display.get_surface()
        self.screen_width, self.screen_height = self.screen.get_size()
        self.level = level
        ship = Ship(self.screen_width // 2, self.screen_height - 100)
        self.ship = pygame.sprite.GroupSingle(ship)

        self.lives = 0
        self.live_img = pygame.image.load(
            'textures/ship.png').convert()
        self.live_x_start_pos = self.screen_width - (
                self.live_img.get_size()[0] * 2 + 20)
        self.score = 0
        self.font = pygame.font.SysFont('pixeled', 40)
        self.big_font = pygame.font.SysFont('pixeled', 72)

        self.aliens = pygame.sprite.Group()
        self.alien_bullets = pygame.sprite.Group()

        self.aliens_direction = 1
        self.aliens_speed = 1
        self.mystery_spawn_time = random.randint(500, 1000)
        self.mystery = pygame.sprite.GroupSingle()
        self.bonuses = pygame.sprite.Group()
        self.active_bonuses = pygame.sprite.Group()
        self.bonuses_spawn_time = random.randint(5, 10)
        self.alien_types = {"B": "blue", "G": "green", "P": "purple",
                            "R": "red", "S": "skin", "Y": "yellow"}
        self.bunker_types = {"B": False, "T": True}

        with open('textures/BunkerShape.txt') as f:
            self.shape = f.readlines()
        self.block_size = 15
        self.blocks = pygame.sprite.Group()
        self.bunker_amount = 4
        self.bunker_x_positions = [
            num * (self.screen_width / self.bunker_amount) for num in
            range(self.bunker_amount)]
        self.create_level()
        music = pygame.mixer.Sound("audio/level_music.wav")
        music.set_volume(1)
        music.play(loops=-1)
        self.laser_sound = pygame.mixer.Sound("audio/shoot_sound.wav")
        self.laser_sound.set_volume(0.3)
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
                    # with open("savegame", "wb") as f:
                    #     pickle.dump(self, f)
                if event.type == ALIENSHOOT and not self.is_paused and not self.is_finished:
                    self.aliens_shoot()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r and self.is_finished:
                    run = False
            self.update()

    def gameplay_draw(self):
        self.blocks.draw(self.screen)
        self.mystery.draw(self.screen)
        self.bonuses.draw(self.screen)
        if not self.is_finished:
            self.ship.sprite.bullets.draw(self.screen)
            self.ship.draw(self.screen)
        self.aliens.draw(self.screen)
        self.alien_bullets.draw(self.screen)
        self.display_score()
        self.display_lives()
        self.victory_message()
        self.lose_message()

    def gameplay_update(self):
        self.ship.update()
        self.ship.sprite.bullets.update()

        self.collision_check()

        self.extra_alien_timer()
        self.active_bonuses_timer()
        self.mystery.update()
        self.bonuses.update()

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
                self.bonuses_timer(alien.rect.x, alien.rect.y)
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
                self.lose_message()
                if self.lives >= 0:
                    ship = Ship(self.screen_width // 2, self.screen_height - 100)
                    self.ship = pygame.sprite.GroupSingle(ship)

        for bonus in self.bonuses:
            if pygame.sprite.spritecollide(bonus, self.ship, False):
                bonus.kill()
                if bonus not in self.active_bonuses:
                    bonus.effect(self)
                    self.active_bonuses.add(bonus)

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
            laser_sprite = Bullet(alien.rect.centerx, alien.rect.bottom, 0, 5,
                                  True)
            self.alien_bullets.add(laser_sprite)
            self.laser_sound.play()

    def create_level(self):
        with open(f"Levels\\{self.level}.txt") as f:
            is_bunkers = False
            lines = f.read().splitlines()
            for row_index, row in enumerate(lines):
                if row == "":
                    is_bunkers = True
                    continue
                for col_index, col in enumerate(row):
                    if col != "*":
                        if is_bunkers:
                            self.create_bunker(self.screen_width / 15,
                                               self.screen_height - 250,
                                               self.bunker_x_positions[
                                                   col_index], self.bunker_types[col])
                        else:
                            self.create_alien(col_index, row_index, self.alien_types[col])

    def create_alien(self, col_index, row_index, alien_type,
                     x_distance=80, y_distance=48, x_offset=70, y_offset=100):
        x = col_index * x_distance + x_offset
        y = row_index * y_distance + y_offset
        self.aliens.add(Alien(x, y, alien_type))

    def create_bunker(self, x_start, y_start, offset_x, is_translucent):
        for row_index, row in enumerate(self.shape):
            for col_index, col in enumerate(row):
                if col == 'x':
                    x = x_start + col_index * self.block_size + offset_x
                    y = y_start + row_index * self.block_size
                    block = Bunker_Block(self.block_size, x, y, is_translucent)
                    self.blocks.add(block)

    def extra_alien_timer(self):
        self.mystery_spawn_time -= 1
        if self.mystery_spawn_time <= 0:
            self.mystery.add(MysteryShip(random.choice([-1, 1])))
            self.mystery_spawn_time = random.randint(500, 1000)

    def bonuses_timer(self, x, y):
        self.bonuses_spawn_time -= 1
        if self.bonuses_spawn_time <= 0:
            self.bonuses.add(Bonus(x, y, random.choice(["freeze", "fast", "life", "bullets"])))
            self.bonuses_spawn_time = random.randint(5, 10)

    def active_bonuses_timer(self):
        for bonus in self.active_bonuses:
            bonus.timer(self)

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
            victory_surf = self.big_font.render('You Win!', True, 'white')
            victory_rect = victory_surf.get_rect(
                center=(self.screen_width / 2, self.screen_height / 2))
            self.screen.blit(victory_surf, victory_rect)
            self.is_finished = True

    def lose_message(self):
        if self.lives < 0:
            lose_surf = self.big_font.render('You Lose!', True, 'white')
            lose_rect = lose_surf.get_rect(
                center=(self.screen_width / 2, self.screen_height / 2))
            self.screen.blit(lose_surf, lose_rect)
            self.is_finished = True


def main():
    pygame.init()
    size = 1350, 1080
    surface = pygame.display.set_mode(size)
    weight,height=surface.get_size()
    pygame.display.set_caption('Space Invaders | By Denis and Isa')
    mytheme = Theme(background_color=(0, 0, 0, 0), widget_font=pygame_menu.font.FONT_8BIT,
                    title_bar_style=pygame_menu.widgets.MENUBAR_STYLE_NONE,
                    widget_selection_effect=pygame_menu.widgets.HighlightSelection(),
                    widget_font_size=48,
                    title_font_size=72)
    menu = pygame_menu.Menu("Space Invaders", 1350, 1080,
                            theme=mytheme)
    game = Game(1)
    menu.add.button('Play', game.run)
    menu.add.button('Exit', pygame_menu.events.EXIT)
    menu.mainloop(surface)



if __name__ == '__main__':
    main()
