import rclpy
import threading
import sys
from rclpy.node import Node
from interfaces.msg import Irc
from interfaces.msg import Inlg
from interfaces.msg import Imm
from diaros.dialogManagement import DialogManagement

class RosDialogManagement(Node):
    def __init__(self, dialogManagement):
        super().__init__('dialog_management')
        self.dialogManagement = dialogManagement
        self.sub_rc = self.create_subscription(Irc, 'RCtoNLG', self.genrate, 1)
        self.pub_nlg = self.create_publisher(Inlg, 'NLGtoSS', 1)
        self.pub_nlg_dr = self.create_publisher(Inlg, 'NLGtoDR', 1)
        self.pub_mm = self.create_publisher(Imm, 'MM', 1)
        self.timer = self.create_timer(0.02, self.ping)
    
    def genrate(self, rc):
        query = rc.word
        if not query == "":
            reply = self.dialogManagement.response(query)
            nlg = Inlg()
            nlg.reply = reply
            print(nlg.reply)
            self.pub_nlg.publish(nlg)
            self.pub_nlg_dr.publish(nlg)

    def ping(self):
        mm = Imm()
        mm.mod = "nlg"
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
    nlg = DialogManagement()
    rclpy.init(args=args)
    rnlg = RosDialogManagement(nlg)

    ros = threading.Thread(target=runROS, args=(rnlg,))

    ros.setDaemon(True)

    ros.start()
    shutdown()

if __name__ == '__main__':
    main()