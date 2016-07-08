import numpy

from bomber import constants
from bomber import exceptions
from bomber import dots


class GameAreaIterator(object):
    def __init__(self, game_area):
        self._game_area = game_area
        self._y_coordinate = 0
        self._x_coordinate = 0

    def __iter__(self):
        return self

    def next(self):
        if self._y_coordinate > self._game_area.height_game_area - 1 or \
           self._x_coordinate > self._game_area.width_game_area - 1:
            raise StopIteration
        result = (
            self._game_area.area[self._y_coordinate][self._x_coordinate],
            self._x_coordinate,
            self._y_coordinate)
        if self._x_coordinate < self._game_area.width_game_area - 1:
            self._x_coordinate += 1
        else:
            self._x_coordinate = 0
            self._y_coordinate += 1
        return result


class GameArea(object):
    def __init__(self, width_game_area, height_game_area, mines_count):
        if mines_count > width_game_area * height_game_area:
            raise exceptions.MinesValueGreaterThenAreaSquare

        self.mines_count = mines_count
        self._width_game_area = width_game_area
        self._height_game_area = height_game_area
        self._game_area_array = []
        self._init_game_area()

    def _place_all_mines(self):
        mine_counter = self.mines_count
        for y_coordinate in range(0, self.height_game_area):
            area_row = []
            for x_coordinate in range(0, self.width_game_area):
                if mine_counter == 0:
                    area_row.append(dots.EmptyDot())
                else:
                    area_row.append(dots.MineDot())
                if mine_counter:
                    mine_counter -= 1
            self._game_area_array.append(area_row)
        numpy.random.shuffle(self._game_area_array)

    def _set_numbers_around_mines(self):
        for dot, x_coordinate, y_coordinate in self.get_all_dots():
            if not isinstance(dot, dots.MineDot):
                continue
            neighbor_dots = self.get_neighbor_dots(x_coordinate, y_coordinate)
            for neighbor_dot, x_neighbor, y_neighbor in neighbor_dots:
                if isinstance(neighbor_dot, dots.EmptyDot):
                    new_number_dot = dots.NumberDot()
                    self._set_dot_for_coordinates(
                        new_number_dot, x_neighbor, y_neighbor)
                elif isinstance(neighbor_dot, dots.NumberDot):
                    neighbor_dot.set_number(neighbor_dot.number + 1)

    def _init_game_area(self):
        self._place_all_mines()
        self._set_numbers_around_mines()

    @property
    def width_game_area(self):
        return self._width_game_area

    @property
    def height_game_area(self):
        return self._height_game_area

    @property
    def area(self):
        return self._game_area_array

    def get_all_dots(self):
        return GameAreaIterator(self)

    def get_neighbor_dots(self, x, y):
        self.get_dot_by_coordinate(x, y)
        neighbor_dots = []
        for offset in constants.VECTOR_NEIGHBOR_DOT_OFFSETS:
            x_neighbor = x + offset[0]
            y_neighbor = y + offset[1]
            try:
                neighbor_dot = self.get_dot_by_coordinate(
                    x_neighbor, y_neighbor
                )
            except exceptions.DotOutsideOfAreaError:
                continue
            neighbor_dots.append((neighbor_dot, x_neighbor, y_neighbor))
        return neighbor_dots

    def get_dot_by_coordinate(self, x, y):
        if x < 0 or y < 0:
            raise exceptions.DotOutsideOfAreaError
        try:
            return self._game_area_array[y][x]
        except IndexError:
            raise exceptions.DotOutsideOfAreaError

    def _set_dot_for_coordinates(self, dot, x, y):
        self._game_area_array[y][x] = dot

    @property
    def is_opening_complete(self):
        is_complete = True
        for dot, _, _ in self.get_all_dots():
            if (isinstance(dot, (dots.NumberDot, dots.EmptyDot)) and dot.is_hidden) \
                    or (isinstance(dot, dots.MineDot) and not dot.is_mine_signed):
                is_complete = False

        return is_complete

    @property
    def is_only_mines_leave(self):
        is_only_mines = True
        for dot, _, _ in self.get_all_dots():
            if (isinstance(dot, (dots.NumberDot, dots.EmptyDot)) and dot.is_hidden):
                is_only_mines = False

        return is_only_mines
