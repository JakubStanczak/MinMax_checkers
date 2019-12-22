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


def draw(board, blacks_turn, depth=0):
    win.fill((255, 255, 255))
    for sq in chain.from_iterable(board):
        sq.draw()

    if black_won is None:
        if blacks_turn:
            text = "it's blacks turn   depth - {}".format(depth)
        else:
            text = "it's whites turn   depth - {}".format(depth)
    else:
        text = "{}'s the winner".format(black_won)
    rendered_text = standard_font.render(text, True, (0, 0, 0))
    win.blit(rendered_text, (20, 5))
    pygame.display.update()


def select_sq(x, y, turn):
    n_turn = False
    global black_turn
    if y < offset:
        return
    x = x // Square.dim
    y = y // Square.dim - offset // Square.dim
    print("You selected {}".format(board[x][y]))
    if board[x][y].selected:
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
        board[x][y].selected = True
        highlight_legal_moves(board[x][y])
        return
    else:
        clean_sel_high()
        if start_pos is not None and if_move_legal(board, black_turn, start_pos, board[x][y])[0]:
            n_turn = move_piece(board, black_turn, start_pos, board[x][y])

    if n_turn:
        black_turn = not black_turn


def clean_sel_high():
    for sq in chain.from_iterable(board):
        sq.selected = False
        sq.highlighted = False


def highlight_legal_moves(start_pos):
    for sq in chain.from_iterable(board):
        if if_move_legal(board, black_turn, start_pos, sq)[0]:
            sq.highlighted = True


def mark_must_capture(current_board, blacks_turn):
    for sq_s in chain.from_iterable(current_board):
        if sq_s.piece is not None:
            sq_s.piece.must_capture = False
            for sq_e in chain.from_iterable(current_board):
                if if_move_legal(current_board, blacks_turn, sq_s, sq_e)[1]:
                    sq_s.piece.must_capture = True


def return_legal_moves(current_board, blacks_turn, start_pos):
    legal_moves = []
    for sq in chain.from_iterable(current_board):
        if if_move_legal(current_board, blacks_turn, start_pos, sq)[0]:
            legal_moves.append(sq)
    return legal_moves


def check_if_king(current_board):
    for x in range(board_width):
        if current_board[x][0].piece is not None:
            if current_board[x][0].piece.black:
                current_board[x][0].piece.king = True
        if current_board[x][board_height - 1].piece is not None:
            if not current_board[x][board_height - 1].piece.black:
                current_board[x][board_height - 1].piece.king = True


def check_if_end(current_board):
    white_count = 0
    black_count = 0
    for sq in chain.from_iterable(current_board):
        if sq.piece is not None:
            if len(return_legal_moves(current_board, sq.piece.black, sq)) > 0:
                if sq.piece.black:
                    black_count += 1
                if not sq.piece.black:
                    white_count += 1
    if white_count == 0:
        return True
    if black_count == 0:
        return False


def check_if_must_capture(current_board, blacks_turn):
    must_capture = False
    for sq in chain.from_iterable(current_board):
        if sq.piece is not None:
            if sq.piece.must_capture and sq.piece.black == blacks_turn:
                must_capture = True
    return must_capture


