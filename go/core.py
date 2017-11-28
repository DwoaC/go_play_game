'''
The game Go implemented pythonicly

A friend in work had an assignment to implement Go for a college course.  We
talked about how to go about finding the cells on the board that have been
captured.

Creating a new game is simple,

    >>> go = Go(size=11)

To playing a move call play with the co-ordinates of the piece.

    >>> go.play(5, 5)

Printing the game reveals the board.

    >>> print(go)
    |             |
    |             |
    |             |
    |             |
    |             |
    |      W      |
    |             |
    |             |
    |             |
    |             |
    |             |

Play swaps back and forth between two players,

    >>> go.play(5, 6)
    >>> print(go)
    |             |
    |             |
    |             |
    |             |
    |             |
    |      WB     |
    |             |
    |             |
    |             |
    |             |
    |             |

Surrounded pieces are captured automaticly,

    >>> go.play(5, 6)
    >>> go.play(5, 7)
    >>> go.play(5, 4)
    >>> go.play(4, 6)
    >>> go.play(6, 5)
    |             |
    |             |
    |             |
    |             |
    |      BW     |
    |      WBW    |
    |      B      |
    |             |
    |             |
    |             |
    |             |

And white captures black,

    >>> go.play(6, 6)
    |             |
    |             |
    |             |
    |             |
    |      BW     |
    |      WWW    |
    |      BW     |
    |             |
    |             |
    |             |
    |             |

Incorrect moves raise an exception

    >>> go.play(6, 6)
    Traceback (most recent call last):
      ...
    go.core.GoException: Piece already present at Cell(6, 6, 1)

'''

# TODO: stop game if players in a loop
# TODO: implment players

WHITE = 1
BLACK = 0

class ParseException(Exception):
    pass

class GoException(Exception):
    pass

board_to_state_mapping = {
    ' ': None,
    'W': WHITE,
    'B': BLACK
}

def parse_board(board):
    size = len(board)
    go = Go(size)
    for board_row, go_row in zip(board, go):
        board_row = board_row.replace('| ', '').replace(' |', '')
        if len(board_row) != len(go_row):
            raise ParseException('Row and Columns dont match')
        for board_cell, go_cell in zip(board_row, go_row):
            go_cell.state = board_to_state_mapping[board_cell]

    return go


class Go:

    def __init__(self, size):
        self.size = size
        self.cells = []
        self.player = WHITE
        for i in range(size):
            row = []
            for j in range(size):
                row.append(Cell(x=i, y=j, board=self))
            self.cells.append(row)

    def __getitem__(self, item):
        return self.cells[item]

    def __str__(self):
        rows = []
        for row in self:
            new_row = '{}'*len(row)
            rows.append(new_row.format(*row))

        output = '| {} |\n' * len(rows)
        return output.format(*rows)[:-1]

    def update(self):
        for patch in self.patches:
            patch.capture()

    @property
    def patches(self):
        checked_cells = []
        patches = []

        for row in self:
            for cell in row:
                if cell is None:
                    continue
                elif cell in checked_cells:
                    continue
                else:
                    patches.append(cell.patch)
                    checked_cells += cell.patch.cells
        return patches

    def play(self, x, y):
        cell = self[x][y]
        if cell.state is not None:
            raise GoException('Piece already present at {}'.format(repr(cell)))
        cell.state = self.player
        self.player = BLACK if self.player == WHITE else WHITE
        self.update()


class Cell:
    def __init__(self, x, y, board, state=None):
        self.x = x
        self.y = y
        self.board = board
        self.state = state

    @property
    def is_captured(self):
        return self.patch.is_captured

    @property
    def patch(self):
        return Patch(starting_cell=self)

    @property
    def neighbors(self):
        neighbors = []
        if self.x > 0:
            neighbors.append(self.board[self.x - 1][self.y])
        if self.x < self.board.size - 1:
            neighbors.append(self.board[self.x + 1][self.y])
        if self.y > 0:
            neighbors.append(self.board[self.x][self.y - 1])
        if self.y < self.board.size - 1:
            neighbors.append(self.board[self.x][self.y + 1])

        return neighbors

    def __repr__(self):
        return '{0.__class__.__name__}({0.x}, {0.y}, {0.state})'.format(self)

    @property
    def cell_state(self):
        return (self.x, self.y, self.state)

    def __eq__(self, other):
        return self.cell_state == other.cell_state

    def __hash__(self):
        return hash(self.cell_state)

    @property
    def has_free_neighbor(self):
        return any(c.state is None for c in self.neighbors)

    def __str__(self):
        inverse_board_to_state_mapping = dict(zip(
            board_to_state_mapping.values(),
            board_to_state_mapping.keys()
        ))
        return str(inverse_board_to_state_mapping[self.state])

class Patch:

    def __init__(self, starting_cell):
        self.cells = []
        self.cells = self.discover_patch(starting_cell)

    def discover_patch(self, starting_cell, patch=None):
        if starting_cell.state is None:
            return []

        if patch is None:
            patch = [starting_cell]

        for neighbor in starting_cell.neighbors:
            if neighbor.state == starting_cell.state and neighbor not in patch:
                patch += [neighbor]
                patch += self.discover_patch(neighbor, patch)

        return list(set(patch))

    @property
    def is_captured(self):
        return not any(c.has_free_neighbor for c in self.cells)

    def __len__(self):
        return len(self.cells)

    def __getitem__(self, item):
        return self.cells[item]

    def capture(self):
        if self.is_captured:
            for cell in self:
                cell.state = WHITE if cell.state == BLACK else BLACK