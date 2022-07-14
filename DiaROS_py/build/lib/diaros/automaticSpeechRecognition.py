#参考: https://tech-blog.optim.co.jp/entry/2020/02/21/163000

#export GOOGLE_APPLICATION_CREDENTIALS="credential.json"
#or
#set GOOGLE_APPLICATION_CREDENTIALS=C:\Users\81802\voice-dialogue\credential.json

import time
import sys

from google.cloud import speech_v1p1beta1 as speech

from diaros.googleSpeechAPI import GoogleSpeechAPI
from diaros.speechInput import SpeechInput

# Audio recording parameters
SHUTDOWN_TIME = 20000
SAMPLE_RATE = 44100
CHUNK_SIZE = 2**10
iDEVICE = 9999 # 今は、spokenInput.py にて、マシンのデフォルトのマイクを選択するようにしてある

class AutomaticSpeechRecognition:
    def __init__(self):
        self.word = ""
        self.is_final = False
        self.bot = ""
        self.turn = 0
        self.frequency = 0.0

        self.asr_manager = GoogleSpeechAPI(SAMPLE_RATE)
        self.mic_manager = SpeechInput(SAMPLE_RATE, CHUNK_SIZE, iDEVICE)

        sys.stdout.write('ASR start up.\n')
        sys.stdout.write('=====================================================\n')

    def get_current_time(self):
        """
        現在の時間を返す

        Returns:
            int -- 現在の時間
        """
        return int(round(time.time() * 1000))

    def processing(self, responses, stream):
        """
        音声認識処理
        """
        for response in responses:

            if not response.results:
                continue

            result = response.results[0]
            if not result.alternatives:
                continue

            transcript = result.alternatives[0].transcript
            self.word = str(transcript)
            self.is_final = result.is_final

    def run(self):
        with self.mic_manager as stream:
            while not stream.closed:
                stream.audio_input = []
                # 音声入力・解析
                audio_generator = stream.generator()
                # 音声認識
                responses = self.asr_manager.recognize(audio_generator)
                # 音声処理
                self.processing(responses, stream)
    
    def pubASR(self):
        return { "you":self.word, "is_final":self.is_final }

    def pubSA(self):
        return { 
            "prevgrad" : self.mic_manager.prevgrad,
            "frequency": self.mic_manager.frequency,
            "grad"     : self.mic_manager.grad,
            "power"    : self.mic_manager.power,
            "zerocross": self.mic_manager.zerocross }