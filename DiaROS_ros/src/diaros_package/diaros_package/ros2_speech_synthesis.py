import rclpy
import threading
import sys
import os
from rclpy.node import Node
from rclpy.logging import set_logger_level
from interfaces.msg import Inlg
from interfaces.msg import Iss
from interfaces.msg import Imm
from diaros.speechSynthesis import SpeechSynthesis
# from interfaces.msg import Time
from datetime import datetime
import signal
import time

class RosSpeechSynthesis(Node):
    def __init__(self, speechSynthesis):
        super().__init__('speech_synthesis')
        self.speechSynthesis = speechSynthesis
        self.sub_nlg = self.create_subscription(Inlg, 'NLGtoSS', self.play, 1)
        self.pub_ss = self.create_publisher(Iss, 'SStoDM', 1)
        # self.pub_ss = self.create_publisher(Iss, 'SStoDR', 1)
        # self.pub_mm = self.create_publisher(Imm, 'MM', 1)
        # self.pub_wav = self.create_publisher(SynthWav, 'SynthWav', 1)  # ← 削除
        self.timer = self.create_timer(0.02, self.send)
        self.is_speaking = False

    def play(self, nlg):
        text = str(nlg.reply)
        print(f"[DEBUG ROS2_SS] 音声合成リクエスト: {text}")
        wav_path = self.speechSynthesis.run(text)
        print(f"[DEBUG ROS2_SS] 音声合成結果: {wav_path}")
        # 音声合成後、ファイル名をIssでpublish
        # wav_msg = SynthWav()
        # wav_msg.filename = wav_path if wav_path else ""
        # self.pub_wav.publish(wav_msg)
        # if not self.is_speaking:
        #     text = str(nlg.reply)
        #     print("speaking..."+text)
        #     self.is_speaking = True
        #     self.speechSynthesis.run(text)
        #     print("finish..."+text)
        #     self.is_speaking = False

    def send(self):
        ss = Iss()
        ss.is_speaking = self.speechSynthesis.speak_end
        # print(ss.is_speaking)
        # 追記
        now = datetime.now()
        ss.timestamp = now.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        # 直近の合成ファイル名を取得して送信
        if hasattr(self.speechSynthesis, 'last_tts_file'):
            ss.filename = self.speechSynthesis.last_tts_file if self.speechSynthesis.last_tts_file else ""
            if ss.filename:
                print(f"[DEBUG ROS2_SS] publish filename: {ss.filename}")
        else:
            ss.filename = ""
            print("[DEBUG ROS2_SS] last_tts_file属性が存在しません")
        self.pub_ss.publish(ss)
        self.speechSynthesis.speak_end = False

        mm = Imm()
        mm.mod = "ss"
        # self.pub_mm.publish(mm)

def runROS(pub):
    rclpy.spin(pub)

def shutdown():
    import signal
    import time
    
    def signal_handler(sig, frame):
        print("Node graceful shutdown received.")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Node shutdown.")
        sys.exit(0)

def main(args=None):
    # rcutilsエラーメッセージを抑制
    os.environ['RCUTILS_LOGGING_SEVERITY_THRESHOLD'] = 'ERROR'
    os.environ['RCUTILS_COLORIZED_OUTPUT'] = '0'
    
    ss = SpeechSynthesis()
    rclpy.init(args=args)
    rss = RosSpeechSynthesis(ss)

    ros = threading.Thread(target=runROS, args=(rss,))

    ros.setDaemon(True)

    ros.start()
    shutdown()

if __name__ == '__main__':
    main()