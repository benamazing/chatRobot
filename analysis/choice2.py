# -*- coding:utf-8 -*-
# encoding=utf-8

import sys
sys.path.append('..')

import tushare as ts
import finance_crawler

# prepare
today_all = ts.get_today_all()
all = ts.get_stock_basics()
hs300 = ts.get_hs300s()
hs300_array = []
for x in hs300.code:
    hs300_array.append(x)

filter_list = []

def filter_by_pb_and_hs300():
    for idx in today_all.index:
        code = today_all.ix[idx]['code']
        name = all.ix[code]['name']
        pb = all.ix[code]['pb']
        if pb < 2 and pb > 0 and code in hs300_array:
            filter_list.append(code)
    return filter_list

def filter_by_asset_debt_ratio(codes):
    result = []
    for code in codes:
        print 'getting debt info of %s' % code
        current_debt, total_debt = finance_crawler.get_debt(code)
        if current_debt is not None:
            total_asset = all.ix[code]['totalAssets']
            liquid_asset = all.ix[code]['liquidAssets']
            if liquid_asset / current_debt > 1.2:
                result.append(code)
    return result

if __name__ == '__main__':
    codes = filter_by_pb_and_hs300()
    print len(codes)
    result = filter_by_asset_debt_ratio(codes)
    print len(result)
    print result



