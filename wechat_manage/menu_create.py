import sys
sys.path.append('..')
from config import wechat
import json

def createMenu():
    with open("conf/wechat_menu.json") as f:
        menu_str = f.read()
        menu = json.loads(menu_str)

    try:
        wechat.delete_menu()
        result = wechat.create_menu(menu)
        print result
    except Exception,e:
        print e

if __name__ == '__main__':
    createMenu()