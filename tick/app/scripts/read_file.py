import os

FILE_NAME = 'tickers.txt'


def tick_iter(file_name=None):
    if file_name is None:
        file_name = FILE_NAME

    if not os.path.isfile(file_name):
        raise AttributeError('file not exists')

    with open(file_name) as f:
        while True:
            tick = f.readline()
            if not tick:
                raise StopIteration
            tick = tick.rstrip()
            if tick:
                yield tick
