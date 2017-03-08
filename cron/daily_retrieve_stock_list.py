__author__ = 'LIBE5'

import sys
sys.path.append('..')
import tushare as ts
import json
import pymongo
from util.logger import cron_logger
import analysis.finance_crawler as crawler


class DailyRetrieve(object):
    def __init__(self):
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

    def retrieveStockBasics(self):
        try:
            df = ts.get_stock_basics()
        except Exception, e:
            cron_logger.exception("get_stock_basics failed")
            df = None
        if df is not None:
            self.stockDB.drop_collection("stock_general_info")
            cron_logger.info("Cleared current data in stock_general_info!")
            self.stockDB["stock_general_info"].insert_many(json.loads(df.reset_index().to_json(orient="records")))
            cron_logger.info("Updated stock_general_info!")

    def supplementDebt(self):
        collection = self.stockDB.get_collection('stock_general_info')
        rs = collection.find().sort("code", 1)
        d_list = list(rs)
        for row in d_list:
            current_debt, total_debt = crawler.get_debt(code=row['code'])
            if current_debt is None:
                current_debt = 0
            if total_debt is None:
                total_debt = 0
            print '%s: %s, %s' % (row['code'], current_debt, total_debt)
            collection.update_one({"code": row['code']}, {"$set": {"current_debt": current_debt, "total_debt": total_debt}})

if __name__ == '__main__':
    d = DailyRetrieve()
    d.retrieveStockBasics()
    d.supplementDebt()
