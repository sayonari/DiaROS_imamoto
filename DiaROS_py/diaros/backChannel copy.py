"""
仕様
- リアルタイム音声入力に対して相槌予測を実行
- 相槌確率が閾値（0.75）を超えた場合に相槌音声を再生
- 相槌後は0.7秒のクールダウン時間を設定
- 相槌確率が変化するまで次の相槌判定を停止
- リアルタイムで相槌確率と処理時間（ms）、相槌判定状態を表示
"""

import pyaudio
import numpy as np
import torch
import torch.nn as nn
import wave
import time
from threading import Thread, Lock, Event
from collections import deque
from queue import Queue
import os
from transformers import Wav2Vec2ForSequenceClassification, AutoConfig
from transformers.models.wav2vec2.modeling_wav2vec2 import Wav2Vec2Model
import sys
import random
from playsound import playsound

# カスタムWav2Vec2モデルの定義
class CustomWav2Vec2ForAizuchi(nn.Module):
    def __init__(self):
        super().__init__()
        self.wav2vec2 = Wav2Vec2Model.from_pretrained("rinna/japanese-wav2vec2-base")
        self.projector = nn.Linear(768, 256)
        self.classifier = nn.Linear(256, 1)
    
    def forward(self, x):
        outputs = self.wav2vec2(x)
        hidden_states = outputs.last_hidden_state
        pooled = hidden_states.mean(dim=1)
        projected = self.projector(pooled)
        logits = self.classifier(projected)
        return logits

# ROSから音声チャンクを受け取るためのグローバルキュー
stream_queue = Queue()
back_channel_result_queue = Queue()  # 追加
THRESHOLD = 0.60

def push_audio_data(data):
    stream_queue.put(data)
    # 追加: キューサイズを表示
    # sys.stdout.write(f"[backChannel.py] push_audio_data: stream_queue size={stream_queue.qsize()}\n")
    sys.stdout.flush()

def get_audio_data():
    if not stream_queue.empty():
        data = stream_queue.get()
        # sys.stdout.write(f"[backChannel.py] get_audio_data: stream_queue size={stream_queue.qsize()}\n")
        sys.stdout.flush()
        return data
    # sys.stdout.write(f"[backChannel.py] get_audio_data: stream_queue EMPTY\n")
    sys.stdout.flush()
    return None

# 新たにグローバル変数として直近の送信済みフラグを追加
last_sent_time = 0

