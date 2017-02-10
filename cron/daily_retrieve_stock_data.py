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

logging.basicConfig(level=logging.WARN, filename='../logs/daily_retrieve_stock_data.log',filemode='w',
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S')

class DeltaRetriveStockData(object):

    def __init__(self):
        self.mongo_host = '127.0.0.1'
        self.mongo_port = 27017
        self.mongo_db_name = 'stock'
        self.mongo_collection_name = 'stock_hist_data'
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
            self.mongo_collection = self.stockDB[self.mongo_collection_name]


    def delta_get_all_stock_data(self):
        logging.info('Starting....')
        stock_list = ts.get_stock_basics()
        threads = []
        for i in range(self.thread_nums):
            t = threading.Thread(target=self.delta_batch_get, args=(stock_list, i,))
            threads.append(t)

        for t in threads:
            t.setDaemon(True)
            t.start()
        for t in threads:
            t.join()
        logging.info('Finished!')


    def delta_batch_get(self, stock_list, threadNo):
        logging.info('Thread %d started.' % threadNo)
        ind = 0
        for code in stock_list.index:
            ind += 1
            if ind % self.thread_nums != threadNo:
                continue
            self.delta_get_stock_by_code(code)

    def delta_get_stock_by_code(self, code=None):
        try:
            now = datetime.datetime.now()
            start_date = (now - datetime.timedelta(days=3)).strftime('%Y-%m-%d')
            k_data = ts.get_k_data(code=code, start=start_date)
            if len(k_data) == 0:
                return

            # 是否有除权除息导致股价变动需要全部重新下载
            need_full_load = False
            results = self.mongo_collection.find({"code":code,"date":k_data.iloc[0][0]})
            if results.count() == 1:
                if results[0]['open'] != k_data.iloc[0]['open'] or results[0]['close'] != k_data.iloc[0]['close']:
                    need_full_load = True
            else:
                need_full_load = True

            if need_full_load:
                logging.warn('%s: need full load due to price changed' % code)
                self.mongo_collection.delete_many({"code":code})
                logging.debug("%s: deleted all records in mongo" % code)
                full_data = ts.get_k_data(code=code, start='2014-01-01')
                if len(full_data) == 0:
                    logging.warn("%s: no history data found" % code)
                    return
                self.mongo_collection.insert_many(json.loads(full_data.to_json(orient='records')))
                logging.debug('%s: inserted full data into mongo' % code)
                logging.warn('%s: Full load done.' % code)

            else:
                for idx in k_data.index:
                    self.mongo_collection.delete_many({"code":code, "date": k_data.ix[idx]['date']})
                self.mongo_collection.insert(json.loads(k_data.to_json(orient='records')))
                logging.warn('%s: Delta load done.' % code)
        except:
            logging.exception('%s: got exception.' % code)

if __name__ == '__main__':
    d = DeltaRetriveStockData()
    d.delta_get_all_stock_data()
