import mock

import nose_parameterized

from bomber import tests
from bomber import base
from bomber import dots
from bomber import exceptions
from bomber import game_area


class BomberTestCase(tests.BaseTestCase):

    @staticmethod
    def _create_bomber(width_game_area, height_game_area, mines_count):
        return base.Bomber(width_game_area, height_game_area, mines_count)

    def _patch_place_expected_game_area(self, expected_game_area_map):
        width = len(expected_game_area_map[0])
        height = len(expected_game_area_map)
        plain_map = [item for sublist in expected_game_area_map
                     for item in sublist]
        mines_count = plain_map.count(-1)
        game_area_only = \
            self._build_game_area_by_map(expected_game_area_map)
        patcher = mock.patch.object(
            game_area.GameArea, "_init_game_area", autospec=True)

        def mock_init_game_area(self_):
            self_._game_area_array = game_area_only

        place_expected_game_area_mock = patcher.start()
        place_expected_game_area_mock.side_effect = mock_init_game_area
        self.addCleanup(patcher.stop)
        return game_area_only, width, height, mines_count, plain_map

    def test_have_game_area(self):
        bomber = self._create_bomber(10, 10, 0)
        self.assertIsInstance(bomber.game_area, game_area.GameArea)

    def test_all_area_is_open_if_mine_was_detonated(self):
        bomber = self._create_bomber(1, 1, 1)
        self.assertRaises(exceptions.MineWasDetonated, bomber.dig, 0, 0)
        for dot, _, _ in bomber.game_area.get_all_dots():
            self.assertFalse(dot.is_hidden)

    def test_square_is_open_if_number_was_excavated(self):
        expected_game_area_map = \
            [[-1, 1],
             [1, 1]]

        _, width, height, mines_count, plain_map = \
            self._patch_place_expected_game_area(
                expected_game_area_map)

        bomber = self._create_bomber(width, height, mines_count)

        number_dot, number_dot_x, number_dot_y = next(
            ((dot, x_, y_) for dot, x_, y_ in bomber.game_area.get_all_dots()
             if isinstance(dot, dots.NumberDot))
        )

        bomber.dig(number_dot_x, number_dot_y)

        self.assertFalse(number_dot.is_hidden)
        self.assertEqual(len(plain_map) - mines_count,
                         [dot.is_hidden for dot, _, _
                          in bomber.game_area.get_all_dots()].count(True))

    def test_bulk_open_if_empty_was_excavated(self):
        expected_game_area_map = \
            [[-1,  2, 0],
             [-1,  2, 0],
             [1,   1, 0]]
        expected_hidden_dots = {(0, 0), (0, 1), (0, 2)}
        empty_dot_coordinates = (2, 0)

        _, width, height, mines_count, plain_map = \
            self._patch_place_expected_game_area(
                expected_game_area_map)
        bomber = self._create_bomber(width, height, mines_count)

        bomber.dig(*empty_dot_coordinates)

        self.assertEqual(
            expected_hidden_dots,
            {(x_, y_) for dot, x_, y_ in bomber.game_area.get_all_dots()
             if dot.is_hidden})

    def test_can_sign_mine(self):
        bomber = self._create_bomber(10, 10, 1)
        x_coordinate = 1
        y_coordinate = 1

        dot = bomber.game_area.get_dot_by_coordinate(x_coordinate,
                                                     y_coordinate)
        bomber.sign_mine(x_coordinate, y_coordinate)
        self.assertTrue(dot.is_mine_signed)
        bomber.sign_mine(x_coordinate, y_coordinate)
        self.assertFalse(dot.is_mine_signed)

    def test_area_open_raises_if_correctly_completed_after_dig(self):
        expected_game_area_map = \
            [[-1,  2],
             [2,  -1]]

        _, width, height, mines_count, plain_map = \
            self._patch_place_expected_game_area(
                expected_game_area_map)
        bomber = self._create_bomber(width, height, mines_count)

        bomber.sign_mine(0, 0)
        bomber.sign_mine(1, 1)
        bomber.dig(0, 1)

        self.assertRaises(exceptions.AreaOpen, bomber.dig, 1, 0)

    def test_area_open_raises_if_correctly_completed_after_sign_mine(self):
        bomber = self._create_bomber(1, 1, 1)
        x_coordinate = 0
        y_coordinate = 0

        self.assertRaises(exceptions.AreaOpen, bomber.sign_mine,
                          x_coordinate, y_coordinate)

    def test_area_open_raises_if_only_mines_live(self):
        expected_game_area_map = \
            [[-1,  2],
             [2,  -1]]

        _, width, height, mines_count, plain_map = \
            self._patch_place_expected_game_area(
                expected_game_area_map)
        bomber = self._create_bomber(width, height, mines_count)

        bomber.dig(0, 1)

        self.assertRaises(exceptions.AreaOpen, bomber.dig, 1, 0)

    def test_area_not_open_if_incorrectly_signed(self):
        expected_game_area_map = \
            [[-1,  2],
             [2,  -1]]
        _, width, height, mines_count, plain_map = \
            self._patch_place_expected_game_area(
                expected_game_area_map)

        bomber = self._create_bomber(width, height, mines_count)
        bomber.sign_mine(1, 1)
        bomber.sign_mine(0, 0)
        bomber.sign_mine(0, 1)
        self.assertIsNone(bomber.dig(1, 0))

    def test_area_open_raises_after_empty_was_excavated(self):
        expected_game_area_map = \
            [[-1,  2, 0],
             [-1,  2, 0],
             [1,   1, 0]]

        _, width, height, mines_count, plain_map = \
            self._patch_place_expected_game_area(
                expected_game_area_map)
        bomber = self._create_bomber(width, height, mines_count)

        bomber.dig(0, 2)

        self.assertRaises(exceptions.AreaOpen, bomber.dig, 2, 0)

    @nose_parameterized.parameterized.expand([
        ("success", {(0, 2)}, {(0, 1)}, (0, 2), {(0, 2), (1, 2), (1, 1)}),
        ("not_all_mines_are_signed", {(0, 2)}, set(), (0, 2), {(0, 2)}),
        ("cant_dig_around_if_not_open_square", set(), set(), (0, 2), set()),
        ("area_open_if_all_mines_signed", {(1, 1)}, {(0, 1), (0, 0)}, (1, 1),
         exceptions.AreaOpen),
    ])
    def test_dig_around(
            self, _, dots_to_dig, dots_to_sign, dot_to_dig_around,
            expected_open_dots_or_exc):
        expected_game_area_map = \
            [[-1,  2, 0],
             [-1,  2, 0],
             [1,   1, 0]]

        _, width, height, mines_count, plain_map = \
            self._patch_place_expected_game_area(
                expected_game_area_map)
        bomber = self._create_bomber(width, height, mines_count)

        for dot in dots_to_dig:
            bomber.dig(*dot)
        for dot in dots_to_sign:
            bomber.sign_mine(*dot)

        if isinstance(expected_open_dots_or_exc, set):
            bomber.dig_around(*dot_to_dig_around)
            self.assertEqual(
                expected_open_dots_or_exc,
                {(x_, y_) for dot, x_, y_ in bomber.game_area.get_all_dots()
                 if not dot.is_hidden})
        else:
            self.assertRaises(expected_open_dots_or_exc, bomber.dig_around,
                              *dot_to_dig_around)

