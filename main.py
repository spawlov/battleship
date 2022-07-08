import numpy as np

from colors import BColors
from exceptions import ShipWrongPlaceException, BoardOutException, \
    BoardUsedException, BoardWrongShipException, BoardException


class Ship:
    def __init__(self, length: int, bow: tuple, place: int, live: int):
        self.length = length
        self.bow = bow
        self.place = place
        self.live = live

    @property
    def dots(self) -> list:
        cords = [self.bow]
        if 1 < self.length <= 4:
            cur_n = self.bow[0]
            cur_l = self.bow[1]
            for _ in range(self.length - 1):
                if self.place == 0:
                    cur_l += 1
                elif self.place == 1:
                    cur_n += 1
                else:
                    raise ShipWrongPlaceException()
                cords.append((cur_n, cur_l))
        return cords

    def shooting(self, shoot: tuple) -> bool:
        return shoot in self.dots


class Board:
    def __init__(self, hidden: bool = False, size: int = 6):
        self.hidden = hidden
        self.board_size = size
        self.dots_busy = []
        self.ships = []
        self.count = 0

        filler = BColors.OKBLUE + chr(8776) + BColors.ENDC
        board = np.array(
            [[filler] * (self.board_size + 1)] * (self.board_size + 1),
            dtype=str
        )
        for i in range(self.board_size + 1):
            board[i][0] = chr(64 + i)
            board[0][i] = str(i)
            board[0][0] = ' '
        self.board = board

    @staticmethod
    def cords_conv(cords: tuple, reverse: bool = False) -> tuple:
        cord_letter = ord(cords[0].upper()) - 64
        cord_number = int(cords[1])
        if reverse:
            return cord_letter, cord_number
        else:
            return cord_number, cord_letter

    def dot_out(self, dots: tuple):
        return not all(
            [1 <= dots[0] <= self.board_size, 1 <= dots[1] <= self.board_size]
        )

    def ship_contour(self, ship: Ship, visible: bool = True):
        near = [(_, __) for _ in range(-1, 2) for __ in range(-1, 2)]
        for dot in ship.dots:
            for dot_l, dot_n in near:
                current = dot[0] + dot_l, dot[1] + dot_n
                if not self.dot_out(current) and current not in self.dots_busy:
                    if visible:
                        self.board[current[0]][current[1]] = \
                            BColors.OKGREEN + chr(8226) + BColors.ENDC
                    self.dots_busy.append(current)

    def add_ship(self, ship: Ship):
        for dot in ship.dots:
            if any([self.dot_out(dot), dot in self.dots_busy]):
                raise BoardWrongShipException()
        for dot in ship.dots:
            self.board[dot[0]][dot[1]] = \
                BColors.HEADER + chr(9632) + BColors.ENDC
            self.dots_busy.append(dot)
        self.ships.append(ship)
        self.ship_contour(ship)

    def shoot(self, dot: tuple) -> bool:
        dot = self.cords_conv(dot, True)
        if self.dot_out(dot):
            raise BoardOutException()
        if dot in self.dots_busy:
            raise BoardUsedException()
        self.dots_busy.append(dot)
        for ship in self.ships:
            if ship.shooting(dot):
                ship.live -= 1
                self.board[dot[0]][dot[1]] = BColors.FAIL + 'x' + BColors.ENDC
                if not ship.live:
                    self.count += 1
                    self.ship_contour(ship, True)
                    print(f'{BColors.FAIL}Корабль уничтожен!{BColors.ENDC}')
                    return False
                else:
                    print(f'{BColors.FAIL}Корабль поврежден!{BColors.ENDC}')
                    return True
        self.board[dot[0]][dot[1]] = BColors.WARNING + '*' + BColors.ENDC
        print(f'{BColors.OKGREEN}Промах!{BColors.ENDC}')
        return False

    def __str__(self):
        result = ''
        for i in range(self.board_size + 1):
            result += '\n'
            for j in range(self.board_size + 1):
                result += self.board[i][j] + '  '
        return result

    def init_game(self):
        self.dots_busy = []


class Player:
    def __init__(self, my_board: Board, enemy_board: Board):
        self.my_board = my_board
        self.en_board = enemy_board

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.en_board.shoot(target)
                return repeat
            except BoardException as e:
                print(e)


if __name__ == '__main__':
    s1 = Ship(2, (3, 3), 1, 2)

    b = Board()
    b.ship_contour(s1)
    print(b)
