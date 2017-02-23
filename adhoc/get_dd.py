# -*- coding:utf-8 -*-
# encoding=utf-8

__author__ = 'LIBE5'
'''获取股票大单交易数据，股票金额超过100万的大单数'''

import datetime
import pymongo
import threading
import json
import tushare as ts
import logging
import analysis

THREAD_NUMS = 30
logging.basicConfig(level=logging.WARN,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S')

mongo_host = '127.0.0.1'
mongo_db_name = 'stock'
stock_hist_data_collection_name = 'stock_hist_data'

# 超过100万才算大单
# amount可选值: 50, 100, 200, 500, 1000
AMOUNT = 100

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
            df = analysis.get_sina_dd_by_amount(code=code, date=date, amount=AMOUNT)
            total_buy_dd = 0
            total_sell_dd = 0
            total_dd = 0
            last_15_mins_buy_dd = 0
            last_15_mins_sell_dd = 0
            last_15_mins_dd = 0
            last_30_mins_buy_dd = 0
            last_30_mins_sell_dd = 0
            last_30_mins_dd = 0
            total_dd_in_rmb = 0
            total_dd_out_rmb = 0
            last_15_mins_dd_in_rmb = 0
            last_15_mins_dd_out_rmb = 0
            last_30_mins_dd_in_rmb = 0
            last_30_mins_dd_out_rmb = 0
            if df is not None and len(df) > 0:
                total_dd = len(df)
                for idx in df.index:
                    if df.ix[idx]['type'] == '买盘':
                        total_buy_dd += 1
                        total_dd_in_rmb += df.ix[idx]['volume'] * df.ix[idx]['price']
                        if df.ix[idx]['time'] >= '14:30:00':
                            last_30_mins_buy_dd += 1
                            last_30_mins_dd += 1
                            last_30_mins_dd_in_rmb += df.ix[idx]['volume'] * df.ix[idx]['price']
                            if df.ix[idx]['time'] >= '14:30:15':
                                last_15_mins_buy_dd +=1
                                last_15_mins_dd +=1
                                last_15_mins_dd_in_rmb += df.ix[idx]['volume'] * df.ix[idx]['price']
                    if df.ix[idx]['type'] == '卖盘':
                        total_sell_dd +=1
                        total_dd_out_rmb += df.ix[idx]['volume'] * df.ix[idx]['price']
                        if df.ix[idx]['time'] >= '14:30:00':
                            last_30_mins_sell_dd += 1
                            last_30_mins_dd += 1
                            last_30_mins_dd_out_rmb += df.ix[idx]['volume'] * df.ix[idx]['price']
                            if df.ix[idx]['time'] >= '14:30:15':
                                last_15_mins_sell_dd +=1
                                last_15_mins_dd +=1
                                last_15_mins_dd_out_rmb += df.ix[idx]['volume'] * df.ix[idx]['price']

            hist_data_collection.update_one({"code":code, "date":date},
                                            {"$set":{"total_dd":total_dd,
                                                     "total_buy_dd":total_buy_dd,
                                                     "total_sell_dd": total_sell_dd,
                                                     "last_15_mins_buy_dd": last_15_mins_buy_dd,
                                                     "last_15_mins_sell_dd": last_15_mins_sell_dd,
                                                     "last_15_mins_dd": last_15_mins_dd,
                                                     "last_30_mins_buy_dd": last_30_mins_buy_dd,
                                                     "last_30_mins_sell_dd": last_30_mins_sell_dd,
                                                     "last_30_mins_dd": last_30_mins_dd,
                                                     "total_dd_in_rmb": total_dd_in_rmb,
                                                     "total_dd_out_rmb": total_dd_out_rmb,
                                                     "last_15_mins_dd_in_rmb": last_15_mins_dd_in_rmb,
                                                     "last_15_mins_dd_out_rmb": last_15_mins_dd_out_rmb,
                                                     "last_30_mins_dd_in_rmb": last_30_mins_dd_in_rmb,
                                                     "last_30_mins_dd_out_rmb": last_30_mins_dd_out_rmb
                                                     }})
        except:
            logging.exception("%s, %s: got exception" % (code, date))

if __name__ == '__main__':
    get_all_dd(start='2017-02-03')

