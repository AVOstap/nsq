# coding: utf-8

import json
from datetime import date

from dateutil.relativedelta import relativedelta

from django.db.models import Min, Max
from django.http import JsonResponse, Http404
from django.template.response import TemplateResponse

from app.utils import pairwise, parse_date
from app.models import Company, InsTrade, Trade


def index(request, is_json_response):
    companys = Company.objects.all()

    if is_json_response:
        return JsonResponse({'company': [comp.code for comp in companys]})

    context = {
        'comp_qs': companys,
    }

    return TemplateResponse(request, 'app/index.html', context)


def ticker(request, tick, is_json_response):
    three_month_ago = date.today() - relativedelta(months=3)
    trade_qs = Trade.objects.filter(company__code=tick, date__gte=three_month_ago)

    if is_json_response:
        return JsonResponse({'trades': [{'date': trade.date,
                                         'open': trade.open_price,
                                         'high': trade.high_price,
                                         'close': trade.close_price,
                                         } for trade in trade_qs]})

    context = {
        'trade_qs': trade_qs,
        'tick': tick,
    }

    return TemplateResponse(request, 'app/ticker.html', context)


def insider(request, tick, is_json_response):
    ins_trade = InsTrade.objects.filter(company__code=tick)

    if is_json_response:
        return JsonResponse({'insider trades': [{
                                                    'insider': trade.insider.name,
                                                    'relation': trade.relation,
                                                    'date': trade.date,
                                                    'transaction_type': trade.transaction_type,
                                                    'owner_type': trade.owner_type,
                                                    'shares_traded': trade.shares_traded,
                                                    'last_price': trade.last_price,
                                                    'shares_head': trade.shares_head,
                                                } for trade in ins_trade]})

    context = {
        'instrade_qs': ins_trade,
        'tick': tick,
    }

    return TemplateResponse(request, 'app/insider.html', context)


def insider_trade(request, tick, name, is_json_response):
    ins_trade_qs = InsTrade.objects.filter(company__code=tick, insider__name=name)

    if is_json_response:
        return JsonResponse({name: [{
                                        'relation': trade.relation,
                                        'date': trade.date,
                                        'transaction_type': trade.transaction_type,
                                        'owner_type': trade.owner_type,
                                        'shares_traded': trade.shares_traded,
                                        'last_price': trade.last_price,
                                        'shares_head': trade.shares_head,
                                    } for trade in ins_trade_qs]})

    context = {
        'instrade_qs': ins_trade_qs,
        'name': name,
        'tick': tick,
    }

    return TemplateResponse(request, 'app/insider_trade.html', context)


def analytics(request, tick, is_json_response):
    try:
        date_from = parse_date(request.GET['date_from'])
        date_to = parse_date(request.GET['date_to'])
    except KeyError:
        raise Http404

    qs = Trade.objects.filter(company__code=tick, date__range=(date_from, date_to)).order_by('-date')
    open_price_list, high_price_list, low_price_list, close_price_list, date_list = zip(
        *qs.values_list('open_price', 'high_price', 'low_price', 'close_price', 'date'))

    data = [open_price_list, high_price_list, low_price_list, close_price_list, ]
    new_data = [map(lambda x: round(x[0] - x[1], 2), pairwise(d)) for d in data]
    new_data = zip(date_list[:-1], *new_data)

    if is_json_response:
        return JsonResponse({'analytics': [{
                                               'date': date,
                                               'open_delta': open_delta,
                                               'high_delta': high_delta,
                                               'low_delta': low_delta,
                                               'close_delta': close_delta
                                           } for date, open_delta, high_delta, low_delta, close_delta in new_data]
                             })

    context = {
        'date_from': date_from,
        'date_to': date_to,
        'tick': tick,
        'open_price_list': json.dumps(open_price_list),
        'high_price_list': json.dumps(high_price_list),
        'low_price_list': json.dumps(low_price_list),
        'close_price_list': json.dumps(close_price_list),
        'date_list': json.dumps(tuple(map(lambda date: date.strftime('%Y-%m-%d'), date_list))),
        'range': qs.aggregate(Max('high_price'), Min('low_price')),
        'new_data': new_data,
    }

    return TemplateResponse(request, 'app/analytics.html', context)


def delta(request, tick, is_json_response):
    model_fields = {'open': 'open_price', 'high': 'high_price', 'low': 'low_price', 'close': 'close_price'}

    try:
        value = int(request.GET['value'])
        price_type = request.GET['type']
        model_field = model_fields[price_type]
    except (KeyError, ValueError):
        raise Http404

    trade_list = list(Trade.objects.filter(company__code=tick).order_by('date'))

    result = get_price_difference(trade_list, model_field, value)

    if is_json_response:
        return JsonResponse({'result': [{
                                            'start_data': start_data,
                                            'end_data': end_data,
                                            'delta': delta
                                        } for start_data, end_data, delta in result]})

    context = {
        'result': result,
        'tick': tick,
    }

    return TemplateResponse(request, 'app/delta.html', context)


def get_price_difference(trade_list, model_field, value):
    result = []

    for i in range(len(trade_list)):
        for j in range(i + 1, len(trade_list)):
            trades_delta = getattr(trade_list[j], model_field) - getattr(trade_list[i], model_field)
            if abs(trades_delta) >= value:
                result.append((abs(trade_list[i].date - trade_list[j].date).total_seconds(), i, j, trades_delta))
                break

    if result:
        result = sorted(result)
        min_span_time = result[0][0]
        result = [(trade_list[start_index].date, trade_list[end_index].date, round(trades_delta, 2)) for
                  span_time, start_index, end_index, trades_delta in result
                  if span_time == min_span_time]

    return result
