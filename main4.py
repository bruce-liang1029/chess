import pygame as pg

# Lesson 1: read the files
# Lesson 2: draw the board and scale the piece
# Lesson 3: reformat the classes for pieces
# Lesson 4: legal moves (1/3) rook, bishop, queen

GRID = 80
WIDTH, HEIGHT = 8 * GRID, 8 * GRID
RESOLUTION = WIDTH, HEIGHT


# Follow the procedure below to make sense of the implementation
# 1. Create Chess class, populate its __init__
# 2. Create App class, implement the full class
# 3. implement the functions `grid_to_rect` and `get_grid`
# 3. Re-visit Chess class, start from `get_legal_moves`
# 4. Implement `get_legal_moves` in Piece class


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


class Piece:
    def __init__(self, image, color, role, grid_pos):
        self.image = pg.transform.scale(image, (GRID, GRID))
        self.color = color
        self.role = role
        self.grid_pos = grid_pos

    def draw(self, screen):
        screen.blit(self.image, (self.grid_pos[1] * GRID, self.grid_pos[0] * GRID))

    # Do this third
    def trace_legal_moves(self, chess, grid_pos, dx, dy):
        gp = grid_pos[0] + dy, grid_pos[1] + dx
        if 0 <= gp[0] < 8 and 0 <= gp[1] < 8:
            side, _ = chess.report(gp, self.color)
            if side == 'friend':
                return []
            elif side == 'opponent':
                return [gp]
            else:
                return [gp] + self.trace_legal_moves(chess, gp, dx, dy)
        else:
            return []

    # Overall, do this last. When `get_legal_moves` is being done, follow the hints below
    def get_legal_moves(self, chess):
        # Do this second
        def trace_orthogonal():
            return self.trace_legal_moves(chess, self.grid_pos, 0, -1) + \
                   self.trace_legal_moves(chess, self.grid_pos, 0, 1) + \
                   self.trace_legal_moves(chess, self.grid_pos, 1, 0) + \
                   self.trace_legal_moves(chess, self.grid_pos, -1, 0)

        # Do this fifth
        def trace_diagonal():
            return self.trace_legal_moves(chess, self.grid_pos, -1, -1) + \
                   self.trace_legal_moves(chess, self.grid_pos, 1, 1) + \
                   self.trace_legal_moves(chess, self.grid_pos, 1, -1) + \
                   self.trace_legal_moves(chess, self.grid_pos, -1, 1)

        # Do this first and do "rook" only
        if self.role == 'rook':
            return trace_orthogonal()
        # Do this forth
        # checkpoint: challenge students to do "bishop" after seeing how "rook" was done.
        elif self.role == 'bishop':
            return trace_diagonal()
        # Do "queen" and else last.
        # checkpoint: challenge students to do "queen" after seeing how "rook" and "bishop" were done.
        elif self.role == 'queen':
            return trace_diagonal() + trace_orthogonal()
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
        # *[Piece(piece_images.get_image('black', 'pawn'), 'black', 'pawn', (1, n)) for n in range(8)],

        # *[Piece(piece_images.get_image('white', 'pawn'), 'white', 'pawn', (6, n)) for n in range(8)],
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


# Create Chess and App classes before proceeding to `get_legal_moves` of the Piece
class Chess:
    def __init__(self, pieces):
        self.pieces = pieces
        self.player = 'white'

    def compute_legal_moves(self, piece):
        print(f'compute legal moves for {piece.role}')
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


# Refactor App class after Chess class
class App:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode(RESOLUTION)
        self.chess = Chess(create_pieces(self.screen))
        self.hover = None
        self.state = 'free'

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
                # Up to this point, populate `get_legal_moves` in class chess
                legal_moves = self.chess.get_legal_moves(self.hover)
                s.fill('yellow')
                s.set_alpha(150)
                [self.screen.blit(s, grid_to_rect(p)) for p in legal_moves]

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    exit(0)
                if event.type == pg.MOUSEMOTION:
                    pos = pg.mouse.get_pos()
                    self.hover = get_grid(pos)


app = App()
app.run()
