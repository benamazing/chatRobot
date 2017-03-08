# -*- coding:UTF-8 -*-
#encoding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import urllib2

deb_url = 'http://quotes.money.163.com/service/zcfzb_%s.html'
headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
}

### get latest current debt and total debt by code ###
def get_debt(code=None):
    if code is None:
        print 'code is required'
        return None

    current_debt = None
    req = urllib2.Request(url=deb_url % code, headers=headers)
    try:
        response = urllib2.urlopen(req)
    except Exception, e:
        print Exception, e
        return None
    lines = response.readlines()
    for line in lines:
        line = line.decode('GBK')
        if line.startswith('流动负债合计'):
            column1 = line.split(',')[1]
            if column1 == '--':
                current_debt = None
            else:
                current_debt = float(line.split(',')[1])
            break

    total_debt = None
    for line in lines:
        line = line.decode('GBK')
        if line.startswith('负债合计'):
            column1 = line.split(',')[1]
            if column1 == '--':
                total_debt = None
            else:
                total_debt = float(line.split(',')[1])
            break

    return (current_debt, total_debt)