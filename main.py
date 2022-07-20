from random import randint

import numpy as np

from colors import BColors
from exceptions import ShipWrongPlaceException, BoardOutException, \
    BoardUserException, BoardWrongShipException, BoardException


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
    ship_img = BColors.HEADER + chr(9632) + BColors.ENDC
    contour_img = BColors.OKGREEN + chr(8226) + BColors.ENDC
    wave_img = BColors.OKBLUE + chr(8776) + BColors.ENDC
    shoot_img = BColors.WARNING + '*' + BColors.ENDC
    damage_img = BColors.FAIL + 'x' + BColors.ENDC

    def __init__(self, hidden: bool = False, size: int = 6):
        self.hidden = hidden
        self.board_size = size
        self.dots_busy = []
        self.ships = []
        self.count = 0

        board = np.array(
            [[self.wave_img] * (self.board_size + 1)] * (self.board_size + 1),
            dtype=str
        )
        for i in range(self.board_size + 1):
            board[i][0] = chr(64 + i)
            board[0][i] = str(i)
            board[0][0] = ' '
        self.board = board

    def dot_out(self, dots: tuple):
        return not all(
            [1 <= dots[0] <= self.board_size, 1 <= dots[1] <= self.board_size]
        )

    def ship_contour(self, ship: Ship, visible: bool = False):
        near = [(_, __) for _ in range(-1, 2) for __ in range(-1, 2)]
        for dot in ship.dots:
            for dot_l, dot_n in near:
                current = dot[0] + dot_l, dot[1] + dot_n
                if not self.dot_out(current) and current not in self.dots_busy:
                    if visible:
                        self.board[current[0]][current[1]] = self.contour_img
                    self.dots_busy.append(current)

    def add_ship(self, ship: Ship):
        for dot in ship.dots:
            if any([self.dot_out(dot), dot in self.dots_busy]):
                raise BoardWrongShipException()
        for dot in ship.dots:
            self.board[dot[0]][dot[1]] = self.ship_img
            self.dots_busy.append(dot)
        self.ships.append(ship)
        self.ship_contour(ship)

    def shoot(self, dot: tuple) -> bool:
        if self.dot_out(dot):
            raise BoardOutException()
        if dot in self.dots_busy:
            raise BoardUserException()
        self.dots_busy.append(dot)
        for ship in self.ships:
            if ship.shooting(dot):
                ship.live -= 1
                self.board[dot[0]][dot[1]] = self.damage_img
                if not ship.live:
                    self.count += 1
                    self.ship_contour(ship, True)
                    print(f'{BColors.FAIL}Корабль уничтожен!{BColors.ENDC}')
                    return False
                else:
                    print(f'{BColors.FAIL}Корабль поврежден!{BColors.ENDC}')
                    return True
        self.board[dot[0]][dot[1]] = self.shoot_img
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

    @property
    def ask(self):
        raise NotImplementedError()

    @property
    def move(self):
        while True:
            try:
                target = self.ask
                repeat = self.en_board.shoot(target)
                return repeat
            except BoardException as e:
                print(e)


class AI(Player):
    cords = None

    @property
    def ask(self):

        if self.cords is None:
            self.cords = self.random_cord
        i, j = self.cords

        if self.en_board.board[i][j] == self.my_board.damage_img:
            if all([
                i + 1 <= 6,
                (i + 1, j) not in self.en_board.dots_busy
            ]):
                self.cords = [i + 1, j]
            elif all([
                i + 1 > 6,
                (i + 1, j) not in self.en_board.dots_busy
            ]):
                self.cords = [i - 1, j]
            elif all([
                j + 1 <= 6,
                (i, j + 1) not in self.en_board.dots_busy
            ]):
                self.cords = [i, j + 1]
            elif all([
                j + 1 > 6,
                (i, j - 1) not in self.en_board.dots_busy
            ]):
                self.cords = [i, j - 1]

        while tuple(self.cords) in self.en_board.dots_busy:
            self.cords = self.random_cord

        print(f'{BColors.OKCYAN}'
              f'Ход компьютера: {chr(self.cords[0] + 64)}{self.cords[1]}'
              f'{BColors.ENDC}'
              )
        return tuple(self.cords)

    @property
    def random_cord(self):
        return [randint(1, self.my_board.board_size),
                randint(1, self.my_board.board_size)]


class User(Player):
    @property
    def ask(self):
        while True:
            cords_inp = input(f'{BColors.OKCYAN}Ваш ход: {BColors.ENDC}')

            if len(cords_inp) != 2:
                print(f'{BColors.FAIL}'
                      f'Первый символ координат - латинская буква '
                      f'от "{chr(65)}" до '
                      f'"{chr(64 + self.my_board.board_size)}" '
                      f'в любом регистре\n'
                      f'Второй символ координат - число от 1 до '
                      f'{self.my_board.board_size}'
                      f'{BColors.ENDC}'
                      )
                continue

            if not any(
                    [65 <= ord(cords_inp[0]) < 65 + self.my_board.board_size,
                     97 <= ord(cords_inp[0]) < 97 + self.my_board.board_size]
            ):
                print(f'{BColors.FAIL}'
                      f'Первый символ - латинская буква '
                      f'от "{chr(65)}" до '
                      f'"{chr(64 + self.my_board.board_size)}" '
                      f'в любом регистре'
                      f'{BColors.ENDC}'
                      )
                continue

            if not 49 <= ord(cords_inp[1]) <= 49 + self.my_board.board_size:
                print(f'{BColors.FAIL}'
                      f'Второй символ должен быть числом от 1 до '
                      f'{self.my_board.board_size}'
                      f'{BColors.ENDC}'
                      )
                continue
            cords = ord(cords_inp[0].upper()) - 64, int(cords_inp[1])
            return cords


