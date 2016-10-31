# coding: utf-8

import sys
from optparse import OptionParser
from multiprocessing import Pool

import load_project

from app.scripts import read_file

from app.scripts.minres import Historical, InsiderTrades


MINERS = (
    Historical,
    InsiderTrades,
)


def func(miner):
    try:
        miner.do_work()
    except Exception as e:
        sys.stdout.write(e.message)


def main(filename, process):
    cocked_miners = (miner(tick) for miner in MINERS for tick in read_file.tick_iter(filename))
    if process > 1:
        pool = Pool(processes=process)
        pool.map(func, cocked_miners)
    else:
        list(map(func, cocked_miners))


if __name__ == '__main__':
    usage = u'usage: %prog [options]'

    opt_parser = OptionParser(usage=usage)

    opt_parser.add_option('-f', '--filename', action='store', dest='file', default='tickers.txt',
                          help=u'read stocks from FILE')
    opt_parser.add_option('-n', '--number-of-process', metavar='NUM', type='int', dest='process', default=1,
                          help=u'NUM of process')

    options, args = opt_parser.parse_args()

    main(options.file, options.process)
