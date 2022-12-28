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
