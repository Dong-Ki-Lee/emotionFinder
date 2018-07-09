from konlpy.tag import Mecab
from pymongo import MongoClient
import re
import accv
import time

# 이 프로그램의 서버는 mongodb의 포트로 26543번을 사용.
client = MongoClient('localhost', 26543)
emotion_db = client.emotion_data
positive_coll = emotion_db.positive
negative_coll = emotion_db.negative
def call_dictionary():
    f = open("./dictionary_data/polarity.csv", 'r')
    cons = re.compile('[ㄱ-ㅎ]')
    dictionary_data = []
    for list in f.readlines():
        dict_line = list.replace('\n', '').split(',')
        text_part = dict_line[0].split(';')
        for i in range(len(text_part)):
            if len(text_part) == 1 or cons.search(text_part[0].split('/')[0]) != None:
                break
            if cons.search(text_part[i].split('/')[0]) != None:
                form_temp = text_part[i-1].split('/')[1] + '+' + text_part[i].split('/')[1]
                text_temp = accv.combine(text_part[i-1].split('/')[0].replace('*','') + text_part[i].split('/')[0].replace('*',''))
                text_part[i-1] = text_temp + '/' + form_temp
                del text_part[i]
                break
        text = ''
        for t in text_part:
            text = text + t + ';'
        text = text.replace('*', '')
        obj = {'ngram' : text, 'emotion' : dict_line[7], 'figure' : float(dict_line[8]), 'n' : len(text[0:-1].split(';'))}
        dictionary_data.append(obj)
    f.close()
    return dictionary_data

def find_emotion(dictionary_data):
    counter = 0
    mecab = Mecab()
    # 이 프로그램의 서버는 mongodb의 포트로 26543번을 사용.
    client = MongoClient('localhost', 26543)

    db = client.twitter_api
    emotion_coll = db.twitter_korean_emotion_data_v1

    twitter_data = emotion_coll.find()
    for twit in twitter_data:
        temp = re.sub(r'[a-zA-Z@.:\n/_ㄱ-ㅎㅏ-ㅣ;0-9%]', '', twit['text'])
        emotion = 0.0
        for dict in dictionary_data:
            change_data = ''
            for dict_text in dict['ngram'].split(';'):
                change_data += dict_text.split('/')[0]
            dict['ngram'] = change_data

        if(len(temp) > 30):
            word_list = mecab.pos(temp)
            i = 0
            ngram = 3
            while i < len(word_list):
                is_over = False
                if len(word_list) < 3:
                    break
                compare = ''
                for n in range(ngram):
                    compare += word_list[i+n][0]

                for dict in dictionary_data:
                    if dict['ngram'] == compare:
                        if dict['emotion'] == 'POS':
                            emotion += dict['figure']
                        elif dict['emotion'] == 'NEG':
                            emotion -= dict['figure']
                        is_over = True
                        break
                if is_over or ngram == 1:
                    i += ngram
                    if len(word_list) - i < 3:
                        ngram = len(word_list) - i
                    else:
                        ngram = 3
                else:
                    ngram -= 1
        if emotion >= 4:
            obj = {'text' : twit['text'], 'figure' : emotion}
            positive_coll.insert_one(obj)
        elif emotion <= -4:
            obj = {'text' : twit['text'], 'figure' : emotion}
            negative_coll.insert_one(obj)
        print(counter)
        counter += 1




dictionary_data = call_dictionary()
print(dictionary_data)
find_emotion(dictionary_data)
