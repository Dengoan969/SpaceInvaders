import unittest
import os

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import pygame
pygame.init()

from game_objects import Ship, Bullet, Alien, Bunker_Block, MysteryShip, Bonus


class MockGame:
    def __init__(self):
        self.aliens_speed = 20
        self.is_freeze = False
        self.lives = 0
        ship = MockShip()
        self.ship = pygame.sprite.GroupSingle(ship)

    def reset(self):
        self.aliens_speed = 20
        self.is_freeze = False
        self.lives = 0
        ship = MockShip()
        self.ship = pygame.sprite.GroupSingle(ship)


class MockShip(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.cooldown = 500
        self.is_diagonal_shoot = False


class TestGameObjects(unittest.TestCase):
    def test_bunker_block_translucent(self):
        block = Bunker_Block(15, 0, 0, True)
        assert block.is_translucent
        assert block.image.get_at((0, 0)) == pygame.color.Color(128, 128, 128)

    def test_bunker_block_not_translucent(self):
        block = Bunker_Block(15, 0, 0, False)
        assert not block.is_translucent
        assert block.image.get_at((0, 0)) == pygame.color.Color(255, 255, 255)

    def test_bunker_block_rect(self):
        block = Bunker_Block(15, 0, 5, True)
        assert block.rect.x == 0
        assert block.rect.y == 5

    def test_alien_rect(self):
        alien = Alien(5, 10, "red")
        assert alien.rect.center == (5, 10)

    def test_alien_rect2(self):
        alien = Alien(5, 10, "blue")
        assert alien.rect.center == (5, 10)

    def test_alien_price(self):
        aliens_prices = {"blue": 100, "skin": 150, "yellow": 200, "red": 250,
                         "green": 300, "purple": 400}
        for alien_color in aliens_prices:
            alien = Alien(5, 0, alien_color)
            assert alien.price == aliens_prices[alien_color]

    def test_alien_update_right(self):
        alien = Alien(5, 10, "blue")
        alien.update(1, 5)
        assert alien.rect.centerx == 10

    def test_alien_update_left(self):
        alien = Alien(5, 10, "blue")
        alien.update(-1, 5)
        assert alien.rect.centerx == 0

    def test_mystery_rect1(self):
        mystery = MysteryShip(1, 500)
        assert mystery.rect.center == (-80, 50)

    def test_mystery_rect2(self):
        screen_width = 500
        mystery = MysteryShip(-1, screen_width)
        assert mystery.rect.center == (screen_width + 80, 50)

    def test_mystery_speed1(self):
        mystery = MysteryShip(1, 500)
        assert mystery.speed == 3

    def test_mystery_speed2(self):
        mystery = MysteryShip(-1, 500)
        assert mystery.speed == -3

    def test_mystery_update1(self):
        mystery = MysteryShip(1, 500)
        old = mystery.rect.x
        mystery.update()
        assert mystery.rect.x == old + 3

    def test_mystery_update2(self):
        mystery = MysteryShip(-1, 500)
        old = mystery.rect.x
        mystery.update()
        assert mystery.rect.x == old - 3

    def test_mystery_update3(self):
        mystery = MysteryShip(1, 500)
        group = pygame.sprite.GroupSingle(mystery)
        for i in range(500):
            mystery.update()
        assert not group.has(mystery)

    def test_mystery_update4(self):
        mystery = MysteryShip(-1, 500)
        group = pygame.sprite.GroupSingle(mystery)
        for i in range(500):
            mystery.update()
        assert not group.has(mystery)

    def test_bonus_type(self):
        freeze = Bonus(0, 0, "freeze", 500)
        assert freeze.bonus_type == "freeze"

    def test_bonus_buffer_none(self):
        freeze = Bonus(0, 0, "freeze", 500)
        assert freeze.buffer is None

    def test_bonus_rect(self):
        freeze = Bonus(5, 12, "freeze", 500)
        assert freeze.rect.center == (5, 12)

    def test_bonus_update(self):
        freeze = Bonus(0, 0, "freeze", 500)
        old = freeze.rect.y
        freeze.update()
        assert freeze.rect.y == old + 2

    def test_bonus_update_out(self):
        bonus = Bonus(0, 0, "freeze", 500)
        group = pygame.sprite.GroupSingle(bonus)
        for i in range(600):
            bonus.update()
        assert not group.has(bonus)

    mock_game = MockGame()

    def test_bonus_freeze(self):
        bonus = Bonus(0, 0, "freeze", 500)
        old_speed = self.mock_game.aliens_speed
        bonus.effect(self.mock_game)
        assert self.mock_game.aliens_speed == 0
        assert self.mock_game.is_freeze
        assert bonus.buffer == old_speed

    def test_bonus_life(self):
        bonus = Bonus(0, 0, "life", 500)
        bonus.effect(self.mock_game)
        assert self.mock_game.lives == 1

    def test_bonus_fast(self):
        bonus = Bonus(0, 0, "fast", 500)
        old_speed = self.mock_game.ship.sprite.cooldown
        bonus.effect(self.mock_game)
        assert self.mock_game.ship.sprite.cooldown == old_speed / 2
        assert bonus.buffer == old_speed

    def test_bonus_bullets(self):
        bonus = Bonus(0, 0, "bullets", 500)
        bonus.effect(self.mock_game)
        assert self.mock_game.ship.sprite.is_diagonal_shoot

    mock_game2 = MockGame()

    def test_undo_freeze(self):
        bonus = Bonus(0, 0, "freeze", 500)
        old_speed = self.mock_game2.aliens_speed
        bonus.effect(self.mock_game2)
        self.mock_game2.aliens_speed += 1
        bonus.effect_undo(self.mock_game2)
        assert self.mock_game2.aliens_speed == old_speed + 1
        assert not self.mock_game2.is_freeze

    def test_undo_fast(self):
        bonus = Bonus(0, 0, "fast", 500)
        old_speed = self.mock_game2.ship.sprite.cooldown
        bonus.effect(self.mock_game2)
        bonus.effect_undo(self.mock_game2)
        assert self.mock_game2.ship.sprite.cooldown == old_speed

    def test_undo_bullets(self):
        bonus = Bonus(0, 0, "bullets", 500)
        bonus.effect(self.mock_game2)
        bonus.effect_undo(self.mock_game2)
        assert not self.mock_game2.ship.sprite.is_diagonal_shoot

    def test_bonus_timer(self):
        bonus = Bonus(0, 0, "freeze", 500)
        old_time = bonus.time
        bonus.timer(self.mock_game2)
        assert bonus.time == old_time - 1

    def test_bonus_timer_event(self):
        bonus = Bonus(0, 0, "freeze", 500)
        group = pygame.sprite.GroupSingle(bonus)
        bonus.effect(self.mock_game2)
        for i in range(bonus.time + 1):
            bonus.timer(self.mock_game2)
        assert bonus.time <= 0
        assert not group.has(bonus)
        assert not self.mock_game2.is_freeze

    def test_bullet_rect(self):
        bullet = Bullet(5, 12, 5, 5, False, 500)
        assert bullet.rect.center == (5, 12)
