import base64
import datetime
import operator
import os

import cv2
import requests

print("=============================================")
print("=  热键(请在摄像头的窗口使用)：             =")
print("=  x: 拍摄图片                              =")
print("=  q: 退出                                  =")
print("=============================================")


def save_origin():
    # 保存原始图片,返回保存图片的路径
    dir_name = (class_name + '/' + datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S_%f') + '/')
    os.mkdir(dir_name)
    cv2.imwrite(dir_name + 'origin.jpg', frame)
    return dir_name


def multiple_individuals_identify(dir_name):
    # 多主体识别，返回排序好的多主体识别结果
    name_of_photo_origin = (dir_name + 'origin.jpg')
    request_url = "https://aip.baidubce.com/rest/2.0/image-classify/v1/multi_object_detect"
    f = open(name_of_photo_origin, 'rb')
    img = base64.b64encode(f.read())
    params = {"image": img}
    request_url = request_url + "?access_token=" + access_token
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    response = requests.post(request_url, data=params, headers=headers)
    if response:
        result = response.json()['result']
    result_order = sorted(result, key=operator.itemgetter('score'), reverse=True)
    return result_order


def cut_individual(individual, img, frame):
    # 将origin按照多主体识别的结果切成一个个cut, 同时在img上绘制矩形，返回cut和矩形数+1的img
    top = individual['location']['top']
    height = individual['location']['height']
    width = individual['location']['width']
    left = individual['location']['left']
    cut = frame[top:top + height, left:left + width]
    img = cv2.rectangle(img, (left, top), (left + width, top + height), (0, 255, 255), 2)
    return cut, img


def single_individual_identify(cut):
    # 对cut进行单主体识别,返回识别结果，将cut存入本地
    cut_base64 = cv2_base64(cut)
    new_params = {"image": cut_base64}
    request_url = "https://aip.baidubce.com/rest/2.0/image-classify/v2/advanced_general" + "?access_token=" + access_token
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    response = requests.post(request_url, data=new_params, headers=headers)
    cv2.imwrite(dir_name + 'cut_' + str(num_of_result) + '.jpg', cut)
    return response.json()['result']


def cv2_base64(image):
    # cv2格式转成base64格式
    base64_str = cv2.imencode('.jpg', image)[1].tobytes()
    base64_str = base64.b64encode(base64_str)
    return base64_str


def face_search(cut):#人脸搜索
    access_token1= "24.5d7a52306b69800634cd64cc64f6f7c5.2592000.1646729435.282335-25559586"
    request_url = "https://aip.baidubce.com/rest/2.0/face/v3/search"
    cut_base64 = cv2_base64(cut)
    newparams = {"image": cut_base64, "image_type": "BASE64", "group_id_list": "screenshot", "quality_control": "NONE",
                 "liveness_control": "NONE"}
    request_url = request_url + "?access_token=" + access_token1
    headers = {'content-type': 'application/json'}
    response = requests.post(request_url, data=newparams, headers=headers)
    if response:
        return response.json()

def face_detect(cut,face_detected):#人脸检测，若有结果返回1
    face_result = face_search(cut)
    try:
        for face in face_result['result']['user_list']:
            if face['score'] > 60:
                print(face['user_id'])
                face_detected = 1
                cv2.imwrite(dir_name + 'face_' + str(num_of_result) + '.jpg', cut)
                break
    except:
        pass
    return face_detected

class_name = 'test'
cap = cv2.VideoCapture(0 + cv2.CAP_DSHOW)
access_token = '24.8f102109268b8c4de7e57f7ed5887012.2592000.1645240208.282335-25536399'

while True:
    # 读取摄像头传来的每帧画面，等待用户摁下键盘
    ret, frame = cap.read()
    frame = cv2.flip(frame, 1, dst=None)
    cv2.imshow("capture", frame)
    input = cv2.waitKey(1) & 0xFF

    if input == ord('x'):
        dir_name = save_origin()  # 保存此刻截的图(origin)，返回包含时间戳的保存目录
        result_order = multiple_individuals_identify(dir_name)  # 对origin 进行多主体识别，结果排序
        num_of_result = 1
        for individual in result_order:
            # 对多主体识别得到的所有结果：
            img = frame
            if individual['score'] < 0.6:  # 只考虑置信度大于0.6的结果
                break
            else:
                cut, img = cut_individual(individual, img, frame)  # 剪切图像为cut，并在origin上又标注一个矩形，得到img
                face_detected = 0
                if face_detect(cut, face_detected) == 0:
                    print(single_individual_identify(cut))  # 图像识别
                num_of_result += 1
        cv2.imwrite(dir_name + 'rectangle.jpg', img)
    if input == ord('q'):
        break
# test
