import pygame
from copy import deepcopy
from itertools import chain

pygame.init()
standard_font = pygame.font.SysFont("calibri", 20, bold=True)

debug_mode = True

class Square:
    dim = 50
    def __init__(self, x, y, black):
        self.x = x
        self.y = y
        self.black = black
        self.selected = False
        self.highlighted = False
        self.piece = None

    def draw(self):
        if self.selected:
            color = (0, 100, 0)
        elif self.highlighted:
            color = (0, 200, 0)
        elif self.black:
            color = (96, 96, 96)
        else:
            color = (255, 255, 255)
        if self.piece is not None and not self.selected:
            if self.piece.must_capture:
                color = (255, 0, 0)
        pygame.draw.rect(win, color, (self.x * self.dim, self.y * self.dim + offset, self.dim , self.dim))
        if self.piece is not None:
            self.piece.draw(self.x, self.y)

    def __repr__(self):
        return "{} {} {}".format(self.x, self.y, self.piece)

class Piece:
    rad = 20

    def __init__(self, black):
        self.black = black
        self.must_capture = False
        self.streak = False
        self.king = False

    def draw(self, x, y):
        color = (0, 0, 0) if self.black else (224, 224, 224)
        pygame.draw.circle(win, color, (x * Square.dim + Square.dim // 2, y * Square.dim + Square.dim // 2 + offset), self.rad)
        if self.king:
            color = (224, 224, 224) if self.black else (0, 0, 0)
        pygame.draw.circle(win, color, (x * Square.dim + Square.dim // 2, y * Square.dim + Square.dim // 2 + offset), self.rad // 2)

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

    for x in range(8):
        for y in range(3):
            if board[x][y].black:
                board[x][y].piece = Piece(False)
        for y in range(5, 8):
            if board[x][y].black:
                board[x][y].piece = Piece(True)


def draw():
    win.fill((255, 255, 255))
    for sq in chain.from_iterable(board):
        sq.draw()

    if winner is None:
        if black_turn:
            text = "it's blacks turn"
        else:
            text = "it's whites turn"
    else:
        text = "{}'s the winner".format(winner)
    rendered_text = standard_font.render(text, True, (0, 0, 0))
    win.blit(rendered_text, (20, 5))
    pygame.display.update()


def select_sq(x, y, turn):
    must_capture = False
    for sq in chain.from_iterable(board):
        if sq.piece is not None:
            if sq.piece.must_capture and sq.piece.black == turn:
                must_capture = True
    print("turn: {} must capture:{}".format(turn, must_capture))
    if y < offset:
        return
    x = x // Square.dim
    y = y // Square.dim - offset // Square.dim
    print("{} {}".format(x, y))
    if board[x][y].selected:
        board[x][y].selected = False
        clean_sel_high()
        return

    # how many were selected previously
    num_selected = 0
    start_pos = None
    for sq in chain.from_iterable(board):
        if sq.selected:
            num_selected += 1
            start_pos = sq

    if num_selected == 0 and board[x][y].piece is not None:
        if board[x][y].piece.black == turn:
            if not must_capture or (must_capture and board[x][y].piece.must_capture):
                board[x][y].selected = True
                highlight_legal_moves(board[x][y])
                return
    else:
        clean_sel_high()
        if start_pos is not None:
            move_piece(start_pos, board[x][y],)


def clean_sel_high():
    for sq in chain.from_iterable(board):
        sq.selected = False
        sq.highlighted = False


def highlight_legal_moves(start_pos):
    for sq in chain.from_iterable(board):
        if if_move_legal(start_pos, sq)[0]:
            sq.highlighted = True

def return_legal_moves(start_pos):
    legal_moves = []
    for sq in chain.from_iterable(board):
        if if_move_legal(start_pos, sq)[0]:
            legal_moves.append(sq)
    return legal_moves

def check_if_must_capture():
    for sq_s in chain.from_iterable(board):
        if sq_s.piece is not None:
            sq_s.piece.must_capture = False
            for sq_e in chain.from_iterable(board):
                if if_move_legal(sq_s, sq_e)[1]:
                    sq_s.piece.must_capture = True


def check_if_king():
    for x in range(board_width):
        if board[x][0].piece is not None:
            if board[x][0].piece.black:
                board[x][0].piece.king = True
        if board[x][board_height - 1].piece is not None:
            if not board[x][board_height - 1].piece.black:
                board[x][board_height - 1].piece.king = True

def check_if_end():
    white_count = 0
    black_count = 0
    for sq in chain.from_iterable(board):
        if sq.piece is not None:
            if len(return_legal_moves(sq)) > 0:
                if sq.piece.black:
                    black_count += 1
                if not sq.piece.black:
                    white_count += 1
    global winner
    if white_count == 0:
        winner = "Black"
    if black_count == 0:
        winner = "White"



def move_piece(start_pos, end_pos):
    print(start_pos)
    print(end_pos)
    if_legal, if_capture = if_move_legal(start_pos, end_pos)
    if not if_legal:
        return
    if not if_capture:
        print("move")
        end_pos.piece = start_pos.piece
        start_pos.piece = None
        next_turn(end_pos, False)
    if if_capture:
        print("capture")
        end_pos.piece = start_pos.piece
        start_pos.piece = None
        board[(start_pos.x + end_pos.x) // 2][(start_pos.y + end_pos.y) // 2].piece = None
        next_turn(end_pos, True)


def next_turn(end_pos, capture):
    global black_turn
    if not capture:
        black_turn = not black_turn
    if capture:
        check_if_must_capture()
        if not end_pos.piece.must_capture:
            black_turn = not black_turn




legal_dir = {True: 1, False: -1}
def if_move_legal(start_pos, end_pos):  # returns ifLegal, ifCapture
    if end_pos.piece is None:
        # move
        if not start_pos.piece.must_capture:
            if not start_pos.piece.king:
                if start_pos.y - end_pos.y == legal_dir[start_pos.piece.black] and abs(end_pos.x - start_pos.x) == 1:
                    return True, False
            else:
                if abs(start_pos.y - end_pos.y) == 1 and abs(end_pos.x - start_pos.x) == 1:
                    return True, False
        # capture
        if abs(start_pos.y - end_pos.y) == 2 and abs(end_pos.x - start_pos.x) == 2:
            between_pos = board[(start_pos.x + end_pos.x)//2][(start_pos.y + end_pos.y)//2]
            if between_pos.piece is not None:
                if between_pos.piece.black != start_pos.piece.black:
                    return True, True
    return False, False


init()
black_turn = True
run = True
winner = None
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            select_sq(*mouse_pos, black_turn)

    check_if_must_capture()
    check_if_king()
    check_if_end()
    draw()




