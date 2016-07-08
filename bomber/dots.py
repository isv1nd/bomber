from bomber import exceptions


class Dot(object):
    def __init__(self):
        self._hidden = True
        self._mine_signed = False

    @property
    def is_hidden(self):
        return self._hidden

    def open(self):
        self._hidden = False

    @property
    def is_mine_signed(self):
        return self._mine_signed

    def sign_mine(self, sign=True):
        self._mine_signed = sign


class MineDot(Dot):
    pass


class EmptyDot(Dot):
    pass


class NumberDot(Dot):
    _number = None

    def __init__(self, number=1):
        super(NumberDot, self).__init__()
        self.set_number(number)

    @property
    def number(self):
        return self._number

    def set_number(self, number):
        self._check_number_is_valid(number)
        self._number = number

    @staticmethod
    def _check_number_is_valid(number):
        if not isinstance(number, int) or (number <= 0 or number >= 9):
            raise exceptions.InvalidNumberForNumberDot
