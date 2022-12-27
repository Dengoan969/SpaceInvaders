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
