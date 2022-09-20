import _BotIO as io
from record import full
from collections import Counter
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns
import camera as ca
from PyQt5 import QtCore, QtGui, QtWidgets
import GUI


rc = {'font.sans-serif': 'SimHei',
      'axes.unicode_minus': False}
sns.set(context='notebook', style='darkgrid', rc=rc)
def nlp_moudle(results, dir_name, self):
    all_results = io.load_from_json_file('results.json')
    flag_found = 0
    for key, value in all_results.items():
        try:
            if value[0][0]['result'] == results[0]['keyword']:
                result_words = value[1]
                flag_found = 1
                break
        except TypeError:
            try:
                if value[0][0][0]['result'] == results[0]['keyword']:
                    result_words = value[1]
                    flag_found = 1
                    break
            except TypeError:
                try:
                    if value[0][0][0][0]['result'] == results[0]['keyword']:
                        result_words = value[1]
                        flag_found = 1
                        break
                except TypeError:
                    pass

    if not flag_found:
        self.is_unregistered=1
        _translate = QtCore.QCoreApplication.translate
        self.pushButton_2.setText(_translate("MainWindow", "当前有未经注册的物品"))
 #       self.plainTextEdit.appendPlainText("您所选择的物品尚未注册")

  #      voice = full(self)  # 录音：每个矩形框都会录一次音！
   #     save_results(results, voice,dir_name)  # 保存结果
        return
    nlp_dict = {}
    word_count = []
    temp = {}
    for result_word in result_words.values():
        for i in result_word:
            for word_key, word_value in i.items():
                nlp_dict[word_value] = {}  # word_key是词本身，world_value是词性
                word_count.append(word_key)
                temp[word_key] = word_value
    num_of_total = Counter(word_count)  # num_of_total 里key是词, value是词出现的次数
    for nword_key, nword_value in temp.items():  # temp中key是词本身 value是词性
        nlp_dict[nword_value][nword_key]=num_of_total[nword_key]

    self.plainTextEdit.appendPlainText(str(nlp_dict))
    return nlp_dict

    #dict2pandas(nlp_dict)

def nlp_face_moudle(results, dir_name, self):    #  这results存用户名 是str
    all_results = io.load_from_json_file('results.json')
    flag_found = 0
    for key, value in all_results.items():
        try:
            if value[0][0]['result'] == results:
                result_words = value[1]
                flag_found = 1
                break
        except TypeError:
            try:
                if value[0][0][0]['result'] == results:
                    result_words = value[1]
                    flag_found = 1
                    break
            except TypeError:
                try:
                    if value[0][0][0][0]['result'] == results:
                        result_words = value[1]
                        flag_found = 1
                        break
                except TypeError:
                    pass

    if not flag_found:

  #      self.plainTextEdit.appendPlainText("此用户尚未注册")

   #     voice = full(self)  # 录音：每个矩形框都会录一次音！
    #    save_face_results(results, voice, dir_name)  # 保存结果
        return
    nlp_dict = {}
    word_count = []
    temp = {}
    for result_word in result_words.values():
        for i in result_word:
            for word_key, word_value in i.items():
                nlp_dict[word_value] = {}  # word_key是词本身，world_value是词性
                word_count.append(word_key)
                temp[word_key] = word_value
    num_of_total = Counter(word_count)  # num_of_total 里key是词, value是词出现的次数
    for nword_key, nword_value in temp.items():  # temp中key是词本身 value是词性
        nlp_dict[nword_value][nword_key] = num_of_total[nword_key]

    self.plainTextEdit.appendPlainText(str(nlp_dict))
    return nlp_dict

    #dict2pandas(nlp_dict)

def dict2pandas(dict):
    df=pd.DataFrame(columns=['name','tag','count'])
    i=0
    for tag, dicts in dict.items():
        for word, count in dicts.items():
            df.loc[i]=[word,tag,count]
            i+=1
    sns.barplot(x='name', y='count', hue='tag', data=df)
    plt.show()

def save_results(results, voice,dir_name):
    flag = False
    all_results = io.load_from_json_file('results.json')
    for logid, value in all_results.items():
        try:
            if ca.IsSameImage(results[0]['keyword'], value[0][0]['result']):
                io.write_voice('results', logid, voice)
                flag = True
                break

        except TypeError:
            try:
                if ca.IsSameImage(results[0]['keyword'], value[0][0][0]['result']):
                    io.write_voice('results', logid, voice)
                    flag = True
                    break
            except TypeError:
                if ca.IsSameImage(results[0]['keyword'], value[0][0][0][0]['result']):
                    io.write_voice('results', logid, voice)
                    flag = True
                    break

    if not flag:
        io.register('results', key=dir_name[7:-1], value={'result': results[0]['keyword']})
        io.register('results', key=dir_name[7:-1], value={'voice': voice})

def save_face_results(results, voice,dir_name):    #  这results存用户名 是str
    flag = False
    all_results = io.load_from_json_file('results.json')
    for logid, value in all_results.items():
        try:
            if ca.IsSameImage(results, value[0][0]['result']):
                io.write_voice('results', logid, voice)
                flag = True
                break

        except TypeError:
            try:
                if ca.IsSameImage(results, value[0][0][0]['result']):
                    io.write_voice('results', logid, voice)
                    flag = True
                    break
            except TypeError:
                if ca.IsSameImage(results, value[0][0][0][0]['result']):
                    io.write_voice('results', logid, voice)
                    flag = True
                    break

    if not flag:
        io.register('results', key=dir_name[7:-1], value={'result': results})
        io.register('results', key=dir_name[7:-1], value={'voice': voice})