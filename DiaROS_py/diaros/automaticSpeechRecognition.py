# import time
# import sys
# import threading
# import queue
# import numpy as np

# import torch
# from transformers import AutoModelForCTC, Wav2Vec2Processor, Wav2Vec2CTCTokenizer
# from transformers.utils import logging
# import difflib
# import warnings

# # Audio recording parameters
# SAMPLE_RATE = 16000
# CHUNK_SIZE = 240
# MODEL_ID = 'SiRoZaRuPa/wav2vec2-base-kanji-unigram-RS-s-1120'
# AUDIO_DURATION = 5  # seconds
# INPUT_LEN = int(SAMPLE_RATE * AUDIO_DURATION)
# USE_GPU = True

# logging.set_verbosity_error()
# warnings.filterwarnings('ignore')

# def create_diff_list(old, new):
#     diff = list(difflib.ndiff(old, new))
#     lines = []
#     current_text = ""
#     is_change = False
#     for i in diff:
#         if i[0] == ' ':
#             if is_change:
#                 lines.append((1, current_text))
#                 current_text = ""
#             is_change = False
#             current_text += i[2:]
#         elif i[0] == '-':
#             continue
#         elif i[0] == '+':
#             if not is_change:
#                 if current_text:
#                     lines.append((0, current_text))
#                     current_text = ""
#                 is_change = True
#             current_text += i[2:]
#     if current_text:
#         lines.append((is_change, current_text))
#     return lines

# def apply_color_to_diff(lines, end_string=']'):
#     result = ""
#     for is_change, text in lines:
#         if is_change:
#             if lines[-1] == (1, text):
#                 if end_string in text and text.endswith(end_string):
#                     if text[-3] == '雑':
#                         result += f'\033[91m{text[:-4]}\033[0m' + f'\033[42m{text[-4:]}\033[0m'
#                     elif text[-3] == '無':
#                         result += f'\033[91m{text[:-4]}\033[0m' + f'\033[44m{text[-4:]}\033[0m'
#                 else:
#                     result += f'\033[91m{text}\033[0m'
#             else:
#                 result += f'\033[93m{text}\033[0m'
#         else:
#             result += text
#     return result

# class AutomaticSpeechRecognition:
#     def __init__(self):
#         self.last_audio = None
#         self.word = ""
#         self.is_final = False
#         self.recv_count = 0
#         self.audio_buffer = np.array([], dtype=np.float32)
#         self.audio_queue = queue.Queue()
#         self.running = True
#         self.last_sent = ""
#         self.model = None
#         self.processor = None
#         self.tokenizer = None
#         self.model_thread = threading.Thread(target=self.recognition_thread)
#         self.model_thread.daemon = True
#         self.model_thread.start()
#         sys.stdout.write('ASR node start up.\n')
#         sys.stdout.write('=====================================================\n')

#     def update_audio(self, audio_np):
#         self.audio_queue.put(audio_np)
#         self.recv_count += 1

#     def pubASR(self):
#         return {"you": self.word, "is_final": self.is_final}

#     def run(self):
#         while self.running:
#             time.sleep(0.1)

#     def recognition_thread(self):
#         sys.stdout.write('Loading ASR model...\n')
#         self.tokenizer = Wav2Vec2CTCTokenizer.from_pretrained(MODEL_ID)
#         self.processor = Wav2Vec2Processor.from_pretrained(MODEL_ID, tokenizer=self.tokenizer)
#         self.model = AutoModelForCTC.from_pretrained(MODEL_ID)
#         self.model.eval()
#         if USE_GPU and torch.cuda.is_available():
#             device = torch.device("cuda")
#             self.model.to(device)
#         else:
#             device = torch.device("cpu")
#         sys.stdout.write('ASR model loaded.\n')
#         sys.stdout.flush()

#         mic_input = np.array([], dtype=np.float32)
#         last_sent = ""
#         start_time = time.time()
#         last_time = time.time()
#         last_infer_len = 0  # 前回推論時のmic_inputの長さ
#         try:
#             while self.running:
#                 new_data_added = False
#                 while not self.audio_queue.empty():
#                     data = self.audio_queue.get()
#                     mic_input = np.append(mic_input, data)
#                     new_data_added = True
#                 # 5秒を超えたら古いデータから捨てる
#                 if len(mic_input) > INPUT_LEN:
#                     mic_input = mic_input[-INPUT_LEN:]
#                 # 新たな音声が100ms分溜まっていたら推論
#                 # 修正: last_infer_lenの更新タイミングを推論後にし、推論条件を「新しいデータが100ms分以上溜まっている場合」に限定
#                 if len(mic_input) >= int(SAMPLE_RATE * 0.1) and (len(mic_input) - last_infer_len >= int(SAMPLE_RATE * 0.1)):
#                     print(f"Received audio data length: {len(mic_input)}")
#                     sys.stdout.flush()
#                     array = mic_input.astype(np.float32)
#                     inputs = self.processor(array, sampling_rate=SAMPLE_RATE, return_tensors="pt", padding=True)
#                     if USE_GPU and torch.cuda.is_available():
#                         inputs = {k: v.to(device) for k, v in inputs.items()}
#                         self.model = self.model.to(device)
#                     with torch.no_grad():
#                         logits = self.model(**inputs).logits
#                     predicted_ids = torch.argmax(logits, dim=-1)
#                     sentence = self.processor.batch_decode(predicted_ids)[0]
#                     now = time.time()
#                     elapsed_time = now - start_time
#                     process_time = int(1000 * (now - last_time))
#                     last_time = now
#                     diff = create_diff_list(last_sent, sentence)
#                     colored = apply_color_to_diff(diff)
#                     output = f'{elapsed_time:7.3f} ({process_time:5d} ms): {colored}'
#                     if last_sent != sentence:
#                         print(output)
#                     else:
#                         sys.stdout.write("\r" + output + " " * 20 + "\r")
#                         sys.stdout.flush()
#                     self.word = sentence
#                     self.is_final = True if sentence.strip() != "" else False
#                     last_sent = sentence
#                     last_infer_len = len(mic_input)  # 推論後に更新
#                 time.sleep(0.01)  # ループが高速すぎる場合のCPU負荷軽減
#         except Exception as e:
#             print(f"Error in recognition_thread: {e}")

