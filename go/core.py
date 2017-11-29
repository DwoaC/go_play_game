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

A utility function to parse a board from a string or list is available,

    >>> parse_board(
    >>>    '    \n'
    >>>    ' BW \n'
    >>>    ' W  \n'
    >>>    '    ')
    <go.core.Go at 0x106c86e10>


'''

# TODO: stop game if players in a loop
# TODO: implment players

WHITE = 1
BLACK = 0

class ParseException(Exception):
    pass

class GoException(Exception):
    pass

BOARD_STRING_TO_STATE_MAPPING = {
    ' ': None,
    'W': WHITE,
    'B': BLACK
}

STATE_TO_BOARD_STRING_MAPPING = dict(zip(
            BOARD_STRING_TO_STATE_MAPPING.values(),
            BOARD_STRING_TO_STATE_MAPPING.keys()
        ))

def parse_board(board):
    '''
    Parse a str of list of strings in to a board state.

    The player with the least pieces is the next player.

    The rows in the input can contain an optional '| ' or
    ' |' for clarity.  This is the same style used by
    Go's str method.

    The board must be square so the number of rows and
    columns must match.

    The 3 characters used for state are 'W', 'B' and ' '.

    If board is a string '\n' is used to seperate the rows.

    There is massive room for optimisation.  The various
    views of the cells could be cached.  The patches
    could be cached and cells could be added to a patch
    as part of the players move.

    :param board: (str or list(str) board state
    :return: (Go)
    '''

    if isinstance(board, str):
        board = board.split('\n')

    size = len(board)
    go = Go(size)
    for board_row, go_row in zip(board, go):
        board_row = board_row.replace('| ', '').replace(' |', '')
        if len(board_row) != len(go_row):
            raise ParseException('Row and Columns dont match')
        for board_cell, go_cell in zip(board_row, go_row):
            go_cell.state = BOARD_STRING_TO_STATE_MAPPING[board_cell]

    go.player = WHITE if len(go.white_cells) <= len(go.black_cells) else BLACK

    return go


class Go:

    def __init__(self, size):
        '''
        A game of Go.

        The board is a square size x size.

        The next player is determined by self.player and defaults
        to WHITE.  In the real game the first player is BLACK but
        I didn't learn that until after I had the tests written :)

        Go objects support indexing.  To get the cells on the first
        row for instance,
        >>> go = parse_board(
        >>>        '    \n'
        >>>        ' BW \n'
        >>>        ' W  \n'
        >>>        '    ')
        >>> go[1]
        [Cell(1, 0, None), Cell(1, 1, 0), Cell(1, 2, 1), Cell(1, 3, None)]

        The next player can make a move by calling the play method.

        >>> go.play(0, 2)
        >>> print(go)
            |   B  |
            |  BW  |
            |  W   |
            |      |

        A list of patches on the board is produced by the patches attribute

        >>> go.patches
        [<go.core.Patch at 0x106b8f7f0>,
         <go.core.Patch at 0x106c12a58>,
         <go.core.Patch at 0x106b8f898>,
         <go.core.Patch at 0x106b8f518>,
         <go.core.Patch at 0x106b8f128>,
         <go.core.Patch at 0x106b8f1d0>,
         <go.core.Patch at 0x106b8ffd0>,
         <go.core.Patch at 0x106b8ff28>,
         <go.core.Patch at 0x106b8fa90>,
         <go.core.Patch at 0x106b8fac8>,
         <go.core.Patch at 0x106b8f780>,
         <go.core.Patch at 0x106b8f978>,
         <go.core.Patch at 0x106b8fe10>,
         <go.core.Patch at 0x106b8fd68>,
         <go.core.Patch at 0x106b8fb70>,
         <go.core.Patch at 0x106b8fc50>]

        The all_cells attribute can be used to access all cells in a list.

        >>> go.all_cells[2:6]
        [Cell(0, 2, None), Cell(0, 3, None), Cell(1, 0, None), Cell(1, 1, 0)]

        :param size: (int) size of the board.
        '''
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

    @property
    def white_cells(self):
        return [c for c in self.all_cells if c.state == WHITE]

    @property
    def black_cells(self):
        return [c for c in self.all_cells if c.state == BLACK]

    @property
    def all_cells(self):
        cells = []
        for row in self:
            for cell in row:
                cells.append(cell)
        return cells

class Cell:
    def __init__(self, x, y, board, state=None):
        '''
        A location on the board in Go.

        :param x: (int) row the cell takes on the board
        :param y: (int) column the cell takes on the board
        :param board: (Go) the parent Go object
        :param state: (int) Optional. the initial state of
        the cell.
        '''
        self.x = x
        self.y = y
        self.board = board
        self.state = state

    @property
    def is_captured(self):
        'True if the cell is surrounded'

        return self.patch.is_captured

    @property
    def patch(self):
        'The patch the cell is part of.'

        return Patch(starting_cell=self)

    @property
    def neighbors(self):
        '''List of the neighbors of the cell.

        Cells on an edge or in a corner will have fewer
        neighbors.
        '''

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

    @property
    def _cell_state(self):
        '''Convience property of the internal state.'''

        return (self.x, self.y, self.state)

    def __eq__(self, other):
        return self._cell_state == other._cell_state

    def __hash__(self):
        return hash(self._cell_state)

    @property
    def has_free_neighbor(self):
        return any(c.state is None for c in self.neighbors)

    def __repr__(self):
        return '{0.__class__.__name__}({0.x}, {0.y}, {0.state})'.format(self)

    def __str__(self):
        return str(STATE_TO_BOARD_STRING_MAPPING[self.state])

class Patch:

    def __init__(self, starting_cell):
        '''
        A sequence of continuous region of cells of one color.

        Each cell will be a member of only one patch.

        A patch is considered captured if no cell in the patch
        has a free neighbor.  A free neighbor is a neighbor cell
        with a state of None.

        :param starting_cell:
        '''
        self.cells = []
        self.cells = self.discover_patch(starting_cell)

    def discover_patch(self, starting_cell, patch=None):
        '''Return a list of cells in a patch containing starting_cell.

        Recursively searches for neighbors of the same state
        and adds them to a list to return.
        '''
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
        '''If possible capture the patch.'''
        if self.is_captured:
            for cell in self:
                cell.state = WHITE if cell.state == BLACK else BLACK