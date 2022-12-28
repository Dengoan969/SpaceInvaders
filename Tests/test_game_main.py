import unittest
import os
import main
import pickle
from datetime import datetime

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import pygame
pygame.init()


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