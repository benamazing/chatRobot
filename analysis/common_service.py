# -*- coding:utf-8 -*-
# encoding=utf-8

import sys
sys.path.append('..')

import tushare as ts
import finance_crawler
import pymongo
import json
import redis

mongo_host = '127.0.0.1'
mongo_db_name = 'stock'

with open("../conf.json") as f:
    conf_str = f.read()
    conf = json.loads(conf_str)
    if r'mongo_host' in conf:
        mongo_host = conf[r'mongo_host']
    if r'redis_server_host' in conf:
        redis_host = conf[r'redis_server_host']
        redisClient = redis.StrictRedis(host=redis_host)

mongo_client = pymongo.MongoClient(host=mongo_host, port=27017)
mongo_db = mongo_client[mongo_db_name]
stock_general_info = mongo_db['stock_general_info']
stock_hist_data = mongo_db['stock_hist_data']

def get_stock_hist_high_and_low(code=None, days=30):
    if code is None:
        return None
    hist_data = stock_hist_data.find({"code":code}).sort("date",-1).limit(days)
    if hist_data is None or hist_data.count() == 0:
        return None
    high = 0
    low = 1000000
    for row in hist_data:
        if row['high'] > high:
            high = row['high']
            high_date = row['date']
        if row['low'] < low:
            low = row['low']
            low_date = row['date']
    return high, high_date, low, low_date

if __name__ == '__main__':
    print get_stock_hist_high_and_low(code='000001', days=300)
