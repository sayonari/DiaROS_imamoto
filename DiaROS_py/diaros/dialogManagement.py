import sys
import socket
import time
from datetime import datetime, timedelta
from playsound import playsound
import random
import numpy as np
import pyaudio
import queue
import threading
import librosa
import glob
import difflib

### power制御用 ###
import statistics
###---###

### 音声ファイル長計測 ###
from pydub import AudioSegment
###---###

### 音声ファイルソート ###
import os
import glob
###---###

class DialogManagement:
    # グローバル変数を定義
    audio_queue = queue.Queue()  # マイクからの音声データを保存するキュー
    # 設定
    mic_sample_rate = 48000
    sample_rate     = 16000
    frame_duration  = 30  # ms
    CHUNK           = int(mic_sample_rate * frame_duration / 1000)

    ### 音声ファイル長計測関数 ###
    def get_audio_length(self, filename):
        audio = AudioSegment.from_wav(filename)
        return len(audio) / 1000.0  # 長さを秒単位で返す
    
    def update_asr_history(self, text, confidence=1.0):
        """ASR履歴の更新"""
        if text and text.strip():  # 空でないテキストのみ追加
            self.asr_history.append({
                'text': text,
                'confidence': confidence,
                'timestamp': time.time()
            })
            # 履歴を最新10件に制限
            if len(self.asr_history) > 10:
                self.asr_history = self.asr_history[-10:]
    
    def should_generate_response(self):
        """自動応答の判定"""
        current_time = time.time()
        if current_time - self.last_response_time >= self.response_interval:
            if self.asr_history:
                # 最後のASR結果から2秒以上経過していたら応答生成
                last_asr_time = self.asr_history[-1]['timestamp']
                if current_time - last_asr_time >= 2.0:
                    return True
        return False

    def __init__(self):
        self.word = ""
        self.asr = { "you": "", "is_final": False }
        self.asr_history = []  # 追加: 音声認識履歴
        self.last_response_time = 0  # 最後の応答時刻
        self.response_interval = 2.0  # 応答間隔（秒）
        self.user_speak_is_final = False
        self.recognition_result_is_confirmed = False
        self.sa = { "prevgrad" : 0.0,
                    "frequency": 0.0,
                    "grad"     : 0.0,
                    "power"    : 0.0,
                    "zerocross": 0   }
        self.ss = { "is_speaking" : False}# test
        self.power_list = []# powerの過去200msの平均を取るためのリスト
        self.power_ave = 0.0# powerの過去200msの平均
        self.power_calib_list = []
        self.power_calib_ave = 0.0
        self.prev_power_get_time = datetime.now()
        self.speaking_time = datetime.now()
        self.response_pause_length = 1#応答の間隔をあけるための時間
        self.back_channel_pause_length = 2#相槌の間隔をあけるための時間
        self.prev_response_time = datetime.now()
        self.additional_asr_start_time = False
        self.prev_back_channel_time = datetime.now()
        self.response_cnt = 0# 固定応答再生用
        self.back_channel_cnt = 0# 相槌内容確認用
        self.response_numbers = list(range(1, 19))
        self.final_prev = ""
        random.shuffle(self.response_numbers)

        self.prev_response_filename = ""

        self.prev_send_unity_time = datetime.now()# Unityにリップ・シンク停止信号を以前いつ出したか

        self.system_response_length = 3# システムの応答の音声ファイルの長さ

        self.response_update = False  # ← これを必ず__init__で初期化

        self.prev_bc_time = None  # 前回BackChannel受信時刻

        # Use relative path or environment variable for audio file
        import os
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.audio_player_path = os.path.join(base_dir, "hai.wav")
        self.last_back_channel_play_time = 0

        sys.stdout.write('DialogManagement start up.\n')
        sys.stdout.write('=====================================================\n')

        # static_response_archive内のwavファイル一覧を取得し、ソートして保存
        self.static_response_files = sorted(
            glob.glob("static_response_archive/static_response_*.wav")
        )
        self.static_response_index = 0

        # ros2_dm.pyから受け取ったデータと受信時刻
        self.latest_tt_data = None
        self.latest_tt_time = None
        self.latest_bc_data = None
        self.latest_bc_time = None
        self.latest_synth_filename = None # 追加: 音声合成ファイル名を保存する変数

        self.prev_asr_you = ""  # 直前のASR結果をインスタンス変数に
        self.last_asr_update_time = None  # ASR結果が更新された時刻
        self.response_request_sent = False  # 応答要求を送信済みかどうか
        self.pause_threshold_ms = 200  # ポーズ検出閾値（ミリ秒）

    def run(self):
        prev = ""
        carry = ""
        silent_start_time = datetime.now()
        silent_start_check = False
        silent = False
        allow_silence_seconds = 1
        silent_triggered_response = False
        end_announce_flag = False
        back_channel_reservation = False
        user_spoken = False
        user_speak_start_time = False
        user_pause_end_time = datetime.now()

        turn_taking_delay_start_time = False
        turn_taking_threshold = 0.75 
        turn_taking_response_delay_length = 0.9
        last_handled_tt_time = None
        last_response_end_time = None  # 応答音声再生終了時刻
        is_playing_response = False    # 応答音声再生中フラグ
        last_back_channel_time = 0     # 最後に相槌を打った時刻
        is_playing_backchannel = False # 相槌音声再生中フラグ
        last_backchannel_end_time = None # 相槌音声再生終了時刻
        pending_tt_data = None         # 相槌再生中に来た応答判定を一時保存
        pending_tt_time = None
        next_back_channel_allowed_time = 0  # 次に相槌を打てる時刻
        next_back_channel_after_response = 0  # 応答後に相槌を打てる時刻

        BACK_CHANNEL_HIGH_THRESHOLD = 0.75
        BACK_CHANNEL_LOW_THRESHOLD = 0.60
        back_channel_threshold = BACK_CHANNEL_HIGH_THRESHOLD
        last_handled_bc_time = None
        back_channel_cooldown_length = 0.3  # 相槌クールダウン時間（秒）
        back_channel_cooldown_until = None  # 相槌クールダウン終了時刻

        thread_start_time = datetime.now()

        voice_available = False
        standard_power = 0.0
        power_calibration = True

        DEBUG = False


        BAR_MEM = 20  # バーの長さ
        YELLOW = "\033[33m"
        RESET = "\033[0m"

        while True:
            # ここでNLG用にASR結果をwordにセット
            if self.asr["you"]:
                # 文字単位で差分を計算
                diff = list(difflib.ndiff(self.prev_asr_you, self.asr["you"]))
                changed_chars = sum(1 for d in diff if d.startswith('+ ') or d.startswith('- '))
                # 直前のASR結果と異なる場合のみ判定（閾値を3文字に下げる）
                if changed_chars >= 3 and self.asr["you"] != self.prev_asr_you:
                    self.word = self.asr["you"]
                    self.prev_asr_you = self.asr["you"]
                    # ASR履歴に追加
                    self.update_asr_history(self.asr["you"], self.asr.get("confidence", 1.0))
                    sys.stdout.write(f"ASR結果: {self.asr['you']}\n")
                    sys.stdout.flush()
                    # ASR結果が更新されたので時刻を記録し、応答要求フラグをリセット
                    self.last_asr_update_time = datetime.now()
                    self.response_request_sent = False
                    self.response_update = False  # 即座の応答生成は行わない
                else:
                    self.response_update = False
            else:
                self.response_update = False
                
            # ポーズ検出による応答生成（200ms以上の無音）
            if (self.last_asr_update_time is not None and 
                not self.response_request_sent and 
                self.word and self.word.strip()):  # 空でない場合のみ
                time_since_update = datetime.now() - self.last_asr_update_time
                if time_since_update >= timedelta(milliseconds=self.pause_threshold_ms):
                    self.response_update = True
                    self.response_request_sent = True
                    sys.stdout.write(f"[DM] {self.pause_threshold_ms}msポーズ検出 - 応答生成要求\n")
                    sys.stdout.flush()

            # TTデータの判定・再生
            if self.latest_tt_data is not None and self.latest_tt_time != last_handled_tt_time:
                tt_data = self.latest_tt_data
                tt_time = self.latest_tt_time
                probability = float(tt_data.get('confidence', 0.0))
                now = time.time()
                # 相槌音声再生中ならpendingに保存してスキップ
                if is_playing_backchannel and last_backchannel_end_time is not None and now < last_backchannel_end_time:
                    pending_tt_data = tt_data
                    pending_tt_time = tt_time
                    last_handled_tt_time = tt_time
                    continue
                # 応答音声再生中はTTデータを無視
                if is_playing_response and last_response_end_time is not None and now < last_response_end_time:
                    last_handled_tt_time = tt_time
                    continue
                if probability >= turn_taking_threshold:
                    # ここで音声合成ファイル名があればそれを再生
                    if hasattr(self, 'latest_synth_filename') and self.latest_synth_filename:
                        wav_path = self.latest_synth_filename
                        print(f"[DEBUG DM] TT判定時 - latest_synth_filename: {wav_path}")
                        
                        # ファイルが実際に存在するか確認
                        if not os.path.exists(wav_path):
                            sys.stdout.write(f"[ERROR] 音声ファイルが存在しません: {wav_path}\n")
                            sys.stdout.flush()
                            continue
                            
                        try:
                            audio = AudioSegment.from_wav(wav_path)
                            duration_sec = len(audio) / 1000.0
                        except Exception:
                            duration_sec = 2.0
                        sys.stdout.write(f"[TT] 合成音声再生 duration_sec={duration_sec}\n")
                        sys.stdout.flush()
                        
                        # macOSでの音声再生
                        try:
                            if sys.platform == "darwin":
                                # macOSの場合はafplayを使用
                                os.system(f"afplay '{wav_path}'")
                            else:
                                # macOS対応の音声再生
                                if sys.platform == "darwin":
                                    os.system(f"afplay '{wav_path}'")
                                else:
                                    playsound(wav_path, True)
                        except Exception as e:
                            sys.stdout.write(f"[ERROR] 音声再生エラー: {e}\n")
                            sys.stdout.flush()
                        self.asr_history = []  # ★TT応答再生直後のみ履歴を初期化
                        self.last_response_time = time.time()  # 応答時刻を記録
                        self.response_request_sent = False  # 応答要求フラグをリセット
                        self.last_asr_update_time = None  # ASR更新時刻もリセット
                        last_response_end_time = time.time() + duration_sec
                        is_playing_response = True
                        next_back_channel_after_response = last_response_end_time + back_channel_cooldown_length
                        self.latest_synth_filename = ""
                    else:
                        sys.stdout.write("[ERROR] 合成音声ファイル名がありません\n")
                        if hasattr(self, 'latest_synth_filename'):
                            pass  # print(f"[DEBUG DM] latest_synth_filename = '{self.latest_synth_filename}'")
                        else:
                            pass  # print("[DEBUG DM] latest_synth_filename属性が存在しません")
                else:
                    self.response_update = False
                last_handled_tt_time = tt_time
            # 応答音声再生終了後にフラグをリセット
            if is_playing_response and last_response_end_time is not None and time.time() >= last_response_end_time:
                is_playing_response = False
                last_response_end_time = None

            # 相槌音声再生終了後にpendingしていた応答判定があれば処理
            if is_playing_backchannel and last_backchannel_end_time is not None and time.time() >= last_backchannel_end_time:
                is_playing_backchannel = False
                last_backchannel_end_time = None
                if pending_tt_data is not None:
                    probability = float(pending_tt_data.get('confidence', 0.0))
                    now = time.time()
                    if not (is_playing_response and last_response_end_time is not None and now < last_response_end_time):
                        if probability >= turn_taking_threshold:
                            if hasattr(self, 'latest_synth_filename') and self.latest_synth_filename:
                                wav_path = self.latest_synth_filename
                                try:
                                    audio = AudioSegment.from_wav(wav_path)
                                    duration_sec = len(audio) / 1000.0
                                except Exception:
                                    duration_sec = 2.0
                                sys.stdout.write(f"[TT] 合成音声再生(pending) duration_sec={duration_sec}\n")
                                sys.stdout.flush()
                                # macOS対応の音声再生
                                if sys.platform == "darwin":
                                    os.system(f"afplay '{wav_path}'")
                                else:
                                    playsound(wav_path, True)
                                self.asr_history = []  # ★TT応答再生直後のみ履歴を初期化
                                self.latest_synth_filename = ""
                                self.response_request_sent = False
                                self.last_asr_update_time = None
                                last_response_end_time = time.time() + duration_sec
                                is_playing_response = True
                                next_back_channel_after_response = last_response_end_time + back_channel_cooldown_length
                            elif self.static_response_files:
                                wav_path = self.static_response_files[self.static_response_index]
                                try:
                                    audio = AudioSegment.from_wav(wav_path)
                                    duration_sec = len(audio) / 1000.0
                                except Exception:
                                    duration_sec = 2.0
                                sys.stdout.write(f"[TT] 再生音声長 duration_sec={duration_sec}\n")
                                sys.stdout.flush()
                                # macOS対応の音声再生
                                if sys.platform == "darwin":
                                    os.system(f"afplay '{wav_path}'")
                                else:
                                    playsound(wav_path, True)
                                self.asr_history = []  # ★TT応答再生直後のみ履歴を初期化
                                self.response_request_sent = False
                                self.last_asr_update_time = None
                                self.static_response_index += 1
                                if self.static_response_index >= len(self.static_response_files):
                                    self.static_response_index = 0
                                last_response_end_time = time.time() + duration_sec
                                is_playing_response = True
                                next_back_channel_after_response = last_response_end_time + back_channel_cooldown_length
                            else:
                                sys.stdout.write("[ERROR] static_response_archiveに音声ファイルがありません\n")
                    pending_tt_data = None
                    pending_tt_time = None

            # BCデータの判定・再生
            if self.latest_bc_data is not None and self.latest_bc_time != last_handled_bc_time:
                bc_data = self.latest_bc_data
                bc_time = self.latest_bc_time
                now = time.time()
                probability = float(bc_data.get('confidence', 0.0))
                # 応答音声再生直後のクールダウン or 直近の相槌から相槌音声長+cooldown秒未満は相槌を打たない
                if (now < next_back_channel_after_response) or \
                   (now < next_back_channel_allowed_time) or is_playing_backchannel:
                    last_handled_bc_time = bc_time
                    continue
                if probability >= back_channel_threshold:
                    try:
                        wav_path = f"static_back_channel_{random.randint(1, 2)}.wav"
                        audio = AudioSegment.from_wav(wav_path)
                        duration_sec = len(audio) / 1000.0
                        # macOS対応の音声再生
                        if sys.platform == "darwin":
                            os.system(f"afplay '{wav_path}'")
                        else:
                            playsound(wav_path, True)
                        last_back_channel_time = time.time()
                        is_playing_backchannel = True
                        last_backchannel_end_time = last_back_channel_time + duration_sec
                        # 相槌音声の長さ+クールダウンだけ次の相槌を禁止
                        next_back_channel_allowed_time = last_back_channel_time + duration_sec + back_channel_cooldown_length
                    except Exception as e:
                        sys.stdout.write(f"\n[ERROR] 相槌音声再生失敗: {e}\n")
                        sys.stdout.flush()
                last_handled_bc_time = bc_time

            #現在の時刻をmsまで表示
            # if DEBUG:sys.stdout.write("ループタイミング："+datetime.now().strftime('%Y/%m/%d %H:%M:%S.%f')[:-3])
            # self.sa["power"]を表示
                                    
            ### パワーによる無声区間検出 ###
            # 声を張って話すとパワーが0.69ぐらい
            # ぼそぼそ話すとパワーが0.36ぐらい
            # 動画のパワーが0.046ぐらい
            # キャリブレーション用の音声の返しが0.032
            # 会場の環境音は0.06
            
            if power_calibration:
                # if DEBUG:sys.stdout.write("\n"+f"power: {self.sa['power']}")
                # if DEBUG:sys.stdout.write("\n"+f"standard_power: {standard_power}")
                if DEBUG:sys.stdout.flush()
                
                self.power_calib_list.append(self.sa["power"])
                time_difference = datetime.now() - thread_start_time
                if time_difference >= timedelta(seconds=2.0):
                    self.power_calib_ave = statistics.mean(self.power_calib_list)
                    standard_power = self.power_calib_ave * 8
                    power_calibration = False
                    if DEBUG:sys.stdout.write("\n"+f"power: {self.sa['power']}\n")
                    if DEBUG:sys.stdout.write("\n"+f"standard_power: {standard_power}\n")
                    if DEBUG:sys.stdout.flush()
            else:
                standard_power = 0.20

            # system_response_length秒以上時間が経過していたら
            if self.sa["power"] < standard_power:
                # if DEBUG:sys.stdout.write('\r'+f"無声")
                # if DEBUG:sys.stdout.flush()
                # voice_available = False
                user_speak_start_time = False
                user_pause_end_time = datetime.now()
            else:
                # if DEBUG:sys.stdout.write('\r'+f"有声")
                # if DEBUG:sys.stdout.flush()
                # voice_available = True
                time_difference = datetime.now() - user_pause_end_time
                if time_difference >= timedelta(seconds=0.2):# ユーザ発話が0.5秒以上のとき
                    # Unityに応答停止信号を送信# デバッグ中
                    # if DEBUG:sys.stdout.write('\r'+f"Unityに応答停止信号を送信")
                    # if DEBUG:sys.stdout.flush()
                    # dummy_signal = "STOP"
                    # client.sendto(dummy_signal.encode('utf-8'),(HOST,PORT))
                    pass
                time_difference = datetime.now() - self.prev_response_time                            

            #1msごとの過去200msのパワーの平均を出す
            time_difference = datetime.now() - self.prev_power_get_time
            if time_difference >= timedelta(seconds=0.001):
                self.prev_power_get_time = datetime.now()
                # 変数power_aveに過去20回のself.sa["power"]の平均値を保存していく
                
                # self.power_listの最初の要素を削除する
                self.power_list.append(self.sa["power"])
                if len(self.power_list) > 200:  # 要素数が200を超えていたら
                    self.power_list.pop(0)  # 最初の要素を削除
                self.power_ave = statistics.mean(self.power_list)  # 全要素の平均値を計算
            if self.power_ave > standard_power:
                # user_spoken = True # ユーザが一度話したことを記録
                # sys.stdout.write('\n'+f"user_spoken:{user_spoken}")
                voice_available = True
                # sys.stdout.write('\n'+f"voice_available:{voice_available}")
                silent_start_time = datetime.now() # 有声である限り無声区間の開始時刻を更新し続ける
                # if DEBUG:sys.stdout.write('\n'+f"Unityに応答停止信号を送信")
                # # if DEBUG:sys.stdout.flush()

                # time_difference = datetime.now() - self.prev_send_unity_time
                # if time_difference >= timedelta(seconds=0.16):
                #     self.prev_send_unity_time = datetime.now()
                #     dummy_signal = "STOP"
                #     client.sendto(dummy_signal.encode('utf-8'),(HOST,PORT))
            else:
                voice_available = False
            time_difference = datetime.now() - silent_start_time

            if self.additional_asr_start_time == False and voice_available == False and user_spoken == True and time_difference >= timedelta(seconds=1.5):# ユーザが過去に一度話していて、現在は黙っていて、1.5s無声のとき
                time_difference = datetime.now() - self.prev_response_time
                if time_difference >= timedelta(seconds=self.system_response_length + 1.0): # システムが話し終わるまで応答しない
                    if DEBUG:sys.stdout.write('\n'+f"1.5秒の無音で応答した時刻{datetime.now()}\n")
                    if DEBUG:sys.stdout.flush()
                    
                    # DiaROS_ros/tmp ディレクトリ内の .wav ファイルを名前順にソート
                    current_file_dir = os.path.dirname(os.path.abspath(__file__))
                    tmp_dir = os.path.abspath(os.path.join(current_file_dir, '../../DiaROS_ros/tmp'))
                    filenames = sorted(glob.glob(os.path.join(tmp_dir, "*.wav")))

                    # 名前順で最新のファイル名を取得
                    latest_filename = filenames[-1] if filenames else ""
                    sys.stdout.write('\n最新の音声ファイル名' + latest_filename +  '\n')
                    sys.stdout.write('\n前回の音声ファイル名' + self.prev_response_filename +  '\n')
                    sys.stdout.flush()


                    # 最新のファイル名が self.prev_response_filename と異なる場合に限り、そのファイル名を出力
                    if latest_filename != self.prev_response_filename:
                        self.prev_response_filename = latest_filename
                        sys.stdout.write('\n1.5秒無音' + latest_filename + '\n')
                        # filenameのファイルが存在すればファイルを開く
                        try:
                            with open(latest_filename, 'r'):
                                # client.sendto(latest_filename.encode('utf-8'),(HOST,PORT))
                                self.system_response_length = self.get_audio_length(latest_filename)
                                self.additional_asr_start_time = False
                                self.response_cnt = self.response_cnt + 1
                                prev = self.asr["you"] # システムが応答・相槌を返答する
                                carry = ""
                                self.prev_response_time = datetime.now()
                                silent_start_time = datetime.now()
                                user_spoken = False
                                user_speak_start_time = False
                        except FileNotFoundError:
                            pass
                    else:
                        self.additional_asr_start_time = datetime.now()
                        sys.stdout.write('\nadditional start' + '\n')
                        # playsound("additional_asr_response.wav", True)
                        # print(f"The length of the audio file is {self.system_response_length} seconds.")
                    
            time_difference = datetime.now() - self.prev_response_time
            if self.additional_asr_start_time == False and time_difference >= timedelta(seconds=self.system_response_length + 1.0) and prev != self.asr["you"] and self.asr["is_final"]: # 音声認識結果で発話の同定を行った上でAPIが発話終了判定を出したとき
                if DEBUG:sys.stdout.write("\n"+f"APIの発話終了判定で応答を返す\n")
                if DEBUG:sys.stdout.flush()
                prev = self.asr["you"] # システムが応答・相槌を返答する
                carry = ""
                self.prev_response_time = datetime.now()
                # ./tmp/ ディレクトリ内の .wav ファイルを名前順にソート
                filenames = sorted(glob.glob("./tmp/*.wav"))

                # 名前順で最新のファイル名を取得
                latest_filename = filenames[-1] if filenames else ""
                sys.stdout.write('\n最新の音声ファイル名' + latest_filename +  '\n')
                sys.stdout.write('\n前回の音声ファイル名' + self.prev_response_filename +  '\n')
                sys.stdout.flush()

                # 最新のファイル名が self.prev_response_filename と異なる場合に限り、そのファイル名を出力
                if latest_filename != self.prev_response_filename:
                    self.prev_response_filename = latest_filename

                    # Unityに応答の信号を送信する
                    sys.stdout.write('\napiで応答' + latest_filename + '\n')
                    # dummy_signalのファイルが存在するか確認
                    try:
                        with open(latest_filename, 'r'):
                            # client.sendto(latest_filename.encode('utf-8'),(HOST,PORT))
                            self.system_response_length = self.get_audio_length(latest_filename)
                            self.additional_asr_start_time = False
                            self.response_cnt = self.response_cnt + 1
                            # print(f"The length of the audio file is {self.system_response_length} seconds.")
                            silent_start_time = datetime.now()
                            user_spoken = False
                            user_speak_start_time = False

                    except FileNotFoundError:
                        pass
                        # playsound("additional_asr_response.wav", True)
                else:
                    self.additional_asr_start_time = datetime.now()
                    sys.stdout.write('\nadditional start' + '\n')

    # 応答・相槌が切り替わらなくとも対話管理をさせる            
    def pubDM(self):
        should_respond = False
        
        if self.response_update is True:
            should_respond = True
            self.response_update = False
        
        if should_respond and self.word and self.word.strip():  # 空でない場合のみ応答生成
            # 現在のwordのみを送信（シンプルな応答のため）
            words = [self.word]
            
            sys.stdout.write(f"[DM→NLG] 応答生成要求: {words}\n")
            sys.stdout.flush()
            return { "words": words, "update": True}
        else:
            # 空の要求は送信しない
            return { "words": [], "update": False}

    def updateASR(self, asr):
        # ここでASR結果の履歴を管理
        self.asr["you"] = asr["you"]
        self.asr["is_final"] = asr["is_final"]
        self.asr_history.append(self.asr["you"])  # 追加: 新たな音声認識結果を受信するたびに履歴に追加

    def updateSA(self, sa):
        self.sa["prevgrad"] = sa["prevgrad"]
        self.sa["frequency"] = sa["frequency"]
        self.sa["grad"] = sa["grad"]
        self.sa["power"] = sa["power"]
        self.sa["zerocross"] = sa["zerocross"]

    def updateSS(self, ss):
        self.ss["is_speaking"] = ss["is_speaking"]  # test
        self.ss["timestamp"] = ss["timestamp"]
        # 追加: 音声合成ファイル名を受信したらTT閾値超え時に再生用に保存
        if "filename" in ss and ss["filename"]:
            self.latest_synth_filename = ss["filename"]
            # print(f"[DEBUG DM] updateSS - filename受信: {self.latest_synth_filename}")
        # デバッグログを抑制（filenameが空の場合は正常動作）
        # print(f"[ROS2] {ss['timestamp']}")
        if self.ss["is_speaking"] is True:
            self.speaking_time = datetime.now()

    def updateTT(self, data):
        # ros2_dm.pyからデータを受け取った時刻を記録
        self.latest_tt_data = data
        self.latest_tt_time = datetime.now()

    def updateBC(self, data):
        # ros2_dm.pyからデータを受け取った時刻を記録
        self.latest_bc_data = data
        self.latest_bc_time = datetime.now()
        # 受信時刻と推論値を全桁出力
        now = self.latest_bc_time