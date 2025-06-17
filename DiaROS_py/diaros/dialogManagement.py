# google-speech-apiに変更する 応答生成 Unity通信 パワーによる有声検出 音声ファイル長によるSPEAK制御 音声認識切り替え 認識結果>５文字なら対話生成する 何応答目かを音声ファイル名にして記憶し、Unityで読めるようにする 時刻ファイルに対応させる
# 打ち切り応答＞話題提供
# 応答＆相槌UDPアーカイブ３秒制限 ５秒以上の沈黙で強制応答
# smの認識結果表示を無効化してる
import sys
import socket
import time
from datetime import datetime, timedelta
from playsound import playsound
import random
import numpy as np
import webrtcvad
import pyaudio
import queue
import threading
import librosa
import glob

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

    def __init__(self):
        self.word = ""
        self.asr = { "you": "", "is_final": False }
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

        self.audio_player_path = "/home/DiaROS/DiaROS_deep_model/DiaROS_py/diaros/hai.wav"
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

        DEBUG = True


        BAR_MEM = 20  # バーの長さ
        YELLOW = "\033[33m"
        RESET = "\033[0m"

        prev_asr_you = ""  # 直前のASR結果を保存
        while True:
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
                    if self.static_response_files:
                        wav_path = self.static_response_files[self.static_response_index]
                        try:
                            audio = AudioSegment.from_wav(wav_path)
                            duration_sec = len(audio) / 1000.0
                        except Exception:
                            duration_sec = 2.0
                        sys.stdout.write(f"[TT] 再生音声長 duration_sec={duration_sec}\n")
                        sys.stdout.flush()
                        playsound(wav_path, True)
                        self.static_response_index += 1
                        if self.static_response_index >= len(self.static_response_files):
                            self.static_response_index = 0
                        last_response_end_time = time.time() + duration_sec
                        is_playing_response = True
                        # 応答終了後に相槌クールダウンを設ける
                        next_back_channel_after_response = last_response_end_time + back_channel_cooldown_length
                    else:
                        sys.stdout.write("[ERROR] static_response_archiveに音声ファイルがありません\n")
                # ここでNLG用にASR結果をwordにセット
                if self.asr["you"]:
                    self.word = self.asr["you"]
                    self.response_update = True
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
                            if self.static_response_files:
                                wav_path = self.static_response_files[self.static_response_index]
                                try:
                                    audio = AudioSegment.from_wav(wav_path)
                                    duration_sec = len(audio) / 1000.0
                                except Exception:
                                    duration_sec = 2.0
                                sys.stdout.write(f"[TT] 再生音声長 duration_sec={duration_sec}\n")
                                sys.stdout.flush()
                                playsound(wav_path, True)
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
                    # self.word = carry+self.asr["you"]
                    # 変数self.asr["you"]の内容からprevの内容を引いた内容を変数self.wordに代入する(apiの認識結果の初期化がされないときの暫定処置)
                    # if self.asr["you"] != prev:
                    #     self.word = self.asr["you"]
                    # else:
                    # 音声認識の長さが5文字以上であれば
                    # sys.stdout.write('入力文：' + self.word + '\n')                    
                    # Unityに応答信号を送信

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
            # ###---###
            # try:
            #     receive_data, addr = s.recvfrom(1024)
            #     decoded_data = receive_data.decode('utf-8')
            #     # print(f"受信したデータ: {decoded_data}")
            # except BlockingIOError:
            #     # if DEBUG:sys.stdout.write('\n'+f"例外発生No data received within the timeout period\n")
            #     receive_data = None
            #     decoded_data = None
            #     # ノンブロッキングソケットでは、接続が即座に確立しない場合にこの例外が発生します。
            #     pass
            # if not receive_data:# データがなかった時
            #     pass
            # elif decoded_data.startswith("turn_taking:"): #ターンテイキングモデルからのデータを受信した瞬間
            #     turn_taking_label = decoded_data[len("turn_taking:"):]
            #     time_difference = datetime.now() - self.prev_response_time
            #     if self.additional_asr_start_time == False and time_difference >= timedelta(seconds=self.system_response_length + 1.0) and turn_taking_label == "SPEAK": #ターンテイキングモデルからのデータが応答だったとき
            #         # 上のif文から外した条件and self.speaking_time < datetime.now()
            #         # if DEBUG:sys.stdout.write('\n'+f"ターンテイキングモデルからSPEAK判定を受信した時刻{datetime.now()}\n")
            #         turn_taking_delay_start_time = datetime.now()
            #         back_channel_threshold = back_channel_high_threshold
            #     elif turn_taking_label == "STOP": #
            #         back_channel_threshold = back_channel_low_threshold
            #         # if DEBUG:sys.stdout.write('\n'+f"ターンテイキングモデルからSTOP判定を受信した時刻{datetime.now()}\n")
            # elif decoded_data.startswith("back_channel_prediction:"): #バックチャネルモデルからのデータを受信した瞬間
            #     back_channel_label = float(decoded_data[len("back_channel_prediction:"):])
            #     time_difference = datetime.now() - self.prev_back_channel_time
            #     if time_difference >= timedelta(seconds=self.back_channel_pause_length) and back_channel_label > back_channel_threshold:
            #         time_difference = datetime.now() - self.prev_response_time
            #         if time_difference >= timedelta(seconds=self.system_response_length + 0.5):
            #             if DEBUG:sys.stdout.write('\n'+f"相槌を返す\n")
            #             ###固定相槌再生パターン###
            #             self.back_channel_cnt += 1
            #             # if voice_available == False:
            #             #     playsound(f"static_back_channel_{random.randint(1, 3)}.wav", True)
            #             dummy = "dummy"
            #             client.sendto(dummy.encode('utf-8'),(HOST,PORT))
            #             self.prev_back_channel_time = datetime.now()
            #             back_channel_limit = True # 連続で相槌を打たないように制限をかける
            #         ##---###
            #         # self.word = "dummy"
            #         # prev = self.asr["you"]#システムが応答・相槌を返答する
            #         # carry = carry + self.asr["you"]
            #         # self.response_update = True
            #     else:
            #         #相槌打たずに待つ
            #         back_channel_limit = False # 一度相槌を打たなければ制限解除
            # if user_spoken == True and turn_taking_delay_start_time != False:
            #     time_difference = datetime.now() - turn_taking_delay_start_time
            #     if time_difference >= timedelta(seconds=turn_taking_response_delay_length): # SPEAK判定の0.9秒後に実際に応答を行う
            #         turn_taking_delay_start_time = False # 過去0.7秒で少しでも話してたら棄却する
            #         time_difference = datetime.now() - silent_start_time
            #         if time_difference >= timedelta(seconds=turn_taking_response_delay_length - 0.2): # SPEAK判定が出てからずっと無声なら

            #             ### 固定応答文再生パターン ###
            #             # if datetime.now() - thread_start_time >= timedelta(seconds=3):playsound(f"static_response_archive/static_response_{random.randint(1, 12)}.wav", True)
            #             ###---###

            #             ### 応答生成パターン ###
            #             # print("応答判定受信時刻："+datetime.now().strftime('%Y/%m/%d %H:%M:%S.%f')[:-3]) # 現在時刻を表示
            #             sys.stdout.write('\n'+f"ターンテイキングモデルで応答を返す時刻{datetime.now()}\n")
            #             # self.word = carry+self.asr["you"]
            #             # 変数self.asr["you"]の内容からprevの内容を引いた内容を変数self.wordに代入する(apiの認識結果の初期化がされないときの暫定処置)
            #             # if self.asr["you"] != prev:
            #             #     self.word = self.asr["you"].replace(prev, '')
            #             # else:
            #             prev = self.asr["you"] # システムが応答・相槌を返答する
            #             carry = ""
            #             self.prev_response_time = datetime.now()

            #             # ./tmp/ ディレクトリ内の .wav ファイルを名前順にソート
            #             filenames = sorted(glob.glob("./tmp/*.wav"))

            #             # 名前順で最新のファイル名を取得
            #             latest_filename = filenames[-1] if filenames else ""
            #             sys.stdout.write('\n最新の音声ファイル名' + latest_filename +  '\n')
            #             sys.stdout.write('\n前回の音声ファイル名' + self.prev_response_filename +  '\n')
            #             sys.stdout.flush()

            #             # 最新のファイル名が self.prev_response_filename と異なる場合に限り、そのファイル名を出力
            #             if latest_filename != self.prev_response_filename:
            #                 self.prev_response_filename = latest_filename
            #                 sys.stdout.write('\nターンテイキング' + latest_filename + '\n')
            #                 # dummy_signalのファイルが存在するか確認
            #                 try:
            #                     with open(latest_filename, 'r'):
            #                         # client.sendto(latest_filename.encode('utf-8'),(HOST,PORT))
            #                         self.system_response_length = self.get_audio_length(latest_filename) 
            #                         # print(f"The length of the audio file is {self.system_response_length} seconds.")
            #                         self.additional_asr_start_time = False
            #                         self.response_cnt = self.response_cnt + 1
            #                         silent_start_time = datetime.now()
            #                         user_spoken = False
            #                         user_speak_start_time = False

            #                 except FileNotFoundError:
            #                     pass
            #             else:
            #                 self.additional_asr_start_time = datetime.now()
            #                 sys.stdout.write('\nadditional start' + '\n')
            #                 # playsound("additional_asr_response.wav", True)
            #                 # self.ss["is_speaking"] = True#編集中
            #                     ###---###
            #         else: # SPEAK判定が出てから有声が一瞬でもあれば応答しない
            #             pass
                
            # ## 開発中 Unityに遅延ファイルを読ませる必要あり ###
            # if self.additional_asr_start_time != False:
            #     time_difference = datetime.now() - self.additional_asr_start_time
            #     # ./tmp/ ディレクトリ内の .wav ファイルを名前順にソート
            #     filenames = sorted(glob.glob("./tmp/*.wav"))

            #     # 名前順で最新のファイル名を取得
            #     latest_filename = filenames[-1] if filenames else ""
            #     sys.stdout.write('\n最新の音声ファイル名' + latest_filename +  '\n')
            #     sys.stdout.write('\n前回の音声ファイル名' + self.prev_response_filename +  '\n')
            #     sys.stdout.flush()


            #     # 最新のファイル名が self.prev_response_filename と異なる場合に限り、そのファイル名を出力
            #     if latest_filename != self.prev_response_filename:
            #         self.prev_response_filename = latest_filename

            #         if time_difference >= timedelta(seconds=2): # ５文字以上の音声認識ができるように
            #             try:
            #                 with open(latest_filename, 'r'):
            #                     sys.stdout.write('\nファイルはあった' + '\n')
            #                     sys.stdout.flush()
            #                     # client.sendto(latest_filename.encode('utf-8'),(HOST,PORT))
            #                     self.system_response_length = self.get_audio_length(latest_filename) 
            #                     # print(f"The length of the audio file is {self.system_response_length} seconds.")
            #                     self.additional_asr_start_time = False
            #                     self.response_cnt = self.response_cnt + 1
            #                     # print(f"The length of the audio file is {self.system_response_length} seconds。")
            #                     silent_start_time = datetime.now()
            #                     user_spoken = False
            #                     user_speak_start_time = False
            #                     prev = self.asr["you"] # システムが応答・相槌を返答する
            #                     carry = ""
            #                     self.prev_response_time = datetime.now()
            #             except FileNotFoundError: # 結局５文字以上の音声認識ができなければ
            #                 pass                                
            #     else:
            #         self.additional_asr_start_time = False
            #         sys.stdout.write('\n結局対話生成できなかった' + '\n')
            #         sys.stdout.write('\n遅延後' + latest_filename + '\n')
            #         sys.stdout.flush()
            #         # playsound("asr_failed.wav", True)# google speech apiの発話終了判定検証のため無効化
            #         self.response_cnt = self.response_cnt + 1
            #         # print(f"The length of the audio file is {self.system_response_length} seconds。")
            #         silent_start_time = datetime.now()
            #         user_spoken = False
            #         prev = self.asr["you"] # システムが応答・相槌を返答する
            #         carry = ""
            #         self.prev_response_time = datetime.now()
                
            #                 # 結局２文字以下のときはすみません。ききとれませんでした。       

            # time.sleep(0.01)
            # # ASR結果が変化したら標準出力
            # if self.response_update is True:
                
            #     prev_asr_you = self.asr["you"]

    # 応答・相槌が切り替わらなくとも対話管理をさせる            
    def pubDM(self):
        if self.response_update is True:
            self.response_update = False
            # print(f"[ASR結果] {self.word}")
            # sys.stdout.flush()
            return { "word": self.word, "update": True}
        else:
            return { "word": self.word, "update": False}

    def updateASR(self, asr):
        self.asr["you"] = asr["you"]
        self.asr["is_final"] = asr["is_final"]
    
    def updateSA(self, sa):
        self.sa["prevgrad"] = sa["prevgrad"]
        self.sa["frequency"] = sa["frequency"]
        self.sa["grad"] = sa["grad"]
        self.sa["power"] = sa["power"]
        self.sa["zerocross"] = sa["zerocross"]

    def updateSS(self, ss):
        self.ss["is_speaking"] = ss["is_speaking"]# test
        self.ss["timestamp"] = ss["timestamp"]
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
        # now_str = now.strftime("%H:%M:%S.%f")[:-3]
        # sys.stdout.write(f"[responseControl.py] RecvBC {now_str} result={data.get('result')} confidence={data.get('confidence'):.10f}\n")
        # sys.stdout.flush()