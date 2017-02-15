# -*- coding:utf-8 -*-
# encoding=utf-8
__author__ = 'LIBE5'

''' 获取当天都目前为止的大单量 '''

import tushare as ts
import time
import threading
import logging
import datetime

THREAD_NUMS = 30
logging.basicConfig(level=logging.INFO,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S')

# Global variables
today = datetime.datetime.now().strftime('%Y-%m-%d')
stocks = ts.get_stock_basics()
results = []

# 超过500手的算大单
vol = 500

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
        if df is None:
            item['over_500_total'] = 0
        else:
            item['over_500_total'] = len(df)
        results.append(item)


while True:
    logging.info('start...')
    print 'name', 'code', 'over_500_total', 'price', 'high', 'p_change'
    time.sleep(1)
    results = []
    get_realtime_dd_multi_threads(stock_list=stocks)
    results = sorted(results, key=lambda x:x['over_500_total'], reverse=True)
    codes = [results[x]['code'] for x in range(30)]
    df = ts.get_realtime_quotes(codes)
    id = 0
    for idx in df.index:
        results[id]['name'] = df.ix[idx]['name']
        results[id]['pre_close'] = float(df.ix[idx]['pre_close'])
        results[id]['price'] = float(df.ix[idx]['price'])
        results[id]['high'] = float(df.ix[idx]['high'])
        results[id]['p_change'] = round((results[idx]['price'] / results[idx]['pre_close'] - 1) * 100, 2)
        id += 1

    for x in range(30):
        print results[x]['name'], results[x]['code'], results[x]['over_500_total'], results[x]['price'], results[x]['high'], results[x]['p_change']

    time.sleep(1)
    logging.info("stop for 5 minutes, wait for next time...")
    time.sleep(300)
