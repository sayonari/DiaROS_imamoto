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

### スクリプト・コマンド実行の厳格なルール / Strict Rules for Script and Command Execution
**既存のスクリプトやツールを必ず確認・活用すること。** 新規作成前に徹底的な調査が必要です。
1. **必ず既存実装を探す**: コマンドやスクリプトを実行する前に、同じ機能のものが既に存在しないか十分に確認
2. **既存ツールを精査**: 見つかった場合は内容を精査し、目的に合致すれば必ずそれを使用
3. **新規作成は最終手段**: 既存のものがない場合のみ新規作成を検討
4. **ビルドは必ずビルドスクリプトを使用**: `scripts/build/build_diaros.sh`など既存のビルドスクリプトを使用
5. **スクリプトの配置ルール**: 
   - **scripts/ルートディレクトリには直接ファイルを置かない**
   - 必ず適切なサブディレクトリに配置する:
     - `build/`: ビルド関連
     - `debug/`: デバッグ・モニタリング
     - `launch/`: 起動スクリプト
     - `setup/`: セットアップ・設定
     - `test/`: テストスクリプト
     - `utils/`: その他ユーティリティ

### 改行コードの統一 / Line Ending Consistency
**すべてのシェルスクリプトはLF（Unix形式）で作成すること。**
- Windowsの改行コード（CRLF）は使用禁止
- 新規作成時は必ずLFを使用
- エディタの設定を確認してLFに統一

**重要：スクリプト作成時の手順**
1. 必ずWriteツールで作成すること（Editツールは改行コードが不正になる場合がある）
2. 作成後、以下のコマンドで改行コードを確認・修正：
   ```bash
   # 改行コードの確認
   file /path/to/script.sh
   
   # CRLFをLFに変換（macOS）
   sed -i '' 's/\r$//' /path/to/script.sh
   
   # または dos2unix を使用
   dos2unix /path/to/script.sh
   ```
3. 実行権限を付与：
   ```bash
   chmod +x /path/to/script.sh
   ```

### パスの汎用性維持 / Path Portability
**絶対パスは使用禁止。** 公開リポジトリとして配布されるため、汎用性を保つこと。
- スクリプト内では相対パスを使用
- 環境依存の絶対パスは避ける
- ユーザー固有のパスをハードコードしない

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

### 高速応答生成API (High-Speed Response Generation)
DiaROSでは対話リズム維持のため、1500ms以内の応答が必要です。以下のAPIを推奨：

**推奨API (優先順位順):**
- **OpenAI API (ChatGPT)**: ~500-1000ms、最も高速で安定
- **Anthropic API (Claude)**: ~800-1200ms、高品質応答
- **ローカルモデル**: ~2000-5000ms、オフライン動作可能（非推奨）

**API設定方法:**
```bash
# 1. APIセットアップスクリプト実行（推奨）
./setup_api.sh

# 2. 手動設定
export OPENAI_API_KEY="sk-your-openai-api-key"
export ANTHROPIC_API_KEY="sk-ant-your-anthropic-api-key"
```

### 音声認識API
- **Google Speech-to-Text API**: For speech recognition

Set environment variables:
```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/google/credentials.json"
```

### 応答時間最適化設定
システム起動時に以下の優先順位で自動選択：
1. OpenAI API（設定済みの場合）
2. Anthropic API（設定済みの場合）  
3. ローカルモデル（APIキー未設定時）

**応答時間警告**: 1500ms超過時に警告メッセージを表示

## Task Management

### ToDo管理
プロジェクトの改善・修正タスクは`ToDo.md`ファイルで管理されています：
- **完了済みタスク**: ASR改善、API統合、エラー抑制など
- **将来的なタスク**: パフォーマンス最適化、機能拡張など
- **詳細**: `./ToDo.md`を参照

### 最近の主要改善
1. **200msポーズ検出**: 対話リズム維持の実装
2. **高速応答API**: OpenAI/Claude API統合（<1500ms）
3. **システム安定化**: 全エラー・警告メッセージの除去
4. **macOS最適化**: ネイティブ環境での完全動作

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

## プロジェクト構造 / Project Structure

### 重要：実際のプロジェクトパス構成
**DiaROSプロジェクトは以下の場所に配置されています：**
```
/Users/sayonari/_data/_DiaROS_mac/DiaROS_pixi/
├── diaros_workspace/              # Pixi仮想環境ワークスペース
└── DiaROS_imamoto/               # DiaROSメインディレクトリ
    ├── DiaROS_py/                # Pythonコアライブラリ
    ├── DiaROS_ros/               # ROS2パッケージ
    ├── scripts/                  # ユーティリティスクリプト
    └── CLAUDE.md                 # このファイル
```

### 音声ファイルの場所
- **相槌音声**: `DiaROS_ros/static_back_channel_*.wav`
- **静的応答**: `DiaROS_ros/static_response_source/static_response_*.wav`
- **合成音声**: `DiaROS_ros/tmp/*.wav`

### スクリプト実行時の注意
- スクリプトはPixi環境内で実行する必要があります
- 作業ディレクトリ: `cd ~/_data/_DiaROS_mac/DiaROS_pixi/diaros_workspace && pixi shell`
- 実行例: `pixi run python3 ../DiaROS_imamoto/scripts/test/test_audio_playback.py`