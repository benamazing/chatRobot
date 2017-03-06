# -*- coding:utf-8 -*-
# encoding=utf-8
__author__ = 'LIBE5'
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import pymongo
import threading
import json
import logging
import datetime
import csv

THREAD_NUMS = 20

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
mongo_collection = mongo_db[stock_hist_data_collection_name]

logging.warn('start')

days = mongo_collection.find({"total_dd":{"$gt":0}}).distinct(key="date")
days.sort()
start_dt = days[0]

codes = mongo_collection.distinct(key="code")
csvfile = file('result.csv', 'wb')
writer = csv.writer(csvfile)
writer.writerow(['code', 'name', 'outstanding', 'totals', 'pe', 'holders', 'date', 'open', 'high', 'close', 'low', 'volume', 'p_change',
                 'total_dd', 'total_buy_dd', 'total_sell_dd',
                 'last_30_mins_dd', 'last_30_mins_buy_dd', 'last_30_mins_sell_dd',
                 'last_15_mins_dd', 'last_15_mins_buy_dd', 'last_15_mins_sell_dd',
                 'total_dd_in_rmb', 'total_dd_out_rmb', 'last_15_mins_dd_in_rmb',
                 'last_15_mins_dd_out_rmb', 'last_30_mins_dd_in_rmb', 'last_30_mins_dd_out_rmb',
                 'next_day_high_p', 'next_day_close_p'])

for code in codes:
    code_info = mongo_db['stock_general_info'].find_one({"code":code}, {"_id":0})
    if code_info is None:
        print code
        continue
    code_name = code_info['name']
    timeToMarket = code_info['timeToMarket']
    outstanding = code_info['outstanding']
    totals = code_info['totals']
    pe = code_info['pe']
    holders = code_info['holders']
    rs = mongo_collection.find({"code":code, "date":{"$gt":start_dt}}).sort("date", 1)
    sorted_rs = list(rs)
    if len(sorted_rs) == 0:
        continue

    for i in range(0, len(sorted_rs)-1):
        sorted_rs[i]['next_day_high_p'] = round((sorted_rs[i+1]['high'] / sorted_rs[i]['close'] - 1) * 100, 2)
        sorted_rs[i]['next_day_close_p'] = round((sorted_rs[i+1]['close'] / sorted_rs[i]['close'] - 1) * 100, 2)
    for i in sorted_rs:
        total_dd = 'N/A'
        total_buy_dd = 'N/A'
        total_sell_dd = 'N/A'
        last_30_mins_dd = 'N/A'
        last_30_mins_buy_dd = 'N/A'
        last_30_mins_sell_dd = 'N/A'
        last_15_mins_dd = 'N/A'
        last_15_mins_buy_dd = 'N/A'
        last_15_mins_sell_dd = 'N/A'
        total_dd_in_rmb = 'N/A'
        total_dd_out_rmb = 'N/A'
        last_15_mins_dd_in_rmb = 'N/A'
        last_15_mins_dd_out_rmb = 'N/A'
        last_30_mins_dd_in_rmb = 'N/A'
        last_30_mins_dd_out_rmb = 'N/A'
        p_change = 'N/A'
        next_day_high_p = 'N/A'
        next_day_close_p = 'N/A'

        
        if i.has_key('p_change'):
            p_change = i['p_change']
        if i.has_key('next_day_high_p'):
            next_day_high_p = i['next_day_high_p']
        if i.has_key('next_day_close_p'):
            next_day_close_p = i['next_day_close_p']

        if i.has_key('total_dd'):
            total_dd = i['total_dd']
        if i.has_key('total_buy_dd'):
            total_buy_dd = i['total_buy_dd']
        if i.has_key('total_sell_dd'):
            total_sell_dd = i['total_sell_dd']
        if i.has_key('last_30_mins_dd'):
            last_30_mins_dd = i['last_30_mins_dd']
        if i.has_key('last_30_mins_buy_dd'):
            last_30_mins_buy_dd = i['last_30_mins_buy_dd']
        if i.has_key('last_30_mins_sell_dd'):
            last_30_mins_sell_dd = i['last_30_mins_sell_dd']
        if i.has_key('last_15_mins_dd'):
            last_15_mins_dd = i['last_15_mins_dd']
        if i.has_key('last_15_mins_buy_dd'):
            last_15_mins_buy_dd = i['last_15_mins_buy_dd']
        if i.has_key('last_15_mins_sell_dd'):
            last_15_mins_sell_dd = i['last_15_mins_sell_dd']

        if i.has_key('total_dd_in_rmb'):
            total_dd_in_rmb = i['total_dd_in_rmb']
        if i.has_key('total_dd_out_rmb'):
            total_dd_out_rmb = i['total_dd_out_rmb']
        if i.has_key('last_15_mins_dd_in_rmb'):
            last_15_mins_dd_in_rmb = i['last_15_mins_dd_in_rmb']
        if i.has_key('last_15_mins_dd_out_rmb'):
            last_15_mins_dd_out_rmb = i['last_15_mins_dd_out_rmb']
        if i.has_key('last_30_mins_dd_in_rmb'):
            last_30_mins_dd_in_rmb = i['last_30_mins_dd_in_rmb']
        if i.has_key('last_30_mins_dd_out_rmb'):
            last_30_mins_dd_out_rmb = i['last_30_mins_dd_out_rmb']

        if next_day_high_p != 'N/A' and next_day_close_p != 'N/A' and p_change != 'N/A':
            writer.writerow([i['code'], code_name, outstanding, totals, pe, holders, i['date'], i['open'],i['high'],i['close'],i['low'],i['volume'], p_change,
                             total_dd,total_buy_dd,total_sell_dd,
                             last_30_mins_dd,last_30_mins_buy_dd, last_30_mins_sell_dd,
                             last_15_mins_dd,last_15_mins_buy_dd, last_15_mins_sell_dd,
                             total_dd_in_rmb, total_dd_out_rmb, last_15_mins_dd_in_rmb,
                             last_15_mins_dd_out_rmb, last_30_mins_dd_in_rmb, last_30_mins_dd_out_rmb,
                             next_day_high_p,next_day_close_p])
csvfile.close()

logging.warn('end')



