# -*- coding:utf-8 -*-
# encoding=utf-8
__author__ = 'LIBE5'

import pymongo
import logging
import json
import threading
import datetime

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

code_list = hist_data_collection.distinct(key='code')

def cal_price_change_all():
    code_list = hist_data_collection.distinct(key='code')
    threads = []
    for i in range(THREAD_NUMS):
        t = threading.Thread(target=cal_price_change_single_thread, args=(code_list, i,))
        threads.append(t)
    for t in threads:
        t.setDaemon(True)
        t.start()
    for t in threads:
        t.join()

def cal_price_change_single_thread(code_list, threadNo):
    ind = 0
    for code in code_list:
        ind += 1
        if ind % THREAD_NUMS != threadNo:
            continue
        cal_stock_price_change(stock_code=code)

def cal_stock_price_change(stock_code=None):
    logging.info('%s: start' % stock_code)
    results = hist_data_collection.find({"code":stock_code}).sort("date", 1)
    data_list = list(results)
    for x in range(1,len(data_list)):
        pre_close = data_list[x-1]['close']
        close = data_list[x]['close']
        p_change = round((close / pre_close - 1) * 100, 2)
        hist_data_collection.update_one({"code": stock_code, "date": data_list[x]['date']}, {"$set":{"p_change":p_change}})
    logging.info('%s: end' % stock_code)

if __name__ == '__main__':
    start = datetime.datetime.now()
    print '%s: start' % start.strftime("%Y-%m-%d %H:%M:%S")
    cal_price_change_all()
    end = datetime.datetime.now()
    print '%s: end' % end.strftime("%Y-%m-%d %H:%M:%S")
    print 'cost time: %s' % (end-start)