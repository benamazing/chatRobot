# -*- coding:utf-8 -*-
# encoding=utf-8

import sys
sys.path.append('..')

__author__ = 'LIBE5'
'''获取股票大单交易数据，股票交易超过500手的大单数'''

import datetime
import pymongo
import threading
import json
import tushare as ts
import logging

THREAD_NUMS = 30
logging.basicConfig(level=logging.WARN,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S')

mongo_host = '127.0.0.1'
mongo_db_name = 'stock'
stock_hist_data_collection_name = 'stock_hist_data'

with open("../conf.json") as f:
    conf_str = f.read()
    conf = json.loads(conf_str)
    if r'mongo_host' in conf:
        mongo_host = conf[r'mongo_host']

mongo_client = pymongo.MongoClient(host=mongo_host, port=27017)
mongo_db = mongo_client[mongo_db_name]
hist_data_collection = mongo_db[stock_hist_data_collection_name]

def get_all_dd(start, end=None):
    start_date = datetime.datetime.strptime(start, '%Y-%m-%d')
    if end is None:
        end_date = datetime.datetime.now() - datetime.timedelta(days=1)
    else:
        end_date = datetime.datetime.strptime(end, '%Y-%m-%d')
    df = ts.get_stock_basics()
    idx = start_date
    while idx <= end_date:
        date = idx.strftime('%Y-%m-%d')
        get_dd_by_date_multi_threads(date=date, stock_list=df)
        idx = idx + datetime.timedelta(days=1)


def get_dd_by_date_multi_threads(date, stock_list, **kwargs):
    count = hist_data_collection.count({"date": date})
    if count != 0:
        logging.warn("%s: start..." % date)
        threads = []
        for i in range(THREAD_NUMS):
            t = threading.Thread(target=get_dd_by_date_single_thread, args=(date, stock_list, i,))
            threads.append(t)
        for t in threads:
            t.setDaemon(True)
            t.start()
        for t in threads:
            t.join()
        logging.warn("%s: end..." % date)


def get_dd_by_date_single_thread(date, stock_list, threadNo):
    ind = 0
    for code in stock_list.index:
        ind += 1
        if ind % THREAD_NUMS != threadNo:
            continue
        try:
            df = ts.get_sina_dd(code=code, date=date, vol=500)
            total_buy_500 = 0
            total_sell_500 = 0
            total_500 = 0
            last_15_mins_buy_500 = 0
            last_15_mins_sell_500 = 0
            last_15_mins_500 = 0
            last_30_mins_buy_500 = 0
            last_30_mins_sell_500 = 0
            last_30_mins_500 = 0
            if df is not None and len(df) > 0:
                total_500 = len(df)
                for idx in df.index:
                    if df.ix[idx]['type'] == '买盘':
                        total_buy_500 += 1
                        if df.ix[idx]['time'] >= '14:30:00':
                            last_30_mins_buy_500 += 1
                            last_30_mins_500 += 1
                            if df.ix[idx]['time'] >= '14:30:15':
                                last_15_mins_buy_500 +=1
                                last_15_mins_500 +=1
                    if df.ix[idx]['type'] == '卖盘':
                        total_sell_500 +=1
                        if df.ix[idx]['time'] >= '14:30:00':
                            last_30_mins_sell_500 += 1
                            last_30_mins_500 += 1
                            if df.ix[idx]['time'] >= '14:30:15':
                                last_15_mins_sell_500 +=1
                                last_15_mins_500 +=1

            hist_data_collection.update_one({"code":code, "date":date},
                                            {"$set":{"total_500":total_500,
                                                     "total_buy_500":total_buy_500,
                                                     "total_sell_500": total_sell_500,
                                                     "last_15_mins_buy_500": last_15_mins_buy_500,
                                                     "last_15_mins_sell_500": last_15_mins_sell_500,
                                                     "last_15_mins_500": last_15_mins_500,
                                                     "last_30_mins_buy_500": last_30_mins_buy_500,
                                                     "last_30_mins_sell_500": last_30_mins_sell_500,
                                                     "last_30_mins_500": last_30_mins_500,
                                                     }})
        except:
            logging.exception("%s, %s: got exception" % (code, date))

if __name__ == '__main__':
    start_day = (datetime.datetime.now() - datetime.timedelta(days=4)).strftime('%Y-%m-%d')
    get_all_dd(start=start_day)

