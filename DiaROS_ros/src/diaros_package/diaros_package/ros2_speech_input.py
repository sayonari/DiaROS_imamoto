import rclpy
import threading
from rclpy.node import Node
from std_msgs.msg import Float32MultiArray
import numpy as np
import sys
import os

from diaros.speechInput import stream_queue, SpeechInput

class MicPublisher(Node):
    def __init__(self):
        super().__init__('speech_input')
        self.pub_mic = self.create_publisher(Float32MultiArray, 'mic_audio_float32', 10)
        self.timer = self.create_timer(0.01, self.publish_audio)  # 10ms to match speechInput chunk size
        self.send_count = 0

    def publish_audio(self):
        if not stream_queue.empty():
            data = stream_queue.get()
            float_array = np.frombuffer(data, dtype=np.float32)
            msg_mic = Float32MultiArray()
            msg_mic.data = float_array.tolist()
            self.pub_mic.publish(msg_mic)
            self.send_count += 1
            # 先頭データも表示
            first_val = float_array[0] if len(float_array) > 0 else None
            # sys.stdout.write(f"[ros2_speech_input] Published mic_audio_float32 #{self.send_count} (len={len(float_array)}) first={first_val}\n")
            # sys.stdout.flush()

def runROS(node):
    rclpy.spin(node)

def runSpeechInput():
    # 環境変数AUDIO_DEVICE_INDEXからデバイスを取得（未設定ならNone=デフォルトデバイス）
    device_str = os.environ.get('AUDIO_DEVICE_INDEX', '')
    device = None
    if device_str:
        try:
            device = int(device_str)
            sys.stdout.write(f"[ros2_speech_input] Using audio device index from env: {device}\n")
        except ValueError:
            sys.stderr.write(f"[ros2_speech_input] Invalid AUDIO_DEVICE_INDEX: {device_str}, using default\n")
    else:
        sys.stdout.write("[ros2_speech_input] Using default audio device (AUDIO_DEVICE_INDEX not set)\n")
    
    speech_input = SpeechInput(16000, 160, device)  # 10msチャンク
    try:
        while True:
            # SpeechInputは内部でマイク監視ループを持つため何もしない
            pass
    except KeyboardInterrupt:
        pass

def shutdown():
    while True:
        key = input()
        if key == "kill":
            print("kill command received.")
            sys.exit()

def main(args=None):
    rclpy.init(args=args)
    mic_publisher = MicPublisher()
    # SpeechInputを別スレッドで起動
    mic_thread = threading.Thread(target=runSpeechInput, daemon=True)
    mic_thread.start()
    # runROSをマルチスレッドで起動
    ros_thread = threading.Thread(target=runROS, args=(mic_publisher,), daemon=True)
    ros_thread.start()
    shutdown()
    mic_publisher.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
