# coding: utf-8

import os
import locale
from multiprocessing.dummy import Pool as ThreadPool

import requests

from django.db import transaction

from app.models import Insider, InsTrade, Company, Trade
from app.scripts import html_parser
from app.utils import parse_date


if os.name == 'nt':
    locale.setlocale(locale.LC_ALL, 'english_USA')
else:
    locale.setlocale(locale.LC_ALL, 'en_US.utf8')


class MinerError(Exception):
    pass


class BaseMiner(object):
    TIMEOUT = 60
    URL = ''

    def __init__(self, tick):
        self.tick = tick

    @transaction.atomic
    def do_work(self):
        html_code = self.downloader(self.URL.format(tick=self.tick))

        company = self.get_company(self.tick, html_code)

        self.store_in_base(company, html_code)

        self.do_specific_work(company, html_code)

    def do_specific_work(self, company, first_page_html_code):
        pass

    def store_in_base(self, company, html_code):
        for data_item in html_parser.parse(html_code):
            self.prepare_data(data_item)
            self.save(data_item, company)

    @classmethod
    def downloader(cls, url, params=None):
        params = params or {}
        request = requests.get(url=url, timeout=cls.TIMEOUT, params=params)
        if request.status_code == requests.codes.ok:
            return request.text

    @classmethod
    def save(cls, array, tick):
        raise NotImplementedError

    @classmethod
    def prepare_data(cls, array):
        raise NotImplementedError

    @classmethod
    def get_company(cls, tick, html_code):
        company, is_created = Company.objects.get_or_create(code=tick)

        if is_created or company.name is None:
            company_name = html_parser.get_full_name_or_none(html_code)
            if company_name is not None:
                company.name = company_name
                company.save()

        return company


class Historical(BaseMiner):
    URL = 'http://www.nasdaq.com/symbol/{tick}/historical'
    NUMBER_OF_COLUMNS = 6

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

    @classmethod
    def prepare_data(cls, array):
        if len(array) != cls.NUMBER_OF_COLUMNS:
            raise MinerError('wrong number of columns')
        array[0] = parse_date(array[0])
        array[1] = locale.atof(array[1])
        array[2] = locale.atof(array[2])
        array[3] = locale.atof(array[3])
        array[4] = locale.atof(array[4])
        array[5] = locale.atoi(array[5])


class InsiderTrades(BaseMiner):
    URL = 'http://www.nasdaq.com/symbol/{tick}/insider-trades'
    MAX_PARSE_DEPTH = 10
    NUMBER_OF_COLUMNS = 8

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

    @classmethod
    def prepare_data(cls, array):
        if len(array) != cls.NUMBER_OF_COLUMNS:
            raise MinerError('wrong number of columns')
        array[2] = parse_date(array[2])
        array[-3] = locale.atoi(array[-3])
        array[-2] = locale.atof(array[-2])
        array[-1] = locale.atoi(array[-1])

    def do_specific_work(self, company, first_page_html_code):
        last_page_index = html_parser.get_last_page_index_or_none(first_page_html_code)

        if last_page_index is None:
            return

        last_page_index = min(last_page_index, self.MAX_PARSE_DEPTH)

        def func(index):
            return self.downloader(self.URL.format(tick=self.tick), params={'page': index})

        pool = ThreadPool(4)
        res = pool.map(func, range(2, last_page_index + 1))

        for code in res:
            self.store_in_base(company, code)
