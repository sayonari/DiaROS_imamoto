import rclpy
import threading
from rclpy.node import Node
from std_msgs.msg import Float32MultiArray
import numpy as np
import sys

from diaros.speechInput import stream_queue, SpeechInput

class MicPublisher(Node):
    def __init__(self):
        super().__init__('speech_input')
        self.pub_mic = self.create_publisher(Float32MultiArray, 'mic_audio_float32', 10)
        self.timer = self.create_timer(0.005, self.publish_audio)
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
    speech_input = SpeechInput(16000, 160, 0)  # 10msチャンク
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
    mic_thread = threading.Thread(target=runSpeechInput)
    mic_thread.setDaemon(True)
    mic_thread.start()
    # runROSをマルチスレッドで起動
    ros_thread = threading.Thread(target=runROS, args=(mic_publisher,))
    ros_thread.setDaemon(True)
    ros_thread.start()
    shutdown()
    mic_publisher.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
