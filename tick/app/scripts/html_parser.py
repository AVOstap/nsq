# coding: utf-8

from BeautifulSoup import BeautifulSoup


def parse(html):
    b = BeautifulSoup(html)
    data_table = b.find('div', {'class': 'genTable'})

    if not data_table:
        return

    for tr_tag in data_table.findAll('tr'):
        data_list = []

        for td_tag in tr_tag.findAll('td'):
            if td_tag.string:
                data_list.append(td_tag.string.strip())
            else:
                data_list.append(td_tag.a.string)

        if not data_list:
            continue

        yield data_list
