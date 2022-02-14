
# encoding:utf-8

import requests
import json
import urllib


def sentiment_classify(text_1 , text_2):
    access_token = '24.8ac8665b84218da54a6e6f7b7afb9073.2592000.1647169432.282335-25569559'
    raw = {"word_1":"内容" , "word_2":"内容"}
    raw['word_1'] = text_1
    raw['word_2'] = text_2
    data = json.dumps(raw).encode('utf-8')
    host = "https://aip.baidubce.com/rpc/2.0/nlp/v2/word_emb_sim?charset=UTF-8&access_token="+access_token
    request = urllib.request.Request(url=host,data=data)
    request.add_header('Content-Type', 'application/json')
    response = urllib.request.urlopen(request)
    content = response.read().decode('utf-8')
    rdata = json.loads(content)
    return rdata

if __name__=='__main__':
    print ("请输入第一个词语")
    word_f = input()
    print ("请输入第二个词语")
    word_s = input()

    print (sentiment_classify(word_f , word_s))