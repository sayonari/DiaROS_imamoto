# macOSネイティブ環境でのDiaROS完全セットアップガイド

## 概要
このドキュメントは、M1/M2/M3 MacでDiaROSをネイティブ実行し、Metal Performance Shaders（MPS）を活用して最高のパフォーマンスを得るための完全なセットアップガイドです。

## システム要件
- macOS 12+ (Monterey以降)
- Apple Silicon Mac (M1/M2/M3)
- 16GB以上のメモリ推奨
- 約10GBの空きディスク容量

## 1. 事前準備

### 1.1 Xcodeコマンドラインツールのインストール
```bash
xcode-select --install
```

### 1.2 Homebrewのインストール
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# パスを通す（Apple Siliconの場合）
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zshrc
source ~/.zshrc
```

## 2. ROS2 Humbleのインストール

### 2.1 依存パッケージのインストール
```bash
# 基本的な依存関係
brew install python@3.10 cmake pkg-config
brew install eigen pcl opencv
brew install assimp tinyxml2 tinyxml
brew install log4cxx spdlog
brew install cunit

# ROS2依存関係
brew install console_bridge
brew install poco
brew install qt@5 pyqt@5
```

### 2.2 ROS2のインストール
```bash
# ROS2リポジトリを追加
brew tap ros2/ros2

# ROS2 Humbleをインストール
brew install ros-humble-desktop

# 環境設定を.zshrcに追加
echo 'source /opt/homebrew/opt/ros/humble/setup.zsh' >> ~/.zshrc
echo 'export ROS_DOMAIN_ID=0' >> ~/.zshrc
echo 'export ROS_LOCALHOST_ONLY=0' >> ~/.zshrc
source ~/.zshrc
```

### 2.3 ROS2動作確認
```bash
# 別々のターミナルで実行
# ターミナル1
ros2 run demo_nodes_cpp talker

# ターミナル2
ros2 run demo_nodes_cpp listener
```

## 3. Python環境のセットアップ

### 3.1 Python仮想環境の作成
```bash
# DiaROS用のディレクトリを作成
mkdir -p ~/DiaROS_workspace
cd ~/DiaROS_workspace

# Python 3.10の仮想環境を作成
python3.10 -m venv diaros_env
source diaros_env/bin/activate

# pipのアップグレード
pip install --upgrade pip setuptools wheel
```

### 3.2 PyTorch（MPS対応版）のインストール
```bash
# PyTorchとその関連パッケージ
pip install torch torchvision torchaudio

# MPS対応確認
python -c "import torch; print(f'MPS available: {torch.backends.mps.is_available()}')"
# "MPS available: True"と表示されればOK
```

### 3.3 音声処理・深層学習パッケージのインストール
```bash
# Transformersと関連パッケージ
pip install transformers sentencepiece fugashi unidic-lite
pip install huggingface-hub

# 音声処理パッケージ
pip install numpy==1.24.3  # aubio互換性のため
pip install scipy librosa soundfile
pip install pyaudio sounddevice
pip install webrtcvad pydub
pip install pyworld

# aubioのインストール（音響解析用）
pip install aubio

# その他の依存関係
pip install matplotlib requests pyyaml
pip install openai  # OpenAI API使用時のみ

# ROS2 Python パッケージ
pip install empy lark catkin_pkg
```

### 3.4 追加の音声関連セットアップ
```bash
# PortAudioのインストール（PyAudio用）
brew install portaudio

# 必要に応じてPyAudioを再インストール
pip uninstall pyaudio
pip install pyaudio
```

## 4. VOICEVOXのインストール

### 4.1 VOICEVOX Engineのダウンロード
```bash
# VOICEVOXのダウンロードディレクトリを作成
mkdir -p ~/DiaROS_workspace/voicevox
cd ~/DiaROS_workspace/voicevox

# 最新版をダウンロード（バージョンは適宜変更）
curl -L https://github.com/VOICEVOX/voicevox_engine/releases/download/0.14.0/macos-x64.zip -o voicevox.zip
unzip voicevox.zip
```

### 4.2 VOICEVOXの起動テスト
```bash
# VOICEVOX Engineを起動
cd macos-x64
./run

# 別ターミナルで動作確認
curl http://localhost:50021/version
```

## 5. DiaROSのクローンとセットアップ

### 5.1 リポジトリのクローン
```bash
cd ~/DiaROS_workspace
git clone https://github.com/sayonari/DiaROS_imamoto.git DiaROS
cd DiaROS
```

### 5.2 ROS2ワークスペースのビルド
```bash
# インターフェースのビルド
cd DiaROS_ros
source /opt/homebrew/opt/ros/humble/setup.zsh
colcon build --cmake-args -DCMAKE_C_FLAGS=-fPIC --packages-select interfaces
source ./install/local_setup.bash

