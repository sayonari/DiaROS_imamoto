import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from interfaces.msg import List

class TestMod(Node):
    def __init__(self):
        super().__init__('test')
        self.sub = self.create_subscription(List, 'test_topic', self.callback, 1)
    
    def callback(self, msg):
        #self.get_logger().info("Sub: {0} {1} {2} {3}".format( msg.n, msg.you, msg.bot, msg.frequency ) )
        print("Test: {0} {1} {2} {3}".format( msg.n, msg.you, msg.bot, msg.frequency ))

def main(args=None):
    rclpy.init(args=args)
    sub_test = TestMod()
    rclpy.spin(sub_test)

if __name__ == '__main__':
    main()