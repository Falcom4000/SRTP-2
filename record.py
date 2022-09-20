# pyrec.py 文件内容
import os
import time as t
import wave

import numpy as np
import pyaudio
from aip import AipSpeech
from ltp import LTP
from scipy import fftpack
from PyQt5.Qt import QThread
from PyQt5.QtWidgets import QMessageBox
import cv2


class ThreadClass(QtCore.QThread):
    any_signal = QtCore.pyqtSignal(int)

    def __init__(self, parent=None, index=0):
        super(ThreadClass, self).__init__(parent)
        self.index = index
        self.is_running = True

    def run(self):
        print('Starting thread...', self.index)
        cnt = 0
        while (True):
            cnt += 1
            if cnt == 99: cnt = 0
            time.sleep(0.01)
            self.any_signal.emit(cnt)

    def stop(self):
        self.is_running = False
        print('stopping thread...', self.index)
        self.terminate()


def wav_to_pcm(wav_file, class_name):
    # 假设 wav_file = "音频文件.wav"
    # wav_file.split(".") 得到["音频文件","wav"] 拿出第一个结果"音频文件"  与 ".pcm" 拼接 等到结果 "音频文件.pcm"
    pcm_file = "%s.pcm" % ((class_name + wav_file).split(".")[0])

    # 就是此前我们在cmd窗口中输入命令,这里面就是在让Python帮我们在cmd中执行命令
    os.system("ffmpeg -loglevel quiet -y  -i %s  -acodec pcm_s16le -f s16le -ac 1 -ar 16000 %s" % (class_name + wav_file, pcm_file))

    return pcm_file


def play_mp3(file_name):
    class_name = 'sounds/'
    os.system('ffplay '+'-nodisp -autoexit ' + class_name + file_name)


def recognize(file, class_name, self):
    APP_ID = '25559029'
    API_KEY = 'PIIyG8nXV0DeVWgo8O0fNGuy'
    SECRET_KEY = 'FuiB46Ek3iHd0elRx49KTm9Xbh1QrHO1'
    client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)
    pcm_file = wav_to_pcm(file,class_name)
    with open(pcm_file, 'rb') as fp:
        file_context = fp.read()
    res = client.asr(file_context, 'pcm', 16000, {'dev_pid': 1536, })
    try:
        res_str = res['result'][0]

        self.plainTextEdit.appendPlainText(str(res_str))

        return res_str
    except:
        return '的'


def nlp(res_str, self):
    ltp = LTP()
    segment, hidden = ltp.seg([res_str])
    pos = ltp.pos(hidden)

    self.plainTextEdit.appendPlainText(str(segment))
    self.plainTextEdit.appendPlainText(str(pos))

    dict={}
    voice=[]
    i =0
    for word in segment[0]:
        dict[word]=pos[0][i]
        i+=1
    voice.append(dict)
    return voice

def synth_sound(res_str, self,synth_name):
    APP_ID = '25559029'
    API_KEY = 'PIIyG8nXV0DeVWgo8O0fNGuy'
    SECRET_KEY = 'FuiB46Ek3iHd0elRx49KTm9Xbh1QrHO1'
    class_name='sounds/'
    client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)
    synth_context = client.synthesis(res_str, 'zh', 1, {'vol': 5})
    if not isinstance(synth_context, dict):
        with open(class_name + synth_name, 'wb') as f:
            f.write(synth_context)
    else:

        self.plainTextEdit.appendPlainText(str(synth_context))


def recording(filename, class_name, self, time=0, threshold=2000):
    """
    :param filename: 文件名
    :param time: 录音时间,如果指定时间，按时间来录音，默认为自动识别是否结束录音
    :param threshold: 判断录音结束的阈值
    :return:
    """
    CHUNK = 1024  # 块大小
    FORMAT = pyaudio.paInt16  # 每次采集的位数
    CHANNELS = 1  # 声道数
    RATE = 16000  # 采样率：每秒采集数据的次数
    RECORD_SECONDS = time  # 录音时间
    WAVE_OUTPUT_FILENAME = class_name + filename  # 文件存放位置
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    frames = []

    choice = QMessageBox.question(self, 'Change Text?', 'Would you like to change the button text?',
                                  QMessageBox.Yes | QMessageBox.No)  # 1

    if choice == QMessageBox.Yes:  # 2
        if time > 0:
        #for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            while(1):
                data = stream.read(CHUNK)
                frames.append(data)

                if choice == QMessageBox.No:  # 4
                    break
    elif choice == QMessageBox.No:  # 4
        pass

    stream.stop_stream()
    stream.close()
    p.terminate()
    with wave.open(WAVE_OUTPUT_FILENAME, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

def full(self):
    class_name = 'sounds/'
    record_name = 'record.wav'
    recording(record_name, class_name, self, time=5)
    res_str = recognize(record_name,class_name, self)
    return nlp(res_str, self)

def name_full(self):
    class_name = 'sounds/'
    record_name = 'record.wav'
    recording(record_name, class_name, self, time=5)
    res_str = recognize(record_name,class_name, self)
    return res_str

if __name__ == '__main__':
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    RATE = 16000
    RECORD_SECONDS = 5
    class_name = 'sounds/'
    record_name = 'record.wav'
    synth_name = 'synth.mp3'

    from MainLogic import ui

    recording(record_name, class_name, ui, time=10)
    # rec(record_name)
    res_str = recognize(record_name,class_name, ui)
    ui.plainTextEdit.appendPlainText(str(nlp(res_str, ui)))

    synth_sound(res_str, ui,synth_name)
    play_mp3(synth_name)
