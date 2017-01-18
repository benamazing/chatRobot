# -*- coding: utf-8 -*-
import tornado.escape
import tornado.web


class Index(tornado.web.RequestHandler):
    def get(self):
        self.render("hs300.html")

    def post(self):
        pass