# DiaROSパッケージのビルド
colcon build --packages-select diaros_package
source ./install/local_setup.bash
```

### 5.3 Pythonモジュールのインストール
```bash
# DiaROSのPythonモジュールをインストール
cd ../DiaROS_py
pip install -e .
```

## 6. 音声デバイスの設定

### 6.1 利用可能なデバイスの確認
```bash
# 音声入力デバイスを確認
python3 -c "import pyaudio; p=pyaudio.PyAudio(); print('Input devices:'); [print(f'{i}: {p.get_device_info_by_index(i)[\"name\"]}') for i in range(p.get_device_count()) if p.get_device_info_by_index(i)['maxInputChannels']>0]"
```

### 6.2 デバイス設定（必要に応じて）
```bash
# デバイス番号を環境変数で指定（例：デバイス0を使用）
export AUDIO_DEVICE_INDEX=0
```

## 7. HuggingFaceモデルへのアクセス設定

### 7.1 HuggingFaceアカウントの作成とトークン取得
1. https://huggingface.co/ でアカウント作成
2. https://huggingface.co/settings/tokens でアクセストークンを作成
3. 以下のモデルページでライセンスに同意：
   - https://huggingface.co/SiRoZaRuPa/japanese-HuBERT-base-VADLess-ASR-RSm

### 7.2 トークンの設定
```bash
# HuggingFace CLIでログイン
pip install huggingface-hub
huggingface-cli login
# トークンを入力

# または環境変数で設定
export HF_TOKEN=your_token_here
```

## 8. DiaROSの起動

### 8.1 必要なプロセスの起動
```bash
# ターミナル1: VOICEVOX Engineを起動
cd ~/DiaROS_workspace/voicevox/macos-x64
./run
```

### 8.2 環境変数の設定
```bash
# ターミナル2: DiaROS用の環境設定
cd ~/DiaROS_workspace/DiaROS
source diaros_env/bin/activate
source /opt/homebrew/opt/ros/humble/setup.zsh
source DiaROS_ros/install/local_setup.bash

# MPSを使用（推奨）
export DIAROS_DEVICE=mps

# パフォーマンス最適化
export OMP_NUM_THREADS=8
export TORCH_NUM_THREADS=8
```

### 8.3 DiaROSの起動
```bash
# 同じターミナル2で実行
cd ~/DiaROS_workspace/DiaROS
ros2 launch diaros_package sdsmod.launch.py
```

## 9. 動作確認

### 9.1 システムの状態確認
```bash
# 別ターミナルで実行
# ノード一覧
ros2 node list

# トピック一覧
ros2 topic list

# ノード間の通信を可視化
ros2 run rqt_graph rqt_graph
```

### 9.2 音声認識テスト
システムが起動したら、マイクに向かって話しかけてください：
- 「こんにちは」
- 「今日の天気はどうですか」
- 「ありがとうございます」

## 10. トラブルシューティング

### 10.1 PyAudioエラー
```bash
# PortAudioの再インストール
brew reinstall portaudio
pip uninstall pyaudio
pip install pyaudio
```

### 10.2 MPSエラー
```bash
# MPSフォールバックを有効化
export PYTORCH_ENABLE_MPS_FALLBACK=1
```

### 10.3 音声が認識されない
```bash
# マイクの権限を確認
# システム設定 → プライバシーとセキュリティ → マイク → ターミナルを許可

# 音声デバイスのテスト
python3 ~/DiaROS_workspace/DiaROS/scripts/test_audio_simple.py
```

### 10.4 VOICEVOXが起動しない
```bash
# 権限の付与
chmod +x ~/DiaROS_workspace/voicevox/macos-x64/run
```

## 11. パフォーマンスモニタリング

### 11.1 GPU使用状況の確認
```bash
# Activity Monitorで「GPU History」を確認
# または
sudo powermetrics --samplers gpu_power -i 1000 -n 10
```

### 11.2 推論速度の確認
DiaROSの出力に表示される処理時間を確認：
- `[Device] Using MPS (Metal Performance Shaders) on Apple Silicon`
- 各モジュールの処理時間がログに表示されます

## まとめ

これで、M1/M2/M3 MacでDiaROSをネイティブ実行し、MPSを活用した高速な音声対話システムが動作するはずです。Docker環境と比較して約10倍の推論速度向上が期待できます。

問題が発生した場合は、各セクションのトラブルシューティングを参照してください。