# NOTE 音声入力長固定
import time
import sys
import threading
import queue
import numpy as np

import torch
from transformers import AutoModelForCTC, Wav2Vec2Processor, Wav2Vec2CTCTokenizer
from transformers.utils import logging
import difflib
import warnings

# Audio recording parameters
SAMPLE_RATE = 16000
CHUNK_SIZE = 240
# MODEL_ID = 'SiRoZaRuPa/wav2vec2-base-kanji-unigram-RS-s-1120'
MODEL_ID = 'SiRoZaRuPa/japanese-HuBERT-base-VADLess-ASR-RSm'
AUDIO_DURATION = 5  # seconds
INPUT_LEN = int(SAMPLE_RATE * AUDIO_DURATION)
USE_GPU = True

logging.set_verbosity_error()
warnings.filterwarnings('ignore')

def create_diff_list(old, new):
    diff = list(difflib.ndiff(old, new))
    lines = []
    current_text = ""
    is_change = False
    for i in diff:
        if i[0] == ' ':
            if is_change:
                lines.append((1, current_text))
                current_text = ""
            is_change = False
            current_text += i[2:]
        elif i[0] == '-':
            continue
        elif i[0] == '+':
            if not is_change:
                if current_text:
                    lines.append((0, current_text))
                    current_text = ""
                is_change = True
            current_text += i[2:]
    if current_text:
        lines.append((is_change, current_text))
    return lines

def apply_color_to_diff(lines, end_string=']'):
    result = ""
    for is_change, text in lines:
        if is_change:
            if lines[-1] == (1, text):
                if end_string in text and text.endswith(end_string):
                    if text[-3] == '雑':
                        result += f'\033[91m{text[:-4]}\033[0m' + f'\033[42m{text[-4:]}\033[0m'
                    elif text[-3] == '無':
                        result += f'\033[91m{text[:-4]}\033[0m' + f'\033[44m{text[-4:]}\033[0m'
                else:
                    result += f'\033[91m{text}\033[0m'
            else:
                result += f'\033[93m{text}\033[0m'
        else:
            result += text
    return result

