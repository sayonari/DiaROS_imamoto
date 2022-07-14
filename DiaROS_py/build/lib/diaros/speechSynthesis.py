from gtts import gTTS
from datetime import datetime
import time
from playsound import playsound
import shutil
import os 

class SpeechSynthesis():
    def __init__(self):
        self.tl = "ja"
        self.TMP_DIR = './tmp/'

        # remove TMP directory & remake ----
        if os.path.exists(self.TMP_DIR):
            du = shutil.rmtree(self.TMP_DIR)
            time.sleep(0.3)

        os.mkdir(self.TMP_DIR)
    
    def run(self, text):
        print(f'TTS:{text}')

        try:
            tts = gTTS(text, lang=self.tl)
            tts_file = './{}/cnt_{}.mp3'.format(self.TMP_DIR, datetime.now().microsecond)
            tts.save(tts_file)
            playsound(tts_file, True)
            os.remove(tts_file)
        except Exception as e:
            print('gTTS error: TTS sound is not generated...')
            print(e.args)

if __name__ == "__main__":
    tts = SpeechSynthesis()

    while True:
        text = input('input: ')
        tts.run(text)
