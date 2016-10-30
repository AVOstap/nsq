# coding: utf-8

import locale
import os
import requests

import read_file
import html_parser

import load_project

from app.models import Company, Insider, InsTrade, Trade
from app.utils import parse_date

if os.name == 'nt':
    locale.setlocale(locale.LC_ALL, 'english_USA')
else:
    locale.setlocale(locale.LC_ALL, 'en_US.utf8')


def main():
    init_b(Historical, read_file.tick_iter())
    init_b(InsiderTrades, read_file.tick_iter())


def init_b(miner, tick_iter):
    if not issubclass(miner, BaseMiner):
        raise AttributeError
    for tick in tick_iter:
        m = miner(tick)
        m.do_work()


class BaseMiner(object):
    TIMEOUT = 60
    URL = ''

    def __init__(self, tick):
        self.tick = tick

    @classmethod
    def downloader(cls, url):
        request = requests.get(url=url, timeout=cls.TIMEOUT)
        if request.status_code != requests.codes.ok:
            raise Exception
        return request.text

    @classmethod
    def save(cls, array, tick):
        raise NotImplementedError

    @staticmethod
    def prepare_data(array):
        raise NotImplementedError

    def do_work(self):
        html_code = self.downloader(self.URL.format(tick=self.tick))
        comp, is_created = Company.objects.get_or_create(code=self.tick)

        if is_created or comp.name is None:
            company_name = html_parser.get_full_name(html_code)
            comp.name = company_name
            comp.save()

        for data_item in html_parser.parse(html_code):
            self.prepare_data(data_item)
            self.save(data_item, comp)


class Historical(BaseMiner):
    URL = 'http://www.nasdaq.com/symbol/{tick}/historical'

    @classmethod
    def save(cls, array, company):
        Trade.objects.create(
            company=company,
            date=array[0],
            open_price=array[1],
            high_price=array[2],
            low_price=array[3],
            close_price=array[4],
            volume=array[5])

    @staticmethod
    def prepare_data(array):
        if len(array) != 6:
            raise AttributeError
        array[0] = parse_date(array[0])
        array[1] = locale.atof(array[1])
        array[2] = locale.atof(array[2])
        array[3] = locale.atof(array[3])
        array[4] = locale.atof(array[4])
        array[5] = locale.atoi(array[5])


class InsiderTrades(BaseMiner):
    URL = 'http://www.nasdaq.com/symbol/{tick}/insider-trades'

    @classmethod
    def save(cls, array, company):
        ins, _ = Insider.objects.get_or_create(name=array[0])
        InsTrade.objects.create(insider=ins,
                                company=company,
                                relation=array[1],
                                date=array[2],
                                transaction_type=array[3],
                                owner_type=array[4],
                                shares_traded=array[5],
                                last_price=array[6],
                                shares_head=array[7])

    @staticmethod
    def prepare_data(array):
        if len(array) != 8:
            raise AttributeError
        array[2] = parse_date(array[2])
        array[-3] = locale.atoi(array[-3])
        array[-2] = locale.atof(array[-2])
        array[-1] = locale.atoi(array[-1])


if __name__ == '__main__':
    main()
