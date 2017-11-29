import unittest

from go import Go, WHITE, BLACK, parse_board, GoException

class TestGo(unittest.TestCase):

    def setUp(self):
        go = Go(size=4)
        go[2][2].state = WHITE
        go[1][2].state = BLACK
        go[3][2].state = BLACK
        go[2][1].state = BLACK
        go[2][3].state = BLACK

        self.small_board_white_surrounded = go

        go = Go(size=4)
        go[2][2].state = WHITE
        go[1][2].state = WHITE
        go[3][2].state = WHITE
        go[2][1].state = WHITE
        go[2][3].state = WHITE

        self.small_board_all_white = go

        go = Go(size=4)
        go[2][2].state = WHITE
        go[1][2].state = None
        go[3][2].state = BLACK
        go[2][1].state = BLACK
        go[2][3].state = BLACK

        self.small_board_white_almost_surrounded = go

        board = [
            '|             |',
            '|             |',
            '|             |',
            '|             |',
            '|      BB     |',
            '|     BWWB    |',
            '|      BB     |',
            '|             |',
            '|             |',
            '|             |',
            '|             |',
        ]

        self.big_board_white_captured = parse_board(board)



    def test_neighbors(self):
        go = self.small_board_white_surrounded
        self.assertListEqual(
            go[2][2].neighbors,
            [go[1][2], go[3][2], go[2][1], go[2][3]]
        )

    def test_has_free_neighbor(self):
        go = self.small_board_all_white
        self.assertTrue(go[1][2].has_free_neighbor)
        self.assertFalse(go[2][2].has_free_neighbor)

    def test_patch_small_patch_white_surrounded(self):
        go = self.small_board_white_surrounded
        self.assertListEqual(
            go[2][2].patch.cells,
            [go[2][2]]
        )

    def test_patch_small_patch_all_white(self):
        go = self.small_board_all_white
        self.assertListEqual(
            sorted(go[2][2].patch.cells, key=lambda c: c._cell_state),
            [go[1][2], go[2][1], go[2][2], go[2][3], go[3][2]]
        )

    def test_captured(self):
        self.assertFalse(self.small_board_white_almost_surrounded[2][2].is_captured)
        self.assertTrue(self.small_board_white_surrounded[2][2].is_captured)
        self.assertFalse(self.small_board_all_white[2][2].is_captured)

    def test_bigger_board(self):

        go = self.big_board_white_captured

        self.assertTrue(
            go[5][6].is_captured
        )
        self.assertTrue(
            go[7][5].is_captured,
            str(go[7][5])
        )

    def test_update_board(self):
        go = self.big_board_white_captured
        go.update()
        self.assertEqual(
            str(go),
            '\n'.join([
            '|             |',
            '|             |',
            '|             |',
            '|             |',
            '|      BB     |',
            '|     BBBB    |',
            '|      BB     |',
            '|             |',
            '|             |',
            '|             |',
            '|             |'])
        )

    def test_play_game(self):
        go = Go(size=11)
        go.play(5, 5)
        expected_board = '\n'.join(
               ['|             |',
                '|             |',
                '|             |',
                '|             |',
                '|             |',
                '|      W      |',
                '|             |',
                '|             |',
                '|             |',
                '|             |',
                '|             |'])
        self.assertEqual(
            str(go),
            expected_board,
            '\n' + repr(str(go)) + '\n' + repr(expected_board)
        )

        go.play(4, 5)
        self.assertEqual(
            str(go),
            '\n'.join([
                '|             |',
                '|             |',
                '|             |',
                '|             |',
                '|      B      |',
                '|      W      |',
                '|             |',
                '|             |',
                '|             |',
                '|             |',
                '|             |']),
            str(go)
        )

        with self.assertRaises(GoException):
            go.play(4, 5)
        self.assertEqual(
            str(go),
            '\n'.join([
                '|             |',
                '|             |',
                '|             |',
                '|             |',
                '|      B      |',
                '|      W      |',
                '|             |',
                '|             |',
                '|             |',
                '|             |',
                '|             |']),
            str(go)
        )

        go.play(3, 5)
        expected_board =  '\n'.join([
                '|             |',
                '|             |',
                '|             |',
                '|      W      |',
                '|      B      |',
                '|      W      |',
                '|             |',
                '|             |',
                '|             |',
                '|             |',
                '|             |'])
        self.assertEqual(
            str(go),
            expected_board,
            str(go)
        )

        go.play(5, 6)
        expected_board = '\n'.join([
                '|             |',
                '|             |',
                '|             |',
                '|      W      |',
                '|      B      |',
                '|      WB     |',
                '|             |',
                '|             |',
                '|             |',
                '|             |',
                '|             |'])
        self.assertEqual(
            str(go),
            expected_board,
            str(go)
        )

        go.play(4, 6)
        self.assertEqual(
            str(go),
            '\n'.join([
                '|             |',
                '|             |',
                '|             |',
                '|      W      |',
                '|      BW     |',
                '|      WB     |',
                '|             |',
                '|             |',
                '|             |',
                '|             |',
                '|             |']),
            str(go)
        )

        go.play(5, 4)
        self.assertEqual(
            str(go),
            '\n'.join([
                '|             |',
                '|             |',
                '|             |',
                '|      W      |',
                '|      BW     |',
                '|     BWB     |',
                '|             |',
                '|             |',
                '|             |',
                '|             |',
                '|             |']),
            str(go)
        )

        go.play(4, 4)
        self.assertEqual(
            str(go),
            '\n'.join([
                '|             |',
                '|             |',
                '|             |',
                '|      W      |',
                '|     WWW     |',
                '|     BWB     |',
                '|             |',
                '|             |',
                '|             |',
                '|             |',
                '|             |']),
            str(go)
        )