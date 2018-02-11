import copy
import math
import time
import random

# TODO: Reimplement this class using collections.Counters and not lists
class Polynomial:
    def __init__(self, coefs):
        self.coefs = coefs

    def __repr__(self):
        prnt_str = ""
        for deg, coef in enumerate(self.coefs):
            if coef > 0 and deg != 0:
                prnt_str += " + " + str(coef) + "*x^" + str(deg)
            elif coef > 0 and deg == 0:
                prnt_str += str(coef) + "*x^" + str(deg)
            elif coef < 0:
                prnt_str += " - " + str(-coef) + "*x^" + str(deg)
        if prnt_str != "" and (prnt_str[1] == '+' or prnt_str[1] == '1'):
            prnt_str = prnt_str[3:]
        return prnt_str

    def __add__(self, other):
        poly = Polynomial([])
        if len(other.coefs) > len(self.coefs):
            for i in range(len(other.coefs)):
                if i < len(self.coefs):
                    poly.coefs.append(self.coefs[i] + other.coefs[i])
                else:
                    poly.coefs.append(other.coefs[i])
        else:
            for i in range(len(self.coefs)):
                if i < len(other.coefs):
                    poly.coefs.append(self.coefs[i] + other.coefs[i])
                else:
                    poly.coefs.append(self.coefs[i])

        return poly

    def __sub__(self, other):
        poly = Polynomial([])
        for i in range(len(other.coefs)):
            if i < len(self.coefs):
                poly.coefs.append(self.coefs[i] - other.coefs[i])
            else:
                poly.coefs.append(0 - other.coefs[i])
        return poly

    def __mul__(self, other):
        poly = Polynomial([0] * (len(self.coefs) + len(other.coefs) - 1))  # Length is sum of highest degree + 1
        for deg1, coef1 in enumerate(self.coefs):
            for deg2, coef2 in enumerate(other.coefs):
                # Multiplies coefficients and places them in the index related to
                # the sum of the degrees of x
                poly.coefs[deg1 + deg2] += coef1 * coef2
        return poly

    def __len__(self):
        return len(self.coefs)

    def degree(self):
        poly = self.coefs[:]
        while poly[-1] == 0:
            poly.pop()
        return len(poly) - 1

    def latexFormat(self):
        """
        :return: LaTex formatted polynomial string
        """
        prnt_str = r"$"
        terms = []
        for deg, coef in enumerate(self.coefs):
            terms.append(str(coef) + "x^{" + str(deg) + '}')
        prnt_str += '+'.join(terms) + '$'
        return prnt_str


