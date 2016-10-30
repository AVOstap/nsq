# coding: utf-8

import re
from bs4 import BeautifulSoup

try:
    # Python 3
    from urllib.parse import urlparse, parse_qs
except ImportError:
    # Python 2
    from urlparse import urlparse, parse_qs


def parse(html):
    html_tree = BeautifulSoup(html, 'html.parser')
    data_table = html_tree.find('div', {'class': 'genTable'})

    if not data_table:
        return

    for tr_tag in data_table.findAll('tr'):
        data_list = []

        for td_tag in tr_tag.findAll('td'):
            if td_tag.string:
                data_list.append(td_tag.string.strip())
            else:
                data_list.append('0')

        if not data_list or not any(data_list):
            continue

        yield data_list


def get_full_name(html):
    try:
        return re.search('followObjTitle = "(.+)";', html).group(1)
    except AttributeError:
        pass


def get_last_page_index_or_none(html):
    html_tree = BeautifulSoup(html, 'html.parser')
    last_page_link = html_tree.find(id='quotes_content_left_lb_LastPage')
    if not last_page_link:
        return
    last_page_query = urlparse(last_page_link['href']).query
    index = parse_qs(last_page_query)['page'][0]
    return int(index)


if __name__ == '__main__':
    import sys
    with open('goog.txt') as f:
        text = f.read()
    sys.stdout.write(str(get_last_page_index_or_none(text)))
    for i in parse(text):
        sys.stdout.write(str(i))
