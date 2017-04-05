# -*- coding:utf-8 -*-
# encoding=utf-8

import sys
sys.path.append('..')

import json
import pymongo
import tushare as ts
import datetime
from util.mail_util import mail_service


class BaseScheduleOperation(object):

    def __init__(self, send_mail=1):
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
        self.stock_actions_collection = self.stockDB['stock_daily_actions']
        self.stock_holiday_collection = self.stockDB['stock_holidays']
        self.strategy_name = self._get_strategy_name()

        self.strategy = self.get_strategy()

        # 获取当前资金情况
        self.balance, self.market_cap, self.total_cap = self.get_current_capitals()

        # 获取计时器
        self.counter = self.get_current_counter()

        # 获取当前持仓
        self.hold_stocks = self.get_current_hold_stocks()

        self.stocks_pool = []

        self.actions = []

        self.send_mail = send_mail
        # email content
        self.mail_content = ''
        self.stock_list_log = ''

    # need to be implemented
    @staticmethod
    def _get_strategy_name(self):
        return 'Basic Strategy'

    def operate(self):
        today = datetime.datetime.now()

        # 周六日
        if today.weekday() == 5 or today.weekday() == 6:
            print 'Today is weekend'
            self.mail_content += 'Today is weekend\r\n'
            return

        count = self.stock_holiday_collection.count({"date": today.strftime('%Y-%m-%d')})

        # 节假日
        if count > 0:
            print 'Today is holiday'
            self.mail_content += 'Today is holiday\r\n'
            return

        if self.counter % int(self.strategy['period']) == 0:
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

    # need to be implemented
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
            if target['code'] in df.index:
                open_price = float(df.ix[target['code']]['open'])
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

    def get_strategy(self):
        rs = self.strategy_collection.find({"strategy_name": self.strategy_name})
        if rs.count() == 0:
            return None
        return rs[0]

    def get_current_capitals(self):
        rs = self.capital_collection.find({"strategy_name": self.strategy_name}).sort("date", -1)
        if rs.count() == 0:
            return self.strategy['init_cap'], 0, self.strategy['init_cap']
        return rs[0]['balance'], rs[0]['market_cap'], rs[0]['total_cap']

    def get_current_counter(self):
        rs = self.counter_collection.find({"strategy_name": self.strategy_name})
        if rs.count() == 0:
            return None
        return rs[0]['counter']

    def get_current_hold_stocks(self):
        dt = datetime.datetime.now() - datetime.timedelta(days=15)
        rs = self.hold_stocks_collection.find({"strategy_name": self.strategy_name}).sort("date", -1)
        if rs.count() == 0:
            return dict()
        return rs[0]['stocks']

    def summary(self):
        print '%-15s%-15s%-15s%-15s%-15s' % ('Operation', 'Code', 'Name', 'Price', 'Amount')
        self.mail_content += '%-15s%-15s%-15s%-15s%-15s' % ('Operation', 'Code', 'Name', 'Price', 'Amount') + '\r\n'
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        for action in self.actions:
            print '%-15s%-15s%-15s%-15s%-15s' % (action['operation'], action['code'], action['name'], action['price'], action['amount'])
            self.mail_content += '%-15s%-15s%-15s%-15s%-15s' % (action['operation'], action['code'], action['name'], action['price'], action['amount']) + '\r\n'
            action['date'] = today
            self.stock_actions_collection.insert(action)
        self.update_counter()
        self.update_hold_stocks()
        self.update_balance()

        # send result mail
        if self.send_mail == 1:
            today = datetime.datetime.now().strftime('%Y-%m-%d')
            mail_service.send_text_mail(to_addr=['lxb_sysu@163.com'],
                                        subject='%s: %s' % (self.strategy_name, today), plain_text=self.mail_content)

    def update_counter(self):
        self.counter_collection.update_one({"strategy_name": self.strategy_name}, {"$set":{"counter": self.counter}})

    def update_hold_stocks(self):
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        self.hold_stocks_collection.insert({"strategy_name": self.strategy_name, "date": today, "stocks": self.hold_stocks})

    def update_balance(self):
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        self.capital_collection.insert({"strategy_name": self.strategy_name, "date": today, "balance": self.balance, "market_cap": self.market_cap, "total_cap": self.total_cap})

