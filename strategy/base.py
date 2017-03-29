# -*- coding:utf-8 -*-
# encoding=utf-8

import sys
sys.path.append('..')

import json
import pymongo
import tushare as ts
import datetime
from urllib2 import HTTPError
from util.mail_util import mail_service
import pandas as pd

# 定期的strategy
class BaseScheduleStrategy(object):
    def __init__(self, start, period, stock_amount, init_cap, send_mail=1):
        self.stock_amount = stock_amount
        self.start = start
        self.period = period
        self.init_cap = init_cap
        self.balance = init_cap
        self.market_cap = 0
        self.total_cap = self.balance + self.market_cap
        self.hold_stocks = {}
        self.counter = 0
        self.strategy_name = 'Basic Strategy'
        self.stocks_pool = []

        # email content
        self.mail_content = ''
        self.send_mail = send_mail

    def simulate(self):
        start_date = datetime.datetime.strptime(self.start, '%Y-%m-%d')
        idx = start_date
        x = self.hist_data_collection.find({}).sort("date", -1).limit(1)
        end_date = datetime.datetime.strptime(x[0]['date'], '%Y-%m-%d')

        while idx <= end_date:
            self.operate(idx)
            self.summary(idx)
            idx = idx + datetime.timedelta(days=1)

        # send result mail
        if self.send_mail == 1:
            mail_service.send_text_mail(to_addr=['lxb_sysu@163.com'], subject='%s: %s, %s, %s' % (self.strategy_name, self.period, self.stock_amount, self.init_cap), plain_text=self.mail_content)


    def operate(self, date):
        pass

    def buy(self, target_list, date):
        date_str = date.strftime('%Y-%m-%d')
        if len(target_list) == 0:
            return
        piece_cap = self.balance / len(target_list)
        for target in target_list:
            r = self.hist_data_collection.find({"code": target['code'], "date": date_str})
            #if r.count() == 0:
            #    print 'Failed to buy %s' % code
            if r.count() == 1:
                if r[0]['open'] == r[0]['close'] and r[0]['high'] == r[0]['open'] and r[0]['high'] == r[0]['low']:
                    return
                buy_price = r[0]['open']
                buy_amount = int(piece_cap / (buy_price * 100)) * 100
                self.hold_stocks[target['code']] = buy_amount
                self.balance = self.balance - buy_amount * buy_price
                print 'Buy %s-%s' % (target['code'], target['name'])
                self.mail_content = self.mail_content + 'Buy %s-%s' % (target['code'], target['name']) + '\r\n'


    def sell(self, code, date):
        date_str = date.strftime('%Y-%m-%d')
        r = self.hist_data_collection.find({"code": code, "date": date_str})
        if r.count() == 1:
            sell_price = r[0]['open']
            sell_amount = self.hold_stocks[code]
            self.hold_stocks.pop(code)
            self.balance = self.balance + sell_amount * sell_price
        print 'Sell %s' % code
        self.mail_content = self.mail_content + 'Sell %s' % code + '\r\n'

    def summary(self, date):
        date_str = date.strftime('%Y-%m-%d')
        self.market_cap = 0
        ss = ""
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
            ss = ss + '    %s: %s: %s' % (code, amount, amount * price)
        self.total_cap = self.balance + self.market_cap
        #print '%s---Total: %2f\tBalance: %2f\tMarket_cap: %2f' % (date, self.total_cap, self.balance, self.market_cap)
        print '%s,%2f' % (date.strftime('%Y-%m-%d'), round(self.total_cap, 2))
        self.mail_content = self.mail_content + '%s,%2f' % (date.strftime('%Y-%m-%d'), round(self.total_cap, 2)) + '\r\n'
        self.stock_list_log = self.stock_list_log + date.strftime('%Y-%m-%d') + ss + "\r\n"


    # 从tushare获取输入日期的上一个交易日的股票基本面信息
    def get_last_trade_stock_basics_from_tushare(self, date):
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


    # 从本地mongoDB获取输入日期的上一个交易日的股票基本面信息
    def get_last_trade_stock_basics_from_mongo(self, date):
        pre_day = date - datetime.timedelta(days=1)
        pre_day_str = pre_day.strftime('%Y-%m-%d')
        rs = self.stockDB['stock_hist_basics'].find({"date": pre_day_str}, {"_id":0})
        while rs.count() == 0:
            pre_day = datetime.datetime.strptime(pre_day_str, '%Y-%m-%d') - datetime.timedelta(days=1)
            pre_day_str = pre_day.strftime('%Y-%m-%d')
            rs = self.stockDB['stock_hist_basics'].find({"date": pre_day_str})
        df = pd.DataFrame(list(rs)).set_index('code')
        return df

