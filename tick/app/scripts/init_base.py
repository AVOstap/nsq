import downlader
import read_file
import html_parser
from datetime import datetime, date
import locale

import load_project

from app.models import Company, Insider, InsTrade, Trade

locale.setlocale(locale.LC_ALL, 'english_USA')


def test_iter():
    tick_list = ['goog', 'stt', ]
    for tick in tick_list:
        yield tick


def main():
    tick_iter = read_file.tick_iter()
    d_type = downlader.H_TYPE

    dwl_iter = downlader.downloader(test_iter(), d_type=d_type)
    for tick, text in dwl_iter:
        for r in html_parser.parse(text):
            if d_type == downlader.I_TYPE:
                print tick, prepare_date_i(r)
                save_data_i(r, tick)
            elif d_type == downlader.H_TYPE:
                print tick, prepare_data_h(r)
                save_data_h(r, tick)
            else:
                raise Exception


def save_data_i(r, tick):
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


def save_data_h(r, tick):
    comp, _ = Company.objects.get_or_create(company_code=tick)
    Trade.objects.create(
        company=comp,
        date=r[0],
        open_price=r[1],
        high_price=r[2],
        low_price=r[3],
        close_price=r[4],
        volume=r[5])


def prepare_data_h(array):
    if len(array) != 6:
        raise AttributeError

    array[0] = parse_date(array[0])
    array[1] = locale.atof(array[1])
    array[2] = locale.atof(array[2])
    array[3] = locale.atof(array[3])
    array[4] = locale.atof(array[4])
    array[5] = locale.atoi(array[5])

    return array



def parse_date(date_in_text):
    try:
        return datetime.strptime(date_in_text, '%m/%d/%Y').date()
    except ValueError:
        return date.today()
# delete fallback

def prepare_date_i(array):
    if len(array) != 8:
        raise AttributeError
    array[2] = datetime.strptime(array[2], '%m/%d/%Y').date()
    array[-3] = locale.atoi(array[-3])
    array[-2] = locale.atof(array[-2])
    array[-1] = locale.atoi(array[-1])

    return array


if __name__ == '__main__':
    main()
