# -*- coding: utf-8 -*-

import os
import json
import tornado.web
import tushare as ts
import redis
import pymongo
#import aiml

from wechat_sdk.core.conf import WechatConf
from wechat_sdk.basic import WechatBasic
from util.mongo_util import *
import tuling

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

mongo_host = '127.0.0.1'
redis_host = '127.0.0.1'
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

    # for tuling apikey
    if r'tuling_apikey' in conf:
        tuling_apikey = conf['tuling_apikey']
    if r'tuling_url' in conf:
        tuling_url = conf['tuling_url']

    if r'redis_server_host' in conf:
        redis_host = conf['redis_server_host']

    if r'mongo_host' in conf:
        mongo_host = conf['mongo_host']

tulingRobot = tuling.Tuling(url=tuling_url, apikey=tuling_apikey)

wx_config = WechatConf(token=wx_token, appid=wx_appid, appsecret=wx_appsecret, encrypt_mode=wx_mode)
wechat = WechatBasic(conf=wx_config)

mongo = MongoUtil()

redisClient = redis.StrictRedis(host=redis_host)

mongo_stock_db_name = 'stock'
mongoClient = pymongo.MongoClient(host=mongo_host)
mongo_stock_db = mongoClient[mongo_stock_db_name]

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
    (r'/wx', wx.WX),
    (r'/hs300listjson', hs300.HS300Json),
    (r'/hs300', hs300.HS300),
    (r'/stock', stockList.StockList),
    (r'/stocklistjson', stockList.StockListJson),
    (r'/sample', sample.Sample)
#    (r'/aiml', aiml.Alice)
]
