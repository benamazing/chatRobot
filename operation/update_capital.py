# -*- coding:utf-8 -*-
# encoding=utf-8

import json
import pymongo
import tushare as ts
import sys
sys.path.append('..')

mongo_host = '127.0.0.1'
mongo_port = 27017
mongo_db_name = 'stock'

with open("../conf.json") as f:
    conf_str = f.read()
    conf = json.loads(conf_str)
    if r'mongo_host' in conf:
        mongo_host = conf['mongo_host']
    if r'mongo_db_name' in conf:
        mongo_db_name = conf['mongo_db_name']

mongoClient = pymongo.MongoClient(host=mongo_host, port=mongo_port)
stockDB = mongoClient[mongo_db_name]
hist_data_collection = stockDB['stock_hist_data']

strategy_collection = stockDB['stock_strategies']
capital_collection = stockDB['stock_capitals']
hold_stocks_collection = stockDB['stock_hold_stocks']

def update_capital_by_strategy_name(strategy_name):
    rs = hold_stocks_collection.find({"strategy_name": strategy_name}).sort("date", -1).limit(1)
    if rs.count() == 0:
        return
    stocks = rs[0]['stocks']
    market_cap = 0
    for code in stocks.keys():
        df = ts.get_realtime_quotes(code)
        price = float(df.ix[0]['price'])
        market_cap += price * int(stocks[code])
    rs2 = capital_collection.find({"strategy_name": strategy_name}).sort("date", -1).limit(1)
    if rs2.count() == 0:
        return
    current_balance = rs2[0]['balance']
    date = rs2[0]['date']
    total_cap = current_balance + market_cap
    capital_collection.update({"strategy_name": strategy_name, "date": date}, {"$set": {"total_cap": total_cap, "market_cap": market_cap}})


def update_all_capital():
    rs = strategy_collection.find({})
    if rs.count() == 0:
        return
    for strategy in rs:
        strategy_name = strategy['strategy_name']
        update_capital_by_strategy_name(strategy_name)


if __name__ == '__main__':
    update_all_capital()