class RealtimeAizuchiPredictor:
    def __init__(self, model_path, sample_rate=16000, chunk_duration_ms=1000):
        self.sample_rate = sample_rate
        self.chunk_duration_ms = chunk_duration_ms
        self.chunk_samples = int(sample_rate * chunk_duration_ms / 1000)
        self.inference_interval_ms = 100  # 100msごとに推論
        self.inference_interval_samples = int(sample_rate * self.inference_interval_ms / 1000)
        self.samples_since_last_inference = 0
        self.buffer_lock = Lock()
        self.audio_buffer = np.zeros(0, dtype=np.float32)
        self.max_buffer_samples = self.chunk_samples * 2  # バッファ肥大化防止
        self.prediction_queue = Queue()
        self.audio_level_queue = Queue()
        self.processing_time_queue = Queue()
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        sys.stdout.write(f"使用デバイス: {self.device}\n")
        sys.stdout.flush()
        
        try:
            config = AutoConfig.from_pretrained(
                "rinna/japanese-wav2vec2-base",
                output_hidden_states=True
            )
            
            self.feature_extractor = Wav2Vec2ForSequenceClassification.from_pretrained(
                "rinna/japanese-wav2vec2-base",
                config=config
            ).to(self.device)
            self.feature_extractor.eval()
            
            sys.stdout.write("wav2vecモデルの読み込みが完了しました\n")
            sys.stdout.flush()
            
        except Exception as e:
            sys.stdout.write(f"wav2vecモデルの読み込みに失敗しました: {e}\n")
            sys.stdout.flush()
            raise
        
        try:
            self.model = CustomWav2Vec2ForAizuchi()
            state_dict = torch.load(model_path, map_location=self.device)
            
            wav2vec2_params = {
                k.replace('wav2vec2.', ''): v 
                for k, v in state_dict.items() 
                if k.startswith('wav2vec2.')
            }
            
            self.model.wav2vec2.load_state_dict(wav2vec2_params)
            self.model.projector.weight.data = state_dict['projector.weight']
            self.model.projector.bias.data = state_dict['projector.bias']
            self.model.classifier.weight.data = state_dict['classifier.weight']
            self.model.classifier.bias.data = state_dict['classifier.bias']
            
            self.model.to(self.device)
            self.model.eval()
            
            sys.stdout.write("相槌予測モデルの読み込みが完了しました\n")
            sys.stdout.flush()
        except Exception as e:
            sys.stdout.write(f"相槌予測モデルの読み込みに失敗しました: {e}\n")
            sys.stdout.flush()
            raise
        
        # スレッド起動を削除
        # self.is_running = True
        # self.processing_thread = Thread(target=self.process_audio)
        # self.processing_thread.start()

    # process_audioはもう使わない

    def process_chunk(self, new_chunk):
        # mainループから呼び出す
        self.audio_buffer = np.concatenate([self.audio_buffer, new_chunk])
        self.samples_since_last_inference += len(new_chunk)
        # バッファ肥大化防止
        if len(self.audio_buffer) > self.max_buffer_samples:
            self.audio_buffer = self.audio_buffer[-self.max_buffer_samples:]
        result = None
        # 1000ms分以上バッファがあり、かつ100ms分新規データが溜まったら推論
        if self.audio_buffer.shape[0] >= self.chunk_samples and self.samples_since_last_inference >= self.inference_interval_samples:
            start_time = time.time()
            audio_chunk = self.audio_buffer[-self.chunk_samples:]  # 最新1000ms
            try:
                audio_tensor = torch.from_numpy(audio_chunk).float().to(self.device)
                with torch.no_grad():
                    prediction = self.model(audio_tensor.unsqueeze(0))
                    probability = torch.sigmoid(prediction).item()
                end_time = time.time()
                processing_time = (end_time - start_time) * 1000
                result = (probability, processing_time)
            except Exception as e:
                sys.stdout.write(f"処理中にエラーが発生しました: {e}\n")
                import traceback
                sys.stdout.write(traceback.format_exc())
                sys.stdout.flush()
                result = None
            self.samples_since_last_inference = 0  # 推論したのでリセット
        return result

    def get_audio_level(self):
        if not self.audio_level_queue.empty():
            return self.audio_level_queue.get()
        return None

    def stop(self):
        # スレッド管理不要
        pass

def create_level_bar(level, width=40, threshold=0.01):
    normalized_level = min(1.0, level / threshold)
    bar_length = int(normalized_level * width)
    return '[' + '#' * bar_length + '-' * (width - bar_length) + ']'

def move_cursor_up(n):
    sys.stdout.write(f'\033[{n}A')
    sys.stdout.flush()

def clear_line():
    sys.stdout.write('\033[K')
    sys.stdout.flush()

class AudioPlayer:
    def __init__(self, audio_file):
        self.audio_file = audio_file
        self.is_playing = Event()
        
    def play_audio(self):
        if self.is_playing.is_set():
            return
            
        try:
            wf = wave.open(self.audio_file, 'rb')
            p = pyaudio.PyAudio()
            
            def callback(in_data, frame_count, time_info, status):
                data = wf.readframes(frame_count)
                return (data, pyaudio.paContinue)
            
            stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                          channels=wf.getnchannels(),
                          rate=wf.getframerate(),
                          output=True,
                          stream_callback=callback)
            
            self.is_playing.set()
            stream.start_stream()
            
            while stream.is_active():
                time.sleep(0.1)
            
            stream.stop_stream()
            stream.close()
            wf.close()
            p.terminate()
            self.is_playing.clear()
            
        except Exception as e:
            sys.stdout.write(f"音声再生中にエラーが発生しました: {e}\n")
            sys.stdout.flush()
            self.is_playing.clear()

    def play_async(self):
        Thread(target=self.play_audio).start()