def move_piece(current_board, blacks_turn, start_pos, end_pos):
    # print(start_pos)
    # print(end_pos)

    capture = False if abs(start_pos.x - end_pos.x) == 1 else True

    if not capture:
        # print("move function will move {} to {}".format(start_pos, end_pos))
        end_pos.piece = start_pos.piece
        start_pos.piece = None
        n_turn = next_turn(current_board, blacks_turn, end_pos, False)
    else:
        # print("move function will capture moving {} to {}".format(start_pos, end_pos))
        end_pos.piece = start_pos.piece
        start_pos.piece = None
        current_board[(start_pos.x + end_pos.x) // 2][(start_pos.y + end_pos.y) // 2].piece = None
        n_turn = next_turn(current_board, blacks_turn, end_pos, True)
    return n_turn


def next_turn(current_board, blacks_turn, end_pos, capture):
    mark_must_capture(current_board, blacks_turn)
    n_turn = False
    if not capture:
        n_turn = True
    else:
        mark_must_capture(current_board, blacks_turn)
        if not end_pos.piece.must_capture:
            n_turn = True
    return n_turn

legal_dir = {True: 1, False: -1}
def if_move_legal(current_board, blacks_turn, start_pos, end_pos):  # returns ifLegal, ifCapture
    must_capture = check_if_must_capture(current_board, blacks_turn)
    if end_pos.piece is None and start_pos.piece is not None:
        if start_pos.piece.black == blacks_turn:
            # move
            if not must_capture:
                if not start_pos.piece.king:
                    if start_pos.y - end_pos.y == legal_dir[start_pos.piece.black] and abs(end_pos.x - start_pos.x) == 1:
                        return True, False
                else:
                    if abs(start_pos.y - end_pos.y) == 1 and abs(end_pos.x - start_pos.x) == 1:
                        return True, False
            # capture
            if abs(start_pos.y - end_pos.y) == 2 and abs(end_pos.x - start_pos.x) == 2:
                between_pos = current_board[(start_pos.x + end_pos.x)//2][(start_pos.y + end_pos.y)//2]
                if between_pos.piece is not None:
                    if between_pos.piece.black != start_pos.piece.black:
                        return True, True
    return False, False


def evaluate_board(current_board):
    score = 0
    for sq in chain.from_iterable(current_board):
        if sq.piece is not None:
            if sq.piece.black == black_maximizing:
                if sq.piece.king:
                    score += 2
                else:
                    score += 1
            else:
                if sq.piece.king:
                    score -= 2
                else:
                    score -= 1
    return score


def deep_copy_board(board_this_turn):
    board_next_turn = []
    for column in board_this_turn:
        column_next = []
        for sq in column:
            column_next.append(deepcopy(sq))
        board_next_turn.append(column_next)
    return board_next_turn


def minmax(board_this_turn, blacks_turn, depth, a, b):
    if depth >= max_minmax_depth or check_if_end(board_this_turn) is not None:
        return None, None, evaluate_board(board_this_turn)
    else:
        possible_moves = []
        for start_pos in chain.from_iterable(board_this_turn):
            if start_pos.piece is not None:
                possible_moves.append([start_pos, return_legal_moves(board_this_turn, blacks_turn, start_pos)])
        if blacks_turn == black_maximizing:
            best_score = [None, None, -float("inf")]
        else:
            best_score = [None, None, float("inf")]
        for s_pos, legal_moves in possible_moves:
            print("legal moves for {} in depth {} are {}".format(s_pos, depth, legal_moves))
            for e_pos in legal_moves:
                # print("lets try {}".format(e_pos))
                board_next_turn = deepcopy(board_this_turn)
                n_turn = move_piece(board_next_turn, blacks_turn, board_next_turn[s_pos.x][s_pos.y], board_next_turn[e_pos.x][e_pos.y])
                draw(board_next_turn, blacks_turn, depth)
                # pygame.time.delay(200)
                pygame.event.pump()
                next_turn = not blacks_turn if n_turn else blacks_turn

                print("IT IS TIME FOR NEXT TURN {} so now it is blacks turn {}".format(n_turn, next_turn))
                mark_must_capture(board_next_turn, next_turn)
                check_if_king(board_next_turn)
                score = [board_next_turn[s_pos.x][s_pos.y], board_next_turn[e_pos.x][e_pos.y], minmax(board_next_turn, next_turn, depth+1, a, b)[2]]
                if blacks_turn == black_maximizing:
                    if score[2] > best_score[2]:
                        best_score = score
                    a = max(score[2], a)
                    if a <= b:
                        print("PRUNING b")
                        return best_score
                else:
                    if score[2] < best_score[2]:
                        best_score = score
                    b = min(score[2], b)
                    if a >= b:
                        print("PRUNING a")
                        return best_score

        return best_score


max_minmax_depth = 6
init()
black_turn = False
run = True
black_won = None
black_maximizing = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN: # and black_turn:
            mouse_pos = pygame.mouse.get_pos()
            select_sq(*mouse_pos, black_turn)

    mark_must_capture(board, black_turn)
    check_if_king(board)
    black_won = check_if_end(board)
    draw(board, black_turn)

    if not black_turn and black_won is None:
        board_this_turn = deepcopy(board)
        start_pos, end_pos, score = minmax(board_this_turn, black_turn, 0, -float("inf"), float("inf"))
        print("score of this move is {}".format(score))
        print("the move is {} to {}".format(board[start_pos.x][start_pos.y], board[end_pos.x][end_pos.y]))
        n_turn = move_piece(board, black_turn, board[start_pos.x][start_pos.y], board[end_pos.x][end_pos.y])
        if n_turn:
            black_turn = not black_turn

    mark_must_capture(board, black_turn)
    check_if_king(board)
    black_won = check_if_end(board)
    draw(board, black_turn)

