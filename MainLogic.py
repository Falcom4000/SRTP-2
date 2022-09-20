import sys
import cv2
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QPushButton, QGroupBox, QVBoxLayout
from PyQt5.QtWebEngineWidgets import *
import threading

import _BotIO as io
import camera as ca
import facedw as fa
import nlp
import GUI
from record import full
from record import name_full
from record import synth_sound, play_mp3
#  一次性读全部内容，返回列表
with open("facen.txt", "r", encoding="utf-8") as f:
    facenum = int(f.read())  # 存系统中脸的总个数
    #  print("facenum:", facenum)

with open("usern.txt", "r", encoding="utf-8") as f:
    usernum = int(f.read())  # 存系统中用户的总个数
    #  print("usernum:", usernum)

f = open("name.txt", "r", encoding="utf-8")
name = f.read().splitlines()  # 存系统中用户对应的名字 这个列表的索引是user的顺序 内容是user的名字
#  print("name:", name)


class Main(QMainWindow, GUI.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        '''self.browser=QWebEngineView()
        # 加载html代码
        with open("help.html", 'r', encoding="utf-8") as web:
            self.browser.setHtml(web.read())
            #self.browser.show()
            self.browser.setWindowTitle('帮助页面')'''

        self.setupUi(self)
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.show_viedo)
        self.cap_video = 0
        self.flag = 0
        self.img = []
        self.pushButton.clicked.connect(self.use)
        self.pushButton_2.clicked.connect(self.train)
        self.pushButton_4.clicked.connect(self.play_synth_mp3)
        self.label.setScaledContents(True)
        self.cap_video = cv2.VideoCapture(0)
        self.timer.start(50)
        self.is_unregistered=0
        self.to_read_words=''
        self.synth_name = 'synth.mp3'

    def play_synth_mp3(self):
        synth_sound(self.to_read_words,ui,self.synth_name)
        play_mp3(self.synth_name)
        self.to_read_words=''
        self.textEdit.clear()

    def show_viedo(self):
        ret, self.img = self.cap_video.read()
        #self.img = cv2.flip(self.img, 1, dst=None)
        if ret:
            self.show_cv_img(self.img)

    def show_cv_img(self, img):
        shrink = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        QtImg = QtGui.QImage(shrink.data,
                             shrink.shape[1],
                             shrink.shape[0],
                             shrink.shape[1] * 3,
                             QtGui.QImage.Format_RGB888)
        jpg_out = QtGui.QPixmap(QtImg).scaled(self.label.width(), self.label.height())
        self.label.setScaledContents(True)
        self.label.setPixmap(jpg_out)

    def clickButton(self):
        sender = self.sender()
        self.textEdit.insertPlainText(sender.text())
        self.to_read_words=self.to_read_words+sender.text()


    def use(self):

        class_name = 'images'
        frame=self.img
        self.timer.stop()

        groupbox = QGroupBox()
        self.vlayout = QVBoxLayout(groupbox)
        while self.toolBox.count():
            self.toolBox.removeItem(0)

        dir_name = ca.save_origin(class_name, frame)  # 保存此刻截的图(origin)，返回包含时间戳的保存目录

        self.plainTextEdit.appendPlainText('人脸检测：')
        flag, f_result_order = fa.haveface(dir_name, self)  # 看origin有没有人脸 dir_name好像是包含时间戳的保存目录

        if flag == 0 or flag == 2:  # 没人脸 or 出错了
            self.plainTextEdit.appendPlainText(str(f_result_order['error_msg']))
        if flag == 1:  # 有人脸
            for face in f_result_order['result']['face_list']:
                # 对所有人脸：
                img = frame
                if face['quality']['completeness'] == 1 and face['quality']['blur'] < 0.7:
                    # 检测到的人脸质量正常
                    cut, img = fa.cut_individual(face, img, frame)
                    global facenum
                    facenum = facenum + 1
                    cv2.imwrite('face_' + str(facenum) + '.jpg', cut)
                    #  写之前清空文件中的原有数据(覆盖)
                    with open("facen.txt", 'w', encoding="utf-8") as f:
                        f.write(str(facenum))

                    flag, f_results = fa.face_find(cut, self)

                    self.show_cv_img(cut)
                    cv2.waitKey(1000)
                    global name
                    if flag == 1:  # 人脸已经注册过
                        thisname = name[int(f_results)]
                        self.plainTextEdit.appendPlainText("此人是" + thisname)
                    if flag == 0:  # 人脸没有注册过
                        self.plainTextEdit.appendPlainText("此人未注册，请使用语音说出此人的名字")
                        global usernum
                        #  写之前清空文件中的原有数据(覆盖)
                        with open("usern.txt", 'w', encoding="utf-8") as f:
                            f.write(str(usernum))
                        thisname = name_full(self)
                        name.append(thisname)
                        #  写之前清空文件中的原有数据(不覆盖)
                        with open("name.txt", 'a', encoding="utf-8") as f:
                            f.write(thisname + '\n')

                        self.plainTextEdit.appendPlainText("人脸注册：")

                        self.plainTextEdit.appendPlainText(str(fa.face_registration(cut, usernum)))

                        usernum = usernum + 1  # 先注册再++ 可以用上name[0]

                    button_dict = nlp.nlp_face_moudle(thisname, dir_name, self)  # 这results存用户名 是str

                    if button_dict:
                        for key, value in button_dict.items():
                            for k, v in value.items():
                                self.buttonfrist = QPushButton(k, self)
                                self.buttonfrist.clicked.connect(self.clickButton)
                                #  self.page.addWidget(self.buttonfrist, k)

                                self.vlayout.addWidget(self.buttonfrist)

                cv2.imwrite(dir_name + 'rectangle.jpg', img)


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
                        #self.show_cv_img(cut)
                        #cv2.waitKey(1000)
                        self.plainTextEdit.appendPlainText(str(temps))
                        button_dict = nlp.nlp_moudle(results, dir_name, self)
                        if button_dict:
                            for key, value in button_dict.items():
                                for k, v in value.items():
                                    self.buttonfrist = QPushButton(k, self)
                                    self.buttonfrist.clicked.connect(self.clickButton)
                                    #  self.page.addWidget(self.buttonfrist, k)
                                    self.vlayout.addWidget(self.buttonfrist)

                else:
                    pass
                num_of_result += 1
            cv2.imwrite(dir_name + 'rectangle.jpg', img)
            self.toolBox.addItem(groupbox, '待选词')
            self.show_cv_img(img)
            cv2.waitKey(5000)
        if (self.is_unregistered==1):
            self.is_unregistered = 0
            msg = QMessageBox(self)  # 实例化一个QMessageBox对象
            msg.setWindowTitle("Question")
            msg.setText("当前有未经注册的物品，是否进入训练模式")
            msg.setIcon(QMessageBox.Question)

            # 调用addButton方法
            msg.addButton("是", QMessageBox.YesRole)
            msg.addButton("否", QMessageBox.NoRole)
            msg.exec()
            if(msg.clickedButton().text() == "是") :
                msg.close()
                self.train()
            else:
                msg.close()
            _translate = QtCore.QCoreApplication.translate
            self.pushButton_2.setText(_translate("MainWindow", "训练模式"))
            self.timer.start(50)
            return
        self.timer.start(50)

    def train(self):
        class_name = 'images'
        frame = self.img
        self.timer.stop()
        dir_name = ca.save_origin(class_name, frame)  # 保存此刻截的图(origin)，返回包含时间戳的保存目录
        global printtext

        flag, f_result_order = fa.haveface(dir_name, self)  # 看origin有没有人脸 dir_name好像是包含时间戳的保存目录
        if flag == 0 or flag == 2:  # 没人脸 or 出错了

            self.plainTextEdit.appendPlainText(str(f_result_order['error_msg']))

        if flag == 1:  # 有人脸
            for face in f_result_order['result']['face_list']:
                # 对所有人脸：
                img = frame
                if face['quality']['completeness'] == 1 and face['quality']['blur'] < 0.7:
                    # 检测到的人脸质量正常
                    cut, img = fa.cut_individual(face, img, frame)
                    global facenum
                    facenum = facenum + 1
                    cv2.imwrite('face_' + str(facenum) + '.jpg', cut)
                    #  写之前清空文件中的原有数据(覆盖)
                    with open("facen.txt", 'w', encoding="utf-8") as f:
                        f.write(str(facenum))

                    flag, f_results = fa.face_find(cut, self)

                    self.show_cv_img(cut)
                    cv2.waitKey(2000)
                    global name
                    if flag == 1:  # 人脸已经注册过
                        thisname = name[int(f_results)]

                        self.plainTextEdit.appendPlainText("此人是" + thisname)

                    if flag == 0:  # 人脸没有注册过

                        self.plainTextEdit.appendPlainText("此人未注册，请使用语音说出此人的名字")
                        global usernum
                        thisname = name_full(self)
                        name.append(thisname)
                        #  写之前清空文件中的原有数据(不覆盖)
                        with open("name.txt", 'a', encoding="utf-8") as f:
                            f.write(thisname + '\n')

                        self.plainTextEdit.appendPlainText("人脸注册：")

                        self.plainTextEdit.appendPlainText(str(fa.face_registration(cut, usernum)))

                        usernum = usernum + 1  # 先注册再++ 可以用上name[0]
                        #  写之前清空文件中的原有数据(覆盖)
                        with open("usern.txt", 'w', encoding="utf-8") as f:
                            f.write(str(usernum))
                    self.plainTextEdit.appendPlainText("* 录音中...")
                    voice = full(self)  # 录音：每个矩形框都会录一次音！
                    self.plainTextEdit.appendPlainText("* 录音结束...")
                    save_face_results(thisname, voice, dir_name)  # 保存结果
                cv2.imwrite(dir_name + 'rectangle.jpg', img)
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
                    results = ca.single_individual_identify(cut, dir_name, num_of_result)  # 图像识别 传后两个参数就是为了存截图
                    temps = []  # 定义temps为空列表
                    for i in results:  # 通用物体识别会识别出不止一个主体 遍历一下
                        if i['score'] > 0.6:
                            temps.append(i)  # 如果有匹配分数大于0.6的 就把识别出的物体插入temps列表
                    if temps:  # 如果temps列表里面有物体
                        self.plainTextEdit.appendPlainText(str(temps))
                        self.plainTextEdit.appendPlainText("* 录音中...")
                        self.show_cv_img(cut)
                        cv2.waitKey(2000)

                        voice = full(self)  # 录音：每个矩形框都会录一次音！ voice应该是列表 里面存分好的词
                        self.plainTextEdit.appendPlainText("* 录音结束...")
                        save_results(results, voice, dir_name)  # 保存结果
                else:
                    pass
                num_of_result += 1  # 遍历一个主体之后就计数加1
            cv2.imwrite(dir_name + 'rectangle.jpg', img)
        self.timer.start(50)


