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
        self.model_thread = threading.Thread(target=self.recognition_thread)
        self.model_thread.daemon = True
        self.model_thread.start()
        sys.stdout.write('ASR node start up.\n')
        sys.stdout.write('=====================================================\n')

    def update_audio(self, audio_np):
        self.audio_queue.put(audio_np)
        self.recv_count += 1

    def pubASR(self):
        if self.new_result:
            self.new_result = False
            return {"you": self.word, "is_final": self.is_final}
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
            self.model, device = device_utils.move_model_to_device(self.model, verbose=True)
        except:
            # フォールバック（device_utilsが使えない場合）
            if USE_GPU and torch.cuda.is_available():
                device = torch.device("cuda")
                self.model.to(device)
            else:
                device = torch.device("cpu")
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
                    if USE_GPU and torch.cuda.is_available():
                        inputs = {k: v.to(device) for k, v in inputs.items()}
                        self.model = self.model.to(device)
                    with torch.no_grad():
                        logits = self.model(**inputs).logits
                    predicted_ids = torch.argmax(logits, dim=-1)
                    sentence = self.processor.batch_decode(predicted_ids)[0]
                    now = time.time()
                    elapsed_time = now - start_time
                    process_time = int(1000 * (now - last_time))
                    last_time = now
                    diff = create_diff_list(last_sent, sentence)
                    colored = apply_color_to_diff(diff)
                    output = f'{elapsed_time:7.3f} ({process_time:5d} ms): {colored}'
                    # if last_sent != sentence:
                    #     print(output)
                    # else:
                    #     sys.stdout.write("\r" + output + " " * 20 + "\r")
                    #     sys.stdout.flush()
                    self.word = sentence
                    self.is_final = True
                    self.new_result = True  # 追加: 新しい認識結果が得られた
                    last_sent = sentence
                # time.sleep(0.01)  # ループが高速すぎる場合のCPU負荷軽減
        except Exception as e:
            print(f"Error in recognition_thread: {e}")


