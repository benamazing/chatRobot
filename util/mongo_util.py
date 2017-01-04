import pymongo
import datetime
import random, string

def random_word(char_length, num_length):
    return ''.join(random.choice(string.lowercase) for i in range(char_length)).join(random.choice(string.digits) for i in range(num_length))

class MongoUtil(object):
    def __init__(self, host='localhost', port=27017, db_name='wx'):
        self.host = host
        self.port = port
        self.db_name = db_name
        self.user_collection_name = 'user'
        self.client = pymongo.MongoClient(self.host, self.port)
        self.db = self.client[self.db_name]
        self.user_collection = self.db[self.user_collection_name]

    def __del__(self):
        self.client.close()

    def insert_user(self, openid):
        user = {'openid': openid, 'userid': random_word(4, 5), 'crt_time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'status': 1}
        self.user_collection.insert_one(user)

    def del_user(self, openid):
        self.user_collection.remove({'openid': openid})

    def query(self, openid):
        results = self.user_collection.find({"openid": openid})
        if results.count() == 0:
            return None
        else:
            return results[0]
