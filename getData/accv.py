'''
Automatically combine consonants and vowels in a sentence
작성자 : Dongki Lee
모듈 기능 : hgtk 라이브러리에서는 전체가 decompose된 항목을 compose, 그 반대의 경우만 할 수 있다.
이 모듈에서는 hgtk의 decompose, compose 기능을 이용하여 문장이 들어왔을 때 가ㄴ다 -> 간다 처럼 받침만이 떨어진 문장을 원래 문장으로 돌릴 수 있게 해주는 기능을 구현하였다.
생성 날자 : 2018.07.05
수정 로그 :
2018.07.05 : 모듈 최초버전 구현
'''
import hgtk
import re

def combine(input_string):
    need_to_bind = re.compile('[ㄱ-ㅎ]')
    m = need_to_bind.search(input_string)
    if m == None:
        return input_string
    else:
        start = m.start()
        decompose = list(hgtk.letter.decompose(input_string[start - 1]))
        remove_key = input_string[start]
        if decompose[2] == '':
            decompose[2] = remove_key
            composed_letter = hgtk.letter.compose(decompose[0], decompose[1], decompose[2])
            input_string = input_string[0:start-1] + composed_letter + input_string[start+1:]
        else:
            input_string = input_string[0:start] + input_string[start+1:]
        return input_string
