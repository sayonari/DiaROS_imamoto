import rclpy
import threading
import sys
import os
from interfaces.msg import Iasr
from interfaces.msg import Imm
from rclpy.node import Node
from rclpy.logging import set_logger_level
import signal
import time

"""
言語理解モジュールを組み込む場合利用する
(現在は音声認識結果を対話管理へ流しているだけ)
"""

class RosNaturalLanguageUnderstanding(Node):
    def __init__(self, languageUnderstanding):
        super().__init__('natural_language_understanding')
        self.languageUnderstanding = languageUnderstanding
        self.sub_asr = self.create_subscription(Iasr, 'ASRtoNLU', self.send, 1)
        self.pub_nlu = self.create_publisher(Iasr, 'NLUtoDM', 1)
        # self.pub_mm = self.create_publisher(Imm, 'MM', 1)
        self.timer = self.create_timer(1, self.ping)
        sys.stdout.write('LanguageUnderstanding start up.\n')
        sys.stdout.write('=====================================================\n')

    def send(self, asr):
        dm = Iasr()
        dm.you = asr.you
        dm.is_final = asr.is_final
        self.pub_nlu.publish(dm)

    def ping(self):
        mm = Imm()
        mm.mod = "lu"
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
    
    nlu = ""
    rclpy.init(args=args)
    rnlu = RosNaturalLanguageUnderstanding(nlu)

    ros = threading.Thread(target=runROS, args=(rnlu,))

    ros.setDaemon(True)

    ros.start()
    shutdown()

if __name__ == '__main__':
    main()