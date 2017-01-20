
import tushare as ts
import pymongo
import json

# get 2010-2016 stock performance report
year = range(2010,2017)
season = range(1,5)

mongo_host = '127.0.0.1'
mongo_db_name = 'stock'
stock_report_collection_name = 'stock_report'

with open("../conf.json") as f:
    conf_str = f.read()
    conf = json.loads(conf_str)
    if r'mongo_host' in conf:
        mongo_host = conf[r'mongo_host']

mongo_client = pymongo.MongoClient(host=mongo_host, port=27017)
mongo_db = mongo_client[mongo_db_name]
mongo_collection = mongo_db[stock_report_collection_name]

for y in year:
    for s in season:
        results = mongo_collection.count({"year": y, "season": s})
        if results > 1000:
            print '%s-%s report data already exist in mongoDB, passed...' % (y, s)
            continue
        if results > 0:
            print 'Incomplete report for %s-%s' % (y,s)
            print 'Delete the records in mongoDB for %s-%s' % (y,s)
            mongo_collection.delete_many({"year": y, "season" :s})
        print 'Start to retrieve the performance report for %s-%s.....' % (y,s)
        retry = 0
        while retry < 3:
            try:
                df = ts.get_report_data(y,s)
                jsonString = df.to_json(orient="records", force_ascii=True)
                jsonObjs = json.loads(jsonString)
                for obj in jsonObjs:
                    obj['year'] = y
                    obj['season'] = s
                mongo_collection.insert_many(jsonObjs)
                break
            except Exception, e:
                print 'Failed to get report data', e
                print 'retryCount = %s' % retry
                retry += 1
        if retry == 3:
            print 'Failed to retrieve report for %s-%s, after 3 tries' % (y,s)
        else:
            print 'Successfully retrived the report data for %s-%s.' %(y,s)

print 'Done processing!'
