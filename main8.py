import pygame as pg

# Lesson 1: read the files
# Lesson 2: draw the board and scale the piece
# Lesson 3: reformat the classes for pieces
# Lesson 4: legal moves (1/3) rook, bishop, queen
# Lesson 5: legal moves (2/3) king, knight
# Lesson 6: legal moves (3/3) pawn
# Lesson 7: Mouse control states
# Lesson 8: End Game

GRID = 80
WIDTH, HEIGHT = 8 * GRID, 8 * GRID
RESOLUTION = WIDTH, HEIGHT

# 1. Introduce `winner` in class Chess
# 2. adjust `winner` in class Chess
# 3. check `winner` in class Chess

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
    def __init__(self, image, color, role, grid_pos):
        self.image = pg.transform.scale(image, (GRID, GRID))
        self.color = color
        self.role = role
        self.grid_pos = grid_pos

    def draw(self, screen):
        screen.blit(self.image, (self.grid_pos[1] * GRID, self.grid_pos[0] * GRID))

    def trace_legal_moves(self, chess, grid_pos, dx, dy, cont):
        gp = apply_dx_dy(grid_pos, (dx, dy))
        if 0 <= gp[0] < 8 and 0 <= gp[1] < 8:
            side, _ = chess.report(gp, self.color)
            if side == 'friend':
                return []
            elif side == 'opponent':
                return [gp]
            else:
                return [gp] + (self.trace_legal_moves(chess, gp, dx, dy, cont) if cont else [])
        else:
            return []

    def get_legal_moves(self, chess):
        def trace_orthogonal(cont):
            return self.trace_legal_moves(chess, self.grid_pos, 0, -1, cont) + \
                   self.trace_legal_moves(chess, self.grid_pos, 0, 1, cont) + \
                   self.trace_legal_moves(chess, self.grid_pos, 1, 0, cont) + \
                   self.trace_legal_moves(chess, self.grid_pos, -1, 0, cont)

        def trace_diagonal(cont):
            return self.trace_legal_moves(chess, self.grid_pos, -1, -1, cont) + \
                   self.trace_legal_moves(chess, self.grid_pos, 1, 1, cont) + \
                   self.trace_legal_moves(chess, self.grid_pos, 1, -1, cont) + \
                   self.trace_legal_moves(chess, self.grid_pos, -1, 1, cont)

        if self.role == 'rook':
            return trace_orthogonal(True)
        elif self.role == 'bishop':
            return trace_diagonal(True)
        elif self.role == 'queen':
            return trace_diagonal(True) + trace_orthogonal(True)
        elif self.role == 'king':
            return trace_diagonal(False) + trace_orthogonal(False)
        elif self.role == 'knight':
            moves = (
                (-1, -2), (1, -2),
                (-1, 2), (1, 2),
                (2, -1), (2, 1),
                (-2, -1), (-2, 1)
            )
            legal_moves = []
            for move in moves:
                gp = apply_dx_dy(self.grid_pos, move)
                side, _ = chess.report(gp, self.color)
                if side == 'opponent' or side == 'none':
                    legal_moves.append(gp)
            return legal_moves
        elif self.role == 'pawn':
            legal_moves = []
            dy = -1 if self.color == 'white' else 1
            # capture?
            for dx in [-1, 1]:
                gp = apply_dx_dy(self.grid_pos, (dx, dy))
                side, _ = chess.report(gp, self.color)
                if side == 'opponent':
                    legal_moves.append(gp)
            # march 1?
            gp = apply_dx_dy(self.grid_pos, (0, dy))
            side, _ = chess.report(gp, self.color)
            if side == 'none':
                legal_moves.append(gp)
                # march 2?
                if (self.color == 'black' and self.grid_pos[0] == 1) or \
                        (self.color == 'white' and self.grid_pos[0] == 6):
                    dy = -2 if self.color == 'white' else 2
                    gp = apply_dx_dy(self.grid_pos, (0, dy))
                    side, _ = chess.report(gp, self.color)
                    if side == 'none':
                        legal_moves.append(gp)
            return legal_moves
        else:
            print("not implemented")
            return []


