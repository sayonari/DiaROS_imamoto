from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument, SetEnvironmentVariable
from launch.substitutions import LaunchConfiguration
from launch.conditions import IfCondition
import os

def generate_launch_description():
    # Declare launch arguments
    mic_arg = DeclareLaunchArgument(
        'mic',
        default_value='true',
        description='Enable microphone input'
    )
    
    # Set environment variables to suppress rcutils errors
    env_vars = [
        SetEnvironmentVariable('RCUTILS_LOGGING_SEVERITY_THRESHOLD', 'ERROR'),
        SetEnvironmentVariable('RCUTILS_COLORIZED_OUTPUT', '0'),
        SetEnvironmentVariable('RCUTILS_CONSOLE_OUTPUT_FORMAT', '[{severity}] [{name}]: {message}'),
        SetEnvironmentVariable('ROS_LOG_DIR', '/tmp/ros_logs'),  # 短いパスに設定
    ]
    
    # Get launch configuration
    mic = LaunchConfiguration('mic')
    
    # Define nodes without prefix (environment variables are already set)
    speech_input_node = Node(
        package='diaros_package',
        executable='ros2_speech_input',
        name='ros2_speech_input',
        output='screen',
        condition=IfCondition(mic)
    )
    
    acoustic_analysis_node = Node(
        package='diaros_package',
        executable='ros2_acoustic_analysis',
        name='ros2_acoustic_analysis',
        output='screen'
    )
    
    asr_node = Node(
        package='diaros_package',
        executable='ros2_automatic_speech_recognition',
        name='ros2_automatic_speech_recognition',
        output='screen'
    )
    
    nlu_node = Node(
        package='diaros_package',
        executable='ros2_natural_language_understanding',
        name='ros2_natural_language_understanding',
        output='screen'
    )
    
    dialog_management_node = Node(
        package='diaros_package',
        executable='ros2_dialog_management',
        name='ros2_dialog_management',
        output='screen'
    )
    
    speech_synthesis_node = Node(
        package='diaros_package',
        executable='ros2_speech_synthesis',
        name='ros2_speech_synthesis',
        output='screen'
    )
    
    turn_taking_node = Node(
        package='diaros_package',
        executable='ros2_turn_taking',
        name='ros2_turn_taking',
        output='screen'
    )
    
    back_channel_node = Node(
        package='diaros_package',
        executable='ros2_back_channel',
        name='ros2_back_channel',
        output='screen'
    )
    
    # Return launch description
    return LaunchDescription([
        mic_arg,
        *env_vars,  # 環境変数の設定
        speech_input_node,
        acoustic_analysis_node,
        asr_node,
        nlu_node,
        dialog_management_node,
        speech_synthesis_node,
        turn_taking_node,
        back_channel_node
    ])