import unittest
from view import Grid
import pygame


class MyTestCase(unittest.TestCase):
    def test_coord_to_grid(self):
        Holder = Grid(120, 100, pygame)
        self.assertEqual(Holder.coord_to_grid(304, 233), (7, 5))
        self.assertEqual(Holder.coord_to_grid(130, 117), (0, 0))
        self.assertNotEqual(Holder.coord_to_grid(304, 233), (7, 2))
        self.assertNotEqual(Holder.coord_to_grid(304, 200), (7, 5))


if __name__ == '__main__':
    unittest.main()
