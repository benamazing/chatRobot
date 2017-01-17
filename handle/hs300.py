# -*- coding: utf-8 -*-

import tornado.escape
import tornado.web
from config import *


class HS300(tornado.web.RequestHandler):
    def get(self):
        hs300 = redisClient.get("hs300_list")
        if hs300 is None or hs300 == '':
            df = ts.get_hs300s()
            sorted_list = df.sort_values('weight', ascending=False)
            result = [{"code":sorted_list.ix[i]['code'], "name": sorted_list.ix[i]['name'], "weight": sorted_list.ix[i]['weight']} for i in sorted_list.index]
            data = {"data": result}
            redisClient.set("hs300_list", json.dumps(data), ex=86400)
        self.write(redisClient.get("hs300_list"))

    def post(self):
        self.get()