def save_results(results, voice, dir_name):
    flag = False
    all_results = io.load_from_json_file('results.json')  # 返回的是一个字典类型
    for logid, value in all_results.items():  # .items()以列表返回可遍历的(键, 值) 元组数组
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
                try:
                    if ca.IsSameImage(results[0]['keyword'], value[0][0][0][0]['result']):
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


def save_face_results(results, voice, dir_name):  # 这results存用户名 是str
    flag = False
    all_results = io.load_from_json_file('results.json')  # 返回的是一个字典类型
    for logid, value in all_results.items():  # .items()以列表返回可遍历的(键, 值) 元组数组
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


if __name__ == '__main__':
    # 只有直接运行这个脚本，才会往下执行
    # 别的脚本文件执行，不会调用这个条件句

    # 实例化，传参
    app = QApplication(sys.argv)

    # 创建对象
    # mainWindow = QMainWindow()
    # 创建ui，引用demo1文件中的Ui_MainWindow类
    ui = Main()
    # 调用Ui_MainWindow类的setupUi，创建初始组件
    # ui.setupUi(mainWindow)
    # 创建窗口
    ui.show()
    ui.showFullScreen()
    # 进入程序的主循环，并通过exit函数确保主循环安全结束(该释放资源的一定要释放)
    sys.exit(app.exec_())
