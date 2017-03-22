# -*- coding:utf-8 -*-
# encoding=utf-8

import sys
sys.path.append('..')

import json
import pymongo
import tushare as ts
import datetime
from urllib2 import HTTPError

'''测试:'''

class Strategy(object):

    def __init__(self,start,period,stock_amount, init_cap):
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

        self.stocks_pool = []

        # 中证500为股票池
        # zz500 = ts.get_zz500s()
        # for x in zz500.code:
        #     self.stocks_pool.append(x)

        # 沪深300为股票池
        hs300 = ts.get_hs300s()
        for x in hs300.code:
            self.stocks_pool.append(x)

        # df = ts.get_stock_basics()
        # for code in df.index:
        #     if df.ix[code]['timeToMarket'] < 20160101:
        #         self.stocks_pool.append(code)

        self.stock_amount = stock_amount
        self.start = start
        self.period = period
        self.init_cap = init_cap
        self.balance = init_cap
        self.market_cap = 0
        self.total_cap = self.balance + self.market_cap
        self.hold_stocks = {}
        self.counter = 0


    def simulate(self):
        start_date = datetime.datetime.strptime(self.start, '%Y-%m-%d')
        idx = start_date
        x = self.hist_data_collection.find({}).sort("date", -1).limit(1)
        end_date = datetime.datetime.strptime(x[0]['date'], '%Y-%m-%d')

        while idx <= end_date:
            self.operate(idx)
            self.summary(idx)
            idx = idx + datetime.timedelta(days=1)

    def operate(self, date):
        date_str = date.strftime('%Y-%m-%d')
        count = self.hist_data_collection.find({"date":date_str}).count()

        # 非交易日
        if count == 0:
            return

        if self.counter % self.period == 0:
            df = self.get_last_trade_stock_basics(date)

            # sorted_list = self.sort_stock_pool_by_pb(df)

            # 限制流通市值在100-200亿
            sorted_list = self.sort_stock_pool_by_pb_filter_big(df, [0, 500000], date)
            target_list = sorted_list[0:5]

            # 卖出不在target_list里面的股票
            for code in self.hold_stocks.keys():
                if code not in target_list:
                    self.sell(code, date)

            # 买入不在持有列表里的股票
            will_buy_list = []
            for code in target_list:
                if code not in self.hold_stocks.keys():
                    will_buy_list.append(code)
            self.buy(will_buy_list, date)

        self.counter += 1


    def summary(self, date):
        date_str = date.strftime('%Y-%m-%d')
        self.market_cap = 0
        for item in self.hold_stocks.items():
            code = item[0]
            amount = item[1]

            # 如果当天停牌，则获取上一个非停牌日的收市价
            r = self.hist_data_collection.find({"code":code, "date":date_str})
            while r.count() == 0:
                date_str = (datetime.datetime.strptime(date_str, '%Y-%m-%d') - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
                r = self.hist_data_collection.find({"code":code, "date":date_str})
            price = r[0]['close']
            self.market_cap = self.market_cap + amount * price
        self.total_cap = self.balance + self.market_cap

        #print '%s---Total: %2f\tBalance: %2f\tMarket_cap: %2f' % (date, self.total_cap, self.balance, self.market_cap)
        print '%s,%2f' % (date.strftime('%Y-%m-%d'), self.total_cap)

    # 获取输入日期的上一个交易日的股票基本面信息
    def get_last_trade_stock_basics(self, date):
        pre_day = date - datetime.timedelta(days=1)
        df = None
        while df is None:
            try:
                pre_day_str = pre_day.strftime('%Y-%m-%d')
                df = ts.get_stock_basics(date=pre_day_str)
            except HTTPError, e:
                pre_day = datetime.datetime.strptime(pre_day_str, '%Y-%m-%d') - datetime.timedelta(days=1)
                df = None
        return df


    def sort_stock_pool_by_pb(self, df):
        items = []
        for code in self.stocks_pool:
            item = {}
            item['code'] = code
            item['pb'] = df.ix[code]['pb']
            items.append(item)
        items = sorted(items, key=lambda x:x['pb'])
        return [item['code'] for item in items]

    # 限制流通市值 < limit
    def sort_stock_pool_by_pb_filter_big(self, df, limit_range, date):
        items = []
        for code in self.stocks_pool:
            delta = 1
            pre_day_str = (date - datetime.timedelta(days=delta)).strftime('%Y-%m-%d')
            result = self.hist_data_collection.find({"code": code, "date": pre_day_str})
            while result.count() == 0 and pre_day_str >= self.start:
                delta += 1
                pre_day_str = (date - datetime.timedelta(days=delta)).strftime('%Y-%m-%d')
                result = self.hist_data_collection.find({"code": code, "date": pre_day_str})
            if result.count() == 0:
                continue
            item = {}
            item['price'] = result[0]['close']

            # 有些历史数据的outstanding是以万为单位的，所以要除以10000
            if df.outstanding.max() > 1000000:
                item['outstanding'] = df.ix[code]['outstanding'] / 10000
            else:
                item['outstanding'] = df.ix[code]['outstanding']
            item['outstanding_cap'] = item['price'] * item['outstanding']
            item['code'] = code
            item['pb'] = df.ix[code]['pb']
            if item['outstanding_cap'] < limit_range[0] or item['outstanding_cap'] > limit_range[1]:
                continue
            items.append(item)
        items = sorted(items, key=lambda x:x['pb'])
        return [item['code'] for item in items]

    def buy(self, code_list, date):
        date_str = date.strftime('%Y-%m-%d')
        if len(code_list) == 0:
            return
        piece_cap = self.balance / len(code_list)
        for code in code_list:
            r = self.hist_data_collection.find({"code": code, "date": date_str})
            #if r.count() == 0:
            #    print 'Failed to buy %s' % code
            if r.count() == 1:
                if r[0]['open'] == r[0]['close'] and r[0]['high'] == r[0]['open'] and r[0]['high'] == r[0]['low']:
                    return
                buy_price = r[0]['open']
                buy_amount = int(piece_cap / (buy_price * 100)) * 100
                self.hold_stocks[code] = buy_amount
                self.balance = self.balance - buy_amount * buy_price
                print 'Buy %s' % code


    def sell(self, code, date):
        date_str = date.strftime('%Y-%m-%d')
        r = self.hist_data_collection.find({"code": code, "date": date_str})
        if r.count() == 1:
            sell_price = r[0]['open']
            sell_amount = self.hold_stocks[code]
            self.hold_stocks.pop(code)
            self.balance = self.balance + sell_amount * sell_price
        print 'Sell %s' % code

if __name__ == '__main__':
    s = Strategy(start='2016-08-30',period=10,stock_amount=5, init_cap=100000)
    s.simulate()




