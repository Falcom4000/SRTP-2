# pyrec.py 文件内容
import os
import time as t
import wave

import numpy as np
import pyaudio
from aip import AipSpeech
from ltp import LTP
from scipy import fftpack


def rec(file_name):
    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("开始录音,请说话......")

    frames = []

    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("录音结束,请闭嘴!")

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(class_name + file_name, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()


def wav_to_pcm(wav_file,class_name):
    # 假设 wav_file = "音频文件.wav"
    # wav_file.split(".") 得到["音频文件","wav"] 拿出第一个结果"音频文件"  与 ".pcm" 拼接 等到结果 "音频文件.pcm"
    pcm_file = "%s.pcm" % ((class_name + wav_file).split(".")[0])

    # 就是此前我们在cmd窗口中输入命令,这里面就是在让Python帮我们在cmd中执行命令
    os.system("ffmpeg -y  -i %s  -acodec pcm_s16le -f s16le -ac 1 -ar 16000 %s" % (class_name + wav_file, pcm_file))

    return pcm_file


def play_mp3(file_name):
    os.system('ffplay ' + class_name + file_name)


def recognize(file,class_name):
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
        print(res_str)
        return res_str
    except:
        return '的'


def nlp(res_str):
    APP_ID = '25559029'
    API_KEY = 'PIIyG8nXV0DeVWgo8O0fNGuy'
    SECRET_KEY = 'FuiB46Ek3iHd0elRx49KTm9Xbh1QrHO1'
    client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)
    ltp = LTP()
    segment, hidden = ltp.seg([res_str])
    pos = ltp.pos(hidden)
    print(segment)
    print(pos)
    dict={}
    voice=[]
    i =0
    for word in segment[0]:
        dict[word]=pos[0][i]
        i+=1
    voice.append(dict)
    return voice

def synth_sound(res_str):
    APP_ID = '25559029'
    API_KEY = 'PIIyG8nXV0DeVWgo8O0fNGuy'
    SECRET_KEY = 'FuiB46Ek3iHd0elRx49KTm9Xbh1QrHO1'
    client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)
    synth_context = client.synthesis(res_str, 'zh', 1, {'vol': 5})
    if not isinstance(synth_context, dict):
        with open(class_name + synth_name, 'wb') as f:
            f.write(synth_context)
    else:
        print(synth_context)


'''class recordThread(threading.Thread):
    def __init__(self, threadID, name, recordname, synthname):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.recordname = recordname
        self.synthname = synthname

    def run(self):
        rec(self.recordname)
        res_str = recognize(self.recordname)
        nlp(res_str)
        pygame.mixer.music.load(self.synthname)
        pygame.mixer.music.play()
        print('播放开始')
        time_now = pygame.time.get_ticks()
        while True:
            if (pygame.time.get_ticks() - time_now) > 5000:
                pygame.mixer.music.stop()
                pygame.mixer.music.unload()
                print('播放结束')
                break
        return res_str'''


def recording(filename,class_name,time=0, threshold=2000):
    """
    :param filename: 文件名
    :param time: 录音时间,如果指定时间，按时间来录音，默认为自动识别是否结束录音
    :param threshold: 判断录音结束的阈值
    :return:
    """
    CHUNK = 1024  # 块大小
    FORMAT = pyaudio.paInt16  # 每次采集的位数
    CHANNELS = 2  # 声道数
    RATE = 16000  # 采样率：每秒采集数据的次数
    RECORD_SECONDS = time  # 录音时间
    WAVE_OUTPUT_FILENAME = class_name + filename  # 文件存放位置
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    print("* 录音中...")
    t.sleep(0.5)
    frames = []
    if time > 0:
        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames.append(data)
    else:
        stopflag = 0
        stopflag2 = 0
        while True:
            data = stream.read(CHUNK)
            rt_data = np.frombuffer(data, np.dtype('<i2'))
            # print(rt_data*10)
            # 傅里叶变换
            fft_temp_data = fftpack.fft(rt_data, rt_data.size, overwrite_x=True)
            fft_data = np.abs(fft_temp_data)[0:fft_temp_data.size // 2 + 1]

            # 测试阈值，输出值用来判断阈值
            # print(sum(fft_data) // len(fft_data))

            # 判断麦克风是否停止，判断说话是否结束，# 麦克风阈值，默认7000
            if sum(fft_data) // len(fft_data) > threshold:
                stopflag += 1
            else:
                stopflag2 += 1
            oneSecond = int(RATE / CHUNK)
            if stopflag2 + stopflag > 5 * oneSecond:
                if stopflag2 > 5 * oneSecond // 3 * 2:
                    break
                else:
                    stopflag2 = 0
                    stopflag = 0
            frames.append(data)
    print("* 录音结束")
    stream.stop_stream()
    stream.close()
    p.terminate()
    with wave.open(WAVE_OUTPUT_FILENAME, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

def full():
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    RATE = 16000
    RECORD_SECONDS = 5
    class_name = 'sounds/'
    record_name = 'record.wav'
    recording(record_name, class_name ,time=10)
    res_str = recognize(record_name,class_name)
    return nlp(res_str)

if __name__ == '__main__':
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    RATE = 16000
    RECORD_SECONDS = 5
    class_name = 'sounds/'
    record_name = 'record.wav'
    synth_name = 'synth.mp3'
    recording(record_name, time=10)
    # rec(record_name)
    res_str = recognize(record_name,class_name)
    print(nlp(res_str))
    synth_sound(res_str)
    #play_mp3(synth_name)
