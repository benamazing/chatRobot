# -*- coding:utf-8 -*-
# encoding=utf-8

import sys
sys.path.append('..')

import json
import pymongo
import tushare as ts
import datetime
import pandas as pd
from urllib2 import HTTPError
from util.mail_util import mail_service

class BaseScheduleOperation(object):

    def __init__(self, start, period, stock_amount, init_cap, send_mail=1, source='mongo'):
        self.mongo_host = '127.0.0.1'
        self.mongo_port = 27017
        self.mongo_db_name = 'stock'

        with open("../conf.json") as f:
            conf_str = f.read()
            conf = json.loads(conf_str)
            if r'mongo_host' in conf:
                self.mongo_host = conf['mongo_host']
            if r'mongo_db_name' in conf:
                self.mongo_db_name = conf['mongo_db_name']

        self.mongoClient = pymongo.MongoClient(host=self.mongo_host, port=self.mongo_port)
        self.stockDB = self.mongoClient[self.mongo_db_name]
        self.hist_data_collection = self.stockDB['stock_hist_data']

        # Initialize the strategy parameters
        self.strategy_collection = self.stockDB['stock_strategies']
        self.capital_collection = self.stockDB['stock_capitals']
        self.counter_collection = self.stockDB['stock_counters']
        self.hold_stocks_collection = self.stockDB['stock_hold_stocks']
        self.stock_holiday_collection = self.stockDB['stock_holidays']
        self.strategy_name = 'Basic Strategy'
        self.strategy = self.get_strategy_by_name(self.strategy_name)

        # 获取当前资金情况
        self.balance, self.market_cap, self.total_cap = self.get_current_capitals(self.strategy_name)

        # 获取计时器
        self.counter = self.get_current_counter(self.strategy_name)

        # 获取当前持仓
        self.hold_stocks = self.get_current_hold_stocks(self.strategy_name)

        self.stock_pool = []

        self.actions = []

        self.source = source

        # email content
        self.mail_content = ''
        self.stock_list_log = ''

        self.send_mail = send_mail

    def operate(self):
        today = datetime.datetime.now()

        # 周六日
        if today.weekday() == 5 or today.weekday() == 6:
            return

        count = self.stock_holiday_collection.count({"date": today.strftime('%Y-%m-%d')})

        # 节假日
        if count == 0:
            return

        if self.counter % self.strategy['period'] == 0:
            target_list = self.get_target_list()
            codes = [item['code'] for item in target_list]

            # 卖出不在target_list里面的股票
            for code in self.hold_stocks.keys():
                if code not in codes:
                    self.sell(code)

            # 卖出ST股
            df = ts.get_stock_basics()
            for code in self.hold_stocks.keys():
                if df.ix[code]['name'].find('*ST') >= 0:
                    self.sell(code)

            # 买入不在持有列表里的股票
            will_buy_list = []
            for code in codes:
                if code not in self.hold_stocks.keys():
                    will_buy_list.append(target_list[codes.index(code)])
            self.buy(will_buy_list)
        self.counter += 1

    def get_target_list(self):
        return []

    def buy(self, target_list):
        date_str = datetime.datetime.now().strftime('%Y-%m-%d')
        if len(target_list) == 0:
            return
        piece_cap = self.balance / len(target_list)
        df = ts.get_realtime_quotes(symbols=[x['code'] for x in target_list])
        df = df.set_index('code')
        for target in target_list:
            if target['code'] in df.index():
                open_price = df.ix[target['code']]['open']
                buy_amount = int(piece_cap / (open_price * 100)) * 100
                self.hold_stocks[target['code']] = buy_amount
                self.balance -= buy_amount * open_price
                action = dict()
                action['operation'] = 'buy'
                action['code'] = target['code']
                action['name'] = target['name']
                action['price'] = open_price
                action['amount'] = buy_amount

                self.actions.append(action)

    def sell(self, code):
        date_str = datetime.datetime.now().strftime('%Y-%m-%d')
        df = ts.get_realtime_quotes(code)
        if df is not None:
            open_price = df.iloc[0]['open']
            sell_amount = self.hold_stocks[code]
            self.hold_stocks.pop(code)
            self.balance = self.balance + sell_amount * open_price
            action = dict()
            action['operation'] = 'sell'
            action['code'] = code
            action['name'] = df.iloc[0]['name']
            action['price'] = open_price
            action['amount'] = sell_amount
            self.actions.append(action)

    def get_strategy_by_name(self, strategy_name):
        rs = self.strategy_collection.find({"strategy_name": strategy_name})
        if rs.count() == 0:
            return None
        return rs[0]

    def get_current_capitals(self, strategy_name):
        rs = self.capital_collection.find({"strategy_name": strategy_name})
        if rs.count() == 0:
            return 0, 0, 0
        return rs[0]['balance'], rs[0]['market_cap'], rs[0]['total_cap']

    def get_current_counter(self, strategy_name):
        rs = self.counter_collection.find({"strategy_name": strategy_name})
        if rs.count() == 0:
            return None
        return rs[0]['counter']

    def get_current_hold_stocks(self, strategy_name):
        dt = datetime.datetime.now() - datetime.timedelta(days=15)
        rs = self.hold_stocks_collection.find({"strategy_name": strategy_name}).sort("date", -1)
        if rs.count() == 0:
            return dict()
        return rs[0]['stocks']


