import rclpy
from rclpy.node import Node
from interfaces.msg import Iss
from diaros.timestamp_display import TimestampDisplay
import threading
import sys
import os
import signal
import time

class Ros2TimeListener(Node):
    def __init__(self, timestamp_display):
        super().__init__('ros2_time_listener')
        self.subscription = self.create_subscription(Iss, 'SStoDM', self.listener_callback, 10)
        self.timestamp_display = timestamp_display

    def listener_callback(self, msg):
        self.timestamp_display.update(msg.timestamp)

def runROS(node):
    rclpy.spin(node)

def shutdown():
    import signal
    import time
    
    def signal_handler(sig, frame):
        print("[ros2_time_listener] Gracefully shutting down...")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("[ros2_time_listener] Shutdown complete.")
        sys.exit(0)

def main(args=None):
    # rcutilsエラーメッセージを抑制
    import os
    os.environ['RCUTILS_LOGGING_SEVERITY_THRESHOLD'] = 'ERROR'
    os.environ['RCUTILS_COLORIZED_OUTPUT'] = '0'
    os.environ['RCUTILS_CONSOLE_OUTPUT_FORMAT'] = '[{severity}] {message}'
    
    rclpy.init(args=args)
    timestamp_display = TimestampDisplay()
    node = Ros2TimeListener(timestamp_display)
    
    # ROSノードを別スレッドで実行
    ros_thread = threading.Thread(target=runROS, args=(node,), daemon=True)
    ros_thread.start()
    
    # シャットダウン処理
    shutdown()
    
    # クリーンアップ
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
