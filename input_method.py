#encoding=utf-8
import jieba
import chardet

count = 0  # 统计现在数到初始分词中的第几个词
my_sum = 0  # 统计目前一共有几个不同的词
class Word:
    def __init__(self, name):
        self.name = name
        self.front = []
        self.behind = []

line = open('chatdata.txt',encoding="utf-8").read()

seg_list=list(jieba.cut(line))

my_word = []
reflect=[]
for i in range(99999):
    reflect.append(0)

for name in seg_list:
    #
    if seg_list.index(name) == count:  # 如果当前词语在语料库是第一次出现
        my_word.append(Word(name))  # 为这个词语创建一个对象
        reflect[seg_list.index(name)] = my_sum
        my_sum = my_sum+1
    if count != 0:  # 如果这个词不是seg_list里的第一个词
        my_word[reflect[seg_list.index(name)]].front.append(seg_list[count-1])  # 把这个词的前一个词统计上
    if count != len(seg_list)-1:  # 如果这个词不是seg_list里的最后一个词
        my_word[reflect[seg_list.index(name)]].behind.append(seg_list[count+1])  # 把这个词的后一个词统计上

    count = count+1  # 统计现在算到seg_list的第几个词了

'''
for i in my_word:
    print(i.name)
    dict1 = {}
    for key in i.front:
        dict1[key] = dict1.get(key, 0) + 1
    dict1 = sorted(dict1.items(), key=lambda d:d[1], reverse = True)
    print('前：', dict1)
    dict2 = {}
    for key in i.behind:
        dict2[key] = dict2.get(key, 0) + 1
    dict2 = sorted(dict2.items(), key=lambda d:d[1], reverse = True)
    print('后：', dict2)
'''

while True:
    message = input("请输入词语：")
    if message == 'q':
        break
    if message in seg_list:
        dict1 = {}
        for key in my_word[reflect[seg_list.index(message)]].front:
            dict1[key] = dict1.get(key, 0) + 1
        dict1 = sorted(dict1.items(), key=lambda d:d[1], reverse = True)
        print('前：', dict1)
        dict2 = {}
        for key in my_word[reflect[seg_list.index(message)]].behind:
            dict2[key] = dict2.get(key, 0) + 1
        dict2 = sorted(dict2.items(), key=lambda d:d[1], reverse = True)
        print('后：', dict2)
    else:
        print("词语未录入")




