# -*- coding: utf-8 -*-

import tornado.escape
import tornado.web
from config import *


class HS300(tornado.web.RequestHandler):
    def get(self):
        df = ts.get_hs300s()
        sorted_list = df.sort_values('weight', ascending=False)
        result = [{"code":sorted_list.ix[i]['code'], "name": sorted_list.ix[i]['name'], "weight": sorted_list.ix[i]['weight']} for i in sorted_list.index]
        data = {"data": result}
        self.write(json.dumps(data))

    def post(self):
        self.get()



