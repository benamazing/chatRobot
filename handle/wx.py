# -*- coding: utf-8 -*-

import tornado.escape
import tornado.web

from config import *
from wechat_sdk.messages import *

class WX(tornado.web.RequestHandler):
    def get(self):
        signature = self.get_argument('signature', 'default')
        nonce = self.get_argument('nonce', 'default')
        timestamp = self.get_argument('timestamp', 'default')
        echostr = self.get_argument('echostr', 'default')

        if signature != 'default' and timestamp != 'default' and nonce != 'default' and echostr != 'default' \
                and wechat.check_signature(signature, timestamp, nonce):
            self.write(echostr)
        else:
            self.write('Error 404!')

    def post(self):
        signature = self.get_argument('signature', 'default')
        nonce = self.get_argument('nonce', 'default')
        timestamp = self.get_argument('timestamp', 'default')
        if signature != 'default' and timestamp != 'default' and nonce != 'default' and wechat.check_signature(signature, timestamp, nonce):
            body = self.request.body.decode('utf-8')
            wechat.parse_data(body)
            print wechat.message.raw
            open_id = wechat.message.source
            if mongo.query(open_id) is None:
                mongo.insert_user(open_id)
            userid = mongo.query(open_id)['userid']
            if isinstance(wechat.message, TextMessage):
                content = wechat.message.content
                answer = tulingRobot.chat(content, userid)
                xml = wechat.response_text(content=answer)
                self.write(xml)
                return
            if isinstance(wechat.message, ImageMessage):
                xml = wechat.response_text(content='暂时只支持文字聊天')
                self.write(xml)
                return

