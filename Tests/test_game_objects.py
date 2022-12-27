import unittest

import pygame.color

from game_objects import Ship, Bullet, Alien, Bunker_Block, MysteryShip, Bonus


class TestGameObjects(unittest.TestCase):
    def test_bunker_block_translucent(self):
        block = Bunker_Block(15,0,0,True)
        assert block.is_translucent == True
        assert block.image.get_at((0,0)) == pygame.color.Color(128,128,128)

    def test_bunker_block_not_translucent(self):
        block = Bunker_Block(15,0,0,False)
        assert block.is_translucent == False
        assert block.image.get_at((0,0)) == pygame.color.Color(255, 255, 255)

    def test_bunker_block_rect(self):
        block = Bunker_Block(15,0,5,True)
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
            alien = Alien(5,0,alien_color)
            assert alien.price == aliens_prices[alien_color]

    def test_alien_update_right(self):
        alien = Alien(5, 10, "blue")
        alien.update(1, 5)
        assert alien.rect.centerx == 10

    def test_alien_update_left(self):
        alien = Alien(5, 10, "blue")
        alien.update(-1, 5)
        assert alien.rect.centerx == 0

    display = pygame.display.set_mode((1920, 1080))

    def test_mystery_rect1(self):
        mystery = MysteryShip(1)
        assert mystery.rect.center == (-80, 50)

    def test_mystery_rect2(self):
        screen_width = pygame.display.get_surface().get_width()
        mystery = MysteryShip(-1)
        assert mystery.rect.center == (screen_width+80, 50)

    def test_mystery_speed1(self):
        mystery = MysteryShip(1)
        assert mystery.speed == 3

    def test_mystery_speed2(self):
        mystery = MysteryShip(-1)
        assert mystery.speed == -3

    def test_mystery_update1(self):
        mystery = MysteryShip(1)
        old = mystery.rect.x
        mystery.update()
        assert mystery.rect.x == old + 3

    def test_mystery_update2(self):
        mystery = MysteryShip(-1)
        old = mystery.rect.x
        mystery.update()
        assert mystery.rect.x == old - 3

    def test_mystery_update3(self):
        mystery = MysteryShip(1)
        group = pygame.sprite.GroupSingle(mystery)
        for i in range(682):
            mystery.update()
        assert not group.has(mystery)

    def test_mystery_update4(self):
        mystery = MysteryShip(-1)
        group = pygame.sprite.GroupSingle(mystery)
        for i in range(682):
            mystery.update()
        assert not group.has(mystery)
