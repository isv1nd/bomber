import testtools

from bomber import dots
from bomber import game_area as base_game_area


class BaseTestCase(testtools.TestCase):
    @staticmethod
    def _create_game_area(width_game_area, height_game_area, mines_count):
        return base_game_area.GameArea(
            width_game_area, height_game_area, mines_count)

    @staticmethod
    def _get_area_with_mines_like_bin_array(game_area):
        bin_array = []
        for dot, _, _ in game_area.get_all_dots():
            if isinstance(dot, dots.MineDot):
                bin_array.append(1)
            else:
                bin_array.append(0)
        return bin_array

    @staticmethod
    def _build_game_area_by_map(game_area_map, mines_only=False):
        game_area = []
        for row in game_area_map:
            area_row = []
            for dot in row:
                if 0 <= dot < 9:
                    if mines_only or dot == 0:
                        area_row.append(dots.EmptyDot())
                    else:
                        area_row.append(dots.NumberDot(dot))
                else:
                    area_row.append(dots.MineDot())
            game_area.append(area_row)
        return game_area

    @staticmethod
    def _build_map_by_game_area(game_area):
        game_area_map = [
            [None for _ in range(game_area.width_game_area)]
            for _ in range(game_area.height_game_area)]
        for dot, x_coordinate, y_coordinate in game_area.get_all_dots():
            if isinstance(dot, dots.MineDot):
                game_area_map[y_coordinate][x_coordinate] = -1
            elif isinstance(dot, dots.NumberDot):
                game_area_map[y_coordinate][x_coordinate] = dot.number
            else:
                game_area_map[y_coordinate][x_coordinate] = 0
        return game_area_map
