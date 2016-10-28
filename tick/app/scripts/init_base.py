# coding: utf-8

import locale
import requests

import downlader, read_file, html_parser

import load_project

from app.models import Company, Insider, InsTrade, Trade
from app.utils import parse_date

locale.setlocale(locale.LC_ALL, 'english_USA')


def main():
    tick_iter = read_file.tick_iter()
    Historical(tick_iter)
    InsiderTrades(tick_iter)



def save_insider_trades(r, tick):
    comp, _ = Company.objects.get_or_create(company_code=tick)
    ins, _ = Insider.objects.get_or_create(name=r[0])
    InsTrade.objects.create(insider=ins,
                            company=comp,
                            relation=r[1],
                            date=r[2],
                            transaction_type=r[3],
                            owner_type=r[4],
                            shares_traded=r[5],
                            last_price=r[6],
                            shares_head=r[7])


def save_historical(r, tick):
    comp, _ = Company.objects.get_or_create(company_code=tick)
    Trade.objects.create(
        company=comp,
        date=r[0],
        open_price=r[1],
        high_price=r[2],
        low_price=r[3],
        close_price=r[4],
        volume=r[5])


def prepare_data_historical(array):
    if len(array) != 6:
        raise AttributeError

    array[0] = parse_date(array[0])
    array[1] = locale.atof(array[1])
    array[2] = locale.atof(array[2])
    array[3] = locale.atof(array[3])
    array[4] = locale.atof(array[4])
    array[5] = locale.atoi(array[5])


def prepare_data_insider_trades(array):
    if len(array) != 8:
        raise AttributeError
    array[2] = parse_date(array[2])
    array[-3] = locale.atoi(array[-3])
    array[-2] = locale.atof(array[-2])
    array[-1] = locale.atoi(array[-1])


class BaseMiner(object):
    TIMEOUT = 60


    @classmethod
    def downloader(cls, tick_iter, url):
        for tick in tick_iter:
            request = requests.get(url=url, timeout=cls.TIMEOUT)
            if request.status_code != 200:
                continue
            yield tick, request.text

    @classmethod
    def save(cls, array, tick):
        raise NotImplementedError

    @staticmethod
    def prepare_data(array):
        raise NotImplementedError


class Historical(BaseMiner):
    URL = 'http://www.nasdaq.com/symbol/{tick}/historical',

    @classmethod
    def save(cls, array, tick):
        comp, _ = Company.objects.get_or_create(company_code=tick)
        Trade.objects.create(
            company=comp,
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
    def save(cls, array, tick):
        comp, _ = Company.objects.get_or_create(company_code=tick)
        ins, _ = Insider.objects.get_or_create(name=array[0])
        InsTrade.objects.create(insider=ins,
                                company=comp,
                                relation=array[1],
                                date=array[2],
                                transaction_type=array[3],
                                owner_type=array[4],
                                shares_traded=array[5],
                                last_price=array[6],
                                shares_head=array[7])

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


if __name__ == '__main__':
    main()
