""""
仕様
200ms以上の無音でバッファ削除 フラグを建てる
200ms以上のバッファ && 200ms以上の無音 -> 音声をモデルに入力
フラグが立っている状態で音声が入力される -> フラグを消してバッファに音声を貯める
200ms未満のバッファ && 200ms以上の無音 -> バッファ削除 && フラグを建てる
"""

import pyaudio
# import matplotlib.pyplot as plt
import numpy as np
import webrtcvad
import time
# from model_turntaking import ModelTurntaking
import threading
import queue
import sys
from scipy.io.wavfile import write

# デモ用モデル読み込み

import torch
import torch.nn as nn
from torch.utils.data import Dataset
from torch.utils.data import DataLoader
import torch.optim as optim
import torchaudio
import torchaudio.functional as Fa
import torch.nn.functional as F
import torchaudio.transforms as T
import os
import glob
# from IPython.display import Audio, display
# import pandas as pd
# from tqdm.notebook import tqdm
# import matplotlib.pyplot as plt
from torch.nn.utils.rnn import pad_sequence
from torch.nn.utils.rnn import pack_padded_sequence
from torch.nn.utils.rnn import pad_packed_sequence
# import torchvision.transforms as transforms
# import torchvision.models as models
# import parselmouth
import numpy as np
# import csv
# import librosa
# import librosa.display
# import re
# import json
import time
# from einops import rearrange, repeat
# from einops.layers.torch import Rearrange
# import math
# import h5py
from transformers import Wav2Vec2ForSequenceClassification, Wav2Vec2FeatureExtractor

# デモで使うモデル
# wav2vecと自作modelの2段構成
class ModelTurntaking:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(self.device)

        # wav2vecの準備
        MODEL_ID = "rinna/japanese-wav2vec2-base"
        self.feature_extractor = Wav2Vec2FeatureExtractor.from_pretrained(MODEL_ID)
        self.wav2vec = Wav2Vec2ForSequenceClassification.from_pretrained(MODEL_ID, output_hidden_states=True).to(self.device)
        self.wav2vec.classifier = nn.Linear(in_features=256, out_features=1)

        self.model = self.model_load()

        n = self.count_parameters(self.model)
        print("Number of parameters: %s" % n)

    def count_parameters(self, model):
        return sum(p.numel() for p in model.parameters() if p.requires_grad)

    def get_likely_index(self, tensor):
        # バッチの各要素について、最も確率の高いラベルインデックスを得る
        return tensor.argmax(dim=-1)

    def model_load(self):
        print(torch.__version__)
        print(torchaudio.__version__)
        # 日本語訳注：cudaと出力されればOKです

        model = self.wav2vec
        model.to(self.device)

        model_path = '/home/DiaROS/DiaROS_deep_model/DiaROS_py/diaros/model.pth'
        model.load_state_dict(torch.load(model_path))
        print(torch.load(model_path).keys())

        return model

    def judge_turntaking(self, sound_array):
        inputs = self.feature_extractor(sound_array, sampling_rate=16000, return_tensors="pt")
        inputs = inputs.to(self.device)
        with torch.no_grad():
            output = self.model(**inputs)
            output = output.logits

        
        pred = self.get_likely_index(output)
        sigmoid = nn.Sigmoid()
        if sigmoid(output)[0] > 0.75:
            pred = 0
        else:
            pred = 1

        return pred, sigmoid(output)

# グローバル変数
import queue
stream_queue = queue.Queue()

def push_audio_data(data):
    stream_queue.put(data)

def get_audio_data():
    if not stream_queue.empty():
        return stream_queue.get()
    return None

# 設定 ######################################################################
mic_sample_rate = 16000
sample_rate     = 16000
frame_duration  = 30  # ms
CHUNK           = int(mic_sample_rate * frame_duration / 1000)
FORMAT          = pyaudio.paFloat32  # <- 追加

TurnJudgeThreshold = 0.650

