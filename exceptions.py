from colors import BColors


class BoardException(Exception):
    pass


class BoardOutException(BoardException):
    def __str__(self):
        return f'{BColors.FAIL}Выстрел за пределы игрового поля!{BColors.ENDC}'


class BoardUserException(BoardException):
    def __str__(self):
        return f'{BColors.FAIL}' \
               f'Говорят снаряд два раза в одну воронку не попадает...' \
               f'{BColors.ENDC}'


class BoardWrongShipException(BoardException):
    pass


class ShipWrongPlaceException(Exception):
    pass
