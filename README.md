# DiaROS
**[English ver is HERE](README_en.md)**

## 目次

- [概要](#概要)
- [システムの特徴](#システムの特徴)
- [Demo video](#demo-video)
- [システムインストール方法](#システムインストール方法)
  - [0. システム要件](#0-システム要件)
  - [1. ROS2 Humble をインストールする](#1-ros2-humble-をインストールする)
    - [1.1 基本インストール](#11-基本インストール)
    - [1.2（オプション）Turtlesim でのテスト](#12オプションturtlesim-でのテスト)
  - [2. 依存パッケージのインストール](#2-依存パッケージのインストール)
    - [2.1 システムパッケージ](#21-システムパッケージ)
    - [2.2 Python仮想環境の作成（推奨）](#22-python仮想環境の作成推奨)
  - [3. 音声対話システムインストール](#3-音声対話システムインストール)
    - [3.1 環境設定](#31-環境設定)
    - [3.2 Pythonパッケージのインストール](#32-pythonパッケージのインストール)
    - [3.3 VOICEVOX（日本語音声合成）のインストール](#33-voicevox日本語音声合成のインストール)
    - [3.4 音声対話システムモジュールのインストール](#34-音声対話システムモジュールのインストール)
    - [3.5 ROSパッケージのビルド](#35-rosパッケージのビルド)
  - [4. 実行手順](#4-実行手順)
    - [4.1 音声対話システムの起動](#41-音声対話システムの起動)
    - [4.2 システムの停止](#42-システムの停止)
  - [5. ROS2モニタリングツールの活用](#5-ros2モニタリングツールの活用)
    - [5.0 DiaROS専用モニタリングツール（Docker環境）](#50-diaros専用モニタリングツールdocker環境)
    - [5.1 rqt_graph - ノードとトピックの可視化](#51-rqt_graph---ノードとトピックの可視化)
    - [5.2 ros2 topic - トピックの監視](#52-ros2-topic---トピックの監視)
    - [5.3 ros2 bag - データの記録と再生](#53-ros2-bag---データの記録と再生)
    - [5.4 rqt_plot - データの可視化](#54-rqt_plot---データの可視化)
    - [5.5 その他の便利なコマンド](#55-その他の便利なコマンド)
  - [6. トラブルシューティング](#6-トラブルシューティング)
    - [6.1 サウンドデバイス（USBヘッドセット）が認識されない場合](#61-サウンドデバイスusbヘッドセットが認識されない場合)
    - [6.2 デフォルトサウンドデバイスの固定](#62-デフォルトサウンドデバイスの固定)
    - [6.3 ALSA関連のエラーメッセージを抑制](#63-alsa関連のエラーメッセージを抑制)
    - [6.4 Python GTTSでのエラー対処](#64-python-gttsでのエラー対処)
    - [6.5 ROS2関連のトラブル](#65-ros2関連のトラブル)
  - [7. 開発者向け情報](#7-開発者向け情報)
    - [7.1 プロジェクト構造](#71-プロジェクト構造)
    - [7.2 主要なROSトピック](#72-主要なrosトピック)
    - [7.3 ディープラーニングモデル](#73-ディープラーニングモデル)
    - [7.4 音声デバイス管理](#74-音声デバイス管理)
  - [8. ライセンスと謝辞](#8-ライセンスと謝辞)
  - [9. macOSネイティブ実行（Apple Silicon GPU活用）](#9-macosネイティブ実行apple-silicon-gpu活用)
    - [9.1 概要](#91-概要)
    - [9.2 クイックセットアップ（Pixiを使用）](#92-クイックセットアップpixiを使用)
    - [9.3 パフォーマンス比較](#93-パフォーマンス比較)
    - [9.4 環境変数とデバイス選択](#94-環境変数とデバイス選択)
    - [9.5 トラブルシューティング](#95-トラブルシューティング)
    - [9.6 必要なモデルへのアクセス](#96-必要なモデルへのアクセス)
  - [10. 付録：外部APIの使用（オプション）](#10-付録外部apiの使用オプション)
    - [10.1 Google Speech-to-Text API（音声認識）](#101-google-speech-to-text-api音声認識)
    - [10.2 OpenAI API（応答生成）](#102-openai-api応答生成)
    - [10.3 A3RT Talk API（代替応答生成）](#103-a3rt-talk-api代替応答生成)
    - [10.4 ROS2なしでの実行（実験的）](#104-ros2なしでの実行実験的)

## Author
西村良太 豊橋技術科学大学  
nishimura.ryota.tz@tut.jp

## Developer
- 西村 良太 (Ryota Nishimura)
- 森 貴大 (Takahiro Mori) https://bitbucket.org/takahiro_mori_win/
- 今本 麟太朗 (Rintaroh Imamoto) https://github.com/iris-aegis

## Demo video
[<img width="300" alt="youtube" src="https://user-images.githubusercontent.com/16011609/199163853-a00c3d9b-b4ea-483f-8d22-d1affb59dcd9.png">
](https://www.youtube.com/watch?v=2EkJCJpSpS4)

## 概要
リアルタイム音声対話システムをROS2対応にさせたものです．システム自体の構成は単純で，中身も単純ですが，その分，音声対話システムのROS対応の方法が理解できると思います．基本的には，python実装された音声対話システムの各モジュール間の通信をROSでラップした構成になっています．この構成にすることで，通信内容をROSで監視することが可能となり，通信内容の確認，記録，再生が可能となるため，システム開発・デバッグの効率が格段に上がります．

## 注意事項
- まだバグが含まれています．バグ取り段階です．

## システムの特徴
メインブランチにはディープラーニングベースの音声認識と自然言語生成が含まれています：
- Hugging Face Transformersを使用した高精度ローカル音声認識
- 日本語GPT-2モデルを使用したローカル言語生成
- VOICEVOXによる自然な音声合成
- 最適なパフォーマンスのためGPU推奨（CPU動作も可能）
- 完全オフライン動作 - APIキー不要


# システムインストール方法
以下にシステムのインストール方法を記載します．

## 0. システム要件
- OS: Ubuntu 22.04 LTS / macOS 12+ (Monterey以降)
- Python: 3.10.x（Ubuntu 22.04のデフォルト）
- ROS2: Humble Hawksbill
- GPU: 
  - Linux: NVIDIA GPU（CUDA対応）推奨
  - macOS: Apple Silicon（M1/M2/M3）のMetal Performance Shaders対応


## 1. ROS2 Humble をインストールする
https://docs.ros.org/en/humble/Installation/Ubuntu-Install-Debians.html

### 1.1 基本インストール
```bash
# ロケール設定
sudo locale-gen en_US en_US.UTF-8
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
export LANG=en_US.UTF-8

# ROS2リポジトリの追加
sudo apt update && sudo apt install curl -y
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null

# ROS2 Humbleインストール
sudo apt update
sudo apt upgrade -y
sudo apt install ros-humble-desktop -y
sudo apt install ros-dev-tools -y

# 環境設定を.bashrcに追加
echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

### 1.2（オプション）Turtlesim でのテスト
```bash
# 別々のターミナルで実行
# ターミナル1:
ros2 run turtlesim turtlesim_node

# ターミナル2:
ros2 run turtlesim turtle_teleop_key
```


## 2. 依存パッケージのインストール

### 2.1 システムパッケージ
```bash
# 開発ツール
sudo apt update
sudo apt install -y git gcc g++ make cmake build-essential

# Python関連
sudo apt install -y python3-pip python3-dev python3-venv
sudo apt install -y python-is-python3

# オーディオ関連
sudo apt install -y portaudio19-dev libportaudio2
sudo apt install -y libsndfile1-dev

# その他の依存関係
sudo apt install -y libcairo2-dev libgirepository1.0-dev
sudo apt install -y libxt-dev libssl-dev libffi-dev
sudo apt install -y zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev
sudo apt install -y python3-tk tk-dev
```

### 2.2 Python仮想環境の作成（推奨）
```bash
# プロジェクトディレクトリで実行
python3 -m venv venv
source venv/bin/activate

# pipのアップグレード
pip install --upgrade pip setuptools wheel
```


## 3. 音声対話システムインストール

### 3.1 環境設定
`~/.bashrc` にROS2環境を追加:
```bash
# ROS2環境
source /opt/ros/humble/setup.bash
```

### 3.2 Pythonパッケージのインストール

```bash
# ディープラーニングフレームワーク（ローカル音声認識・言語生成用）
pip install torch transformers

# 音声処理関連
pip install numpy scipy matplotlib
pip install pyaudio sounddevice
pip install aubio  # または: pip install git+https://github.com/aubio/aubio/

# 音声合成関連
pip install gtts playsound pydub

# その他のユーティリティ
pip install requests pyworld

# ROS2関連（GUI用）
pip install PyQt5==5.15.* PySide2 pydot

# オプション：Google Cloud Speech API（クラウドベース認識を使用する場合）
# pip install google-cloud-speech
```

### 3.3 VOICEVOX（日本語音声合成）のインストール

VOICEVOXは高品質な日本語音声合成エンジンです．

1. VOICEVOXエンジンのダウンロード
```bash
# 最新版を確認: https://github.com/VOICEVOX/voicevox_engine/releases
wget https://github.com/VOICEVOX/voicevox_engine/releases/download/0.14.1/voicevox_engine-linux-cpu-0.14.1.7z
7z x voicevox_engine-linux-cpu-0.14.1.7z
```

2. VOICEVOXの起動
```bash
cd voicevox_engine-linux-cpu-0.14.1
./run
# デフォルトでhttp://localhost:50021で起動
```

3. Python用クライアントのインストール
```bash
pip install voicevox-client
```

### 3.4 音声対話システムモジュールのインストール
`DiaROS/DiaROS_py`ディレクトリで以下を実行:

```bash
cd ~/DiaROS/DiaROS_py
pip install -e .
```

### 3.5 ROSパッケージのビルド

```bash
# colconのインストール
sudo apt install python3-colcon-common-extensions

# ワークスペースに移動
cd ~/DiaROS/DiaROS_ros

# インターフェース（メッセージ型）のビルド
colcon build --cmake-args -DCMAKE_C_FLAGS=-fPIC --packages-select interfaces
source ./install/local_setup.bash

# DiaROSパッケージのビルド
colcon build --packages-select diaros_package
source ./install/local_setup.bash
```


## 4. 実行手順

### 4.1 音声対話システムの起動
```bash
# 新しいターミナルで
cd ~/DiaROS/DiaROS_ros
source /opt/ros/humble/setup.bash
source ./install/local_setup.bash

# VOICEVOXを使用する場合は事前に起動しておく
# （別ターミナルで ./voicevox_engine/run を実行）

# （オプション）音声デバイスの設定とテスト
cd ~/DiaROS
python3 scripts/set_default_mic.py
# または簡易音声テスト
python3 scripts/test_audio_simple.py

# 音声対話システムの実行
ros2 launch diaros_package sdsmod.launch.py
# または設定済みスクリプトを使用（デバイスを設定した場合）
/path/to/config/launch_diaros_with_mic.sh
```

### 4.2 システムの停止
`Ctrl+C` で終了します．


## 5. ROS2モニタリングツールの活用

### 5.0 DiaROS専用モニタリングツール（Docker環境）

DiaROSには専用の統合モニタリングスクリプト`monitor.sh`が用意されています：

```bash
# Docker環境でモニタリングツールを起動
./scripts/monitor.sh
```

このスクリプトは以下の機能を提供します：
- 基本的なROS2モニタリングツール（rqt、rqt_graph等）
- DiaROS専用の対話フロー監視
- 音声認識・合成の状態監視
- 性能測定ツール（トピック周期、遅延測定等）
- システムリソース監視

**📖 詳細な使い方**: [docs/monitoring_guide.md](docs/monitoring_guide.md) を参照してください。

### 5.1 rqt_graph - ノードとトピックの可視化
```bash
# システム全体の通信構造を視覚的に確認
ros2 run rqt_graph rqt_graph
```

### 5.2 ros2 topic - トピックの監視
```bash
# 利用可能なトピック一覧
ros2 topic list

# 特定トピックの内容をリアルタイム表示
ros2 topic echo /speech_recognition
ros2 topic echo /dialogue_response
ros2 topic echo /speech_synthesis

# トピックの周波数確認
ros2 topic hz /audio_input
```

### 5.3 ros2 bag - データの記録と再生
```bash
# すべてのトピックを記録
ros2 bag record -a

# 特定のトピックのみ記録
ros2 bag record /speech_recognition /dialogue_response

# 記録したデータの情報確認
ros2 bag info <bag_file>

# 記録したデータの再生
ros2 bag play <bag_file>
```

### 5.4 rqt_plot - データの可視化
```bash
# 音声レベルなどの数値データをグラフ表示
ros2 run rqt_plot rqt_plot
```

### 5.5 その他の便利なコマンド
```bash
# ノード一覧
ros2 node list

# ノード情報
ros2 node info /speech_recognition_node

# サービス一覧
ros2 service list

# パラメータ一覧
ros2 param list
```


## 6. トラブルシューティング

### 6.1 サウンドデバイス（USBヘッドセット）が認識されない場合
```bash
# カーネルモジュールの更新
sudo apt update
sudo apt upgrade linux-generic

# 再起動後、デバイスを確認
pactl list short sources
pactl list short sinks
```

### 6.2 デフォルトサウンドデバイスの固定

#### 自動設定（推奨）
```bash
# 音声デバイス設定スクリプトを使用
cd ~/DiaROS
python3 scripts/set_default_mic.py
```

このスクリプトは以下を実行します：
- 利用可能な音声入力デバイスを一覧表示
- デバイスを選択してテスト可能
- DiaROS用の設定を保存
- 設定済みデバイスで起動するスクリプトを作成

#### 手動設定
```bash
# 入力デバイス一覧確認
pactl list short sources

# デフォルトデバイスの設定
pactl set-default-source <device_name>

# ~/.bashrcに追加して永続化
echo "pactl set-default-source <device_name>" >> ~/.bashrc

# またはDiaROS用に環境変数を設定
export AUDIO_DEVICE_INDEX=<device_number>
```

### 6.3 ALSA関連のエラーメッセージを抑制
Unknown PCM cardsなどのエラーが表示される場合：
```bash
# /usr/share/alsa/alsa.conf の不要な設定をコメントアウト
sudo nano /usr/share/alsa/alsa.conf
# cards.pcm.rear, cards.pcm.center_lfe などの行をコメントアウト
```

### 6.4 Python GTTSでのエラー対処
```bash
# No module named 'gi' エラーの場合
sudo apt install libcairo2-dev libgirepository1.0-dev
pip install pycairo PyGObject
```

### 6.5 ROS2関連のトラブル
```bash
# 環境変数の確認
printenv | grep ROS

# ワークスペースのクリーンビルド
cd ~/DiaROS/DiaROS_ros
rm -rf build/ install/ log/
colcon build
```


## 7. 開発者向け情報

### 7.1 プロジェクト構造
```
DiaROS/
├── DiaROS_py/          # Python音声対話システムモジュール
├── DiaROS_ros/         # ROS2パッケージ
│   ├── interfaces/     # メッセージ型定義
│   └── diaros_package/ # メインパッケージ
└── docs/               # ドキュメント
```

### 7.2 主要なROSトピック
- `/audio_input`: マイクからの音声入力
- `/speech_recognition`: 音声認識結果
- `/dialogue_response`: 対話システムの応答
- `/speech_synthesis`: 音声合成結果
- `/audio_output`: スピーカーへの音声出力

### 7.3 ディープラーニングモデル
システムは高度な音声処理のためにディープラーニングモデルを使用しています：
- **音声認識**: Hugging Face japanese-HuBERT-base-VADLess-ASRモデル
- **言語生成**: rinna/japanese-gpt2-smallによる自然な応答生成
- **音声合成**: VOICEVOXによる高品質な日本語音声
- 最適なパフォーマンスのためGPU推奨（CUDA対応）

### 7.4 音声デバイス管理
DiaROSには音声デバイスを管理するツールが含まれています：
- **scripts/set_default_mic.py**: インタラクティブなデバイス設定ツール
  - 利用可能な音声入力デバイスを一覧表示
  - デバイスの機能をテスト
  - デバイス設定を保存
  - 事前設定済みデバイスで起動するスクリプトを作成
- **scripts/test_audio_simple.py**: 簡易音声テストスクリプト
  - PyAudioのデバイス検出を確認
  - リアルタイムで音声レベルを表示
- **自動デバイス検出**: Docker環境ではPulseAudioデバイスを優先
- **環境変数**: `AUDIO_DEVICE_INDEX`でデバイスを指定可能


## 8. ライセンスと謝辞
本システムは研究目的で開発されています．
各種APIの利用規約に従ってご使用ください．

### 使用している主要なライブラリ・API
- ROS2 Humble
- Hugging Face Transformers（ローカル音声認識・言語生成）
- VOICEVOX（日本語音声合成）
- PyAudio
- その他多数のオープンソースライブラリ


## 9. macOSネイティブ実行（Apple Silicon GPU活用）

### 9.1 概要
Apple Silicon Mac（M1/M2/M3）では、Metal Performance Shaders（MPS）を使用してGPUアクセラレーションが可能です。Docker環境ではMPSが使用できないため、最高のパフォーマンスを得るにはネイティブ実行を推奨します。

**詳細なセットアップガイド**: 📖 [docs/macos_native_setup.md](docs/macos_native_setup.md) を参照してください。

### 9.2 クイックセットアップ（Pixiを使用）

#### 必要なツールのインストール
```bash
# Xcodeコマンドラインツール
xcode-select --install

# Homebrew（まだの場合）
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zshrc
source ~/.zshrc
```

#### Pixiを使ったROS2環境のセットアップ（推奨）

##### 1. Pixiのインストールとプロジェクト作成
```bash
# Pixiのインストール
curl -fsSL https://pixi.sh/install.sh | bash
source ~/.zshrc  # または ~/.bashrc

# プロジェクトディレクトリの作成
mkdir -p ~/DiaROS_pixi && cd ~/DiaROS_pixi

# Pixiプロジェクトの初期化（Python 3.9を使用）
pixi init diaros_workspace -c robostack-humble -c conda-forge
cd diaros_workspace
```

##### 2. ROS2 Humbleとツールのインストール
```bash
# Python 3.9を最初に追加（重要）
pixi add python=3.9

# ROS2 Humbleのインストール
pixi add ros-humble-desktop colcon-common-extensions pip

# ビルドツールの追加
pixi add cython setuptools-scm
```

##### 3. DiaROSのクローン
```bash
cd ~/DiaROS_pixi
git clone https://github.com/sayonari/DiaROS_imamoto.git
```

##### 4. Pixi環境でのPythonパッケージインストール
```bash
# Pixi環境に入る
cd ~/DiaROS_pixi/diaros_workspace
pixi shell

# 基本パッケージのインストール
pip install numpy==1.24.3  # NumPy 1.xに固定（重要）
pip install torch torchvision torchaudio
pip install transformers huggingface-hub
pip install pyaudio sounddevice librosa scipy
pip install matplotlib requests pyyaml webrtcvad pyworld soundfile

# aubioのインストール（macOSでのビルドエラー対策）
brew install aubio  # Homebrewでライブラリをインストール
export PKG_CONFIG_PATH="/opt/homebrew/lib/pkgconfig:$PKG_CONFIG_PATH"
export CFLAGS="-Wno-error=incompatible-function-pointer-types"
export LDFLAGS="-L/opt/homebrew/lib"  
export CPPFLAGS="-I/opt/homebrew/include"
pip install aubio --no-cache-dir

# 追加の必須パッケージ
pip install playsound pydub PyObjC

# インストール確認
python -c "import torch; print(f'MPS available: {torch.backends.mps.is_available()}')"
pip list | grep -E "aubio|pyaudio|torch|transformers|playsound|pydub"
```

**詳細**: 📖 [docs/macos_pixi_ros2_setup.md](docs/macos_pixi_ros2_setup.md)

#### DiaROSのビルドと起動（Pixi環境）

##### 5. ROS2パッケージのビルド
```bash
# Pixi環境でDiaROSディレクトリに移動
cd ~/DiaROS_pixi/DiaROS_imamoto/DiaROS_ros

# 環境変数の設定（重要）
export Python3_ROOT_DIR=$CONDA_PREFIX
export Python3_EXECUTABLE=$CONDA_PREFIX/bin/python
export Python3_INCLUDE_DIR=$CONDA_PREFIX/include/python3.9
export Python3_LIBRARY=$CONDA_PREFIX/lib/libpython3.9.dylib
export Python3_NumPy_INCLUDE_DIR=$(python -c "import numpy; print(numpy.get_include())")

# interfacesパッケージのビルド
colcon build \
  --cmake-args \
  -DCMAKE_C_FLAGS=-fPIC \
  -DPython3_FIND_STRATEGY=LOCATION \
  -DPython3_ROOT_DIR=$CONDA_PREFIX \
  --packages-select interfaces

# 環境変数の設定（DiaROSパッケージ用）
export ROS_DISTRO=humble
export ROS_VERSION=2
export ROS_PYTHON_VERSION=3
export AMENT_PREFIX_PATH=$PWD/install/interfaces:$CONDA_PREFIX
export CMAKE_PREFIX_PATH=$PWD/install/interfaces:$CONDA_PREFIX
export PYTHONPATH=$PWD/install/interfaces/lib/python3.9/site-packages:$PYTHONPATH

# DiaROSパッケージのビルド
colcon build --packages-select diaros_package
```

##### 6. DiaROS Pythonモジュールのインストール
```bash
# DiaROS_pyディレクトリに移動
cd ../DiaROS_py

# pyproject.tomlのPythonバージョン要件を確認（3.9以上であること）
# 必要に応じて編集: requires-python = ">=3.9"

# インストール
pip install -e .

# インストール確認
python -c "import diaros; print('DiaROS module imported successfully')"
```

##### 7. VOICEVOXの起動（別ターミナル）
```bash
# VOICEVOXをダウンロード
cd ~/Downloads
curl -L https://github.com/VOICEVOX/voicevox_engine/releases/download/0.14.0/macos-x64.zip -o voicevox.zip
unzip voicevox.zip
cd macos-x64
./run
```

##### 7.5. HuggingFaceトークンの設定（必要な場合）
一部のモデルへのアクセスにはトークンが必要です：
```bash
# HuggingFace CLIでログイン
pip install huggingface-cli
huggingface-cli login

# または環境変数で設定
export HF_TOKEN=your_token_here
```

##### 8. DiaROSの起動
```bash
# DiaROSディレクトリに移動
cd ~/DiaROS_pixi/DiaROS_imamoto/DiaROS_ros

# 環境変数の設定
export DIAROS_DEVICE=mps  # Apple Silicon GPUを使用
export AMENT_PREFIX_PATH=$PWD/install/diaros_package:$PWD/install/interfaces:$AMENT_PREFIX_PATH
export PYTHONPATH=$PWD/install/diaros_package/lib/python3.9/site-packages:$PWD/install/interfaces/lib/python3.9/site-packages:$PYTHONPATH

# 動的ライブラリパスの設定（必要な場合）
export DYLD_LIBRARY_PATH=$PWD/install/interfaces/lib:$DYLD_LIBRARY_PATH

# power_calibration.wavファイルのコピー（初回のみ）
cp ../DiaROS_py/diaros/power_calibration.wav .

# DiaROSの起動
ros2 launch diaros_package sdsmod.launch.py
```

### 9.3 パフォーマンス比較

| 環境 | デバイス | 音声認識 | 言語生成 | ターンテイキング |
|------|----------|---------|---------|---------------|
| Docker | CPU (8コア) | ~500ms | ~1000ms | ~200ms |
| Native | MPS (GPU) | ~50ms | ~100ms | ~20ms |
| Native | CPU | ~300ms | ~800ms | ~150ms |

**結果**: MPSを使用することで、**最大10倍の高速化**を実現！

### 9.4 環境変数とデバイス選択

```bash
# MPSを優先的に使用（推奨）
export DIAROS_DEVICE=mps

# CPUに固定する場合
export DIAROS_DEVICE=cpu

# 自動選択（デフォルト）
unset DIAROS_DEVICE
```

デバイスの優先順位：
1. 環境変数`DIAROS_DEVICE`の指定
2. MPS（Apple Silicon GPU）
3. CUDA（NVIDIA GPU）
4. CPU

### 9.5 トラブルシューティング

#### PyAudioエラー
```bash
brew reinstall portaudio
pip uninstall pyaudio && pip install pyaudio
```

#### aubioビルドエラー
「incompatible function pointer types」エラーが出る場合：
```bash
# Homebrewでaubioライブラリをインストール
brew install aubio

# コンパイラフラグを設定
export PKG_CONFIG_PATH="/opt/homebrew/lib/pkgconfig:$PKG_CONFIG_PATH"
export CFLAGS="-Wno-error=incompatible-function-pointer-types"
export LDFLAGS="-L/opt/homebrew/lib"
export CPPFLAGS="-I/opt/homebrew/include"

# aubioをインストール
pip install aubio --no-cache-dir
```

詳細: [docs/macos_aubio_build_fix.md](docs/macos_aubio_build_fix.md)

#### ROS2パッケージが見つからない
「Package 'diaros_package' not found」エラーが出る場合：
```bash
# 環境変数を正しく設定
export AMENT_PREFIX_PATH=$PWD/install/diaros_package:$PWD/install/interfaces:$AMENT_PREFIX_PATH
export ROS_DISTRO=humble
export ROS_VERSION=2

# パッケージの確認
ros2 pkg list | grep diaros
```

#### Pythonバージョンの不一致
CMakeがPython 3.12を見つける場合：
```bash
# Pixi環境のPython 3.9を明示的に指定
export Python3_EXECUTABLE=$CONDA_PREFIX/bin/python
export Python3_ROOT_DIR=$CONDA_PREFIX
```

#### MPSエラー
```bash
# フォールバックを有効化
export PYTORCH_ENABLE_MPS_FALLBACK=1
```

#### 動的ライブラリロードエラー
「Library not loaded: @rpath/libinterfaces__rosidl_generator_py.dylib」エラーが出る場合：
```bash
# 動的ライブラリパスを設定
export DYLD_LIBRARY_PATH=$PWD/install/interfaces/lib:$DYLD_LIBRARY_PATH
```

#### マイク権限
システム設定 → プライバシーとセキュリティ → マイク → ターミナルを許可

### 9.6 必要なモデルへのアクセス

HuggingFaceの制限付きモデルを使用するため：
1. https://huggingface.co/ でアカウント作成
2. 以下のモデルページでライセンスに同意：
   - [japanese-HuBERT-base-VADLess-ASR-RSm](https://huggingface.co/SiRoZaRuPa/japanese-HuBERT-base-VADLess-ASR-RSm)
3. アクセストークンを設定：
   ```bash
   huggingface-cli login
   # または
   export HF_TOKEN=your_token_here
   ```

## 10. 付録：外部APIの使用（オプション）

DiaROSは現在、外部APIなしで完全にローカルで動作しますが、より高い精度を求める場合はクラウドベースのサービスを使用することも可能です：

### 10.1 Google Speech-to-Text API（音声認識）
1. Google Cloud Consoleでプロジェクトを作成
2. Speech-to-Text APIを有効化
3. サービスアカウントキーを作成（JSON形式）
4. 詳細手順: https://cloud.google.com/speech-to-text/docs/before-you-begin?hl=ja
5. 環境変数を設定:
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS="$HOME/secret/google_stt_key.json"
   ```

### 10.2 OpenAI API（応答生成）
1. https://platform.openai.com/ でアカウント作成
2. APIキーを作成
3. 環境変数を設定:
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```
4. `naturalLanguageGeneration.py`で`self.use_local_model = False`に変更

### 10.3 A3RT Talk API（代替応答生成）
1. APIキーを取得: https://a3rt.recruit.co.jp/product/talkAPI/
2. APIキーをテキストファイルに保存
3. 環境変数を設定:
   ```bash
   export A3RT_APIKEY="$HOME/secret/a3rt_api_key.txt"
   ```
   注：現在の実装ではOpenAI APIまたはローカルモデルが使用されています

### 10.4 ROS2なしでの実行（実験的）
ROS2を使わずにDiaROSの基本機能を試すこともできます。ただし、この方法では一部の機能が制限されます：
- モジュール間の通信監視ができない
- システムの記録・再生機能が使えない
- デバッグが困難

詳細は [docs/macos_quick_start.md](docs/macos_quick_start.md) を参照してください。