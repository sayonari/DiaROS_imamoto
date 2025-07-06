# 旧response_control

import rclpy
import threading
import sys
import time
import os
from rclpy.node import Node
from rclpy.logging import set_logger_level
from interfaces.msg import Iasr
from interfaces.msg import Isa
from interfaces.msg import Iss
from interfaces.msg import Idm
from interfaces.msg import Imm
from interfaces.msg import Itt
from interfaces.msg import Ibc  # 追加
from interfaces.msg import Iaa
from diaros.dialogManagement import DialogManagement
import sys
import os
sys.path.append(os.path.expanduser('~/DiaROS_deep_model/DiaROS_py/diaros'))
from playsound import playsound

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
        self.timer = self.create_timer(0.01, self.callback)  # 10msごとに変更（1msは過剰）
        self.recv_count = 0  # 受信回数カウンタ追加
        self.prev_recv_time = None  # 前回受信時刻

    def dm_update(self, dm):
        new = { "you": dm.you, "is_final": dm.is_final }
        self.dialogManagement.updateASR(new)
        
    def ss_update(self, ss):# test
        new = {
            "is_speaking": ss.is_speaking,
            "timestamp": ss.timestamp,
            "filename": ss.filename,  # ← 追加: 合成音声ファイル名を渡す
            "utterance_id": ss.utterance_id if hasattr(ss, 'utterance_id') else None  # 発話IDを追加
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
        pub_dm_return = self.dialogManagement.pubDM()
        words = pub_dm_return['words']
        dm_result_update = pub_dm_return['update']
        utterance_id = pub_dm_return.get('utterance_id', '')

        # デバッグログ追加
        if dm_result_update or (words and len(words) > 0):
            print(f"[DEBUG ros2_dm] update={dm_result_update}, words={words}, utterance_id={utterance_id}")
            sys.stdout.flush()

        # updateフラグがTrueかつwordsが空でない場合のみ送信
        if dm_result_update is True and words and any(w and w.strip() for w in words):
            dm = Idm()
            # wordsが文字列のリストであることを確認
            if isinstance(words, list) and all(isinstance(w, str) for w in words):
                dm.words = words
            else:
                # 文字列でない要素がある場合は文字列に変換
                dm.words = [str(w) if w is not None else "" for w in words]
            
            # 発話IDを設定
            dm.utterance_id = utterance_id if utterance_id else ""
            
            # 最終チェック：空の文字列のみのリストは送信しない
            if any(w.strip() for w in dm.words):
                self.pub_dm.publish(dm)
                print(f"[ros2_dm] Published to NLG: {dm.words} (ID: {dm.utterance_id})")
                sys.stdout.flush()
        # else:
        #     # 空のメッセージは送信しない（ログも出力しない）
        #     pass

    def aa_update(self, msg):
        new = {
            "prevgrad": 0.0,
            "frequency": 0.0,
            "grad": msg.grad,
            "power": msg.power,
            "zerocross": msg.zerocross
        }
        self.dialogManagement.updateSA(new)

    # def wav_play(self, msg):
    #     filename = msg.filename
    #     if filename:
    #         try:
    #             playsound(filename, True)
    #         except Exception as e:
    #             print(f"[DM] playsound error: {e}")

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
    import signal
    
    def signal_handler(sig, frame):
        print("Graceful shutdown received.")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Dialog management node shutdown.")
        sys.exit(0)

def main(args=None):
    # rcutilsエラーメッセージを抑制
    import os
    os.environ['RCUTILS_LOGGING_SEVERITY_THRESHOLD'] = 'ERROR'
    os.environ['RCUTILS_COLORIZED_OUTPUT'] = '0'
    os.environ['RCUTILS_CONSOLE_OUTPUT_FORMAT'] = '[{severity}] {message}'
    
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
