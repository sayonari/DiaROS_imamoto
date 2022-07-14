import rclpy
import threading
import sys
from rclpy.node import Node
from interfaces.msg import Iasr
from interfaces.msg import Isa
from interfaces.msg import Imm
from diaros.automaticSpeechRecognition import AutomaticSpeechRecognition

class RosAutomaticSpeechRecognition(Node):
    def __init__(self, automaticSpeechRecognition):
        super().__init__('spoken_manager')
        self.automaticSpeechRecognition = automaticSpeechRecognition
        self.pub_asr = self.create_publisher(Iasr, 'ASRtoLU', 1)
        self.pub_sa = self.create_publisher(Isa, 'SAtoRC', 1)
        self.pub_asr_dr = self.create_publisher(Iasr, 'ASRtoDR', 1)
        self.pub_sa_dr = self.create_publisher(Isa, 'SAtoDR', 1)
        self.pub_mm = self.create_publisher(Imm, 'MM', 1)
        self.timer = self.create_timer(0.02, self.callback)

    def callback(self):
        asr = Iasr()
        asr.you = self.automaticSpeechRecognition.pubASR()['you']
        asr.is_final = self.automaticSpeechRecognition.pubASR()['is_final']
        print(asr.you, asr.is_final)
        self.pub_asr.publish(asr)
        self.pub_asr_dr.publish(asr)

        sa = Isa()
        sa.prevgrad = self.automaticSpeechRecognition.pubSA()['prevgrad']
        sa.frequency = self.automaticSpeechRecognition.pubSA()['frequency']
        sa.grad = self.automaticSpeechRecognition.pubSA()['grad']
        sa.power = self.automaticSpeechRecognition.pubSA()['power']
        sa.zerocross = self.automaticSpeechRecognition.pubSA()['zerocross']
        print(sa.prevgrad, sa.frequency, sa.grad, sa.power, sa.zerocross)
        self.pub_sa.publish(sa)
        self.pub_sa_dr.publish(sa)

        mm = Imm()
        mm.mod = "sm"
        self.pub_mm.publish(mm)

def runROS(pub):
    rclpy.spin(pub)

def runModule(automaticSpeechRecognition):
    automaticSpeechRecognition.run()

def shutdown():
    while True:
        key = input()
        if key == "kill":
            print("kill command received.")
            sys.exit()

def main(args=None):
    sm = AutomaticSpeechRecognition()
    rclpy.init(args=args)
    rsm = RosAutomaticSpeechRecognition(sm)

    ros = threading.Thread(target=runROS, args=(rsm,))
    mod = threading.Thread(target=runModule, args=(sm,))

    ros.setDaemon(True)
    mod.setDaemon(True)

    ros.start()
    mod.start()
    shutdown()

if __name__ == '__main__':
    main()