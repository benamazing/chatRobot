__author__ = 'LIBE5'

import tushare as ts
import json
import pymongo


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
            df = None
        if df is not None:
            self.stockDB.drop_collection("stock_general_info")
            self.stockDB["stock_general_info"].insert_many(json.loads(df.reset_index().to_json(orient="records")))

if __name__ == '__main__':
    d = DailyRetrieve()
    d.retrieveStockBasics()
