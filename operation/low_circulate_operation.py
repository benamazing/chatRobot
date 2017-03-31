# -*- coding:utf-8 -*-
# encoding=utf-8

import sys
sys.path.append('..')
import datetime
from base import BaseScheduleOperation
import tushare as ts

class LowCirculateOperation(BaseScheduleOperation):

    def __init__(self, start, period, stock_amount, init_cap, send_mail=1, source='mongo'):
        super(LowCirculateOperation, self).__init__(start, period, stock_amount, init_cap, send_mail, source)
        self.strategy_name = 'Low Circulation Market Value'

        # 中证500为股票池
        # zz500 = ts.get_zz500s()
        # for x in zz500.code:
        #     self.stocks_pool.append(x)

        # 沪深300为股票池
        # hs300 = ts.get_hs300s()
        # for x in hs300.code:
        #     self.stocks_pool.append(x)

        df = ts.get_stock_basics()
        for code in df.index:
            if df.ix[code]['timeToMarket'] < 20160101:
                self.stocks_pool.append(code)

    def operate(self):
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        if self.counter % self.period == 0:
            df = ts.get_stock_basics()

            # 限制流通市值在100-200亿
            sorted_list = self.sort_stock_pool_by_liutong_filter_pb(df, [0, 5])
            target_list = sorted_list[0:self.stock_amount]

            codes = [item['code'] for item in target_list]

            # 卖出不在target_list里面的股票
            for code in self.hold_stocks.keys():
                if code not in codes:
                    self.sell(code)

            # 卖出ST股
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

    # 限制市净率 的 limit
    def sort_stock_pool_by_liutong_filter_pb(self, df, limit_range):
        date = datetime.datetime.now()
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
            item = dict()
            item['price'] = result[0]['close']

            # 有些历史数据的outstanding是以万为单位的，所以要除以10000
            if df.outstanding.max() > 1000000:
                item['outstanding'] = df.ix[code]['outstanding'] / 10000
            else:
                item['outstanding'] = df.ix[code]['outstanding']
            item['outstanding_cap'] = item['price'] * item['outstanding']
            item['code'] = code
            item['name'] = df.ix[code]['name']
            item['pb'] = df.ix[code]['pb']
            if item['pb'] <= 0:
                continue
            if item['pb'] <= limit_range[0] or item['pb'] >= limit_range[1]:
                continue
            # 去掉ST股
            if df.ix[code]['name'].find('*ST') >= 0:
                continue
            items.append(item)
        items = sorted(items, key=lambda x: x['outstanding_cap'])
        return items



if __name__ == '__main__':
    if len(sys.argv) < 4:
        print 'Usage: %s <PERIOD> <STOCK_AMOUNT> <INIT_CAP> <SEND_EMAIL> <SOURCE>' % sys.argv[0]
        print '<PERIOD>: mandatory'
        print '<STOCK_AMOUNT>: mandatory'
        print '<INIT_CAP>: mandatory'
        print '<SEND_EMAIL>: optional, 0/1, default: 1'
        print '<SOURCE>: optional, mongo/tushare, default: mongo'
        exit()
    send_mail = 1
    source = 'mongo'
    if len(sys.argv) == 5:
        send_mail = int(sys.argv[4])
    if len(sys.argv) == 6:
        send_mail = int(sys.argv[4])
        source = sys.argv[5]
    s = LowCirculateOperation(start='2016-08-30', period=int(sys.argv[1]), stock_amount=int(sys.argv[2]),
                               init_cap=int(sys.argv[3]), send_mail=send_mail, source=source)
    s.operate()