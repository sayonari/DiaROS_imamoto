# 旧response_control

import rclpy
import threading
import sys
import time
from rclpy.node import Node
from interfaces.msg import Iasr
from interfaces.msg import Isa
from interfaces.msg import Iss
from interfaces.msg import Idm
from interfaces.msg import Imm
from interfaces.msg import Itt
from interfaces.msg import Ibc  # 追加
from interfaces.msg import Iaa
from diaros.dialogManagement import DialogManagement

class RosDialogManagement(Node):
    def __init__(self, dialogManagement):
        super().__init__('dialog_management')
        self.dialogManagement = dialogManagement
        self.prev_word = ""
        # self.sub_dm = self.create_subscription(Iasr, 'DMtoDM', self.dm_update, 1)
        self.sub_lu = self.create_subscription(Iasr, 'NLUtoDM', self.dm_update, 1)  # NaturalLanguageUnderstanding2DialogManagement（nluでは処理を短絡してるのでIasrをつかう）
        self.sub_aa = self.create_subscription(Iaa, 'AAtoDM', self.aa_update, 1)
        self.sub_tt = self.create_subscription(Itt, 'TTtoDM', self.tt_update, 1) # TurnTaking2DialogManagement
        self.sub_bc = self.create_subscription(Ibc, 'BCtoDM', self.bc_update, 1) # BackChannel2DialogManagement
        self.sub_ss = self.create_subscription(Iss, 'SStoDM', self.ss_update, 1)
        self.pub_dm = self.create_publisher(Idm, 'DMtoNLG', 1)
        # self.pub_mm = self.create_publisher(Imm, 'MM', 1)
        self.timer = self.create_timer(0.001, self.callback)
        self.recv_count = 0  # 受信回数カウンタ追加
        self.prev_recv_time = None  # 前回受信時刻

    def dm_update(self, dm):
        new = { "you": dm.you, "is_final": dm.is_final }
        self.dialogManagement.updateASR(new)

    def sa_update(self, sa):
        new = {
            "prevgrad" : sa.prevgrad,
            "frequency": sa.frequency,
            "grad"     : sa.grad,
            "power"    : sa.power,
            "zerocross": sa.zerocross   }
        self.dialogManagement.updateSA(new)

        mm = Imm()
        mm.mod = "dm"
        # self.pub_mm.publish(mm)
    
    def ss_update(self, ss):# test
        new = {
            "is_speaking": ss.is_speaking,
            "timestamp": ss.timestamp
        }
        # print(f"[SSトピック受信] is_speaking: {new['is_speaking']} / timestamp: {new['timestamp']}")  # 確認用
        self.dialogManagement.updateSS(new)

    def tt_update(self, msg):
        data = {
            'result': msg.result,
            'confidence': msg.confidence
        }
        self.dialogManagement.updateTT(data)

    def bc_update(self, msg):
        data = {
            'result': msg.result,
            'confidence': msg.confidence
        }
        self.recv_count += 1
        now = time.time()
        if self.prev_recv_time is not None:
            elapsed_ms = (now - self.prev_recv_time) * 1000
        else:
            elapsed_ms = 0.0
        self.prev_recv_time = now
        # バーでconfidenceを表示 + 現在時刻（msまで）
        # bar_len = int(round(float(data['confidence']) * 10))
        # bar = '■' * bar_len + ' ' * (10 - bar_len)
        # now_str = time.strftime("%H:%M:%S", time.localtime(now)) + f".{int((now*1000)%1000):03d}"
        # print(f"[ros2_dm.py] Recv#{self.recv_count} {now_str} result={data['result']} confidence={data['confidence']:.10f}")
        # sys.stdout.flush()
        self.dialogManagement.updateBC(data)  # dialogManagement.py側でupdateBCを実装しておくこと

    def callback(self): #  連続して相槌を打てるようにした
        dm = Idm()
        pub_dm_return = self.dialogManagement.pubDM()
        now_word = pub_dm_return['word']
        dm_result_update = pub_dm_return['update']

        if dm_result_update is True:
            dm.word = now_word 
        else:
            dm.word = ""
        self.prev_word = now_word #  現状はprev_wordは使っていない
        #print(dm.word)
        # ここでpublish内容を標準出力
        # print(f"[DM publish] {dm.word}")
        # sys.stdout.flush()
        self.pub_dm.publish(dm)

    def aa_update(self, msg):
        new = {
            "prevgrad": 0.0,
            "frequency": 0.0,
            "grad": msg.grad,
            "power": msg.power,
            "zerocross": msg.zerocross
        }
        self.dialogManagement.updateSA(new)

    # def callback(self):# Admhive wordの内容が変更されていたら対話生成していた
    #     dm = Idm()
    #     now_word = self.dialogManagement.pubDM()['word']
    #     dm.word = now_word if self.prev_word != now_word else ""
    #     self.prev_word = now_word
    #     print(dm.word)
    #     self.pub_dm.publish(dm)
    

def runROS(pub):
    rclpy.spin(pub)

def runDM(dialogManagement):
    dialogManagement.run()

def shutdown():
    while True:
        key = input()
        if key == "kill":
            print("kill command received.")
            sys.exit()

def main(args=None):
    dm = DialogManagement()
    rclpy.init(args=args)
    rdm = RosDialogManagement(dm)

    ros = threading.Thread(target=runROS, args=(rdm,))
    mod = threading.Thread(target=runDM, args=(dm,))

    ros.setDaemon(True)
    mod.setDaemon(True)

    ros.start()
    mod.start()
    shutdown()

if __name__ == '__main__':
    main()
