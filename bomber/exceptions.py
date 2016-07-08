class Base(Exception):
    pass


class BaseError(Base):
    pass


class GameOver(Base):
    pass


class DotOutsideOfAreaError(BaseError):
    pass


class MinesValueGreaterThenAreaSquare(BaseError):
    pass


class InvalidNumberForNumberDot(BaseError):
    pass


class MineWasDetonated(GameOver):
    pass


class AreaOpen(GameOver):
    pass