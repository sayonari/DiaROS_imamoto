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

        # static_response_source内のwavファイル一覧を取得し、ソートして保存
        base_dir = os.path.dirname(os.path.abspath(__file__))
        static_response_dir = os.path.join(base_dir, "../../DiaROS_ros/static_response_source")
        self.static_response_files = sorted(
            glob.glob(os.path.join(static_response_dir, "static_response_*.wav"))
        )
        self.static_response_index = 0

        # ros2_dm.pyから受け取ったデータと受信時刻
        self.latest_tt_data = None
        self.latest_tt_time = None
        self.latest_bc_data = None
        self.latest_bc_time = None
        self.latest_synth_filename = None # 追加: 音声合成ファイル名を保存する変数
        
        # 発話IDベースの音声ファイル管理
        self.utterance_audio_map = {}  # {utterance_id: filename}のマッピング
        self.current_utterance_id = None  # 現在処理中の発話ID
        self.utterance_counter = 0  # 発話IDカウンター
        self.last_requested_word = None  # 最後に応答生成要求を送信した内容

        self.prev_asr_you = ""  # 直前のASR結果をインスタンス変数に
        self.last_asr_update_time = None  # ASR結果が更新された時刻
        self.response_request_sent = False  # 応答要求を送信済みかどうか
        self.pause_threshold_ms = 300  # ポーズ検出閾値（ミリ秒）- 200msから300msに増加して安定化
        self.tt_waiting_for_synth = False  # TT判定後、音声ファイル待機中
        self.tt_wait_start_time = None  # 音声ファイル待機開始時刻
        self.user_speaking = False  # ユーザが発話中かどうか
        self.last_significant_asr = ""  # 最後の有意なASR結果
        self.response_request_time = None  # 応答要求を送信した時刻
        self.min_utterance_length = 2  # 応答生成に必要な最小文字数
        
        # 発話IDベースの同期機構
        self.pending_responses = {}  # 発話ID -> 応答内容のマッピング
        self.completed_utterances = set()  # 完了済み発話IDのセット
        
        # セッションID管理
        self.session_id = None  # 現在の発話セッションID
        self.last_user_speech_time = None  # 最後のユーザ発話時刻
        self.session_pause_threshold_ms = 500  # 新セッション開始のポーズ閾値
        self.response_queue = []  # 応答キュー（発話ID付き）

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
                    current_time = datetime.now()
                    
                    # 新セッションの開始判定（改善版：連続発話時の判定を緩和）
                    # ASRがis_finalでない場合、または最後の応答から時間が短い場合はセッションを維持
                    should_start_new_session = False
                    if self.last_user_speech_time is None:
                        should_start_new_session = True
                    else:
                        time_since_last_speech = (current_time - self.last_user_speech_time).total_seconds() * 1000
                        # 最後の応答から2秒以上経過し、かつ最後の発話から500ms以上経過した場合のみ新セッション
                        time_since_last_response = (current_time - datetime.fromtimestamp(self.last_response_time)).total_seconds() if hasattr(self, 'last_response_time') and self.last_response_time > 0 else float('inf')
                        if time_since_last_speech >= self.session_pause_threshold_ms and time_since_last_response >= 2.0:
                            should_start_new_session = True
                    
                    if should_start_new_session:
                        # 新しいセッション開始
                        self.session_id = f"session_{self.utterance_counter}_{int(time.time()*1000)}"
                        sys.stdout.write(f"[DM] \n========== 新セッション開始: {self.session_id} ==========\n")
                        sys.stdout.flush()
                        # 古いセッションの情報をクリア
                        self.pending_responses.clear()
                        self.utterance_audio_map.clear()
                        self.current_utterance_id = None
                    
                    self.word = self.asr["you"]
                    self.prev_asr_you = self.asr["you"]
                    # ASR履歴に追加
                    self.update_asr_history(self.asr["you"], self.asr.get("confidence", 1.0))
                    sys.stdout.write(f"ASR結果: {self.asr['you']}\n")
                    sys.stdout.flush()
                    # ユーザが発話を開始
                    self.user_speaking = True
                    self.last_asr_update_time = current_time
                    self.last_user_speech_time = current_time  # ユーザ発話時刻を更新
                    self.response_update = False  # 即座の応答生成は行わない
                    # 有意なASR結果を保存（5文字以上）
                    if len(self.asr["you"]) >= 5:
                        self.last_significant_asr = self.asr["you"]
                else:
                    self.response_update = False
            else:
                self.response_update = False
                
            # ポーズ検出による応答生成（300ms以上の無音）
            if (self.user_speaking and  # ユーザが発話中の場合のみ
                self.last_asr_update_time is not None and 
                not self.response_request_sent and 
                self.last_significant_asr and self.last_significant_asr.strip()):  # 有意なASR結果がある場合のみ
                time_since_update = datetime.now() - self.last_asr_update_time
                
                # 2秒以上のポーズで強制的に応答生成/再生
                force_response = time_since_update >= timedelta(seconds=2.0)
                
                if time_since_update >= timedelta(milliseconds=self.pause_threshold_ms) or force_response:
                    # wordが空でなく、かつ最小文字数以上であることを確認
                    if (self.last_significant_asr and self.last_significant_asr.strip() and 
                        len(self.last_significant_asr.strip()) >= self.min_utterance_length):
                        # 既に同じ内容で応答生成要求を送信していないかチェック
                        if not hasattr(self, 'last_requested_word') or self.last_requested_word != self.last_significant_asr:
                            # セッションIDが設定されていない場合は設定
                            if not self.session_id:
                                self.session_id = f"session_{self.utterance_counter}_{int(time.time()*1000)}"
                            
                            # 新しい発話IDを生成（セッションIDを含む）
                            self.utterance_counter += 1
                            self.current_utterance_id = f"{self.session_id}_utt_{self.utterance_counter}"
                            
                            # 応答生成をトリガー
                            self.response_update = True
                            self.response_request_sent = True
                            self.user_speaking = False  # ユーザ発話終了
                            self.word = self.last_significant_asr  # 最後の有意なASR結果を使用
                            self.last_requested_word = self.last_significant_asr  # 最後に要求した内容を記録
                            self.utterance_id = self.current_utterance_id  # 現在の発話IDを設定
                            
                            # ペンディング応答として記録
                            self.pending_responses[self.current_utterance_id] = self.word
                            
                            sys.stdout.write(f"[DM] {self.pause_threshold_ms}msポーズ検出 - 応答生成要求: '{self.word}' (ID: {self.current_utterance_id})\n")
                            sys.stdout.write(f"[DEBUG DM] response_update設定: response_update={self.response_update}, word='{self.word}'\n")
                            sys.stdout.flush()
                            self.response_request_time = datetime.now()
                    else:
                        self.response_update = False

            # 2秒ポーズでの強制応答再生チェック
            if (self.last_asr_update_time is not None and 
                not is_playing_response and
                self.last_significant_asr and self.last_significant_asr.strip()):
                time_since_asr = (datetime.now() - self.last_asr_update_time).total_seconds()
                if time_since_asr >= 2.0:
                    # 現在のセッションの音声ファイルを探す
                    force_play_wav = None
                    force_play_utt_id = None
                    if hasattr(self, 'session_id') and self.session_id:
                        for utt_id, file_path in self.utterance_audio_map.items():
                            if utt_id.startswith(self.session_id) and os.path.exists(file_path):
                                force_play_wav = file_path
                                force_play_utt_id = utt_id
                                break
                    
                    if force_play_wav:
                        # 強制的に応答を再生
                        sys.stdout.write(f"[DM] 2秒ポーズ検出 - 強制応答再生: {force_play_utt_id}\n")
                        sys.stdout.flush()
                        try:
                            audio = AudioSegment.from_wav(force_play_wav)
                            duration_sec = len(audio) / 1000.0
                            if sys.platform == "darwin":
                                os.system(f"afplay '{force_play_wav}'")
                            else:
                                playsound(force_play_wav, True)
                            # 再生後の状態リセット
                            self.last_response_time = time.time()
                            self.response_request_sent = False
                            self.last_asr_update_time = None
                            self.user_speaking = False
                            self.last_significant_asr = ""
                            self.last_requested_word = None
                            is_playing_response = True
                            last_response_end_time = time.time() + duration_sec
                        except Exception as e:
                            sys.stdout.write(f"[ERROR] 強制応答再生エラー: {e}\n")
                            sys.stdout.flush()
                    else:
                        # 音声ファイルがない場合は応答生成を強制トリガー
                        if not self.response_request_sent:
                            sys.stdout.write(f"[DM] 2秒ポーズ検出 - 強制応答生成トリガー\n")
                            sys.stdout.flush()
                            # 応答生成の強制実行処理をここに追加
                            if not self.session_id:
                                self.session_id = f"session_{self.utterance_counter}_{int(time.time()*1000)}"
                            self.utterance_counter += 1
                            self.current_utterance_id = f"{self.session_id}_utt_{self.utterance_counter}"
                            self.response_update = True
                            self.response_request_sent = True
                            self.user_speaking = False
                            self.word = self.last_significant_asr
                            self.last_requested_word = self.last_significant_asr
                            self.utterance_id = self.current_utterance_id
                            self.pending_responses[self.current_utterance_id] = self.word
                            # 2秒ポーズ検出の無限ループを防ぐためにタイムスタンプをリセット
                            self.last_asr_update_time = None
            
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
                    # TT判定成功をマーク（音声ファイル待ち状態へ）
                    if not hasattr(self, 'tt_waiting_for_synth'):
                        self.tt_waiting_for_synth = False
                    if not hasattr(self, 'tt_wait_start_time'):
                        self.tt_wait_start_time = None
                    
                    # 音声ファイル待ち状態の開始
                    if not self.tt_waiting_for_synth:
                        self.tt_waiting_for_synth = True
                        self.tt_wait_start_time = time.time()
                        sys.stdout.write(f"[TT] 応答タイミング検出 (confidence={probability:.2f}) - 音声ファイル待機開始\n")
                        sys.stdout.flush()
                    
                    # 現在の発話IDに対応する音声ファイルを取得
                    wav_path = None
                    utterance_to_play = None
                    
                    # 現在のセッションに属する発話IDの音声ファイルを探す
                    if hasattr(self, 'session_id') and self.session_id:
                        for utt_id, file_path in self.utterance_audio_map.items():
                            if utt_id.startswith(self.session_id):
                                wav_path = file_path
                                utterance_to_play = utt_id
                                break
                    
                    # セッションIDが一致しない古い応答は無視
                    if wav_path and utterance_to_play:
                        sys.stdout.write(f"[TT] 現セッションの応答を再生: {utterance_to_play}\n")
                    else:
                        # 現在のセッションに一致する応答がない
                        wav_path = None  # 再生をスキップ
                    
                    if wav_path:
                        
                        # ファイルが実際に存在するか確認
                        if not os.path.exists(wav_path):
                            # ファイル待ちのタイムアウトチェック（最大3秒）
                            if self.tt_wait_start_time and (time.time() - self.tt_wait_start_time) > 3.0:
                                sys.stdout.write(f"[ERROR] 音声ファイル待機タイムアウト: {wav_path}\n")
                                sys.stdout.flush()
                                self.tt_waiting_for_synth = False
                                self.tt_wait_start_time = None
                                continue
                            else:
                                # まだタイムアウトしていない場合は次のループで再チェック
                                last_handled_tt_time = None  # 再処理のためリセット
                                continue
                            
                        try:
                            audio = AudioSegment.from_wav(wav_path)
                            duration_sec = len(audio) / 1000.0
                        except Exception:
                            duration_sec = 2.0
                        sys.stdout.write(f"[TT] 合成音声再生 duration_sec={duration_sec}\n")
                        sys.stdout.flush()
                        
                        # 音声再生
                        try:
                            if sys.platform == "darwin":
                                # macOSの場合はafplayを使用
                                sys.stdout.write(f"[TT] 音声再生開始: afplay '{wav_path}'\n")
                                sys.stdout.flush()
                                result = os.system(f"afplay '{wav_path}'")
                                if result != 0:
                                    sys.stdout.write(f"[ERROR] afplay実行エラー: 終了コード {result}\n")
                                    sys.stdout.flush()
                                else:
                                    sys.stdout.write(f"[TT] 音声再生完了\n")
                                    sys.stdout.flush()
                            else:
                                # Linux/Windowsの場合
                                sys.stdout.write(f"[TT] 音声再生開始: playsound '{wav_path}'\n")
                                sys.stdout.flush()
                                playsound(wav_path, True)
                                sys.stdout.write(f"[TT] 音声再生完了\n")
                                sys.stdout.flush()
                        except Exception as e:
                            sys.stdout.write(f"[ERROR] 音声再生エラー: {e}\n")
                            sys.stdout.flush()
                        self.asr_history = []  # ★TT応答再生直後のみ履歴を初期化
                        self.last_response_time = time.time()  # 応答時刻を記録
                        self.response_request_sent = False  # 応答要求フラグをリセット
                        self.last_asr_update_time = None  # ASR更新時刻もリセット
                        self.user_speaking = False  # ユーザ発話フラグもリセット
                        self.last_significant_asr = ""  # 有意なASR結果もクリア
                        self.last_requested_word = None  # 最後に要求した内容もクリア
                        
                        # 現在の発話IDを完了マークしてからクリア
                        if self.current_utterance_id:
                            self.completed_utterances.add(self.current_utterance_id)
                            if self.current_utterance_id in self.pending_responses:
                                del self.pending_responses[self.current_utterance_id]
                            if self.current_utterance_id in self.utterance_audio_map:
                                del self.utterance_audio_map[self.current_utterance_id]
                        self.current_utterance_id = None  # 発話IDをクリア
                        last_response_end_time = time.time() + duration_sec
                        is_playing_response = True
                        next_back_channel_after_response = last_response_end_time + back_channel_cooldown_length
                        self.latest_synth_filename = ""
                        self.tt_waiting_for_synth = False  # 待機状態をリセット
                        self.tt_wait_start_time = None
                    else:
                        # 音声ファイルがまだない場合は、待機を継続
                        if self.tt_waiting_for_synth:
                            # タイムアウトチェック
                            if self.tt_wait_start_time and (time.time() - self.tt_wait_start_time) > 3.0:
                                sys.stdout.write("[TT] 音声ファイル待機タイムアウト - 静的応答を使用\n")
                                sys.stdout.flush()
                                self.tt_waiting_for_synth = False
                                self.tt_wait_start_time = None
                                # 静的応答にフォールバック
                                if self.static_response_files:
                                    wav_path = self.static_response_files[self.static_response_index]
                                    self.static_response_index = (self.static_response_index + 1) % len(self.static_response_files)
                                    try:
                                        audio = AudioSegment.from_wav(wav_path)
                                        duration_sec = len(audio) / 1000.0
                                        if sys.platform == "darwin":
                                            os.system(f"afplay '{wav_path}'")
                                        else:
                                            playsound(wav_path, True)
                                        sys.stdout.write(f"[TT] 静的応答再生完了\n")
                                        sys.stdout.flush()
                                        last_response_end_time = time.time() + duration_sec
                                        is_playing_response = True
                                    except Exception as e:
                                        sys.stdout.write(f"[ERROR] 静的応答再生エラー: {e}\n")
                                        sys.stdout.flush()
                            else:
                                # まだタイムアウトしていない場合は次のループで再チェック
                                wait_time = time.time() - self.tt_wait_start_time
                                # 待機ログを大幅に抑制（初回、1秒、2秒、3秒のみ出力）
                                current_wait_second = int(wait_time)
                                if not hasattr(self, '_last_wait_log_second'):
                                    self._last_wait_log_second = -1
                                
                                if current_wait_second != self._last_wait_log_second and current_wait_second in [0, 1, 2, 3]:
                                    sys.stdout.write(f"[TT] 音声ファイル待機中... ({current_wait_second}秒経過)\n")
                                    sys.stdout.flush()
                                    self._last_wait_log_second = current_wait_second
                                
                                last_handled_tt_time = None  # 再処理のためリセット
                                continue
                else:
                    # self.response_update = False  # ← この行が問題！無条件にFalseにしていた
                    pass
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
                                # 音声再生
                                if sys.platform == "darwin":
                                    sys.stdout.write(f"[TT] 音声再生開始(pending): afplay '{wav_path}'\n")
                                    sys.stdout.flush()
                                    result = os.system(f"afplay '{wav_path}'")
                                    if result != 0:
                                        sys.stdout.write(f"[ERROR] afplay実行エラー: 終了コード {result}\n")
                                        sys.stdout.flush()
                                else:
                                    sys.stdout.write(f"[TT] 音声再生開始(pending): playsound '{wav_path}'\n")
                                    sys.stdout.flush()
                                    playsound(wav_path, True)
                                self.asr_history = []  # ★TT応答再生直後のみ履歴を初期化
                                self.latest_synth_filename = ""
                                self.response_request_sent = False
                                self.last_asr_update_time = None
                                self.user_speaking = False
                                self.last_significant_asr = ""
                                self.last_requested_word = None
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
                                # 音声再生（静的応答）
                                if sys.platform == "darwin":
                                    sys.stdout.write(f"[TT] 静的応答再生: afplay '{wav_path}'\n")
                                    sys.stdout.flush()
                                    result = os.system(f"afplay '{wav_path}'")
                                    if result != 0:
                                        sys.stdout.write(f"[ERROR] afplay実行エラー: 終了コード {result}\n")
                                        sys.stdout.flush()
                                else:
                                    sys.stdout.write(f"[TT] 静的応答再生: playsound '{wav_path}'\n")
                                    sys.stdout.flush()
                                    playsound(wav_path, True)
                                self.asr_history = []  # ★TT応答再生直後のみ履歴を初期化
                                self.response_request_sent = False
                                self.last_asr_update_time = None
                                self.user_speaking = False
                                self.last_significant_asr = ""
                                self.last_requested_word = None
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
                        # 相槌ファイルのパスを正しく設定
                        current_file_dir = os.path.dirname(os.path.abspath(__file__))
                        wav_path = os.path.abspath(os.path.join(current_file_dir, f"../../DiaROS_ros/static_back_channel_{random.randint(1, 2)}.wav"))
                        sys.stdout.write(f"[BC] 相槌ファイルパス: {wav_path}\n")
                        sys.stdout.flush()
                        
                        if not os.path.exists(wav_path):
                            sys.stdout.write(f"[ERROR] 相槌ファイルが存在しません: {wav_path}\n")
                            sys.stdout.flush()
                            last_handled_bc_time = bc_time
                            continue
                            
                        audio = AudioSegment.from_wav(wav_path)
                        duration_sec = len(audio) / 1000.0
                        # 相槌音声再生
                        if sys.platform == "darwin":
                            sys.stdout.write(f"[BC] 相槌再生: afplay '{wav_path}'\n")
                            sys.stdout.flush()
                            result = os.system(f"afplay '{wav_path}'")
                            if result != 0:
                                sys.stdout.write(f"[ERROR] afplay実行エラー: 終了コード {result}\n")
                                sys.stdout.flush()
                        else:
                            sys.stdout.write(f"[BC] 相槌再生: playsound '{wav_path}'\n")
                            sys.stdout.flush()
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
        # pubDMが呼ばれる度にカウント（デバッグ用）
        if not hasattr(self, 'pubdm_count'):
            self.pubdm_count = 0
        self.pubdm_count += 1
        
        # 100回に1回、状態を出力
        if self.pubdm_count % 100 == 0:
            sys.stdout.write(f"[DEBUG pubDM] called {self.pubdm_count} times, response_update={self.response_update}, response_request_sent={self.response_request_sent}, word='{self.word}'\n")
            sys.stdout.flush()
        
        # response_request_sentがTrueかつwordが空でない場合のみ処理
        if self.response_request_sent is True and self.word and self.word.strip():
            # デバッグログ追加
            sys.stdout.write(f"[DEBUG pubDM] 応答送信: response_request_sent={self.response_request_sent}, word='{self.word}'\n")
            sys.stdout.flush()
            
            # 現在のwordのみを送信（シンプルな応答のため）
            words = [self.word]
            
            sys.stdout.write(f"[DM→NLG] 応答生成要求: {words}\n")
            sys.stdout.flush()
            
            # フラグをリセット
            self.response_request_sent = False
            self.response_update = False
            self.word = ""  # wordもクリア
            
            return { "words": words, "update": True, "utterance_id": self.current_utterance_id}
        else:
            # 空の要求は送信しない（updateもFalseにする）
            return { "words": [], "update": False, "utterance_id": None}

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
            
            # 発話IDがある場合はマッピングに追加
            if "utterance_id" in ss and ss["utterance_id"]:
                self.utterance_audio_map[ss["utterance_id"]] = ss["filename"]
                # デバッグログを抑制（必要に応じてコメントアウトを解除）
                # print(f"[DEBUG DM] 発話ID {ss['utterance_id']} → 音声ファイル {ss['filename']} をマッピング")
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