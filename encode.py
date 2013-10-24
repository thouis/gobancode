import sys
import subprocess

formatargs = {'datamatrix': '--square -b 71',
              'qrcode': '-b 58',
              'grid': '-b 142',
              'microqr': '-b 97',
              'aztec': '-b 92'}

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
    encoded = [l for l in encoded.translate(None, "[] ").split('\n') if l]

    boardsize = len(encoded)

    # header
    print "(;FF[4]SZ[{}]AP[gobancode]".format(boardsize)

    black_stones = []
    white_stones = []
    for row, l in enumerate(encoded):
        if l == '': continue
        for col, c in enumerate(l):
            dest = black_stones if c == '1' else white_stones

            char_row = chr(ord('a') + row)
            char_col = chr(ord('a') + col)
            dest.append("[{}{}]".format(char_col, char_row))
    print ";AB{}".format(''.join(black_stones))
    print ";AW{}".format(''.join(white_stones))
    print ")"
