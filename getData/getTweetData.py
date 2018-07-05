
from http.client import IncompleteRead
from tweepy.streaming import StreamListener
from pymongo import MongoClient
from tweepy import OAuthHandler
from tweepy import Stream
from datetime import datetime
import json
import re
import time

from urllib3.exceptions import ProtocolError

# read twitter_api key in file.
with open('./twitter_key.json') as data_file:
    key_data = json.load(data_file)
# 트위터 api access 코드
access_token = key_data["access_token"]
access_token_secret = key_data["access_token_secret"]
consumer_key = key_data["consumer_key"]
consumer_secret = key_data["consumer_secret"]

# 이 프로그램의 서버는 mongodb의 포트로 26543번을 사용.
client = MongoClient('localhost', 26543)
db = client.twitter_api
emotion_coll = db.twitter_korean_emotion_data_v1

# 정규식으로 한글을 포함하고 있는 데이터를 판단
korean = re.compile('.*[가-힣]+.*')


# output data를 받을 listener를 정의. 여기서 받은 데이터를 처리함.
class StdOutListener(StreamListener):
    def on_data(self, data):
        try:
            tweet = json.loads(data)
            text = tweet["text"]

            with_korean = korean.match(text)
            if with_korean:
                print(text)
                id_str = tweet["id_str"]
                d = datetime.strptime(tweet["created_at"], '%a %b %d %H:%M:%S %z %Y')
                created_at = d.strftime('%Y%m%d')
                emotion = 0
                obj = {"created_at": created_at, "id_str": id_str, "text": text, "emotion": emotion}
                print("saved emotion data")
                emotion_coll.insert_one(obj)
        except KeyError:
            # if this data deleted tweet data
            None
        except ProtocolError:
            print("protocol error")
        except IncompleteRead:
            print("incomp")
        except AttributeError:
            print("ATTR")
        return True

    def on_error(self, status_code):
        if status_code == 420:
            print("Too many connections. wait 10 minutes")
            time.sleep(600)
            TweeterCheckin()
        else:
            print(status_code)
            return False
    def on_exception(self, exception):
        print(exception)
        time.sleep(30)
        return

if __name__ == '__main__':
    listener = StdOutListener()
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    stream = Stream(auth, listener)
    while(True):
        try:
            stream.sample()
        except ProtocolError:
            print("protocol error")
            time.sleep(30)
        except KeyboardInterrupt:
            break
