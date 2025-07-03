import rclpy
import threading
from rclpy.node import Node
from rclpy.logging import set_logger_level
from std_msgs.msg import Float32MultiArray
import numpy as np
import sys
import os
import signal
import time

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