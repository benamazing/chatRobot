import tushare as ts
import pandas as pd
import json
import pymongo
import logging
import threading

'''
Get full stock data and store into MongoDB
'''
THREAD_NUMS = 20

logging.basicConfig(level=logging.WARN,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S')

mongo_host = '127.0.0.1'
mongo_db_name = 'stock'
stock_hist_data_collection_name = 'stock_hist_data'

with open("../conf.json") as f:
    conf_str = f.read()
    conf = json.loads(conf_str)
    if r'mongo_host' in conf:
        mongo_host = conf[r'mongo_host']

mongo_client = pymongo.MongoClient(host=mongo_host, port=27017)
mongo_db = mongo_client[mongo_db_name]
mongo_collection = mongo_db[stock_hist_data_collection_name]


def get_all_stock_data():
    logging.info('Starting....')
    stock_list = ts.get_stock_basics()
    threads = []
    for i in range(THREAD_NUMS):
        t = threading.Thread(target=batch_get, args=(stock_list, i,))
        threads.append(t)

    for t in threads:
        t.setDaemon(True)
        t.start()
    for t in threads:
        t.join()
    logging.info('Finished!')


def batch_get(stock_list, threadNo):
    logging.info('Thread %d started.' % threadNo)
    ind = 0
    for code in stock_list.index:
        ind += 1
        if ind % THREAD_NUMS != threadNo:
            continue
        get_stock_by_code(code)


def get_stock_by_code(code=None):

    results = mongo_collection.count({"code": code})
    if results > 0:
        logging.info('%s: data already exists in mongodb' % code)
        return
    else:
        try:
            k_data = ts.get_k_data(code=code, start='2014-01-01')
            if len(k_data) == 0:
                logging.warn('%s: no history data found' % code)
                return
            hist_data = ts.get_hist_data(code=code, start = k_data.iloc[0][0])
            #  reverse order
            #  hist_data = hist_data.iloc[::-1]
            if hist_data is None or k_data is None or len(k_data) != len(hist_data):
                logging.warn('%s: different k_data and hist_data' % code)
            else:
                turnover = pd.Series([hist_data.ix[idx]['turnover'] for idx in reversed(hist_data.index)])
                k_data['turnover'] = turnover
            # mongo_collection.delete_many({"code": code})
            logging.debug('%s: all history data in mongo have been deleted' % code)
            mongo_collection.insert_many(json.loads(k_data.to_json(orient='records')))
            logging.debug('%s: inserted data into mongo' % code)
            logging.info('%s: Done.' % code)
        except:
            logging.exception('%s: got exception' % code)

if __name__ == '__main__':
    get_all_stock_data()
