import pygame
from copy import deepcopy
from itertools import chain

pygame.init()
num_font = pygame.font.SysFont("calibri", 20, bold=True)
mark_font = pygame.font.SysFont("calibri", 70, bold=True)

debug_mode = True

class Square:
    dim = 50
    def __init__(self, x, y, black):
        self.x = x
        self.y = y
        self.sq_black = black
        self.selected = False
        self.piece = None

    def draw(self):
        color_sq = (96, 96, 96) if self.sq_black else (255, 255, 255)
        color = (0, 100, 0) if self.selected else color_sq
        pygame.draw.rect(win, color, (self.x * self.dim, self.y * self.dim + offset, self.dim , self.dim))

    def __repr__(self):
        return "{} {} {}".format(self.x, self.y, self.piece)


class Piece:
    rad = 20

    def __init__(self, x, y, black):
        self.x = x
        self.y = y
        self.black = black
        self.queen = False

    def draw(self):
        color = (0, 0, 0) if self.black else (224, 224, 224)
        pygame.draw.circle(win, color, (self.x * Square.dim + Square.dim // 2, self.y * Square.dim + Square.dim // 2 + offset), self.rad)

    def __repr__(self):
        if self.black:
            return "Black piece"
        else:
            return "White piece"

board_width = 8
board_height = 8
offset = 50

screen_width = board_width * Square.dim
screen_height = board_height * Square.dim + offset
win = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Checkers by Kuba")

board = []
def init():
    for x in range(board_width):
        column = []
        for y in range(board_height):
            column.append(Square(x, y, True if (x + y) % 2 == 1 else False))
        board.append(column)

    # for x in range(8):
    #     for y in range(3):
    #         board[x][y].piece = Piece(x, y, False)
    #     for y in range(5, 8):
    #         board[x][y].piece = Piece(x, y, True)


def draw():
    win.fill((255, 255, 255))
    for sq in chain.from_iterable(board):
        sq.draw()
        if sq.piece is not None:
            sq.piece.draw()
    pygame.display.update()

def select_sq(x, y):
    print()
    print("square selected")
    if y < offset:
        return
    x = x // Square.dim
    y = y // Square.dim - offset // Square.dim
    print("{} {}".format(x, y))
    if board[x][y].selected:
        board[x][y].selected = False
        return

    num_selected = 0
    start_pos = None
    for sq in chain.from_iterable(board):
        if sq.selected:
            num_selected += 1
            start_pos = sq
    if num_selected == 0 and board[x][y].piece is not None:
        board[x][y].selected = True
        return
    else:
        for sq in chain.from_iterable(board):
            sq.selected = False
        move_piece(start_pos, board[x][y])


def move_piece(start_pos, end_pos):
    print(start_pos)
    print(end_pos)
    #  check if move is legal
    end_pos.piece = start_pos.piece
    start_pos.piece = None



init()
run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            select_sq(*mouse_pos)
    draw()