class Game:
    def __init__(self, bsize=6):

        if any([bsize < 6, bsize > 9]):
            self.size = 6
            self.ship_lens = [3, 3, 2, 2, 1, 1, 1]
            self.count_range = 7
        else:
            self.size = bsize
            if self.size == 6:
                self.ship_lens = [3, 3, 2, 2, 1, 1, 1]
                self.count_range = 7
            elif self.size == 7:
                self.ship_lens = [3, 3, 2, 2, 2, 1, 1, 1]
                self.count_range = 8
            elif self.size == 8:
                self.ship_lens = [3, 3, 3, 2, 2, 2, 1, 1, 1]
                self.count_range = 9
            elif self.size == 9:
                self.ship_lens = [4, 3, 3, 3, 2, 2, 2, 1, 1, 1]
                self.count_range = 10

        player = self.random_board
        computer = self.random_board
        computer.hidden = True

        self.ai = AI(computer, player)
        self.us = User(player, computer)

    @property
    def try_board(self):
        board = Board(size=self.size)
        attempts = 0
        for len_ship in self.ship_lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(
                    len_ship,
                    (randint(1, self.size), (randint(1, self.size))),
                    randint(0, 1),
                    len_ship
                )
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.init_game()
        return board

    @property
    def random_board(self):
        board = None
        while board is None:
            board = self.try_board
        return board

    def print_boards(self, hidden):
        result = f'\n{BColors.OKGREEN}' \
                 f'   Игрок:\t\t\t\t\t   Компьютер:' \
                 f'{BColors.ENDC}'
        for i in range(self.size + 1):
            result += '\n'
            for j in range(self.size + 1):
                result += self.us.my_board.board[i][j] + '  '
            result += '\t|\t'
            for k in range(self.size + 1):
                if hidden:
                    comp_board = np.where(
                        self.ai.my_board.board == self.ai.my_board.ship_img,
                        self.ai.my_board.wave_img,
                        self.ai.my_board.board
                    )
                    result += comp_board[i][k] + '  '
                else:
                    result += self.ai.my_board.board[i][k] + '  '
        print(result)

    @staticmethod
    def greet():
        example = f'{BColors.OKGREEN}"A1"{BColors.ENDC}' \
                  f'{BColors.OKCYAN} или {BColors.ENDC}' \
                  f'{BColors.OKGREEN}"e4"{BColors.ENDC}' \
                  f'{BColors.OKCYAN}'
        print(f'''{BColors.OKCYAN}
*****************************************************
*   Привет! Добро пожаловать в игру "Морской бой"   *
*****************************************************
*                 На экране два поля:               *
*           одно Ваше, за второе играет ИИ          *
*****************************************************
*               Правила ввода хода:                 *
*                                                   *
*         Первый символ - латинская буква в         *
*    пределах игрового поля (регистр не важен)      *
*                                                   *
*         Второй символ - арабская цифра в          *
*              пределах игрового поля               *
*                                                   *
*              Например {example}               *
*****************************************************
*   На поле отмечено:                               *
*   {Board.ship_img}{BColors.OKCYAN} - собственно, сам корабль\t\t\t\t\t\t*
*   {Board.damage_img}{BColors.OKCYAN} - повреждение корабля\t\t\t\t\t\t\t*
*   {Board.shoot_img}{BColors.OKCYAN} - клетка, куда был сделан выстрел\t\t\t\t*
*   {Board.contour_img}{BColors.OKCYAN} - свободный контур корабля\t\t\t\t\t*
*****************************************************      
        {BColors.ENDC}''')

    def begin_game(self):
        self.greet()
        num = 0
        while True:
            self.print_boards(hidden=True)

            if num % 2:
                print(f'{BColors.WARNING}Ход игрока...{BColors.ENDC}')
                repeat = self.us.move
            else:
                print(f'{BColors.WARNING}Ход компьютера...{BColors.ENDC}')
                repeat = self.ai.move
            if repeat:
                num -= 1

            if self.ai.my_board.count == self.count_range:
                self.print_boards(hidden=False)
                print(f'{BColors.OKGREEN}Победил игрок!{BColors.ENDC}')
                break

            if self.us.my_board.count == self.count_range:
                self.print_boards(hidden=False)
                print(f'{BColors.FAIL}Победил компьютер!{BColors.ENDC}')
                break
            num += 1


if __name__ == '__main__':
    game = Game()
    game.begin_game()
