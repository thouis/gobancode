import sys
import subprocess
import numpy as np
import random
import scipy.ndimage as nd

formatargs = {'datamatrix': '--square -b 71',
              'qrcode': '-b 58',
              'grid': '-b 142',
              'microqr': '-b 97',
              'aztec': '-b 92'}

def all_alive(board):
    black_groups, black_count = nd.label(board == 1)
    empty_adjacent_count = nd.filters.convolve((board == 0).astype(np.uint8),
                                               np.array([[0, 1, 0], [1, 0, 1], [0, 1, 0]]),
                                               mode='constant')
    black_adjacent_max = nd.maximum(empty_adjacent_count, black_groups,
                                    np.arange(1, black_count))
    if np.any(black_adjacent_max == 0):
        return False
    white_groups, white_count = nd.label(board == 2)
    white_adjacenet_max = nd.maximum(empty_adjacent_count, white_groups,
                                     np.arange(1, white_count))
    if np.any(white_adjacenet_max == 0):
        return False
    return True

def make_alive(board):
    # fix up the board by removing all the white stones, then adding them back
    # in on empty intersections until no more can be added

    # convert to an array of 0/1 with 1 = black
    board = (np.array(board) == '1').astype(int)
    assert all_alive(board)

    # treat 0 as empty, 1 as black, 2 as white
    empty = zip(*np.nonzero(board == 0))
    while len(empty) > 0:
        i, j = empty.pop(random.randrange(len(empty)))

        # fill the intersection with a white stone, and test for aliveness
        board[i, j] = 2
        if not all_alive(board):
            # failure, clear the intersection again
            board[i, j] = 0
    return board


if __name__ == '__main__':
    zintargs = formatargs['qrcode']

    if '--help' in sys.argv[1:]:
        print 'python encode.py [FORMAT] STRING'
        print '  Where FORMAT is one of:'
        for k in formatargs.keys():
            print '     --{}'.format(k)
        print '  Default: --qrcode'
        sys.exit(0)

    for arg in sys.argv[1:-1]:
        if arg.startswith('-'):
            arg = arg.translate(None, '-')
            if arg in formatargs:
                zintargs = formatargs[arg]
            else:
                print "No such format known: {}".format(arg)
                sys.exit(1)

    data = sys.argv[-1]
    encoded = subprocess.check_output('zint --dump {} -d'.format(zintargs).split(' ') + [data])
    encoded = [list(l) for l in encoded.translate(None, "[] ").split('\n') if l]

    boardsize = len(encoded)

    # clean up dead groups
    encoded = make_alive(encoded)

    # header
    print "(;FF[4]SZ[{}]AP[gobancode]".format(boardsize)

    letters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'

    black_stones = []
    white_stones = []
    for row, l in enumerate(encoded):
        for col, c in enumerate(l):
            tmp = "[{}{}]".format(letters[col], letters[row])
            if c == 1:
                black_stones.append(tmp)
            elif c == 2:
                white_stones.append(tmp)
    print ";AB{}".format(''.join(black_stones))
    print ";AW{}".format(''.join(white_stones))
    print ")"
