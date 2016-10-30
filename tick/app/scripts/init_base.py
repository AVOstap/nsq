# coding: utf-8

from optparse import OptionParser
from multiprocessing import Pool

import load_project

from app.scripts import read_file
from app.scripts.minres import Historical, InsiderTrades


def func(miner):
    miner.do_work()


def main(filename, process):
    pool = Pool(processes=process)
    miner_list = (Historical, InsiderTrades)
    pool.map(func, (miner(tick) for miner in miner_list for tick in read_file.tick_iter(filename)))


if __name__ == '__main__':
    usage = u'usage: %prog [options]'

    opt_parser = OptionParser(usage=usage)

    opt_parser.add_option('-f', '--filename', action='store', dest='file', default='tickers.txt',
                          help=u'read stocks from FILE')
    opt_parser.add_option('-n', '--number-of-process', metavar='NUM', type='int', dest='process', default=1,
                          help=u'NUM of process')

    options, args = opt_parser.parse_args()

    main(options.file, options.process)
