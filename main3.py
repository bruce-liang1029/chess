import pygame as pg

# Lesson 1: read the files
# Lesson 2: draw the board and scale the piece
# Lesson 3: reformat the classes for pieces

GRID = 100
WIDTH, HEIGHT = 8 * GRID, 8 * GRID
RESOLUTION = WIDTH, HEIGHT


# Introduce Python `class`.
#   Talk through `self`, `__init__`, member functions before proceeding to coding.
class PiecesImage:
    # Re-write the image producer into one class
    # Load the big collated picture once and then dispatch sub-images
    # whenever they are needed.
    def __init__(self, image_filename, screen):
        self.piece_infos = (
            ('black', 'king'), ('black', 'queen'), ('black', 'bishop'), ('black', 'knight'),
            ('white', 'king'), ('white', 'queen'), ('black', 'rook'), ('black', 'pawn'),
            ('white', 'bishop'), ('white', 'knight'), ('white', 'rook'), ('white', 'pawn'))
        self.pieces_image = pg.image.load(image_filename).convert(screen)
        self.w, self.h = self.pieces_image.get_size()
        self.w //= 4
        self.h //= 3

    # Dispatch a sub-image to a piece
    def get_image(self, color, role):
        idx = self.piece_infos.index((color, role))
        x = self.w * (idx % 4)
        y = self.h * (idx // 4)
        return self.pieces_image.subsurface((x, y), (self.w, self.h))


# This is the class for one piece
class Piece:
    def __init__(self, image, color, role, grid_pos):
        # scale the image whenever it is gotten initially
        self.image = pg.transform.scale(image, (GRID, GRID))
        self.color = color
        self.role = role
        self.grid_pos = grid_pos

    def draw(self, screen):
        # remember we need the `screen` for Bliting
        screen.blit(self.image, (self.grid_pos[1] * GRID, self.grid_pos[0] * GRID))

# This function is to create all pieces
# Don't try to generate all. Try it step by step staring from Rook.
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
        # add Pawn creation last. The asterisk `*` is necessary to "flatten" 8 pieces
        *[Piece(piece_images.get_image('black', 'pawn'), 'black', 'pawn', (1, n)) for n in range(8)],
        # same as above
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


def draw_board(screen):
    for row in range(8):
        for column in range(8):
            color = 'white' if (row + column) % 2 == 0 else 'black'
            coord = row * GRID, column * GRID
            screen.fill(color, pg.Rect(coord, (GRID, GRID)))


pg.init()
screen = pg.display.set_mode(RESOLUTION)
pieces = create_pieces(screen)
while True:
    pg.display.flip()
    draw_board(screen)
    # teach this new form of "for" loop last.
    # Do the traditional "for" first and then re-order
    [piece.draw(screen) for piece in pieces]
