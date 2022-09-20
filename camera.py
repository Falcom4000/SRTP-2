import base64
import datetime
import operator
import os

import cv2
import requests
from synonym import sentiment_classify

'''
print("============================================")
print("============================================")
print("=             欢迎测试本程序                  =")
print("============================================")
print("============================================")
print("============================================")
'''

host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=E2kKXHZ6ReoawMlLjbERhhkO&client_secret=cZO4bvtVxV4OasbGGmI1rUYTNVvh0iQX'
response = requests.get(host)
if response:
    access_token = str(response.json()['access_token'])
else: access_token='24.2f40a01003253f426e6ce84af9720026.2592000.1648123638.282335-25536399'


def save_origin(class_name, frame):
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


def single_individual_identify(cut, dir_name, num_of_result):

    # 对cut进行单主体识别,返回识别结果，将cut存入本地
    cut_base64 = cv2_base64(cut)
    new_params = {"image": cut_base64}
    request_url = "https://aip.baidubce.com/rest/2.0/image-classify/v2/advanced_general" + "?access_token=" + access_token
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    response = requests.post(request_url, data=new_params, headers=headers)
    cv2.imwrite(dir_name + 'cut_' + str(num_of_result) + '.jpg', cut)
    try:
        return (response.json()['result'])
    except:
        return ([])



def cv2_base64(image):
    # cv2格式转成base64格式
    base64_str = cv2.imencode('.jpg', image)[1].tobytes()
    base64_str = base64.b64encode(base64_str)
    return base64_str


def face_search(cut):
    # 人脸搜索
    access_token1 = "24.5d7a52306b69800634cd64cc64f6f7c5.2592000.1646729435.282335-25559586"
    request_url = "https://aip.baidubce.com/rest/2.0/face/v3/search"
    cut_base64 = cv2_base64(cut)
    newparams = {"image": cut_base64, "image_type": "BASE64", "group_id_list": "screenshot", "quality_control": "NONE",
                 "liveness_control": "NONE"}
    request_url = request_url + "?access_token=" + access_token1
    headers = {'content-type': 'application/json'}
    response = requests.post(request_url, data=newparams, headers=headers)
    if response:
        return response.json()


def face_detect(cut, face_detected, dir_name, num_of_result):
    # 人脸检测，若有结果返回1
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


def IsSameImage(text_1, text_2):
    rdata = sentiment_classify(text_1, text_2)
    if text_1 == text_2:
        return True
    try:
        if rdata['result']['score'] > 0.1:
            return True
        else:
            return False
    except:
        return False


