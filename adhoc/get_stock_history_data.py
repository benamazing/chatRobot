import tushare as ts
import pandas as pd
import pandas.core.frame as frame
import numpy
import json
import pymongo
import logging

logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S')

import datetime

start_time = datetime.datetime.now()

mongo_host = '127.0.0.1'
mongo_db_name = 'stock'
stock_report_collection_name = 'stock_hist_data'

with open("../conf.json") as f:
    conf_str = f.read()
    conf = json.loads(conf_str)
    if r'mongo_host' in conf:
        mongo_host = conf[r'mongo_host']

mongo_client = pymongo.MongoClient(host=mongo_host, port=27017)
mongo_db = mongo_client[mongo_db_name]
mongo_collection = mongo_db[stock_report_collection_name]


def get_all_stock_data():
    stock_list = ts.get_stock_basics()
    for code in stock_list.index:
        get_stock_by_code(code)


def get_stock_by_code(code=None):
    k_data = ts.get_k_data(code=code)
    hist_data = ts.get_hist_data(code=code, start = k_data.ix[0][0])
    #  reverse order
    #  hist_data = hist_data.ix[::-1]
    if len(k_data) == len(hist_data):
        turnover = pd.Series([hist_data.ix[idx]['turnover'] for idx in reversed(hist_data.index)])
        k_data['turnover'] = turnover
    else:
        logging.info('%s: has different k_data & hist_data' % code)
    mongo_collection.delete_many({"code": code})
    logging.info('%s: all history data in mongo have been deleted' % code)
    mongo_collection.insert_many(json.loads(k_data.to_json(orient='records')))
    logging.info('%s: inserted data into mongo' % code)
    logging.info('%s: Done.' % code)

if __name__ == '__main__':
    start = datetime.datetime.now()
    logging.info('Starting....')
    get_all_stock_data()
    logging.info('Finished!')