def get_default_device_index():
    p = pyaudio.PyAudio()
    default_index = None
    for i in range(p.get_device_count()):
        dev = p.get_device_info_by_index(i)
        if dev['maxInputChannels'] > 0 and dev['name'] == "default":
            default_index = i
            sys.stdout.write(f"デフォルトデバイスインデックス: {default_index}\n")
            sys.stdout.flush()
            break
    p.terminate()
    if default_index is None:
        raise RuntimeError('デバイス名が"default"のマイクが見つかりません')
    return default_index

def main():
    try:
        sys.stdout.write("\n相槌予測システムを初期化中...\n")
        sys.stdout.flush()
        predictor = RealtimeAizuchiPredictor(
            '/home/DiaROS/DiaROS_deep_model/DiaROS_py/diaros/backChannelModel.pth'
        )
        
        last_trigger_time = 0
        in_cooldown = False
        last_probability = None
        waiting_for_change = False
        
        sys.stdout.write("相槌予測システムを開始します。Ctrl+Cで終了します。\n")
        sys.stdout.write(f"閾値: {THRESHOLD:.2f}\n")
        sys.stdout.write("--------------------\n")
        sys.stdout.flush()
        
        BAR_MEM = 20  # バーの長さ
        YELLOW = "\033[33m"
        RESET = "\033[0m"
        while True:
            result = None
            if not stream_queue.empty():
                new_chunk = stream_queue.get()
                result = predictor.process_chunk(new_chunk)
            current_time = time.time()
            
            if in_cooldown and current_time - last_trigger_time >= 0.7:
                in_cooldown = False
            
            if result is not None:
                probability, processing_time = result
                probability_changed = (last_probability is not None and 
                                    abs(probability - last_probability) > 0.001)
                if waiting_for_change and probability_changed:
                    waiting_for_change = False
                if not waiting_for_change:
                    bar_len = int(round(probability * BAR_MEM))
                    threshold_pos = int(round(THRESHOLD * BAR_MEM))
                    bar = ""
                    for i in range(BAR_MEM):
                        if i == threshold_pos:
                            bar += "|"
                        elif i < bar_len:
                            bar += "■"
                        else:
                            bar += " "
                    now_str = time.strftime("%H:%M:%S", time.localtime(current_time)) + f".{int((current_time*1000)%1000):03d}"
                    if not in_cooldown and probability > THRESHOLD:
                        now = time.time()
                        now_str = time.strftime("%H:%M:%S", time.localtime(now)) + f".{int((now*1000)%1000):03d}"
                        sys.stdout.write(f"{YELLOW}|{bar}| {probability:.10f} [処理時間: {processing_time:.1f}ms] [{now_str}]{RESET}\n")
                        sys.stdout.flush()
                        # try:
                        #     playsound(f"static_back_channel_{random.randint(1, 2)}.wav", True)
                        # except Exception as e:
                        #     sys.stdout.write(f"\n[ERROR] 相槌音声再生失敗: {e}\n")
                        #     sys.stdout.flush()
                        predictor.prediction_queue.put((probability, processing_time))
                        result_flag = 1
                        last_trigger_time = current_time
                        in_cooldown = True
                        waiting_for_change = True
                    else:
                        # 通常出力
                        sys.stdout.write(f"|{bar}| {probability:.10f} [処理時間: {processing_time:.1f}ms] [{now_str}]\n")
                        sys.stdout.flush()
                        result_flag = 0
                else:
                    result_flag = 0
                last_probability = probability
                # すべての推論結果をキューにput
                back_channel_result_queue.put((result_flag, probability))
            else:
                time.sleep(0.01)
    except KeyboardInterrupt:
        sys.stdout.write("\n処理を終了します...\n")
        sys.stdout.flush()
        predictor.stop()
    except Exception as e:
        sys.stdout.write(f"エラーが発生しました: {e}\n")
        sys.stdout.flush()