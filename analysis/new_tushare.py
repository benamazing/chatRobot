# -*- coding:utf-8 -*-
from __future__ import division

import time
import pandas as pd
from tushare.stock import cons as ct
from pandas.compat import StringIO
try:
    from urllib.request import urlopen, Request
except ImportError:
    from urllib2 import urlopen, Request
    

def _code_to_symbol(code):
    if code in ct.INDEX_LABELS:
        return ct.INDEX_LIST[code]
    else:
        if len(code) != 6 :
            return ''
        else:
            return 'sh%s'%code if code[:1] in ['5', '6', '9'] else 'sz%s'%code

SINA_DD_BY_AMOUNT_URL = 'http://vip.stock.finance.sina.com.cn/quotes_service/view/cn_bill_download.php?symbol=%s&num=60&page=1&sort=ticktime&asc=0&volume=0&amount=%d&type=0&day=%s'

def get_sina_dd_by_amount(code=None, date=None, amount=50, retry_count=3, pause=0.001):
    if code is None or len(code)!=6 or date is None:
        return None
    symbol = _code_to_symbol(code)
    amount = amount * 10000
    for _ in range(retry_count):
        time.sleep(pause)
        try:
            re = Request(SINA_DD_BY_AMOUNT_URL % (symbol, amount, date))
            lines = urlopen(re, timeout=10).read()
            lines = lines.decode('GBK')
            if len(lines) < 100:
                return None
            df = pd.read_csv(StringIO(lines), names=ct.SINA_DD_COLS,
                               skiprows=[0])
            if df is not None:
                df['code'] = df['code'].map(lambda x: x[2:])
        except Exception as e:
            print(e)
        else:
            return df
    raise IOError(ct.NETWORK_URL_ERROR_MSG)

