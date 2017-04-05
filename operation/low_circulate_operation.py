# -*- coding:utf-8 -*-
# encoding=utf-8

import sys
sys.path.append('..')
import datetime
from base import BaseScheduleOperation
import tushare as ts

class LowCirculateOperation(BaseScheduleOperation):

    def __init__(self, send_mail=1):
        super(LowCirculateOperation, self).__init__(send_mail)

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

    def _get_strategy_name(self):
        return 'Low Circulation Market Value'

    def get_target_list(self):
        df = ts.get_stock_basics()
        sorted_list = self.sort_stock_pool_by_liutong_filter_pb(df, [0, 5])
        return sorted_list[0: int(self.strategy['stock_amount'])]

    # 限制市净率 的 limit
    def sort_stock_pool_by_liutong_filter_pb(self, df, limit_range):
        date = datetime.datetime.now()
        items = []
        for code in self.stocks_pool:
            delta = 1
            pre_day_str = (date - datetime.timedelta(days=delta)).strftime('%Y-%m-%d')
            result = self.hist_data_collection.find({"code": code, "date": pre_day_str})
            while result.count() == 0 and pre_day_str > '2016-10-01':
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
    s = LowCirculateOperation(send_mail=1)
    s.operate()
    s.summary()
