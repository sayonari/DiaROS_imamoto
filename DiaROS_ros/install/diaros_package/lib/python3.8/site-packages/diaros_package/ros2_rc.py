import rclpy
import threading
import sys
from rclpy.node import Node
from interfaces.msg import Iasr
from interfaces.msg import Isa
from interfaces.msg import Irc
from interfaces.msg import Imm
from diaros.responseControl import ResponseControl

class RosResponseControl(Node):
    def __init__(self, responseControl):
        super().__init__('response_control')
        self.responseControl = responseControl
        self.prev_word = ""
        self.sub_dm = self.create_subscription(Iasr, 'DMtoRC', self.dm_update, 1)
        self.sub_sa = self.create_subscription(Isa, 'SAtoRC', self.sa_update, 1)
        self.pub_rc = self.create_publisher(Irc, 'RCtoNLG', 1)
        self.pub_mm = self.create_publisher(Imm, 'MM', 1)
        self.timer = self.create_timer(0.02, self.callback)

    def dm_update(self, dm):
        new = { "you": dm.you, "is_final": dm.is_final }
        self.responseControl.updateASR(new)

    def sa_update(self, sa):
        new = {
            "prevgrad" : sa.prevgrad,
            "frequency": sa.frequency,
            "grad"     : sa.grad,
            "power"    : sa.power,
            "zerocross": sa.zerocross   }

        self.responseControl.updateSA(new)

        mm = Imm()
        mm.mod = "rc"
        self.pub_mm.publish(mm)

    def callback(self):
        rc = Irc()
        now_word = self.responseControl.pubRC()['word']
        rc.word = now_word if self.prev_word != now_word else ""
        self.prev_word = now_word
        print(rc.word)
        self.pub_rc.publish(rc)
    

def runROS(pub):
    rclpy.spin(pub)

def runModule(responseControl):
    responseControl.run()

def shutdown():
    while True:
        key = input()
        if key == "kill":
            print("kill command received.")
            sys.exit()

def main(args=None):
    rc = ResponseControl()
    rclpy.init(args=args)
    rrc = RosResponseControl(rc)

    ros = threading.Thread(target=runROS, args=(rrc,))
    mod = threading.Thread(target=runModule, args=(rc,))

    ros.setDaemon(True)
    mod.setDaemon(True)

    ros.start()
    mod.start()
    shutdown()

if __name__ == '__main__':
    main()