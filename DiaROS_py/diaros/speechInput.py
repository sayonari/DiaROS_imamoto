### speechInput.py ###
import time
import pyaudio
from six.moves import queue
import sys
import rclpy
from std_msgs.msg import Float32MultiArray
import numpy as np

STREAMING_LIMIT = 10000

# グローバル共有キュー
stream_queue = queue.Queue()

class SpeechInput:
    def __init__(self, rate, chunk_size, device=None):
        sys.stdout.write('speechInput start\n')
        self._rate = rate
        self.chunk_size = 160  # 10ms @ 16kHz
        self._num_channels = 1
        self._buff = queue.Queue()
        self.closed = True
        self.start_time = int(round(time.time() * 1000))
        self.restart_counter = 0
        self.audio_input = []
        self.last_audio_input = []
        self.result_end_time = 0
        self.is_final_end_time = 0
        self.final_request_end_time = 0
        self.bridging_offset = 0
        self.last_transcript_was_final = False
        self.new_stream = True
        self._audio_interface = pyaudio.PyAudio()
        
        # デバイスの選択ロジック
        try:
            if device is None:
                # デフォルトデバイスを使用
                self.mic_info = self._audio_interface.get_default_input_device_info()
                sys.stdout.write(f'Using default input device: {self.mic_info["name"]}\n')
            else:
                # 指定されたデバイスを使用
                self.mic_info = self._audio_interface.get_device_info_by_index(device)
                sys.stdout.write(f'Using specified device {device}: {self.mic_info["name"]}\n')
                
            # デバイスがサポートする入力チャンネル数を確認
            if self.mic_info.get('maxInputChannels', 0) < 1:
                raise ValueError(f"Device {self.mic_info['name']} does not support input")
                
        except Exception as e:
            sys.stderr.write(f'Error getting device info: {e}\n')
            # PulseAudioデバイスを探す（Docker環境用フォールバック）
            device_count = self._audio_interface.get_device_count()
            for i in range(device_count):
                try:
                    info = self._audio_interface.get_device_info_by_index(i)
                    if info.get('maxInputChannels', 0) > 0:
                        # pulseまたはdefaultを含むデバイス名を優先
                        if 'pulse' in info['name'].lower() or 'default' in info['name'].lower():
                            self.mic_info = info
                            device = i
                            sys.stdout.write(f'Found PulseAudio device: {info["name"]} (index: {i})\n')
                            break
                except:
                    continue
            else:
                # それでも見つからない場合は最初の入力デバイスを使用
                for i in range(device_count):
                    try:
                        info = self._audio_interface.get_device_info_by_index(i)
                        if info.get('maxInputChannels', 0) > 0:
                            self.mic_info = info
                            device = i
                            sys.stdout.write(f'Using first available input device: {info["name"]} (index: {i})\n')
                            break
                    except:
                        continue
                else:
                    raise RuntimeError("No input devices found")
        
        # オーディオストリームを開く
        try:
            self._audio_stream = self._audio_interface.open(
                format=pyaudio.paFloat32,
                channels=self._num_channels,
                rate=self._rate,
                input=True,
                input_device_index=self.mic_info["index"],
                frames_per_buffer=self.chunk_size,
                stream_callback=self._fill_buffer,
            )
        except Exception as e:
            sys.stderr.write(f'Error opening audio stream: {e}\n')
            # デバイスインデックスを使わずに再試行（PulseAudioのデフォルトを使用）
            try:
                self._audio_stream = self._audio_interface.open(
                    format=pyaudio.paFloat32,
                    channels=self._num_channels,
                    rate=self._rate,
                    input=True,
                    frames_per_buffer=self.chunk_size,
                    stream_callback=self._fill_buffer,
                )
                sys.stdout.write('Opened audio stream without device index (using system default)\n')
            except Exception as e2:
                sys.stderr.write(f'Failed to open audio stream: {e2}\n')
                raise
        # acousticAnalysisの独立に伴い無効化
        # self.frequency = 0.0
        # self.grad = 0.0
        # self.power = 0.0
        # self.zerocross = 0
        # self.prevgrad = 0.0

    def __enter__(self):
        self.closed = False
        return self

    def __exit__(self, type, value, traceback):
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        self._buff.put(None)
        self._audio_interface.terminate()

    def _fill_buffer(self, in_data, *args, **kwargs):
        sys.stdout.flush()
        stream_queue.put(in_data)
        self._buff.put(in_data)
        # ROS通信処理は削除
        return None, pyaudio.paContinue

    def generator(self):
        while not self.closed:
            data = []
            if self.new_stream and self.last_audio_input:
                chunk_time = STREAMING_LIMIT / len(self.last_audio_input)
                if chunk_time != 0:
                    if self.bridging_offset < 0:
                        self.bridging_offset = 0
                    if self.bridging_offset > self.final_request_end_time:
                        self.bridging_offset = self.final_request_end_time
                    chunks_from_ms = round((self.final_request_end_time -
                                            self.bridging_offset) / chunk_time)
                    self.bridging_offset = (round((len(self.last_audio_input) - chunks_from_ms) * chunk_time))
                    for i in range(chunks_from_ms, len(self.last_audio_input)):
                        data.append(self.last_audio_input[i])
                self.new_stream = False

            chunk = self._buff.get()
            self.audio_input.append(chunk)

            if chunk is None:
                return
            data.append(chunk)

            while True:
                try:
                    chunk = self._buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                    self.audio_input.append(chunk)
                except queue.Empty:
                    break

            yield b''.join(data)

def main():
    rate = 16000
    chunk_size = 160  # 10ms @ 16kHz
    device = None  # デフォルトデバイスを使用
    speech_input = SpeechInput(rate, chunk_size, device)

    try:
        while True:
            time.sleep(1.0)
    except KeyboardInterrupt:
        pass
