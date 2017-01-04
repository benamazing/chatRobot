# -*- coding: utf-8 -*-

import os
import json
import tornado.web
#import aiml

from wechat_sdk.core.conf import WechatConf
from wechat_sdk.basic import WechatBasic
from util.mongo_util import *

settings = {
    'static_path': os.path.join(os.path.dirname(__file__), 'static'),
    'template_path': os.path.join(os.path.dirname(__file__), 'view'),
    'login_url': '/',
    'session_timeout': 3600,
}



wx_token = None
wx_appid = None
wx_appsecret = None
wx_mode = None

with open("conf.json") as f:
    conf_str = f.read()
    conf = json.loads(conf_str)
    if r'token' in conf:
        wx_token = conf['token']
    if r'appid' in conf:
        wx_appid = conf['appid']
    if r'appsercet' in conf:
        wx_appsecret = conf['appsercet']
    if r'encrypt_mode' in conf:
        wx_mode = conf['encrypt_mode']

wx_config = WechatConf(token=wx_token, appid=wx_appid, appsecret=wx_appsecret, encrypt_mode=wx_mode)
wechat = WechatBasic(conf=wx_config)

mongo = MongoUtil()

#cur_dir = os.getcwd()
#print 'cur_dir:', cur_dir
#os.chdir('./res/alice')
#alice = aiml.Kernel()
#alice.learn("startup.xml")
#alice.respond('LOAD ALICE')
#os.chdir(cur_dir)
#print 'cur_dir:', os.getcwd()

from handle import *

handlers = [
    (r'/', common.Index),
    (r'/wx', wx.WX)
#    (r'/aiml', aiml.Alice)
]
