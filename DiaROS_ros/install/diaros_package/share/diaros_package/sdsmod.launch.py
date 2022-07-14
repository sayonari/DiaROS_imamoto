from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='diaros_package',
            executable='sm',
            output='screen'
        ),
        Node(
            package='diaros_package',
            executable='lu',
            output='screen'
        ),
        Node(
            package='diaros_package',
            executable='dm',
            output='screen'
        ),
        Node(
            package='diaros_package',
            executable='rc',
            output='screen'
        ),
        Node(
            package='diaros_package',
            executable='nlg',
            output='screen'
        ),
        Node(
            package='diaros_package',
            executable='ss',
            output='screen'
        ),
    ])