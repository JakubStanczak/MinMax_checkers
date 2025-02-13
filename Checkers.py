import pygame
from copy import deepcopy
from itertools import chain

pygame.init()
standard_font = pygame.font.SysFont("calibri", 20, bold=True)

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
    global legal_dir
    if player_plays_black is None:
        for x in range(board_width):
            column = []
            for y in range(board_height):
                column.append(Square(x, y, True if (x + y) % 2 == 1 else False))
            board.append(column)

        board[2][1].piece = Piece(False)
        board[4][1].piece = Piece(True)
        board[3][1].selected = True
    else:
        for sq in chain.from_iterable(board):
            sq.piece = None
        legal_dir = {player_plays_black: 1, not player_plays_black: -1}
        clean_sel_high()
        for x in range(8):
            for y in range(3):
                if board[x][y].black:
                    board[x][y].piece = Piece(not player_plays_black)
            for y in range(5, 8):
                if board[x][y].black:
                    board[x][y].piece = Piece(player_plays_black)


def draw(board, blacks_turn):
    win.fill((255, 255, 255))
    for sq in chain.from_iterable(board):
        sq.draw()
    if against_player:
        if player_plays_black is None:
            text = "Pic your color"
        else:
            if black_won is None:
                if blacks_turn == player_plays_black:
                    text = "it's your turn".format(max_minmax_depth)
                else:
                    text = "it's mine turn, i'm planing {} moves ahead now".format(max_minmax_depth)
            elif black_won == player_plays_black:
                text = "You are the winner"
            else:
                text = "You lost. Nothing can stop this AI now"
    else:
        text = "Black {} White {}, score {}, turn num {}".format(max_dept_AI_when_fighting[0], max_dept_AI_when_fighting[1], str(fight_score), turn_num)

    rendered_text = standard_font.render(text, True, (0, 0, 0))
    win.blit(rendered_text, (2, 10))
    pygame.display.update()

def select_color(x, y):
    global player_plays_black
    global against_player
    if y < offset:
        return
    x = x // Square.dim
    y = y // Square.dim - offset // Square.dim
    if board[x][y].piece is not None:
        player_plays_black = board[x][y].piece.black
        init()
    elif board[x][y].selected:
        player_plays_black = False
        against_player = False
        init()

def select_sq(x, y):
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
            if current_board[x][0].piece.black == player_plays_black:
                current_board[x][0].piece.king = True
        if current_board[x][board_height - 1].piece is not None:
            if current_board[x][board_height - 1].piece.black != player_plays_black:
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
    if turn_num > 100:
        score = evaluate_board(current_board)
        if score < 0:
            return False
        else:
            return True


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

legal_dir = {}
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

def how_many_left(current_board):
    num = 0
    for sq in chain.from_iterable(current_board):
        if sq.piece:
            num += 1
    return num

def minmax(board_this_turn, blacks_turn, depth, a, b):
    if depth >= max_minmax_depth:
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
            # print("legal moves for {} in depth {} are {}".format(s_pos, depth, legal_moves))
            for e_pos in legal_moves:
                # print("lets try {}".format(e_pos))
                board_next_turn = deepcopy(board_this_turn)
                n_turn = move_piece(board_next_turn, blacks_turn, board_next_turn[s_pos.x][s_pos.y], board_next_turn[e_pos.x][e_pos.y])
                # draw(board_next_turn, blacks_turn, depth)
                # pygame.time.delay(200)
                pygame.event.pump()
                next_turn = not blacks_turn if n_turn else blacks_turn
                # print("IT IS TIME FOR NEXT TURN {} so now it is blacks turn {}".format(n_turn, next_turn))
                mark_must_capture(board_next_turn, next_turn)
                check_if_king(board_next_turn)
                score = [board_next_turn[s_pos.x][s_pos.y], board_next_turn[e_pos.x][e_pos.y], minmax(board_next_turn, next_turn, depth+1, a, b)[2]]
                if blacks_turn == black_maximizing:
                    if score[2] > best_score[2]:
                        best_score = score
                        a = max(score[2], a)
                        if best_score[2] > b or check_if_must_capture(board_this_turn, blacks_turn):
                            # print("PRUNING max")
                            return best_score

                else:
                    if score[2] < best_score[2]:
                        best_score = score
                        b = min(score[2], a)
                        if best_score[2] < a or check_if_must_capture(board_this_turn, blacks_turn):
                            # print("PRUNING min")
                            return best_score

        return best_score


# when AI against AI
max_dept_AI_when_fighting = [2, 3]  # black, white
num_of_fights = 20
fight_score = [0, 0]  # black, white
fight_num = 0
turn_num = 0

max_minmax_depth = 2
player_plays_black = None
init()
black_turn = False
run = True
black_won = None
black_maximizing = True
against_player = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN and against_player:  # and black_turn:
            mouse_pos = pygame.mouse.get_pos()
            if player_plays_black == black_turn:
                select_sq(*mouse_pos)

                pieces_left = how_many_left(board)
                if pieces_left > 20:
                    max_minmax_depth = 2
                elif pieces_left > 14:
                    max_minmax_depth = 3
                else:
                    max_minmax_depth = 4
                # max_minmax_depth = 2 if how_many_left(board) > 18 else 3

            elif player_plays_black is None:
                select_color(*mouse_pos)

    draw(board, black_turn)

    if player_plays_black is not None:
        mark_must_capture(board, black_turn)
        check_if_king(board)
        black_won = check_if_end(board)
        draw(board, black_turn)

        if (black_turn != player_plays_black or not against_player) and black_won is None:
            if not against_player:
                max_minmax_depth = max_dept_AI_when_fighting[0] if black_turn else max_dept_AI_when_fighting[1]
                turn_num += 1
            board_this_turn = deepcopy(board)
            start_pos, end_pos, score = minmax(board_this_turn, black_turn, 0, -float("inf"), float("inf"))
            print("score of this move is {}".format(score))
            print(start_pos)
            print(end_pos)
            print("the move is {} to {}".format(board[start_pos.x][start_pos.y], board[end_pos.x][end_pos.y]))
            n_turn = move_piece(board, black_turn, board[start_pos.x][start_pos.y], board[end_pos.x][end_pos.y])
            # pygame.time.delay(500)
            if n_turn:
                black_turn = not black_turn

    if not against_player and black_won is not None:
        if black_won:
            fight_score[0] += 1
        else:
            fight_score[1] += 1
        if fight_num < num_of_fights:
            fight_num += 1
            turn_num = 0
            black_won = None
            init()