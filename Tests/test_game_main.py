import unittest
import os
import main
import pickle
from datetime import datetime

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import pygame

pygame.init()

from game_objects import Ship, Bullet, Alien, Bunker_Block, MysteryShip, Bonus


class MockScreen:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def get_size(self):
        return self.width, self.height

    def fill(self, color):
        pass


class MockSound:
    def play(self):
        pass


class TestGameLevel(unittest.TestCase):
    def test_get_score_table_empty(self):
        if os.path.exists("score_table.dat"):
            os.remove("score_table.dat")
        current_score = 555
        score_time = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
        score_table = [f"{current_score} {score_time}"]
        result = main.get_score_table(current_score)
        assert score_table == result

    def test_get_score_table(self):
        score_table = ["555 31/12/2022, 12:59:59", "444 31/12/2022, 12:59:59"]
        with open('score_table.dat', 'wb') as file:
            pickle.dump(score_table, file)
        current_score = 445
        score_time = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
        score_table.insert(1, f"{current_score} {score_time}")
        result = main.get_score_table(current_score)
        assert score_table == result

    def test_get_score_table_full(self):
        score_table = ["555 31/12/2022, 12:59:59", "444 31/12/2022, 12:59:59",
                       "333 31/12/2022, 12:59:59", "222 31/12/2022, 12:59:59",
                       "111 31/12/2022, 12:59:59"]
        with open('score_table.dat', 'wb') as file:
            pickle.dump(score_table, file)
        current_score = 112
        score_time = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
        score_table.pop()
        score_table.append(f"{current_score} {score_time}")
        result = main.get_score_table(current_score)
        assert score_table == result

    def test_level_init(self):
        screen = MockScreen(1920, 1080)
        screen_width, screen_height = screen.get_size()
        level = main.GameLevel(1, screen)
        assert level.lives == 0
        assert level.score == 0
        assert level.aliens_direction == 1
        assert level.aliens_speed == 1
        assert not level.is_lost
        assert not level.is_win
        assert not level.is_freeze
        ship = level.ship.sprite
        assert ship.rect.center == (screen_width // 2, screen_height - 100)
        assert ship.screen_width == screen_width
        assert ship.screen_height == screen_height

    def test_not_update_when_lost(self):
        screen = MockScreen(1920, 1080)
        screen_width, screen_height = screen.get_size()
        level = main.GameLevel(1, screen)
        level.is_lost = True
        bullet = Bullet(0, 0, 0, 5,
                        True, screen_height)
        old_y = bullet.rect.y
        level.alien_bullets.add(bullet)
        level.update()
        assert bullet.rect.y == old_y

    def test_move_aliens_down(self):
        screen = MockScreen(1920, 1080)
        level = main.GameLevel(1, screen)
        old_y = []
        for alien in level.aliens:
            old_y.append((alien, alien.rect.y))
        level.move_aliens_down(50)
        for alien in old_y:
            assert alien[0].rect.y == alien[1] + 50

    def test_aliens_not_shoot(self):
        screen = MockScreen(1920, 1080)
        level = main.GameLevel(1, screen)
        level.aliens = pygame.sprite.Group()
        level.aliens_shoot()
        assert not level.alien_bullets.sprites()

    def test_alien_shoot(self):
        screen = MockScreen(1920, 1080)
        level = main.GameLevel(1, screen)
        assert not level.alien_bullets.sprites()
        alien = Alien(0, 0, "red")
        level.aliens = pygame.sprite.Group(alien)
        level.laser_sound = MockSound()
        level.aliens_shoot()
        assert level.alien_bullets.sprites()

    def test_alien_position_check_right(self):
        screen = MockScreen(1920, 1080)
        screen_width, screen_height = screen.get_size()
        level = main.GameLevel(1, screen)
        alien = Alien(10, 10, "red")
        level.aliens = pygame.sprite.Group(alien)
        old_y = alien.rect.y
        alien.rect.right = screen_width
        level.aliens_position_check()
        assert alien.rect.y == old_y + 20
        assert level.aliens_direction == -1

    def test_alien_position_check_left(self):
        screen = MockScreen(1920, 1080)
        level = main.GameLevel(1, screen)
        alien = Alien(10, 10, "red")
        level.aliens = pygame.sprite.Group(alien)
        old_y = alien.rect.y
        alien.rect.left = 0
        level.aliens_position_check()
        assert alien.rect.y == old_y + 20
        assert level.aliens_direction == 1

    def test_alien_position_check_down(self):
        screen = MockScreen(1920, 1080)
        screen_width, screen_height = screen.get_size()
        level = main.GameLevel(1, screen)
        alien = Alien(50, 50, "red")
        level.aliens = pygame.sprite.Group(alien)
        alien.rect.bottom = screen_height
        level.aliens_position_check()
        assert level.is_lost

    def test_check_win(self):
        screen = MockScreen(1920, 1080)
        level = main.GameLevel(1, screen)
        level.check_win()
        assert not level.is_win
        level.aliens = pygame.sprite.Group()
        level.check_win()
        assert level.is_win

    def test_check_lost(self):
        screen = MockScreen(1920, 1080)
        level = main.GameLevel(1, screen)
        level.check_lost()
        assert not level.is_lost
        level.lives = -1
        level.check_lost()
        assert level.is_lost

    def test_active_bonuses_timer(self):
        screen = MockScreen(1920, 1080)
        screen_width, screen_height = screen.get_size()
        level = main.GameLevel(1, screen)
        bonuses = [Bonus(0,0,"freeze", screen_height),
                   Bonus(1,1,"fast", screen_height)]
        level.active_bonuses = pygame.sprite.Group(bonuses)
        old_time = bonuses[0].time
        level.active_bonuses_timer()
        for bonus in bonuses:
            assert bonus.time == old_time - 1

    def test_bonuses_timer(self):
        screen = MockScreen(1920, 1080)
        level = main.GameLevel(1, screen)
        assert not level.bonuses.sprites()
        level.bonuses_spawn_kills = 1
        level.bonuses_timer(0, 0)
        assert level.bonuses.sprites()
        assert level.bonuses_spawn_kills > 1

    def test_mystery_timer(self):
        screen = MockScreen(1920, 1080)
        level = main.GameLevel(1, screen)
        assert not level.mystery.sprites()
        level.mystery_spawn_time = 1
        level.extra_alien_timer()
        assert level.mystery.sprites()
        assert level.mystery_spawn_time > 1
