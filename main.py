import cv2

import camera as ca
import _BotIO as io
from record import full
from collections import Counter


def save_results(results, voice):
    flag = False
    all_results = io.load_from_json_file('results.json')
    for logid, value in all_results.items():
        if ca.IsSameImage(results[0]['keyword'], value[0][0]['result']):
            io.write_voice('results', logid, voice)
            flag = True
            break
    if not flag:
        io.register('results', key=dir_name[7:-1], value={'result': results[0]['keyword']})
        io.register('results', key=dir_name[7:-1], value={'voice': voice})


def train_mode(dir_name):
    result_order = ca.multiple_individuals_identify(dir_name)  # 对origin 进行多主体识别，结果排序
    num_of_result = 1
    for individual in result_order:
        # 对多主体识别得到的所有结果：
        img = frame
        if individual['score'] < 0.6:  # 只考虑置信度大于0.6的结果
            break
        else:
            cut, img = ca.cut_individual(individual, img, frame)  # 剪切图像为cut，并在origin上又标注一个矩形，得到img
            face_detected = 0
            if ca.face_detect(cut, face_detected, dir_name, num_of_result) == 0:
                results = ca.single_individual_identify(cut, dir_name, num_of_result)  # 图像识别
                temps = []
                for i in results:
                    if i['score']>0.6:
                        temps.append(i)
                if temps:
                    print(temps)
                    voice = full()  # 录音：每个矩形框都会录一次音！
                    save_results(results, voice)  # 保存结果
            num_of_result += 1
    cv2.imwrite(dir_name + 'rectangle.jpg', img)


def use_mode(dir_name):
    result_order = ca.multiple_individuals_identify(dir_name)  # 对origin 进行多主体识别，结果排序
    num_of_result = 1
    for individual in result_order:
        # 对多主体识别得到的所有结果：
        img = frame
        if individual['score'] < 0.6:  # 只考虑置信度大于0.6的结果
            break
        else:
            cut, img = ca.cut_individual(individual, img, frame)  # 剪切图像为cut，并在origin上又标注一个矩形，得到img
            face_detected = 0
            if ca.face_detect(cut, face_detected, dir_name, num_of_result) == 0:
                results = ca.single_individual_identify(cut, dir_name, num_of_result)  # 图像识别
                temps = []
                for i in results:
                    if i['score'] > 0.6:
                        temps.append(i)
                if temps:
                    nlp_moudle(results)
            num_of_result += 1
    cv2.imwrite(dir_name + 'rectangle.jpg', img)


def nlp_moudle(results):
    all_results = io.load_from_json_file('results.json')
    flag_found = 0
    for key, value in all_results.items():
        if value[0][0]['result'] == results[0]['keyword']:
            result_words = value[1]
            flag_found = 1
            break
    if not flag_found:
        print("您所选择的物品尚未注册")
        voice = full()  # 录音：每个矩形框都会录一次音！
        save_results(results, voice)  # 保存结果
        return
    nlp_dict = {}
    word_count = []
    temp = {}
    for result_word in result_words.values():
        for word_key, word_value in result_word[0].items():
            nlp_dict[word_value] = []  # word_key是词本身，world_value是词性
            word_count.append(word_key)
            temp[word_key] = word_value
    num_of_total = Counter(word_count)  # num_of_total 里key是词, value是词出现的次数
    for nword_key, nword_value in temp.items():  # temp中key是词本身 value是词性
        nlp_dict[nword_value].append({nword_key: num_of_total[nword_key]})
    print(nlp_dict)


if __name__ == '__main__':

    class_name = 'images'
    cap = cv2.VideoCapture(0 + cv2.CAP_DSHOW)
    access_token = '24.8f102109268b8c4de7e57f7ed5887012.2592000.1645240208.282335-25536399'

    while True:
        # 读取摄像头传来的每帧画面，等待用户摁下键盘
        ret, frame = cap.read()
        frame = cv2.flip(frame, 1, dst=None)
        cv2.imshow("capture", frame)
        input = cv2.waitKey(1) & 0xFF

        if input == ord('x'):
            # 训练模式
            dir_name = ca.save_origin(class_name, frame)  # 保存此刻截的图(origin)，返回包含时间戳的保存目录
            train_mode(dir_name)  # 进入训练模式

        if input == ord('d'):
            # 使用模式
            dir_name = ca.save_origin(class_name, frame)  # 保存此刻截的图(origin)，返回包含时间戳的保存目录
            use_mode(dir_name)  # 进入使用模式

        if input == ord('q'):
            break
