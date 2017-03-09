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
redisClient = None

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

# get hs300
hs300_array = []
if redisClient is None:
    print 'Retriving hs300 from tushare...'
    hs300 = ts.get_hs300s()
    for x in hs300.code:
        hs300_array.append(x)
else:
    hs300 = redisClient.get("hs300_list")
    if hs300 is None or hs300 == '':
        df = ts.get_hs300s()
        sorted_list = df.sort_values('weight', ascending=False)
        result = [{"code":sorted_list.ix[i]['code'], "name": sorted_list.ix[i]['name'], "weight": sorted_list.ix[i]['weight']} for i in sorted_list.index]
        data = {"data": result}
        redisClient.set("hs300_list", json.dumps(data), ex=86400)
    print 'Retrieveing hs300 from cache...'
    hs300_json_str = redisClient.get("hs300_list")
    hs300_json = json.loads(hs300_json_str)
    for stocks in hs300_json['data']:
        hs300_array.append(stocks['code'])

def avg_debt_to_asset_ratio():
    ratios = []
    rs = stock_general_info.find()
    for row in rs:
        ratios.append(row['total_debt'] / row['totalAssets'])
    avg_ration = float(sum(ratios)) / len(ratios)
    return avg_ration


def select_stocks():
    selected = []
    avg_ratio = avg_debt_to_asset_ratio()
    for code in hs300_array:
        rs = stock_general_info.find({"code": code})
        if rs.count() != 1:
            continue
        stock = rs[0]
        pb = stock['pb']
        total_asset = stock['totalAssets']
        total_debt = stock['total_debt']
        liquid_asset = stock['liquidAssets']
        current_debt = stock['current_debt']

        # 筛掉市净率大于2的
        if pb <= 0 or pb >= 2:
            continue

        # 筛掉资产负债率小于平均值的
        if total_debt / total_asset <= avg_ratio:
            continue

        # 筛掉流动资产不足流动负债1.2倍的
        if current_debt == 0:
            continue
        if liquid_asset / current_debt <= 1.2:
            continue

        selected.append(code)

    return  selected

if __name__ == '__main__':
    stocks = select_stocks()
    for code in stocks:
        stock = stock_general_info.find_one({"code": code})
        print '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s' % (stock['code'], stock['name'], stock['pb'],
                                          stock['pe'], stock['totalAssets'], stock['liquidAssets'],
                                          stock['total_debt'], stock['current_debt'],
                                                       round(stock['liquidAssets']/stock['current_debt'], 2),
                                                       round(stock['total_debt']/stock['totalAssets'], 2))



