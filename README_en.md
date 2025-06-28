# DiaROS
**[日本語バージョンはこちら](README.md)**

## Author
Ryota Nishimura (Tokushima University)  
nishimura@is.tokushima-u.ac.jp

## Developer
- Ryota Nishimura
- Takahiro Mori https://bitbucket.org/takahiro_mori_win/

## Demo video
[<img width="300" alt="youtube" src="https://user-images.githubusercontent.com/16011609/199163853-a00c3d9b-b4ea-483f-8d22-d1affb59dcd9.png">
](https://www.youtube.com/watch?v=2EkJCJpSpS4)

## Overview
DiaROS is a ROS2-compatible real-time spoken dialog system. While the system architecture is straightforward, it effectively demonstrates how to integrate a spoken dialog system with ROS2. The implementation wraps inter-module communication of a Python-based spoken dialog system with ROS2 messaging. This architecture enables monitoring, recording, and replaying communication content through ROS2 tools, significantly improving development and debugging efficiency.

## Important Notes
- This system is still under development and may contain bugs.

## System Features
The main branch includes deep learning-based speech recognition and natural language generation:
- High-accuracy local speech recognition using Hugging Face Transformers
- Local language generation using Japanese GPT-2 models
- Natural speech synthesis with VOICEVOX
- GPU recommended for optimal performance (CPU operation also supported)
- Completely offline operation - no API keys required


# System Installation Guide
The following sections describe the complete system installation process.

## 0. System Requirements
- OS: Ubuntu 22.04 LTS
- Python: 3.10.x (Ubuntu 22.04 default)
- ROS2: Humble Hawksbill


## 1. Install ROS2 Humble
Follow the official installation guide: https://docs.ros.org/en/humble/Installation/Ubuntu-Install-Debians.html

### 1.1 Basic Installation
```bash
# Configure locale
sudo locale-gen en_US en_US.UTF-8
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
export LANG=en_US.UTF-8

# Add ROS2 repository
sudo apt update && sudo apt install curl -y
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null

# Install ROS2 Humble
sudo apt update
sudo apt upgrade -y
sudo apt install ros-humble-desktop -y
sudo apt install ros-dev-tools -y

# Add environment setup to .bashrc
echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

### 1.2 (Optional) Turtlesim Test
```bash
# Run in separate terminals
# Terminal 1:
ros2 run turtlesim turtlesim_node

# Terminal 2:
ros2 run turtlesim turtle_teleop_key
```


## 2. Install Dependencies

### 2.1 System Packages
```bash
# Development tools
sudo apt update
sudo apt install -y git gcc g++ make cmake build-essential

# Python-related packages
sudo apt install -y python3-pip python3-dev python3-venv
sudo apt install -y python-is-python3

# Audio-related packages
sudo apt install -y portaudio19-dev libportaudio2
sudo apt install -y libsndfile1-dev

# Additional dependencies
sudo apt install -y libcairo2-dev libgirepository1.0-dev
sudo apt install -y libxt-dev libssl-dev libffi-dev
sudo apt install -y zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev
sudo apt install -y python3-tk tk-dev
```

### 2.2 Create Python Virtual Environment (Recommended)
```bash
# Create virtual environment in project directory
python3 -m venv venv
source venv/bin/activate

# Upgrade pip and tools
pip install --upgrade pip setuptools wheel
```


## 3. Install Spoken Dialog System

### 3.1 Environment Configuration
Add ROS2 environment to `~/.bashrc`:
```bash
# ROS2 environment
source /opt/ros/humble/setup.bash
```

### 3.2 Install Python Packages

```bash
# Deep learning frameworks (for local speech recognition and language generation)
pip install torch transformers

# Audio processing libraries
pip install numpy scipy matplotlib
pip install pyaudio sounddevice
pip install aubio  # or: pip install git+https://github.com/aubio/aubio/

# Speech synthesis libraries
pip install gtts playsound pydub

# Additional utilities
pip install requests pyworld

# ROS2-related packages (for GUI)
pip install PyQt5==5.15.* PySide2 pydot

# Optional: Google Cloud Speech API (if using cloud-based recognition)
# pip install google-cloud-speech
```

### 3.3 Install VOICEVOX (Japanese Speech Synthesis)

VOICEVOX is a high-quality Japanese speech synthesis engine.

1. Download VOICEVOX engine
```bash
# Check latest version: https://github.com/VOICEVOX/voicevox_engine/releases
wget https://github.com/VOICEVOX/voicevox_engine/releases/download/0.14.1/voicevox_engine-linux-cpu-0.14.1.7z
7z x voicevox_engine-linux-cpu-0.14.1.7z
```

2. Start VOICEVOX
```bash
cd voicevox_engine-linux-cpu-0.14.1
./run
# Runs on http://localhost:50021 by default
```

3. Install Python client
```bash
pip install voicevox-client
```

### 3.4 Install Spoken Dialog System Modules
Execute the following in the `DiaROS/DiaROS_py` directory:

```bash
cd ~/DiaROS/DiaROS_py
pip install -e .
```

### 3.5 Build ROS Packages

```bash
# Install colcon
sudo apt install python3-colcon-common-extensions

# Navigate to workspace
cd ~/DiaROS/DiaROS_ros

# Build interfaces (message types)
colcon build --cmake-args -DCMAKE_C_FLAGS=-fPIC --packages-select interfaces
source ./install/local_setup.bash

# Build DiaROS package
colcon build --packages-select diaros_package
source ./install/local_setup.bash
```


## 4. Execution Instructions

### 4.1 Start the Spoken Dialog System
```bash
# In a new terminal
cd ~/DiaROS/DiaROS_ros
source /opt/ros/humble/setup.bash
source ./install/local_setup.bash

# If using VOICEVOX, start it beforehand
# (In separate terminal: ./voicevox_engine/run)

# (Optional) Configure and test audio device
cd ~/DiaROS
python3 scripts/set_default_mic.py
# Or run simple audio test
python3 scripts/test_audio_simple.py

# Launch spoken dialog system
ros2 launch diaros_package sdsmod.launch.py
# Or use the configured launch script (if device was set)
/path/to/config/launch_diaros_with_mic.sh
```

### 4.2 Stop the System
Press `Ctrl+C` to terminate the system.


## 5. Utilizing ROS2 Monitoring Tools

### 5.1 rqt_graph - Visualize Nodes and Topics
```bash
# Visualize system communication structure
ros2 run rqt_graph rqt_graph
```

### 5.2 ros2 topic - Topic Monitoring
```bash
# List available topics
ros2 topic list

# Monitor specific topic content in real-time
ros2 topic echo /speech_recognition
ros2 topic echo /dialogue_response
ros2 topic echo /speech_synthesis

# Check topic frequency
ros2 topic hz /audio_input
```

### 5.3 ros2 bag - Data Recording and Playback
```bash
# Record all topics
ros2 bag record -a

# Record specific topics only
ros2 bag record /speech_recognition /dialogue_response

# View recorded data information
ros2 bag info <bag_file>

# Playback recorded data
ros2 bag play <bag_file>
```

### 5.4 rqt_plot - Data Visualization
```bash
# Display numerical data such as audio levels in graphs
ros2 run rqt_plot rqt_plot
```

### 5.5 Other Useful Commands
```bash
# List nodes
ros2 node list

# Node information
ros2 node info /speech_recognition_node

# List services
ros2 service list

# List parameters
ros2 param list
```


## 6. Troubleshooting

### 6.1 Sound Device (USB Headset) Not Recognized
```bash
# Update kernel modules
sudo apt update
sudo apt upgrade linux-generic

# After reboot, check devices
pactl list short sources
pactl list short sinks
```

### 6.2 Fix Default Sound Device

#### Automatic Configuration (Recommended)
```bash
# Use the audio device configuration script
cd ~/DiaROS
python3 scripts/set_default_mic.py
```

This script will:
- List all available audio input devices
- Allow you to select and test a device
- Save the configuration for DiaROS
- Create a launch script with the configured device

#### Manual Configuration
```bash
# Check input device list
pactl list short sources

# Set default device
pactl set-default-source <device_name>

# Add to ~/.bashrc for persistence
echo "pactl set-default-source <device_name>" >> ~/.bashrc

# Or set environment variable for DiaROS
export AUDIO_DEVICE_INDEX=<device_number>
```

### 6.3 Suppress ALSA-Related Error Messages
For errors like "Unknown PCM cards":
```bash
# Comment out unnecessary settings in /usr/share/alsa/alsa.conf
sudo nano /usr/share/alsa/alsa.conf
# Comment out lines like cards.pcm.rear, cards.pcm.center_lfe, etc.
```

### 6.4 Fix Python GTTS Errors
```bash
# For "No module named 'gi'" error
sudo apt install libcairo2-dev libgirepository1.0-dev
pip install pycairo PyGObject
```

### 6.5 ROS2-Related Issues
```bash
# Check environment variables
printenv | grep ROS

# Clean rebuild workspace
cd ~/DiaROS/DiaROS_ros
rm -rf build/ install/ log/
colcon build
```


## 7. Developer Information

### 7.1 Project Structure
```
DiaROS/
├── DiaROS_py/          # Python spoken dialog system modules
├── DiaROS_ros/         # ROS2 packages
│   ├── interfaces/     # Message type definitions
│   └── diaros_package/ # Main package
└── docs/               # Documentation
```

### 7.2 Main ROS Topics
- `/audio_input`: Audio input from microphone
- `/speech_recognition`: Speech recognition results
- `/dialogue_response`: Dialog system responses
- `/speech_synthesis`: Speech synthesis results
- `/audio_output`: Audio output to speakers

### 7.3 Deep Learning Models
The system uses advanced deep learning models for speech processing:
- **Speech Recognition**: Hugging Face japanese-HuBERT-base-VADLess-ASR model
- **Language Generation**: rinna/japanese-gpt2-small for natural responses
- **Speech Synthesis**: VOICEVOX for high-quality Japanese speech
- GPU recommended for optimal performance (CUDA support available)

### 7.4 Audio Device Management
DiaROS includes tools for managing audio devices:
- **scripts/set_default_mic.py**: Interactive device configuration tool
  - Lists all available audio input devices
  - Tests device functionality
  - Saves device configuration
  - Creates launch scripts with pre-configured devices
- **scripts/test_audio_simple.py**: Quick audio test script
  - Checks PyAudio device detection
  - Shows real-time audio levels
- **Automatic device detection**: Prefers PulseAudio devices in Docker environments
- **Environment variable**: Use `AUDIO_DEVICE_INDEX` to specify device


## 8. License and Acknowledgments
This system is developed for research purposes.
Please comply with the terms of service of each API used.

### Major Libraries and APIs Used
- ROS2 Humble
- Hugging Face Transformers (local speech recognition and language generation)
- VOICEVOX (Japanese speech synthesis)
- PyAudio
- Various other open-source libraries


## 9. Appendix: Using External APIs (Optional)

While DiaROS now runs completely locally without external APIs, you can optionally configure it to use cloud-based services for potentially higher accuracy:

### 9.1 Google Speech-to-Text API (Speech Recognition)
1. Create a project in Google Cloud Console
2. Enable Speech-to-Text API
3. Create service account key (JSON format)
4. Detailed instructions: https://cloud.google.com/speech-to-text/docs/before-you-begin
5. Set environment variable:
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS="$HOME/secret/google_stt_key.json"
   ```

### 9.2 OpenAI API (Response Generation)
1. Sign up at https://platform.openai.com/
2. Create an API key
3. Set environment variable:
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```
4. Modify `naturalLanguageGeneration.py` to set `self.use_local_model = False`

### 9.3 A3RT Talk API (Alternative Response Generation)
1. Obtain API key: https://a3rt.recruit.co.jp/product/talkAPI/
2. Save API key to a text file
3. Configure environment variable:
   ```bash
   export A3RT_APIKEY="$HOME/secret/a3rt_api_key.txt"
   ```
   Note: Current implementation uses OpenAI API or local models instead