class AutomaticSpeechRecognition:
    def __init__(self):
        self.last_audio = None
        self.word = ""
        self.is_final = False
        self.recv_count = 0
        self.audio_buffer = np.array([], dtype=np.float32)
        self.audio_queue = queue.Queue()
        self.running = True
        self.last_sent = ""
        self.model = None
        self.processor = None
        self.tokenizer = None
        self.new_result = False  # 追加: 新しい認識結果フラグ
        
        # 200msポーズ検出用の変数
        self.last_result_change_time = time.time()
        self.last_stable_result = ""
        self.pause_threshold = 0.2  # 200ms
        self.previous_results = []  # 重なり結果統合用
        self.max_history = 10  # 過去10回分の結果を保持
        
        self.model_thread = threading.Thread(target=self.recognition_thread)
        self.model_thread.daemon = True
        self.model_thread.start()
        sys.stdout.write('ASR node start up.\n')
        sys.stdout.write('=====================================================\n')

    def update_audio(self, audio_np):
        self.audio_queue.put(audio_np)
        self.recv_count += 1

    def remove_tags(self, text):
        """[無音][雑音]などのタグを除去"""
        import re
        return re.sub(r'\[[無雑][音音]\]', '', text).strip()

    def ends_with_silence_tag(self, text):
        """文末が[無音]または[雑音]タグで終わっているかチェック"""
        import re
        return bool(re.search(r'\[[無雑][音音]\]$', text))

    def integrate_overlapping_results(self, new_result):
        """重なりあり音声認識結果の統合処理"""
        if not new_result:
            return ""
        
        # 履歴に追加
        self.previous_results.append(new_result)
        if len(self.previous_results) > self.max_history:
            self.previous_results.pop(0)
        
        # 最も長い結果を基本とし、共通部分を見つけて統合
        if len(self.previous_results) >= 2:
            prev = self.previous_results[-2]
            curr = self.previous_results[-1]
            
            # 共通部分を見つけて統合
            if len(prev) > 0 and len(curr) > 0:
                # 前回結果の末尾と今回結果の先頭で重複を検出
                for i in range(min(len(prev), len(curr)), 0, -1):
                    if prev[-i:] == curr[:i]:
                        # 重複部分を除去して結合
                        integrated = prev + curr[i:]
                        return integrated
            
            # 重複が見つからない場合は現在の結果を返す
            return curr
        
        return new_result

    def check_pause_and_final(self, current_result):
        """200msポーズ検出とis_final判定"""
        now = time.time()
        
        # タグを除去した結果で比較
        clean_result = self.remove_tags(current_result)
        clean_stable = self.remove_tags(self.last_stable_result)
        
        # 結果が変化した場合
        if clean_result != clean_stable:
            self.last_result_change_time = now
            self.last_stable_result = current_result
            self.is_final = False
        else:
            # 200ms間結果が安定している場合
            if now - self.last_result_change_time >= self.pause_threshold:
                self.is_final = True
            else:
                self.is_final = False
        
        # [無音][雑音]タグで終わっている場合も発話終了とみなす
        if self.ends_with_silence_tag(current_result):
            self.is_final = True

    def pubASR(self):
        if self.new_result:
            self.new_result = False
            # タグを除去してから送信
            clean_word = self.remove_tags(self.word)
            return {"you": clean_word, "is_final": self.is_final}
        else:
            return None

    def run(self):
        while self.running:
            time.sleep(0.1)

    def recognition_thread(self):
        sys.stdout.write('Loading ASR model...\n')
        self.tokenizer = Wav2Vec2CTCTokenizer.from_pretrained(MODEL_ID)
        self.processor = Wav2Vec2Processor.from_pretrained(MODEL_ID, tokenizer=self.tokenizer)
        self.model = AutoModelForCTC.from_pretrained(MODEL_ID)
        self.model.eval()
        
        # デバイス選択（MPS/CUDA/CPU自動選択）
        try:
            from . import device_utils
            self.model, self.device = device_utils.move_model_to_device(self.model, verbose=True)
        except:
            # フォールバック（device_utilsが使えない場合）
            if USE_GPU and torch.cuda.is_available():
                self.device = torch.device("cuda")
                self.model.to(self.device)
            else:
                self.device = torch.device("cpu")
        sys.stdout.write('ASR model loaded.\n')
        sys.stdout.flush()

        mic_input = np.array([], dtype=np.float32)  # モデル入力用バッファ
        mic_stack = np.array([], dtype=np.float32)  # マイク入力スタック用バッファ
        MAX_MIC_INPUT_LENGTH = INPUT_LEN * 2  # Maximum buffer size to prevent memory leak
        last_sent = ""
        start_time = time.time()
        last_time = time.time()
        try:
            while self.running:
                # マイク入力をスタック
                while not self.audio_queue.empty():
                    data = self.audio_queue.get()
                    mic_stack = np.append(mic_stack, data)
                # 100ms以上溜まったらmic_inputに移動
                if len(mic_stack) >= int(SAMPLE_RATE * 0.1):
                    mic_input = np.append(mic_input, mic_stack)
                    mic_stack = np.array([], dtype=np.float32)  # スタックをクリア
                    # 5秒を超えたら古いデータから捨てる（メモリリーク防止）
                    if len(mic_input) > INPUT_LEN:
                        mic_input = mic_input[-INPUT_LEN:]
                    # 追加の安全装置：最大長制限
                    elif len(mic_input) > MAX_MIC_INPUT_LENGTH:
                        mic_input = mic_input[-INPUT_LEN:]
                    array = mic_input.astype(np.float32)
                    inputs = self.processor(array, sampling_rate=SAMPLE_RATE, return_tensors="pt", padding=True)
                    # デバイスに入力を移動
                    if self.device.type != 'cpu':
                        inputs = {k: v.to(self.device) for k, v in inputs.items()}
                    with torch.no_grad():
                        logits = self.model(**inputs).logits
                    predicted_ids = torch.argmax(logits, dim=-1)
                    sentence = self.processor.batch_decode(predicted_ids)[0]
                    now = time.time()
                    elapsed_time = now - start_time
                    process_time = int(1000 * (now - last_time))
                    last_time = now
                    
                    # 新しい統合処理と200msポーズ検出を適用
                    integrated_sentence = self.integrate_overlapping_results(sentence)
                    self.check_pause_and_final(integrated_sentence)
                    
                    # デバッグ出力（必要に応じて）
                    diff = create_diff_list(last_sent, integrated_sentence)
                    colored = apply_color_to_diff(diff)
                    output = f'{elapsed_time:7.3f} ({process_time:5d} ms): {colored}'
                    
                    self.word = integrated_sentence
                    self.new_result = True  # 追加: 新しい認識結果が得られた
                    last_sent = integrated_sentence
                # time.sleep(0.01)  # ループが高速すぎる場合のCPU負荷軽減
        except Exception as e:
            print(f"Error in recognition_thread: {e}")


