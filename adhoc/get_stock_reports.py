
import tushare as ts
import pymongo
import json

year = range(2010,2017)
season = range(1,5)

mongo_client = pymongo.MongoClient(host="10.222.48.204", port=27017)

for y in year:
    for s in season:
        print 'Start to retrieve the performance report for %s-%s.....' % (y,s)
        retry = 0
        while retry < 3:
            try:
                df = ts.get_report_data(y,s)
                mongo_client['stock']['stock_report'].insert_many(json.loads(df.to_json(orient="records")))
                break
            except Exception, e:
                print 'Failed to get run ts.get_report_data', e
                print 'retryCount = %s' % retry
                retry += 1
        print 'Finished retriving report for %s-%s.' %(y,s)

print 'Done!'
