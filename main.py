import cv2
import camera as ca
import _BotIO as io
import nlp
from record import full

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
                    if i['score'] > 0.6:
                        temps.append(i)
                if temps:
                    print(temps)
                    cv2.imshow("cut" + str(num_of_result), cut)
                    cv2.waitKey(1)
                    voice = full()  # 录音：每个矩形框都会录一次音！
                    save_results(results, voice,dir_name)  # 保存结果
                    cv2.destroyWindow("cut" + str(num_of_result))
            else:
                pass
            num_of_result += 1
        cv2.imwrite(dir_name + 'rectangle.jpg', img)


def use_mode(dir_name):
    result_order = ca.multiple_individuals_identify(dir_name)  # 对origin 进行多主体识别，结果排序
    num_of_result = 1
    for individual in result_order:
        # 对多主体识别得到的所有结果：
        img = frame
        if individual['score'] < 0.4:  # 只考虑置信度大于0.6的结果
            break
        else:
            cut, img = ca.cut_individual(individual, img, frame)  # 剪切图像为cut，并在origin上又标注一个矩形，得到img
            face_detected = 0
            if ca.face_detect(cut, face_detected, dir_name, num_of_result) == 0:
                results = ca.single_individual_identify(cut, dir_name, num_of_result)
                # 图像识别
                temps = []
                for i in results:
                    if i['score'] > 0.6:
                        temps.append(i)
                if temps:
                    cv2.imshow("cut" + str(num_of_result), cut)
                    cv2.waitKey(1000)
                    print(temps)
                    nlp.nlp_moudle(results,dir_name)
                    cv2.destroyWindow("cut" + str(num_of_result))
            else:
                pass
            num_of_result += 1
        cv2.imwrite(dir_name + 'rectangle.jpg', img)
if __name__ == '__main__':

    class_name = 'images'
    cap = cv2.VideoCapture(0 + cv2.CAP_DSHOW)

    while True:
        # 读取摄像头传来的每帧画面，等待用户摁下键盘
        ret, frame = cap.read()
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
