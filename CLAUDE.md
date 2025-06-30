# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 🔴 最重要事項 / CRITICAL REQUIREMENTS

### 日本語対応 / Japanese Language Support
**必ず日本語で対話してください。** ユーザーとのすべてのコミュニケーションは日本語で行う必要があります。
- コメント、説明、エラーメッセージなど、すべて日本語で記述
- 技術用語は必要に応じて英語併記可
- コード内のコメントも可能な限り日本語で記述

**ALWAYS communicate in Japanese.** All communication with users must be in Japanese.
- Comments, explanations, error messages should all be in Japanese
- Technical terms can include English when necessary
- Code comments should also be in Japanese whenever possible

## Essential Commands

### System Setup and Build
```bash
# Setup ROS2 environment (required before any ROS commands)
cd ~/DiaROS_imamoto/DiaROS_ros
source /opt/ros/humble/setup.bash  # or your ROS2 installation path
source ./install/local_setup.bash

# Build the ROS packages
colcon build --cmake-args -DCMAKE_C_FLAGS=-fPIC --packages-select interfaces
source ./install/local_setup.bash
colcon build --packages-select diaros_package
source ./install/local_setup.bash

# Install Python modules
cd ../DiaROS_py
python -m pip install . --user
```

### Running the System
```bash
# Primary command to launch the spoken dialog system
ros2 launch diaros_package sdsmod.launch.py

# Run without microphone input (for ros2 bag replay)
ros2 launch diaros_package sdsmod.launch.py mic:=false

# Run with muted microphone
ros2 launch diaros_package sdsmod.launch.py mic:=mute
```

### Development and Debugging
```bash
# View ROS2 topics
ros2 topic list

# Monitor topic communication in real-time
ros2 topic echo [topic_name]

# Record system communication for debugging
ros2 bag record [topic1] [topic2] ... [topicN]

# Replay recorded communication
ros2 bag play [bag_file_name]

# Visualize node communication graph
ros2 run rqt_graph rqt_graph

# Plot topic data
ros2 run rqt_plot rqt_plot
```

## High-Level Architecture

DiaROS is a ROS2-based real-time spoken dialog system composed of two main parts:

### Core Python Library (`DiaROS_py/`)
Contains the core dialog system modules in Python:
- **speechInput.py**: Audio input using PyAudio
- **acousticAnalysis.py**: Acoustic analysis using aubio
- **automaticSpeechRecognition.py**: VAD-less ASR
- **dialogManagement.py**: Real-time dialog and backchannel control
- **naturalLanguageGeneration.py**: Response generation (ChatGPT API)
- **speechSynthesis.py**: Speech synthesis using VOICEVOX
- **turnTaking.py**: Turn-taking management
- **backChannel.py**: Backchannel response handling

### ROS2 Package (`DiaROS_ros/`)
ROS2 wrappers that enable:
- Inter-module communication via ROS2 topics
- System monitoring and debugging
- Recording and replay of dialog sessions
- Distributed processing capabilities

#### Key ROS2 Nodes (launched by sdsmod.launch.py):
- `ros2_speech_input`: Audio input node (conditional on `mic` parameter)
- `ros2_acoustic_analysis`: Audio feature extraction
- `ros2_automatic_speech_recognition`: Speech-to-text conversion
- `ros2_natural_language_understanding`: Intent understanding (passthrough)
- `ros2_dialog_management`: Central dialog coordinator
- `ros2_speech_synthesis`: Text-to-speech conversion
- `ros2_turn_taking`: Turn-taking control
- `ros2_back_channel`: Backchannel response generation

#### Custom Message Interfaces (`interfaces/`)
Defines ROS2 message types for dialog system communication.

### Monitoring Tools
- Use built-in ROS2 tools for system monitoring:
  - `ros2 topic echo` for real-time topic monitoring
  - `rqt_graph` for visual system topology
  - `ros2 bag` for recording and playback

## API Requirements

The system requires external API keys:
- **A3RT Talk API**: For chat response generation
- **Google Speech-to-Text API**: For speech recognition

Set environment variables:
```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/google/credentials.json"
export A3RT_APIKEY="/path/to/a3rt/apikey.data"
```

## Development Environment

- **OS**: Ubuntu 22.04 LTS 
- **ROS2**: Humble Hawksbill (primary supported version)
- **Python**: 3.10.x (Ubuntu 22.04 default)
- **Key Dependencies**: PyAudio, aubio, torch, transformers, rclpy, VOICEVOX

## System Architecture Flow

1. **Audio Input**: Microphone → speech_input → acoustic_analysis
2. **Recognition**: acoustic_analysis → automatic_speech_recognition
3. **Understanding**: speech_recognition → natural_language_understanding  
4. **Dialog Management**: Central coordinator managing all dialog flow
5. **Response Generation**: dialog_management → natural_language_generation
6. **Speech Output**: response → speech_synthesis → audio output
7. **Turn Management**: turn_taking monitors and controls speaking turns
8. **Backchannel**: Generates appropriate listener responses during speech

The modular ROS2 architecture allows individual components to be developed, tested, and debugged independently while maintaining real-time communication capabilities.