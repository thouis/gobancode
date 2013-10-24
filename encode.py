import sys
import subprocess

if __name__ == '__main__':
    data = sys.argv[1]
    encoded = subprocess.check_output('zint --dump -b 92 -d'.split(' ') + [data])
    encoded = encoded.translate(None, "[] ").split('\n')

    boardsize = max(len(l) for l in encoded)

    # header
    print "(;FF[4]SZ[{}]AP[gobancode]".format(boardsize)

    row = boardsize
    black_stones = []
    white_stones = []
    for l in encoded:
        if l == '': continue
        for col, c in enumerate(l):
            dest = black_stones if c == '1' else white_stones

            char_row = chr(ord('a') + row - 1)
            char_col = chr(ord('a') + col)
            dest.append("[{}{}]".format(char_row, char_col))
        row -= 1
    print ";AB{}".format(''.join(black_stones))
    print ";AW{}".format(''.join(white_stones))
    print ")"
