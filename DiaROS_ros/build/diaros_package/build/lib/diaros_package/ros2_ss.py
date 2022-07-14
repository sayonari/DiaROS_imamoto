import rclpy
import threading
import sys
from rclpy.node import Node
from interfaces.msg import Inlg
from interfaces.msg import Iss
from interfaces.msg import Imm
from diaros.speechSynthesis import SpeechSynthesis

class RosSpeechSynthesis(Node):
    def __init__(self, speechSynthesis):
        super().__init__('speech_synthesis')
        self.speechSynthesis = speechSynthesis
        self.sub_nlg = self.create_subscription(Inlg, 'NLGtoSS', self.play, 1)
        self.pub_ss = self.create_publisher(Iss, 'SStoDR', 1)
        self.pub_mm = self.create_publisher(Imm, 'MM', 1)
        self.timer = self.create_timer(0.02, self.send)
        self.is_speaking = False

    def play(self, nlg):
        if not self.is_speaking:
            text = str(nlg.reply)
            print("speaking..."+text)
            self.is_speaking = True
            self.speechSynthesis.run(text)
            print("finish..."+text)
            self.is_speaking = False

    def send(self):
        ss = Iss()
        ss.is_speaking = self.is_speaking
        print(ss.is_speaking)
        self.pub_ss.publish(ss)

        mm = Imm()
        mm.mod = "ss"
        self.pub_mm.publish(mm)

def runROS(pub):
    rclpy.spin(pub)

def shutdown():
    while True:
        key = input()
        if key == "kill":
            print("kill command received.")
            sys.exit()

def main(args=None):
    ss = SpeechSynthesis()
    rclpy.init(args=args)
    rss = RosSpeechSynthesis(ss)

    ros = threading.Thread(target=runROS, args=(rss,))

    ros.setDaemon(True)

    ros.start()
    shutdown()

if __name__ == '__main__':
    main()
