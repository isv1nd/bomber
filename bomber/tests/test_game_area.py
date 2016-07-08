import nose_parameterized
import mock

from bomber import game_area as base_game_area
from bomber import dots
from bomber import exceptions
from bomber import tests


class GameAreaTestCase(tests.BaseTestCase):
    def _patch_place_expected_game_area_all_mines(self,
                                                  expected_game_area_map):

        width = len(expected_game_area_map[0])
        height = len(expected_game_area_map)
        mines_count = [item for sublist in expected_game_area_map
                       for item in sublist].count(-1)
        game_area_only_mines = \
            self._build_game_area_by_map(expected_game_area_map,
                                         mines_only=True)
        patcher = mock.patch.object(
            base_game_area.GameArea, "_place_all_mines", autospec=True)

        def mock_place_all_mines(self_):
            self_._game_area_array = game_area_only_mines

        place_all_mines_mock = patcher.start()
        place_all_mines_mock.side_effect = mock_place_all_mines
        self.addCleanup(patcher.stop)
        return game_area_only_mines, width, height, mines_count

    def test_that_any_point_of_area_is_dot_object(self):
        game_area = self._create_game_area(30, 40, 0)
        for dot, _, _ in game_area.get_all_dots():
            self.assertIsInstance(dot, dots.Dot)

    def test_get_empty_square(self):
        game_area = self._create_game_area(30, 40, 0)
        for dot, _, _ in game_area.get_all_dots():
            self.assertIsInstance(dot, dots.EmptyDot)

    def test_get_expected_mine_number_in_square(self):
        mine_count = 10
        mine_counter = 0
        game_area = self._create_game_area(30, 40, mine_count)
        for dot, _, _ in game_area.get_all_dots():
            if isinstance(dot, dots.MineDot):
                mine_counter += 1
        self.assertEqual(mine_count, mine_counter)

    def test_random_mines_order_in_new_game_area(self):
        area_width = 100
        area_height = 100
        mine_count = area_width * area_height / 2
        game_area_1 = self._get_area_with_mines_like_bin_array(
            self._create_game_area(area_width, area_height, mine_count)
        )
        game_area_2 = []

        for _ in range(10):
            game_area_2 = self._get_area_with_mines_like_bin_array(
                self._create_game_area(area_width, area_height,
                                       mine_count)
            )
            if game_area_1 != game_area_2:
                break

        self.assertNotEqual(game_area_1, game_area_2,
                            msg="Game areas are always identical.")

    def test_area_iterator_returns_correct_value_of_dots(self):
        area_width = 10
        area_height = 10
        game_area = self._create_game_area(area_width, area_height, 10)
        self.assertEqual(area_width * area_height,
                         sum(1 for _ in game_area.get_all_dots()))

    def test_area_iterator_returns_correct_coordinates_of_dots(self):
        area_width = 5
        area_height = 5
        expected_coordinates_set = set()
        for y_coordinate in range(area_height):
            for x_coordinate in range(area_width):
                expected_coordinates_set.add((x_coordinate, y_coordinate))
        game_area = self._create_game_area(area_width, area_height, 0)
        actual_coordinates_set = \
            {(x_coordinate, y_coordinate)
             for _, x_coordinate, y_coordinate
             in game_area.get_all_dots()}
        self.assertEqual(expected_coordinates_set, actual_coordinates_set)

    def test_that_mines_value_is_less_than_area_square(self):
        area_width = 10
        area_height = 10
        self.assertRaises(
            exceptions.MinesValueGreaterThenAreaSquare,
            self._create_game_area, area_width, area_height,
            area_width * area_height + 1)

    @nose_parameterized.parameterized.expand([
        (30, 40, 25, 40),
        (30, 40, 30, 25),
        (30, 40, 30, 40),
        (30, 40, -1, 1),
        (30, 40, 1, -1),
        (30, 40, -1, -1),
    ])
    def test_get_dot_raises_if_coordinates_not_in_area(
            self, width_game_area, height_game_area,
            x_coordinate, y_coordinate):
        game_area = self._create_game_area(width_game_area,
                                           height_game_area, 0)
        self.assertRaises(exceptions.DotOutsideOfAreaError,
                          game_area.get_dot_by_coordinate,
                          x_coordinate, y_coordinate)

    @nose_parameterized.parameterized.expand([
        (3, 3, 0, 0, {(0, 1), (1, 1), (1, 0)}),
        (3, 3, 0, 1, {(0, 0), (1, 0), (1, 1), (0, 2), (1, 2)}),
        (3, 3, 1, 1, {(0, 0), (1, 0), (0, 2),
                      (2, 0), (2, 1), (2, 2), (1, 2), (0, 1)}),
        (3, 3, 1, 0, {(0, 0), (0, 1), (1, 1), (2, 0), (2, 1)}),
        (3, 3, 2, 1, {(1, 0), (1, 1), (1, 2), (2, 0), (2, 2)}),
        (3, 3, 1, 2, {(0, 1), (0, 2), (1, 1), (2, 1), (2, 2)}),
        (3, 3, 0, 2, {(0, 1), (1, 2), (1, 1)}),
        (3, 3, 2, 0, {(1, 0), (2, 1), (1, 1)}),
        (3, 3, 2, 2, {(1, 2), (2, 1), (1, 1)}),
    ])
    def test_get_neighbor_dots_returns_correct_coordinates_of_dots(
            self, area_width, area_height, x_coordinate, y_coordinate,
            expected_neighbor_coordinates):
        game_area = self._create_game_area(area_width, area_height, 0)
        actual_neighbor_coordinates = \
            {(x_, y_) for dot, x_, y_
             in game_area.get_neighbor_dots(x_coordinate, y_coordinate)}
        self.assertEqual(
            expected_neighbor_coordinates, actual_neighbor_coordinates)

    def test_numbers_square_around_any_mine(self):
        game_area = self._create_game_area(10, 10, 10)
        for dot, x_coordinate, y_coordinate in game_area.get_all_dots():
            if not isinstance(dot, dots.MineDot):
                continue
            neighbor_dots = game_area.get_neighbor_dots(
                x_coordinate, y_coordinate)
            for neighbor_dot, x_neighbor, y_neighbor in neighbor_dots:
                self.assertIsInstance(neighbor_dot,
                                      (dots.NumberDot, dots.MineDot))

    def test_check_right_numbers_around_any_mine(self):
        expected_game_area_map = [
            [-1, 3, -1, -1,  2,  1],
            [-1, 4,  4,  5, -1,  2],
            [2, -1,  2, -1, -1,  3],
            [1,  2,  3,  3,  3, -1],
            [0,  2, -1,  3,  3,  3],
            [0,  2, -1,  3, -1, -1],
        ]
        _, width, height, mines_count = \
            self._patch_place_expected_game_area_all_mines(
                expected_game_area_map)

        game_area = self._create_game_area(width, height, mines_count)

        self.assertEqual(expected_game_area_map,
                         self._build_map_by_game_area(game_area))

    def test_check_area_opening_complete(self):
        expected_game_area_map = [
            [-1, 3, -1, -1,  2,  1],
            [-1, 4,  4,  5, -1,  2],
            [2, -1,  2, -1, -1,  3],
            [1,  2,  3,  3,  3, -1],
            [0,  2, -1,  3,  3,  3],
            [0,  2, -1,  3, -1, -1],
        ]
        _, width, height, mines_count = \
            self._patch_place_expected_game_area_all_mines(
                expected_game_area_map)

        game_area = self._create_game_area(width, height, mines_count)
        self.assertFalse(game_area.is_opening_complete)

        for dot, _, _ in game_area.get_all_dots():
            if isinstance(dot, (dots.EmptyDot, dots.NumberDot)):
                dot.open()
            else:
                dot.sign_mine()

        self.assertTrue(game_area.is_opening_complete)

    def test_check_area_only_mines_leave(self):
        expected_game_area_map = [
            [-1, 3, -1, -1,  2,  1],
            [-1, 4,  4,  5, -1,  2],
            [2, -1,  2, -1, -1,  3],
            [1,  2,  3,  3,  3, -1],
            [0,  2, -1,  3,  3,  3],
            [0,  2, -1,  3, -1, -1],
        ]
        _, width, height, mines_count = \
            self._patch_place_expected_game_area_all_mines(
                expected_game_area_map)

        game_area = self._create_game_area(width, height, mines_count)
        self.assertFalse(game_area.is_opening_complete)

        for dot, _, _ in game_area.get_all_dots():
            if isinstance(dot, (dots.EmptyDot, dots.NumberDot)):
                dot.open()

        self.assertTrue(game_area.is_only_mines_leave)
