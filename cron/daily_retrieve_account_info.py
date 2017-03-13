# -*- coding:utf-8 -*-
# encoding=utf-8

import sys
sys.path.append('..')
import tushare as ts
import json
import pymongo
import logging
import threading
import datetime
import easytrader

'''每天获取当天的账户持股和资金状况'''


class Account(object):
    def __init__(self):
        self.mongo_host = '127.0.0.1'
        self.mongo_port = 27017
        self.mongo_db_name = 'stock'
        self.thread_nums = 20

        with open("../conf.json") as f:
            conf_str = f.read()
            conf = json.loads(conf_str)
            if r'mongo_host' in conf:
                self.mongo_host = conf['mongo_host']
            if r'mongo_db_name' in conf:
                self.mongo_db_name = conf['mongo_db_name']

        self.mongoClient = pymongo.MongoClient(host=self.mongo_host, port=self.mongo_port)
        self.stockDB = self.mongoClient[self.mongo_db_name]
        self.balance_collection = self.stockDB['account_balance']
        self.hold_stocks_collections = self.stockDB['hold_stocks']
        self.user = easytrader.use('gf')


    def retrieve_balance(self):
        self.user.prepare('gf.json')
        balance = self.user.balance
        item = {}
        item['total_assets'] = balance['data'][0]['asset_balance']
        item['enable_balance'] = balance['data'][0]['enable_balance']
        item['market_balance'] = balance['data'][0]['market_value']
        now = datetime.datetime.now()
        item['date'] = now.strftime("%Y-%m-%d")
        item['time'] = now.strftime('%H:%M:%S')
        self.balance_collection.insert(item)


    def retrieve_hold_stocks(self):
        self.user.prepare('gf.json')
        position = self.user.get_position()
        hold_stocks = {}

        if position is not None and position['success'] is True:
            hold_stocks['total'] = position['total']
            hold_stocks['list'] = []
            for item in position['data']:
                x = {}
                x['av_buy_price'] = item['av_buy_price']
                x['current_amount'] = item['current_amount']
                x['stock_code'] = item['stock_code']
                x['stock_name'] = item['stock_name']
                x['profit'] = item['income_balance']
                hold_stocks['list'].append(x)
            now = datetime.datetime.now()
            hold_stocks['date'] = now.strftime('%Y-%m-%d')
            hold_stocks['time'] = now.strftime('%H:%M:%S')
            self.hold_stocks_collections.insert(hold_stocks)


if __name__ == '__main__':
    account = Account()
    account.retrieve_balance()
    account.retrieve_hold_stocks()