def create_pieces(screen):
    piece_images = PiecesImage('chess_pieces.png', screen)

    return [
        Piece(piece_images.get_image('black', 'rook'), 'black', 'rook', (0, 0)),
        Piece(piece_images.get_image('black', 'knight'), 'black', 'knight', (0, 1)),
        Piece(piece_images.get_image('black', 'bishop'), 'black', 'bishop', (0, 2)),
        Piece(piece_images.get_image('black', 'queen'), 'black', 'queen', (0, 3)),
        Piece(piece_images.get_image('black', 'king'), 'black', 'king', (0, 4)),
        Piece(piece_images.get_image('black', 'bishop'), 'black', 'bishop', (0, 5)),
        Piece(piece_images.get_image('black', 'knight'), 'black', 'knight', (0, 6)),
        Piece(piece_images.get_image('black', 'rook'), 'black', 'rook', (0, 7)),
        *[Piece(piece_images.get_image('black', 'pawn'), 'black', 'pawn', (1, n)) for n in range(8)],

        *[Piece(piece_images.get_image('white', 'pawn'), 'white', 'pawn', (6, n)) for n in range(8)],
        Piece(piece_images.get_image('white', 'rook'), 'white', 'rook', (7, 0)),
        Piece(piece_images.get_image('white', 'knight'), 'white', 'knight', (7, 1)),
        Piece(piece_images.get_image('white', 'bishop'), 'white', 'bishop', (7, 2)),
        Piece(piece_images.get_image('white', 'queen'), 'white', 'queen', (7, 3)),
        Piece(piece_images.get_image('white', 'king'), 'white', 'king', (7, 4)),
        Piece(piece_images.get_image('white', 'bishop'), 'white', 'bishop', (7, 5)),
        Piece(piece_images.get_image('white', 'knight'), 'white', 'knight', (7, 6)),
        Piece(piece_images.get_image('white', 'rook'), 'white', 'rook', (7, 7))
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
        # Introduce `winner`
        self.winner = 'none'

    def compute_legal_moves(self, piece):
        return piece.get_legal_moves(self)

    def report(self, grid_pos, color):
        if 0 <= grid_pos[0] < 8 and 0 <= grid_pos[1] < 8:
            for piece in self.pieces:
                if piece.grid_pos == grid_pos:
                    side = 'friend' if piece.color == color else 'opponent'
                    role = piece.role
                    return side, role
            return 'none', ''
        else:
            return 'OOB', ''

    def get_legal_moves(self, grid_pos):
        for piece in self.pieces:
            if grid_pos == piece.grid_pos and piece.color == self.player:
                return self.compute_legal_moves(piece)
        return []

    def apply_move(self, source, destination):
        # check the state
        for piece in self.pieces:
            if piece.grid_pos == source:
                if piece.color == self.player:
                    if destination in self.get_legal_moves(source):
                        # capture opponent piece
                        for piece in self.pieces:
                            if piece.grid_pos == destination and piece.color != self.player:
                                self.pieces.remove(piece)
                                self.deadpile.append(piece)
                                # adjust `winner`
                                if piece.role == 'king':
                                    self.winner = 'black' if piece.color == 'white' else 'white'
                                    print(f'{self.winner} won!!!')
                                break
                        # move
                        for piece in self.pieces:
                            if piece.grid_pos == source:
                                piece.grid_pos = destination
                                break
                        self.player = 'white' if self.player == 'black' else 'black'
                break

class App:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode(RESOLUTION)
        self.chess = Chess(create_pieces(self.screen))
        self.state = 'free'
        self.hover = None
        self.source = None

    def draw_board(self):
        for row in range(8):
            for column in range(8):
                color = 'white' if (row + column) % 2 == 0 else 'black'
                rect = grid_to_rect((row, column))
                self.screen.fill(color, rect)

    def run(self):
        while True:
            pg.display.flip()
            self.draw_board()
            [piece.draw(self.screen) for piece in self.chess.pieces]
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
                if event.type == pg.MOUSEMOTION:
                    # check `chess.winner`
                    if self.state == 'free' and self.chess.winner == 'none':
                        pos = pg.mouse.get_pos()
                        self.hover = get_grid(pos)
                elif event.type == pg.MOUSEBUTTONDOWN:
                    if self.chess.winner == 'none':
                        left, mid, right = pg.mouse.get_pressed(3)
                        if right:
                            # right-click
                            print("right-click")
                            self.state = 'free'
                            self.hover = None
                            self.source = None
                        elif left:
                            # left-click
                            print('left-click')
                            grid_pos = get_grid(pg.mouse.get_pos())
                            if self.state == 'free':
                                side, _ = self.chess.report(grid_pos, self.chess.player)
                                if side == 'friend':
                                    self.source = grid_pos
                                    self.state = 'selected'
                            elif self.state == 'selected':
                                if grid_pos in self.chess.get_legal_moves(self.source):
                                    self.chess.apply_move(self.source, grid_pos)
                                    self.state = 'free'
                                    self.hover = None
                                    self.source = None


app = App()
app.run()
