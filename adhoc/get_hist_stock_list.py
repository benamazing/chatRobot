# -*- coding:utf-8 -*-
# encoding=utf-8
__author__ = 'LIBE5'

import sys
sys.path.append('..')
import tushare as ts
import json
import pymongo
from util.logger import cron_logger
from urllib2 import HTTPError
import datetime


class BatchRetrieve(object):
    def __init__(self, start, end):
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
            self.collection = self.stockDB.get_collection('stock_hist_basics')

        self.start = start
        self.end = end

    def retrieveStockBasics(self):
        day_str = self.start
        while day_str <= self.end:
            self.retrieveStockBasicsByDay(day=day_str)
            s = datetime.datetime.strptime(day_str, '%Y-%m-%d') + datetime.timedelta(days=1)
            day_str = s.strftime('%Y-%m-%d')


    def retrieveStockBasicsByDay(self, day):
        try:
            df = ts.get_stock_basics(date=day)
        except HTTPError, e:
            cron_logger.warn('%s shall be non-trade day' % day)
            df = None
        except Exception, e:
            cron_logger.exception(e)
        if df is not None:
            df['date'] = day
            self.stockDB['stock_hist_basics'].delete_many({"date": day})
            self.stockDB["stock_hist_basics"].insert_many(json.loads(df.reset_index().to_json(orient="records")))
            cron_logger.info("Done inserting stock_hist_basics for %s" % day)
            print 'Done %s' % day

if __name__ == '__main__':
    d = BatchRetrieve(start='2016-08-29', end='2017-03-21')
    d.retrieveStockBasics()
