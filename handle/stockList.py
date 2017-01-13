# -*- coding: utf-8 -*-

import tornado.escape
import tornado.web
from config import *


class StockListJson(tornado.web.RequestHandler):
    def get(self):
        df = ts.get_stock_basics()
        type=self.get_argument('type', 'simple')
        result = []
        if type == 'simple':
            result = [{"code":code, "name": df.ix[code]["name"], "industry": df.ix[code]["industry"], "area": df.ix[code]["area"]} for code in df.index]
        elif type == "full":
            for code in df.index:
                row = {}
                for field in df:
                    row[field] = df.ix[code][field]
                result.append(row)
        else:
            pass
        data = {"data": result}
        self.write(json.dumps(data))

    def post(self):
        self.get()

class StockList(tornado.web.RequestHandler):
    def get(self):
        self.render("stocklist.html")

    def post(self):
        pass



