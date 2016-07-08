from bomber import dots
from bomber import exceptions
from bomber import game_area


class Bomber(object):
    def __init__(self, width_game_area, height_game_area, mines_count):
        self._game_area = game_area.GameArea(width_game_area,
                                             height_game_area, mines_count)

    def dig(self, x_coordinate, y_coordinate, check_area=True):
        dot = self._game_area.get_dot_by_coordinate(x_coordinate, y_coordinate)
        if isinstance(dot, dots.MineDot):
            for dot, _, _ in self.game_area.get_all_dots():
                dot.open()
            raise exceptions.MineWasDetonated
        if isinstance(dot, dots.NumberDot):
            dot.open()
        else:
            dot.open()
            self._open_neighbors(x_coordinate, y_coordinate)
        if check_area:
            self._check_area()

    def sign_mine(self, x_coordinate, y_coordinate):
        dot = self._game_area.get_dot_by_coordinate(x_coordinate, y_coordinate)
        dot.sign_mine(not dot.is_mine_signed)
        self._check_area()

    def dig_around(self, x_coordinate, y_coordinate):
        dot = self._game_area.get_dot_by_coordinate(x_coordinate, y_coordinate)
        if not (isinstance(dot, dots.NumberDot) and not dot.is_hidden):
            return

        neighbors = self._game_area.get_neighbor_dots(x_coordinate,
                                                      y_coordinate)
        mines_signed = 0
        for dot_, _, _ in neighbors:
            if isinstance(dot_, dots.MineDot) and dot_.is_mine_signed:
                mines_signed += 1

        if mines_signed != dot.number:
            return

        for dot, x_coordinate, y_coordinate in neighbors:
            if not dot.is_mine_signed:
                self.dig(x_coordinate, y_coordinate, check_area=False)
        self._check_area()

    def _open_neighbors(self, x_, y_):
        neighbors = self._game_area.get_neighbor_dots(x_, y_)
        for dot, x_neighbor, y_neighbor in neighbors:
            if dot.is_hidden:
                dot.open()
                if isinstance(dot, dots.EmptyDot):
                    self._open_neighbors(x_neighbor, y_neighbor)

    def _check_area(self):
        if self._game_area.is_only_mines_leave:
            for dot, _, _ in self.game_area.get_all_dots():
                if isinstance(dot, dots.MineDot):
                    dot.sign_mine()

        if self._game_area.is_opening_complete:
            for dot, _, _ in self.game_area.get_all_dots():
                dot.open()
            raise exceptions.AreaOpen

    @property
    def game_area(self):
        return self._game_area
