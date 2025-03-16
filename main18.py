import random
import pygame as pg
import math

# Lesson 1: read the files
# Lesson 2: draw the board and scale the piece
# Lesson 3: reformat the classes for pieces
# Lesson 4: legal moves (1/3) rook, bishop, queen
# Lesson 5: legal moves (2/3) king, knight
# Lesson 6: legal moves (3/3) pawn
# Lesson 7: Mouse control states
# Lesson 8: End Game
# Lesson 9: Polymorphism
# Lesson 10: En Passant
# Lesson 11: Check, Moved, Castling
# Lesson 12: Promotion
# Lesson 13: Introduce Player and Monkey
# Lesson 14: Static Evaluation and clone
# Lesson 15: Think in More Steps (MiniMax)
# Lesson 16: Undo
# Lesson 17: Alpha/Beta Pruning (and fix infinity loop in castling)
# Lesson 18: Checkmate! and add Notation

GRID = 80
WIDTH, HEIGHT = 8 * GRID, 8 * GRID
RESOLUTION = WIDTH, HEIGHT


class PiecesImage:
    def __init__(self, image_filename, screen):
        self.piece_infos = (
            ('black', 'king'), ('black', 'queen'), ('black', 'bishop'), ('black', 'knight'),
            ('white', 'king'), ('white', 'queen'), ('black', 'rook'), ('black', 'pawn'),
            ('white', 'bishop'), ('white', 'knight'), ('white', 'rook'), ('white', 'pawn'))
        self.pieces_image = pg.image.load(image_filename).convert(screen)
        self.w, self.h = self.pieces_image.get_size()
        self.w //= 4
        self.h //= 3

    def get_image(self, color, role):
        idx = self.piece_infos.index((color, role))
        x = self.w * (idx % 4)
        y = self.h * (idx // 4)
        return self.pieces_image.subsurface((x, y), (self.w, self.h))


def apply_dx_dy(grid_pos, dxdy):
    return grid_pos[0] + dxdy[1], grid_pos[1] + dxdy[0]


class Piece:
    def __init__(self, image, color, grid_pos):
        self.image = pg.transform.scale(image, (GRID, GRID))
        self.color = color
        self.grid_pos = grid_pos
        self.moved = False

    def clone_params(self, piece):
        piece.moved = self.moved

    def value(self):
        return 0

    def draw(self, screen):
        screen.blit(self.image, (self.grid_pos[1] * GRID, self.grid_pos[0] * GRID))

    def trace_legal_moves(self, chess, grid_pos, dx, dy, cont):
        gp = apply_dx_dy(grid_pos, (dx, dy))
        if 0 <= gp[0] < 8 and 0 <= gp[1] < 8:
            side = chess.report(gp, self.color)
            if side == 'friend':
                return []
            elif side == 'opponent':
                return [gp]
            else:
                return [gp] + (self.trace_legal_moves(chess, gp, dx, dy, cont) if cont else [])
        else:
            return []

    def trace_orthogonal(self, chess, cont):
        return self.trace_legal_moves(chess, self.grid_pos, 0, -1, cont) + \
               self.trace_legal_moves(chess, self.grid_pos, 0, 1, cont) + \
               self.trace_legal_moves(chess, self.grid_pos, 1, 0, cont) + \
               self.trace_legal_moves(chess, self.grid_pos, -1, 0, cont)

    def trace_diagonal(self, chess, cont):
        return self.trace_legal_moves(chess, self.grid_pos, -1, -1, cont) + \
               self.trace_legal_moves(chess, self.grid_pos, 1, 1, cont) + \
               self.trace_legal_moves(chess, self.grid_pos, 1, -1, cont) + \
               self.trace_legal_moves(chess, self.grid_pos, -1, 1, cont)

    def get_legal_moves(self, chess, ignore_castile=False):
        print("not implemented")
        return []


class Rook(Piece):
    def clone(self):
        new = Rook(self.image, self.color, self.grid_pos)
        super().clone_params(new)
        return new

    def value(self):
        return 10

    def get_legal_moves(self, chess, ignore_castle=False):
        return self.trace_orthogonal(chess, True)


class Knight(Piece):
    def clone(self):
        new = Knight(self.image, self.color, self.grid_pos)
        super().clone_params(new)
        return new

    def value(self):
        return 2

    def get_legal_moves(self, chess, ignore_castle=False):
        moves = (
            (-1, -2), (1, -2),
            (-1, 2), (1, 2),
            (2, -1), (2, 1),
            (-2, -1), (-2, 1)
        )
        legal_moves = []
        for move in moves:
            gp = apply_dx_dy(self.grid_pos, move)
            side = chess.report(gp, self.color)
            if side == 'opponent' or side == 'none':
                legal_moves.append(gp)
        return legal_moves


class Bishop(Piece):
    def clone(self):
        new = Bishop(self.image, self.color, self.grid_pos)
        super().clone_params(new)
        return new

    def value(self):
        return 5

    def get_legal_moves(self, chess, ignore_castle=False):
        return self.trace_diagonal(chess, True)


class Queen(Piece):
    def clone(self):
        new = Queen(self.image, self.color, self.grid_pos)
        super().clone_params(new)
        return new

    def value(self):
        return 100

    def get_legal_moves(self, chess, ignore_castle=False):
        return self.trace_orthogonal(chess, True) + self.trace_diagonal(chess, True)


class King(Piece):
    def clone(self):
        new = King(self.image, self.color, self.grid_pos)
        super().clone_params(new)
        return new

    def value(self):
        return 10000

    def get_legal_moves(self, chess, ignore_castle=False):
        legal_moves = self.trace_orthogonal(chess, False) + self.trace_diagonal(chess, False)
        if not self.moved and not ignore_castle:
            for rook in filter(lambda x: isinstance(x, Rook) and x.color == self.color, chess.pieces):
                if not rook.moved:
                    xs = range(rook.grid_pos[1] + 1, self.grid_pos[1]) \
                        if rook.grid_pos[1] < self.grid_pos[1] else range(self.grid_pos[1] + 1, rook.grid_pos[1])
                    gps = map(lambda x: chess.report((self.grid_pos[0], x), self.color) == 'none', xs)
                    if all(gps):
                        ys = range(xs[0] - 1, xs[-1] + 1)
                        danger_zone = chess.get_danger_zone(self.color)
                        gs = map(lambda x: (self.grid_pos[0], x) in danger_zone, ys)
                        if not any(gs):
                            if rook.grid_pos[1] < self.grid_pos[1]:
                                column = self.grid_pos[1] - 2
                            else:
                                column = self.grid_pos[1] + 2
                            legal_moves.append((self.grid_pos[0], column))
        return legal_moves


class Pawn(Piece):
    def clone(self):
        new = Pawn(self.image, self.color, self.grid_pos)
        super().clone_params(new)
        return new

    def value(self):
        return 1

    def get_legal_moves(self, chess, ignore_castle=False):
        legal_moves = []
        dy = -1 if self.color == 'white' else 1
        # en passant capture?
        if chess.en_passant:
            if chess.en_passant[0] == self.grid_pos[0] and abs(chess.en_passant[1] - self.grid_pos[1]) == 1:
                legal_moves.append((self.grid_pos[0] + dy, chess.en_passant[1]))
        # capture?
        for dx in [-1, 1]:
            gp = apply_dx_dy(self.grid_pos, (dx, dy))
            side = chess.report(gp, self.color)
            if side == 'opponent':
                legal_moves.append(gp)
        # march 1?
        gp = apply_dx_dy(self.grid_pos, (0, dy))
        side = chess.report(gp, self.color)
        if side == 'none':
            legal_moves.append(gp)
            # march 2?
            if (self.color == 'black' and self.grid_pos[0] == 1) or \
                    (self.color == 'white' and self.grid_pos[0] == 6):
                dy = -2 if self.color == 'white' else 2
                gp = apply_dx_dy(self.grid_pos, (0, dy))
                side = chess.report(gp, self.color)
                if side == 'none':
                    legal_moves.append(gp)
        return legal_moves


def create_pieces(piece_images):
    return [
        Rook(piece_images.get_image('black', 'rook'), 'black', (0, 0)),
        Knight(piece_images.get_image('black', 'knight'), 'black', (0, 1)),
        Bishop(piece_images.get_image('black', 'bishop'), 'black', (0, 2)),
        Queen(piece_images.get_image('black', 'queen'), 'black', (0, 3)),
        King(piece_images.get_image('black', 'king'), 'black', (0, 4)),
        Bishop(piece_images.get_image('black', 'bishop'), 'black', (0, 5)),
        Knight(piece_images.get_image('black', 'knight'), 'black', (0, 6)),
        Rook(piece_images.get_image('black', 'rook'), 'black', (0, 7)),
        *[Pawn(piece_images.get_image('black', 'pawn'), 'black', (1, n)) for n in range(8)],

        *[Pawn(piece_images.get_image('white', 'pawn'), 'white', (6, n)) for n in range(8)],
        Rook(piece_images.get_image('white', 'rook'), 'white', (7, 0)),
        Knight(piece_images.get_image('white', 'knight'), 'white', (7, 1)),
        Bishop(piece_images.get_image('white', 'bishop'), 'white', (7, 2)),
        Queen(piece_images.get_image('white', 'queen'), 'white', (7, 3)),
        King(piece_images.get_image('white', 'king'), 'white', (7, 4)),
        Bishop(piece_images.get_image('white', 'bishop'), 'white', (7, 5)),
        Knight(piece_images.get_image('white', 'knight'), 'white', (7, 6)),
        Rook(piece_images.get_image('white', 'rook'), 'white', (7, 7))
    ]


def get_grid(pos):
    return pos[1] // GRID, pos[0] // GRID


def grid_to_rect(grid_pos):
    coord = grid_pos[1] * GRID, grid_pos[0] * GRID
    return pg.Rect(coord, (GRID, GRID))


class Chess:
    def __init__(self, pieces):
        self.pieces = pieces
        self.deadpile = []
        self.player = 'white'
        self.winner = None
        self.en_passant = None
        self.check = False

    def clone(self):
        new_pieces = [piece.clone() for piece in self.pieces]
        new_chess = Chess(new_pieces)
        new_chess.player = self.player
        new_chess.winner = self.winner
        new_chess.en_passant = self.en_passant
        new_chess.check = self.check
        return new_chess

    def compute_legal_moves(self, piece):
        return piece.get_legal_moves(self)

    def report(self, grid_pos, color):
        if 0 <= grid_pos[0] < 8 and 0 <= grid_pos[1] < 8:
            for piece in self.pieces:
                if piece.grid_pos == grid_pos:
                    return 'friend' if piece.color == color else 'opponent'
            return 'none'
        else:
            return 'OOB'

    def get_piece(self, grid_pos):
        for piece in self.pieces:
            if grid_pos == piece.grid_pos:
                return piece
        return None

    def get_legal_moves(self, grid_pos):
        piece = self.get_piece(grid_pos)
        if piece and piece.color == self.player:
            return self.compute_legal_moves(piece)
        return []

    def get_danger_zone(self, color):
        danger_zone = []
        oppo_pieces = filter(lambda x: x.color != color, self.pieces)
        for oppo_piece in oppo_pieces:
            danger_zone += oppo_piece.get_legal_moves(self, ignore_castle=True)
        return set(danger_zone)

    def get_all_moves(self):
        pieces = list(filter(lambda x: x.color == self.player, self.pieces))
        moves = []
        for piece in pieces:
            destinations = piece.get_legal_moves(self)
            for destination in destinations:
                moves.append((piece.grid_pos, destination))
        return moves

    def apply_move(self, source, destination, promotion=None, checkmate_check=True):
        # check the state
        for piece in self.pieces:
            if piece.grid_pos == source:
                if piece.color == self.player:
                    if destination in self.get_legal_moves(source):
                        # capture opponent piece
                        for oppo_piece in list(filter(lambda x: x.color != self.player, self.pieces)):
                            if (oppo_piece.grid_pos == destination) or \
                                    (self.en_passant and isinstance(piece, Pawn) and
                                     destination[1] == oppo_piece.grid_pos[1] and
                                     1 == abs(destination[0] - oppo_piece.grid_pos[0]) and
                                     1 == abs(piece.grid_pos[1] - oppo_piece.grid_pos[1])
                                     ):
                                self.pieces.remove(oppo_piece)
                                self.deadpile.append(oppo_piece)
                                if isinstance(oppo_piece, King):
                                    self.winner = 'black' if oppo_piece.color == 'white' else 'white'
                                break
                        # move
                        self.en_passant = None  # Muse be placed AFTER capture
                        # castling?
                        if isinstance(piece, King) and abs(piece.grid_pos[1] - destination[1]) > 1:
                            if destination[1] > piece.grid_pos[1]:
                                gp = piece.grid_pos[0], 7
                                gpd = piece.grid_pos[0], destination[1] - 1
                            else:
                                gp = piece.grid_pos[0], 0
                                gpd = piece.grid_pos[0], destination[1] + 1
                            rook = next(filter(lambda x: x.grid_pos == gp, self.pieces))
                            rook.grid_pos = gpd
                            rook.moved = True
                        piece.grid_pos = destination
                        if promotion and isinstance(piece, Pawn) and (destination[0] == 0 or destination[0] == 7):
                            (role, image) = promotion
                            if role == 'queen':
                                new_piece = Queen(image, piece.color, destination)
                            elif role == 'bishop':
                                new_piece = Bishop(image, piece.color, destination)
                            elif role == 'knight':
                                new_piece = Knight(image, piece.color, destination)
                            else:
                                new_piece = Rook(image, piece.color, destination)
                            self.pieces.remove(piece)
                            self.deadpile.append(piece)
                            self.pieces.append(new_piece)
                            piece = new_piece
                        piece.moved = True
                        if isinstance(piece, Pawn) and 2 == abs(source[0] - destination[0]):
                            self.en_passant = destination
                        # check?
                        self.check = False
                        if self.winner is None:
                            danger_zone = self.get_danger_zone('black' if self.player == 'white' else 'white')
                            oppo_king = next(filter(lambda x: isinstance(x, King) and x.color != self.player, self.pieces))
                            # 1. detect Checkmate! only inside check
                            self.check = oppo_king.grid_pos in danger_zone
                        self.player = 'white' if self.player == 'black' else 'black'
                        # detect no move situation after switched
                        if self.get_all_moves() is None:
                            self.winner = 'black' if self.player == 'white' else 'white'
                        # 2. perform checkmate detection after switching player
                        if self.check and checkmate_check:
                            checkmate = True
                            for move in self.get_all_moves():
                                new_chess = self.clone()
                                # 3. checkmate_check=False to avoid infinite recursive
                                new_chess.apply_move(move[0], move[1], checkmate_check=False)
                                # after apply_move, the player is switched back to me
                                oppo_color = 'black' if new_chess.player == 'white' else 'white'
                                oppo_king = next(
                                    filter(lambda x: isinstance(x, King) and x.color == oppo_color, new_chess.pieces))
                                if oppo_king.grid_pos in new_chess.get_danger_zone(oppo_color):
                                    continue
                                checkmate = False
                                # print(f'Checkmate is broken move={move}')
                                break
                            if checkmate:
                                self.winner = 'black' if self.player == 'white' else 'white'
                                # print("Checkmate!")
                break

    def evaluate(self):
        sum = 0
        for piece in self.pieces:
            sign = 1 if piece.color == 'white' else -1
            sum += piece.value() * sign
        return sum


class Player:
    def __init__(self, color):
        self.color = color


class Human(Player):
    pass


class Monkey(Player):
    def get_move(self, chess, piece_images):
        pieces = list(filter(lambda x: x.color == self.color, chess.pieces))
        moves = []
        for piece in pieces:
            destinations = piece.get_legal_moves(chess)
            for destination in destinations:
                moves.append((piece.grid_pos, destination))
        move = random.choice(moves)
        promotion = None
        if (move[1][0] == 0 or move[1][0] == 7) and isinstance(chess.get_piece(move[0]), Pawn):
            promotion = 'queen', piece_images.get_image(self.color, 'queen')
        return move, promotion


class Greedy(Player):
    def get_move(self, chess, piece_images):
        pieces = list(filter(lambda x: x.color == self.color, chess.pieces))
        moves = []
        for piece in pieces:
            destinations = piece.get_legal_moves(chess)
            for destination in destinations:
                moves.append((piece.grid_pos, destination))

        # we have all possible moves now
        def get_value(move):
            next_chess = chess.clone()
            next_chess.apply_move(move[0], move[1])
            return next_chess.evaluate()
        values = [get_value(move) for move in moves]
        max_value = max(values) if self.color == 'white' else min(values)
        valid_moves = list(filter(lambda x: get_value(x) == max_value, moves))
        move = random.choice(valid_moves)
        promotion = None
        if (move[1][0] == 0 or move[1][0] == 7) and isinstance(chess.get_piece(move[0]), Pawn):
            promotion = 'queen', piece_images.get_image(self.color, 'queen')
        return move, promotion


indent = 0


class Thinky(Player):
    def minimax(self, chess, depth, piece_images, alpha, beta):
        moves = chess.get_all_moves()
        global indent
        if depth == 0:
            def get_value(move):
                next_chess = chess.clone()
                next_chess.apply_move(move[0], move[1])
                return next_chess.evaluate()

            values = [get_value(move) for move in moves]
            max_value = max(values) if chess.player == 'white' else min(values)
            valid_moves = list(filter(lambda x: get_value(x) == max_value, moves))
            move = random.choice(valid_moves)
            promotion = None
            if (moves[1][0] == 0 or moves[1][0] == 7) and isinstance(chess.get_piece(move[0]), Pawn):
                promotion = 'queen', piece_images.get_image(chess.player, 'queen')
            print(' ' * 4 * indent, end='')
            print(f'{depth}: move={move} value={max_value}')
            return move, promotion, max_value
        else:
            extreme_value = -math.inf if chess.player == 'white' else math.inf
            extreme_move_promotions = []
            n = len(moves)
            for i, move in enumerate(moves):
                promotion = None
                if (moves[1][0] == 0 or moves[1][0] == 7) and isinstance(chess.get_piece(move[0]), Pawn):
                    promotion = 'queen', piece_images.get_image(chess.player, 'queen')
                new_chess = chess.clone()
                new_chess.apply_move(move[0], move[1])
                print(' ' * 4 * indent, end='')
                print(f'{depth}: Evaluate move [{i}/{n}]:{move}')
                indent += 1
                new_move, new_promotion, new_value = \
                    self.minimax(new_chess, depth - 1, piece_images, alpha, beta)
                indent -= 1
                if (chess.player == 'white' and new_value >= extreme_value) or \
                   (chess.player == 'black' and new_value <= extreme_value):
                    if new_value != extreme_value:
                        extreme_move_promotions.clear()
                    extreme_value = new_value
                    extreme_move_promotions.append((move, promotion))
                if chess.player == 'white':
                    alpha = max(extreme_value, alpha)
                else:
                    beta = min(extreme_value, beta)
                if alpha >= beta:
                    break
            extreme_move, extreme_promotion = random.choice(extreme_move_promotions)
            print(' ' * 4 * indent, end='')
            print(f'{depth}: move={extreme_move} value={extreme_value}')
            return extreme_move, extreme_promotion, extreme_value

    def get_move(self, chess, piece_images):
        move, promotion, value = self.minimax(chess, 2, piece_images, -math.inf, math.inf)
        return move, promotion


def notation(move) -> str:
    def coord(row_column) -> str:
        return str(chr(row_column[1] + 65)) + str(8 - row_column[0])
    return coord(move[0]) + '-' + coord(move[1])


class App:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode(RESOLUTION)
        self.piece_images = PiecesImage('chess_pieces.png', self.screen)
        self.chess = Chess(create_pieces(self.piece_images))
        self.saves = [self.chess.clone()]
        self.state = 'free'
        self.hover = None
        self.source = None
        self.players = [Human('white'), Thinky('black')]

    def draw_board(self):
        for row in range(8):
            for column in range(8):
                color = 'white' if (row + column) % 2 == 0 else 'black'
                rect = grid_to_rect((row, column))
                self.screen.fill(color, rect)

    def run(self):
        while True:
            # drawing
            pg.display.flip()
            self.draw_board()
            [piece.draw(self.screen) for piece in self.chess.pieces]

            # draw self.hover
            if self.hover:
                s = pg.surface.Surface((GRID, GRID))
                s.fill('blue')
                s.set_alpha(150)
                self.screen.blit(s, grid_to_rect(self.hover))
                legal_moves = self.chess.get_legal_moves(self.hover)
                s.fill('yellow')
                s.set_alpha(150)
                [self.screen.blit(s, grid_to_rect(p)) for p in legal_moves]

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    exit(0)

                if self.chess.winner is None:
                    current_player = next(filter(lambda x: x.color == self.chess.player, self.players))
                    if isinstance(current_player, Human):
                        if event.type == pg.MOUSEMOTION:
                            if self.state == 'free' and self.chess.winner is None:
                                pos = pg.mouse.get_pos()
                                self.hover = get_grid(pos)
                        elif event.type == pg.KEYDOWN:
                            if pg.key.get_pressed()[pg.K_COMMA]:
                                if len(self.saves) >= 3:
                                    self.saves = self.saves[:-2]
                                    self.chess = self.saves[-1].clone()
                                    self.state = 'free'
                                    self.hover = None
                                    self.source = None
                        elif event.type == pg.MOUSEBUTTONDOWN:
                            # mouse interaction. Move
                            left, mid, right = pg.mouse.get_pressed(3)
                            if right:
                                # right-click
                                self.state = 'free'
                                self.hover = None
                                self.source = None
                            elif left:
                                # left-click
                                grid_pos = get_grid(pg.mouse.get_pos())
                                if self.state == 'free':
                                    side = self.chess.report(grid_pos, self.chess.player)
                                    if side == 'friend':
                                        self.source = grid_pos
                                        self.state = 'selected'
                                elif self.state == 'selected':
                                    if grid_pos in self.chess.get_legal_moves(self.source):
                                        if isinstance(self.chess.get_piece(self.source), Pawn) and \
                                                (grid_pos[0] == 0 or grid_pos[0] == 7):
                                            answer = 0
                                            while answer < 1 or answer > 4:
                                                answer = int(input('Promotion: [1]Queen [2]Bishop [3]Knight [4]Rook'))
                                            role = ['queen', 'bishop', 'knight', 'rook'][answer - 1]
                                            image = self.piece_images.get_image(self.chess.player, role)
                                            self.chess.apply_move(self.source, grid_pos, promotion=(role, image))
                                        else:
                                            self.chess.apply_move(self.source, grid_pos)
                                        print(notation((self.source, grid_pos)))
                                        if self.chess.winner:
                                            print(f'{self.chess.winner} won!!!')
                                        elif self.chess.check:
                                            print("Check!")
                                        self.saves.append(self.chess.clone())
                                        self.state = 'free'
                                        self.hover = None
                                        self.source = None
                    else:
                        move, promotion = current_player.get_move(self.chess, self.piece_images)
                        print(move, promotion)
                        self.chess.apply_move(move[0], move[1], promotion=promotion)
                        print(notation(move))
                        if self.chess.winner:
                            print(f'{self.chess.winner} won!!!')
                        elif self.chess.check:
                            print("Check!")
                        self.saves.append(self.chess.clone())


app = App()
app.run()
