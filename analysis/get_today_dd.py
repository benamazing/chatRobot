# -*- coding:utf-8 -*-
# encoding=utf-8
__author__ = 'LIBE5'

''' 获取当天到目前为止的大单量 '''

import tushare as ts
import time
import threading
import logging
import datetime
import copy

THREAD_NUMS = 30
TOP_COUNT = 30
logging.basicConfig(level=logging.INFO,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S')

# Global variables
today = datetime.datetime.now().strftime('%Y-%m-%d')
stocks = ts.get_stock_basics()
results = []

# 超过1000手的算大单
vol = 1000

def get_realtime_dd_multi_threads(stock_list, **kwargs):
        threads = []
        for i in range(THREAD_NUMS):
            t = threading.Thread(target=get_realtime_dd_single_thread, args=(stock_list, i,))
            threads.append(t)
        for t in threads:
            t.setDaemon(True)
            t.start()
        for t in threads:
            t.join()


def get_realtime_dd_single_thread(stock_list, threadNo):
    ind = 0
    for code in stock_list.index:
        ind += 1
        if ind % THREAD_NUMS != threadNo:
            continue
        item = {}
        item['code'] = code
        df = ts.get_sina_dd(code=code, date=today, vol=vol)
        item['dd_total'] = 0
        item['dd_buy'] = 0
        item['dd_sell'] = 0

        if df is not None:
            for idx in df.index:
                item['dd_total'] += 1
                if df.ix[idx]['type'] == '买盘':
                    item['dd_buy'] += 1
                if df.ix[idx]['type'] == '卖盘':
                    item['dd_sell'] +=1
        results.append(item)

pre_results = []
while True:
    logging.info('start...')
    print '%-10s\tcode\tbuy\tsell\ttotal\tprice\thigh\tp_change\ttrend' % 'name'
    time.sleep(1)
    results = []
    get_realtime_dd_multi_threads(stock_list=stocks)
    results = sorted(results, key=lambda x:x['dd_buy'], reverse=True)
    codes = [results[x]['code'] for x in range(TOP_COUNT)]
    df = ts.get_realtime_quotes(codes)
    id = 0
    for idx in df.index:
        results[id]['name'] = df.ix[idx]['name']
        results[id]['pre_close'] = float(df.ix[idx]['pre_close'])
        results[id]['price'] = float(df.ix[idx]['price'])
        results[id]['high'] = float(df.ix[idx]['high'])
        results[id]['p_change'] = round((results[idx]['price'] / results[idx]['pre_close'] - 1) * 100, 2)
        id += 1

    top_results = results[0:TOP_COUNT]

    if len(pre_results) == 0:
        pre_results = copy.deepcopy(top_results)

    for x in range(TOP_COUNT):
        item = top_results[x]
        matched = False
        previous_rank = 1000
        for y in range(TOP_COUNT):
            if item['code'] == pre_results[y]['code']:
                matched = True
                break
        if matched is True:
            previous_rank = y
        if x > previous_rank:
            arrow = u'↓%d' % (x - previous_rank)
        elif x == previous_rank:
            arrow = '-'
        else:
            if previous_rank == 1000:
                arrow = u'↑new'
            else:
                arrow = u'↑%d' % (previous_rank - x)

        print '%-10s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s' % (results[x]['name'], results[x]['code'], results[x]['dd_buy'], results[x]['dd_sell'],
                                        results[x]['dd_total'], results[x]['price'], results[x]['high'], results[x]['p_change'], arrow)

    pre_results = copy.deepcopy(top_results)
    time.sleep(1)
    logging.info("stop for 1 minute, wait for next time...")
    time.sleep(60)
