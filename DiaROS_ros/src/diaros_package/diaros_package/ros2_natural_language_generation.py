import rclpy
import threading
import sys
import os
import time
from rclpy.node import Node
from rclpy.logging import set_logger_level
from interfaces.msg import Idm
from interfaces.msg import Inlg
from interfaces.msg import Imm
from diaros.naturalLanguageGeneration import NaturalLanguageGeneration
class RosNaturalLanguageGeneration(Node):
    def __init__(self, naturalLanguageGeneration):
        super().__init__('natural_language_generation')
        self.naturalLanguageGeneration = naturalLanguageGeneration
        self.sub_dm = self.create_subscription(Idm, 'DMtoNLG', self.dm_update, 1)
        self.pub_nlg = self.create_publisher(Inlg, 'NLGtoSS', 1)  # NLG→SpeechSynthesis用
        # self.pub_nlg_dr = self.create_publisher(Inlg, 'NLGtoDR', 1)
        # self.pub_mm = self.create_publisher(Imm, 'MM', 1)
        self.timer = self.create_timer(0.02, self.ping)
        self.last_sent_reply = None

    def dm_update(self, msg):
        words = list(msg.words)
        if words:
            self.get_logger().info(f'[NLG] Received words from DM: {words}')
            self.naturalLanguageGeneration.update(words)

    def ping(self):
        # 応答が生成されたらpublish
        if hasattr(self.naturalLanguageGeneration, "last_reply") and self.naturalLanguageGeneration.last_reply != self.last_sent_reply:
            nlg_msg = Inlg()
            nlg_msg.reply = self.naturalLanguageGeneration.last_reply
            self.pub_nlg.publish(nlg_msg)  # ここでNLG生成文をNLGtoSSトピックで送信
            # self.pub_nlg_dr.publish(nlg_msg)  # ← コメントアウト
            self.last_sent_reply = self.naturalLanguageGeneration.last_reply
        mm = Imm()
        mm.mod = "nlg"
        # self.pub_mm.publish(mm)

def runROS(node):
    rclpy.spin(node)

def runNLG(naturalLanguageGeneration):
    naturalLanguageGeneration.run()

def shutdown():
    import signal
    
    def signal_handler(sig, frame):
        print("Natural language generation node graceful shutdown received.")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Natural language generation node shutdown.")
        sys.exit(0)

def main(args=None):
    # rcutilsエラーメッセージを抑制
    import os
    os.environ['RCUTILS_LOGGING_SEVERITY_THRESHOLD'] = 'ERROR'
    os.environ['RCUTILS_COLORIZED_OUTPUT'] = '0'
    os.environ['RCUTILS_CONSOLE_OUTPUT_FORMAT'] = '[{severity}] {message}'
    
    naturalLanguageGeneration = NaturalLanguageGeneration()
    rclpy.init(args=args)
    rnlg = RosNaturalLanguageGeneration(naturalLanguageGeneration)

    ros = threading.Thread(target=runROS, args=(rnlg,))
    mod = threading.Thread(target=runNLG, args=(naturalLanguageGeneration,))

    ros.setDaemon(True)
    mod.setDaemon(True)

    ros.start()
    mod.start()
    shutdown()

if __name__ == '__main__':
    main()