# audio start ###############################################################
def audiostart():
    audio = pyaudio.PyAudio()
    device_id = None
    for i in range(audio.get_device_count()):
        info = audio.get_device_info_by_index(i)
        if 'default' == info['name']:
            device_id = info['index']
            break
    if device_id is None:
        print("defaultのマイク が見つかりませんでした。")
        exit()
    print(f"[default] index:{device_id}")

    stream = audio.open(format=FORMAT,
                        rate=mic_sample_rate,
                        channels=1,
                        input=True,
                        frames_per_buffer=CHUNK,
                        input_device_index=device_id)
    return audio, stream

# audio stop #############################################################
def audiostop(audio, stream):
    stream.stop_stream()
    stream.close()
    audio.terminate()

# draw bar ##############################################################
def draw_bar(volume, max_volume=1.0, bar_length=50):
    """
    音量に応じたバーをCUIに表示します。
    volume: 現在の音量
    max_volume: 最大音量値
    bar_length: バーの最大の長さ
    """
    normalized_volume = int((volume / max_volume) * bar_length)
    bar = "■" * normalized_volume + " " * (bar_length - normalized_volume)
    sys.stdout.write("\r" + bar)
    sys.stdout.flush()

# mic input thread ######################################################
def mic_input_thread(sample_rate, CHUNK):
    audio, stream = audiostart()
    while True:
        data = stream.read(CHUNK)
        audiodata = np.frombuffer(data, dtype='float32')  # <- float32
        stream_queue.put(audiodata)
    audiostop(audio, stream)

# main ##################################################################
if __name__ == '__main__':
    model = ModelTurntaking()
    print("model load successful")

    vad = webrtcvad.Vad()
    vad.set_mode(3)

    sound_available = False
    sound_count = 0
    silent_count = 0
    sound = np.empty(0, dtype='float32')

    mic_thread = threading.Thread(target=mic_input_thread, args=(sample_rate, CHUNK))
    mic_thread.start()

    print(f"判定しきい値: {TurnJudgeThreshold}")

    while True:
        try:
            audiodata = stream_queue.get()
            sound = np.concatenate([sound, audiodata])

            volume = np.sqrt(np.mean(audiodata ** 2))
            draw_bar(volume)

            if sound.shape[0] >= int(5.1 * sample_rate):
                sound = sound[-int(5.1 * sample_rate):]
                assert sound.shape[0] == int(5.1 * sample_rate), 'sound length is illegal.'

            audio_checkvad = (sound[-int(sample_rate * frame_duration / 1000):] * 32767).astype(np.int16)
            audio_checkvad_bytes = audio_checkvad.tobytes()

            if vad.is_speech(audio_checkvad_bytes, sample_rate):
                silent_count = 0
                sound_count += 1
                process_start_time = 0
                if sound_count >= (200 / frame_duration):
                    sound_available = True

            elif sound.shape[0] >= 5 * sample_rate:
                process_start_time = time.perf_counter()
                sound_count = 0
                silent_count += 1
                if silent_count >= (100 / frame_duration):
                    if sound_available:
                        sound_comp = sound / np.abs(sound).max()

                        write('model_input_sound.wav', sample_rate, (sound_comp[:int(5 * sample_rate)] * 32767).astype(np.int16))

                        file_path = "model_input_sound.raw"
                        sound_comp16 = np.array(sound_comp * 32767, dtype='int16')
                        sound_comp16[:int(5 * sample_rate)].tofile(file_path)

                        result, output = model.judge_turntaking(sound_comp[:int(5 * sample_rate)])
                        result = 1 if output[0] > TurnJudgeThreshold else 0

                        label = "STOP (waiting user utterance)" if result == 0 else "SPEAK (system can utter it)"
                        mark = "  " if result == 0 else "###"

                        process_end_time = time.perf_counter()
                        process_time = (process_end_time - process_start_time) * 1000

                        print(f'\r[{label:<30}]\t{output[0][0]:.3f} (STOP/SPEAK) {mark:<3} ({process_time:3.0f}ms)')

                        sound_available = False

        except KeyboardInterrupt:
            print()
            break

    mic_thread.join()
