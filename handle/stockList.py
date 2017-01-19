# -*- coding: utf-8 -*-

import tornado.escape
import tornado.web
from config import *
import redis


class StockListJson(tornado.web.RequestHandler):
    def get(self):
        type=self.get_argument('type', 'simple')
        resultString = ""
        if type == 'simple':
            stock_list_simple_json = redisClient.get("stock_list_simple_json")
            if stock_list_simple_json is None or stock_list_simple_json == '':
                df = ts.get_stock_basics()
                result = [{"code":code, "name": df.ix[code]["name"], "industry": df.ix[code]["industry"], "area": df.ix[code]["area"]} for code in df.index]
                data = {"data": result}
                resultString = json.dumps(data)
                redisClient.set("stock_list_simple_json", resultString, ex=86400)
            else:
                resultString = stock_list_simple_json
        elif type == 'full':
            stock_list_full_json = redisClient.get("stock_list_full_json")
            if stock_list_full_json is None or stock_list_full_json == '':
                result = []
                df = ts.get_stock_basics()
                for code in df.index:
                    row = {}
                    row[code] = str(code)
                    for field in df:
                        if field != 'reserved' and field != 'reservedPerShare':
                            row[field] = str(df.ix[code][field])
                    result.append(row)
                data = {"data": result}
                try:
                    resultString = json.dumps(data)
                except Exception, e:
                    print Exception, ":", e
                redisClient.set("stock_list_full_json", resultString, ex=86400)
            else:
                resultString = stock_list_full_json
        else:
            pass

        self.set_header("Cache-Control", "max-age=86400")
        self.write(resultString)

    def post(self):
        self.get()

class StockList(tornado.web.RequestHandler):
    def get(self):
        self.render("stocklist.html")

    def post(self):
        pass



