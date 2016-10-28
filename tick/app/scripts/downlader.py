# coding: utf-8

import requests
import os

timeout = 60

H_TYPE = 'h'
I_TYPE = 'i'

TYPES = {
    I_TYPE: 'http://www.nasdaq.com/symbol/{tick}/insider-trades',
    H_TYPE: 'http://www.nasdaq.com/symbol/{tick}/historical',
}


def downloader(tick_iter, d_type=I_TYPE):
    for tick in tick_iter:
        if os.path.isfile(tick + '.txt'):
            with open(tick + '.txt') as f:
                yield tick, f.read()
        else:
            request = requests.get(url=TYPES[d_type].format(tick=tick), timeout=timeout)
            if request.status_code != 200:
                continue
            with open(tick + '.txt', 'w') as f:
                f.write(request.text)
            yield request.text
