import rclpy
import threading
import sys
import os
from rclpy.node import Node
from rclpy.logging import set_logger_level
from interfaces.msg import Iasr
# from interfaces.msg import Isa
from interfaces.msg import Imm
from std_msgs.msg import Float32MultiArray
from diaros.automaticSpeechRecognition import AutomaticSpeechRecognition
import numpy as np

class RosAutomaticSpeechRecognition(Node):
    def __init__(self, automaticSpeechRecognition):
        super().__init__('automatic_speech_recognition')
        self.automaticSpeechRecognition = automaticSpeechRecognition
        self.sub_mic = self.create_subscription(Float32MultiArray, 'mic_audio_float32', self.audio_callback, 10)
        self.pub_asr = self.create_publisher(Iasr, 'ASRtoNLU', 1)  # トピック名を変更
        # self.pub_mm = self.create_publisher(Imm, 'MM', 1)
        self.timer = self.create_timer(0.01, self.callback)  # 10ms to match audio input rate

    def audio_callback(self, msg):
        audio_np = np.array(msg.data, dtype=np.float32)
        self.automaticSpeechRecognition.update_audio(audio_np)

    def callback(self):
        asr_result = self.automaticSpeechRecognition.pubASR()
        if asr_result is not None:
            asr = Iasr()
            asr.you = asr_result['you']
            asr.is_final = asr_result['is_final']
            self.pub_asr.publish(asr)
        mm = Imm()
        mm.mod = "asr"

def runROS(pub):
    rclpy.spin(pub)

def runASR(automaticSpeechRecognition):
    automaticSpeechRecognition.run()

def shutdown():
    import signal
    import time
    
    def signal_handler(sig, frame):
        print("Automatic speech recognition node graceful shutdown received.")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Automatic speech recognition node shutdown.")
        sys.exit(0)

def main(args=None):
    # rcutilsエラーメッセージを抑制
    import os
    os.environ['RCUTILS_LOGGING_SEVERITY_THRESHOLD'] = 'ERROR'
    os.environ['RCUTILS_COLORIZED_OUTPUT'] = '0'
    os.environ['RCUTILS_CONSOLE_OUTPUT_FORMAT'] = '[{severity}] {message}'
    
    rclpy.init(args=args)  # ← ここをノード生成より前に移動
    asr = AutomaticSpeechRecognition()
    rasr = RosAutomaticSpeechRecognition(asr)

    ros = threading.Thread(target=runROS, args=(rasr,), daemon=True)
    mod = threading.Thread(target=runASR, args=(asr,), daemon=True)

    ros.start()
    mod.start()
    shutdown()

if __name__ == '__main__':
    main()