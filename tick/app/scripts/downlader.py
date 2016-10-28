# coding: utf-8

import requests

timeout = 60

H_TYPE = 'historical'
I_TYPE = 'insiders-trades'

TYPES = {
    I_TYPE: 'http://www.nasdaq.com/symbol/{tick}/insider-trades',
    H_TYPE: 'http://www.nasdaq.com/symbol/{tick}/historical',
}


def downloader(tick_iter, d_type=I_TYPE):
    for tick in tick_iter:
        request = requests.get(url=TYPES[d_type].format(tick=tick), timeout=timeout)
        if request.status_code != 200:
            continue
        yield tick, request.text