class Board:
    POLYNOMIAL_CACHE = {}

    def __init__(self, h, w, bad_sqrs):
        self.height = h
        self.width = w
        self.board = [(2**w-1) for i in range(h)]
        # Represent binary array as array of ints
        for i in range(h):
            for j in range(w):
                if (i, j) in bad_sqrs:
                    self.board[i] ^= 1 << w - (j + 1)

    def __repr__(self):
        rows = []
        for row in self.board:
            sqrs = []
            for i in range(self.width):
                sqr = str(row & 1)
                row >>= 1
                sqrs.append(sqr)
            rows.append(" ".join(sqrs[::-1]))
        return "\n".join(rows)

    def __is_single_cell(self):
        rows = set(self.board)
        if len(rows) == 2 and 0 in rows:  # should be zero and a power of two
            for val in rows:
                if val and self.board.count(val) > 1:
                    return False
                if val != (val & -val):
                    return False
            return True
        return False

    def __find_rect(self):
        rows = self.board
        row_vals = set(rows) - {0}
        if len(row_vals) == 1:
            val = next(iter(row_vals))
            if self.__is_block(val):
                x = self.__find_msb(val) - self.__find_lsb(val) + 1
                first = rows.index(val)
                last = len(rows) - rows[::-1].index(val)
                if len(set(rows[first:last])) == 1:
                    y = last - first
                    return True, x, y
        return False, None, None

    def __is_empty(self):
        rows = set(self.board)
        if rows == {0}:
            return True
        return False

    def __build_B_i_and_B_e(self):
        B_i = Board(self.height, self.width, {})
        B_i.board = copy.deepcopy(self.board)
        B_e = Board(self.height, self.width, {})
        B_e.board = copy.deepcopy(self.board)
        for i in range(B_i.height):
            if B_i.board[i]:
                msb = B_i.__find_msb(B_i.board[i])
                B_e.board[i] &= ~(1 << (msb - 1))  # Delete cell
                B_i.board[i] = 0  # Delete the row
                for j in range(i, B_i.height):
                    B_i.board[j] &= ~(1 << (msb - 1))  # Delete the column
                return B_i, B_e

    def __binomial(self, n, k):
        if n > 0:
            return int(math.factorial(n) / (math.factorial(k) * math.factorial(n - k)))
        elif n == 0:
            return 0
        elif n < 0:
            return None

    def __rect_frp(self, x, y):
        poly = Polynomial([])
        for k in range(min(x,y) + 1):
            poly.coefs.append(self.__binomial(x, k) * self.__binomial(y, k) * math.factorial(k))
        return poly

    def __number_of_set_bits(self, n):
        """
        Taken from:
        https://graphics.stanford.edu/~seander/bithacks.html#CountBitsSet64
        """
        c = ((n & 0xfff) * 0x1001001001001 & 0x84210842108421) % 0x1f
        c += (((n & 0xfff000) >> 12) * 0x1001001001001 & 0x84210842108421) %0x1f
        c += ((n >> 24) * 0x1001001001001 & 0x84210842108421) % 0x1f
        return c

    def __find_msb(self, n):
        """
        Taken from:
        https://graphics.stanford.edu/~seander/bithacks.html#CountBitsSet64
        """
        if n == 0:
            return 0

        b = [0x2, 0xC, 0xF0, 0xFF00, 0xFFFF0000]
        S = [1, 2, 4, 8, 16]
        r = 0
        for i in range(4, -1, -1):
            if n & b[i]:
                n >>= S[i]
                r |= S[i]
        return r + 1

    def __find_lsb(self, n):
        return self.__find_msb(n & ~(n-1))

    def __is_block(self, n):
        x_1 = self.__find_msb(n)
        x_2 = self.__find_lsb(n)
        cnt = self.__number_of_set_bits(n)
        return (cnt - 1) == (x_1 - x_2)

    def solve(self):
        is_rect, x, y = self.__find_rect()
        if tuple(self.board) in self.POLYNOMIAL_CACHE:
            return self.POLYNOMIAL_CACHE[tuple(self.board)]
        elif self.__is_empty():
            return Polynomial([1])
        elif self.__is_single_cell():
            return Polynomial([1, 1])
        elif is_rect:
            R_of_B = self.__rect_frp(x,y)
            self.POLYNOMIAL_CACHE[tuple(self.board)] = R_of_B
            return R_of_B
        else:
            B_i, B_e = self.__build_B_i_and_B_e()
            R_of_B = B_e.solve() + (B_i.solve() * Polynomial([0, 1]))
            self.POLYNOMIAL_CACHE[tuple(self.board)] = R_of_B
            return R_of_B

    def disp_random_config(self, num_rooks):
        # Displays a random valid configuration of rooks
        board = copy.deepcopy(self.board)
        cords = set()
        rooks = set()
        cnt = 0
        num = 0
        for i in range(self.height):
            for j in range(self.width):
                if board[i] & (1 << (self.width - 1 - j)):
                    cords.add((i, j))
        # find a valid configuration using num_rooks
        while num < num_rooks and cnt < 1000:
            num = 0
            tmp_cords = copy.deepcopy(cords)
            rooks = set()
            cnt += 1
            while len(tmp_cords) > 0 and cnt < num_rooks:
                chosen = random.sample(tmp_cords, 1)[0]
                tmp_cords.remove(chosen)
                rooks.add(chosen)
                num += 1
                board[chosen[0]] = 0  # Delete row in board
                for i in range(self.height):
                    if (i, chosen[1]) in tmp_cords:
                        tmp_cords.remove((i, chosen[1]))
                    for j in range(self.width):
                        if (chosen[0], j) in tmp_cords:
                            tmp_cords.remove((chosen[0], j))
                        board[j] &= ~(1 << j)  # Delete the column
        return rooks

def main():
    # hw = input(
    #     "Input height and width of board separated by a comma and hit enter: ")
    # h = int(hw[:hw.index(',')])
    # w = int(hw[hw.index(',') + 1:])
    # b = set(input("Input space separated tuples of forbidden squares and hit "
    #               "enter. Leave blank for full board. i.e 0,1 1,0 2,5...: "
    #               ).strip(" ").split(' '))
    # bad = set()
    # print(b)
    # if b != {''}:
    #     for elem in b:
    #         bad.add((int(elem[0]), int(elem[2])))
    # print("\nheight: ", h)
    # print("width: ", w)
    # print("forbidden squares: ", bad)
    # brd = Board(h, w, bad)
    # print("\nboard:")
    # print(brd)
    # start = time.time()
    # print("rook polynomial: ", brd.solve())
    # print("run time: ", round(time.time() - start, 3), "seconds")
    # board = Board(4, 4, {(3,3), (2,2), (1,1), (0,0)})
    # print(board)
    # print(board.solve())
    # board.disp_random_config(4)
    p1 = Polynomial([1, 1, 1])
    p2 = Polynomial([1, 1])
    print(p1 + p2)

if __name__ == "__main__":
    main()




