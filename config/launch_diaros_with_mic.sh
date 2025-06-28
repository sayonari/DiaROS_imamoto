#!/bin/bash
# DiaROS起動スクリプト（設定済みマイクデバイス使用）

export AUDIO_DEVICE_INDEX=0
echo "🎤 音声デバイス 0 を使用してDiaROSを起動します..."

cd /workspace/DiaROS_ros
source /opt/ros/humble/setup.bash
source ./install/local_setup.bash

ros2 launch diaros_package sdsmod.launch.py
