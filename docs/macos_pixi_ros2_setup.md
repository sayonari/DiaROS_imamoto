# M1/M2/M3 MacでPixiを使ったROS2 Humbleセットアップガイド

## 概要
Pixiは、Condaエコシステムに基づいたパッケージ管理ツールで、macOSやWindowsでもROS2を簡単にインストールできます。
このガイドでは、Apple Silicon Mac（M1/M2/M3）でPixiを使ってROS2 Humbleをセットアップし、DiaROSを動作させる方法を説明します。

## Pixiの特徴
- **プラットフォーム独立**: Ubuntu以外でもROS2を利用可能
- **環境分離**: 複数のROSバージョンを共存可能
- **依存関係管理**: C++コンパイラまで含めた完全な環境構築

## セットアップ手順

### 1. Pixiのインストール

```bash
# Pixiのインストール（公式インストーラー）
curl -fsSL https://pixi.sh/install.sh | bash

# シェルの再読み込み
source ~/.bashrc  # bashの場合
# または
source ~/.zshrc   # zshの場合

# インストール確認
pixi --version
```

### 2. ROS2プロジェクトの作成

```bash
# DiaROS用のPixiプロジェクトを作成
mkdir -p ~/DiaROS_pixi
cd ~/DiaROS_pixi

# RoboStackチャンネルを使用してプロジェクトを初期化
pixi init diaros_workspace -c robostack-humble -c conda-forge
cd diaros_workspace
```

### 3. ROS2 Humbleのインストール

```bash
# Python 3.9を最初に追加（ROS2 Humbleの要件）
pixi add python=3.9

# ROS2 Humble Desktopパッケージをインストール
# （初回は時間がかかります）
pixi add ros-humble-desktop

# 開発ツールを追加
pixi add colcon-common-extensions "setuptools<=58.2.0"

# C++開発環境（必要な場合）
pixi add ros-humble-ament-cmake-auto compilers pkg-config cmake ninja

# pipを追加
pixi add pip
```

### 4. ROS2動作確認

```bash
# 新しいターミナルで
cd ~/DiaROS_pixi/diaros_workspace

# ターミナル1: Talker
pixi run ros2 run demo_nodes_cpp talker

# ターミナル2: Listener
pixi run ros2 run demo_nodes_cpp listener

# GUI確認（turtlesim）
pixi run ros2 run turtlesim turtlesim_node
```

### 5. DiaROSのセットアップ

```bash
# DiaROSをクローン
cd ~/DiaROS_pixi
git clone https://github.com/sayonari/DiaROS_imamoto.git
cd DiaROS_imamoto

# Pixi環境内でPythonパッケージをインストール
cd ~/DiaROS_pixi/diaros_workspace
pixi shell  # Pixi環境に入る

# 必要なPythonパッケージをインストール
pip install torch torchvision torchaudio
pip install transformers huggingface-hub
pip install numpy==1.24.3 scipy librosa soundfile

# aubioのインストール（macOSでコンパイルエラーが出る場合）
# Homebrewでaubioライブラリをインストール
brew install aubio
export PKG_CONFIG_PATH="/opt/homebrew/lib/pkgconfig:$PKG_CONFIG_PATH"

# コンパイラフラグを設定してaubioをインストール
export CFLAGS="-Wno-error=incompatible-function-pointer-types"
export LDFLAGS="-L/opt/homebrew/lib"
export CPPFLAGS="-I/opt/homebrew/include"
pip install aubio --no-cache-dir

# その他のパッケージ
pip install pyaudio sounddevice webrtcvad pyworld
pip install matplotlib requests pyyaml
```

### 6. DiaROS ROS2パッケージのビルド

```bash
# Pixi環境内で実行
cd ~/DiaROS_pixi/DiaROS_imamoto/DiaROS_ros

# ビルド
colcon build --cmake-args -DCMAKE_C_FLAGS=-fPIC --packages-select interfaces
source ./install/local_setup.bash
colcon build --packages-select diaros_package
source ./install/local_setup.bash

# Pythonモジュールのインストール
cd ../DiaROS_py
pip install -e .
```

### 7. 環境変数の設定

```bash
# Pixi環境内で
export DIAROS_DEVICE=mps  # Apple Silicon GPUを使用
export OMP_NUM_THREADS=8
export TORCH_NUM_THREADS=8
```

### 8. VOICEVOXの起動（別ターミナル）

```bash
# VOICEVOXをダウンロード（まだの場合）
cd ~/Downloads
curl -L https://github.com/VOICEVOX/voicevox_engine/releases/download/0.14.0/macos-x64.zip -o voicevox.zip
unzip voicevox.zip
cd macos-x64
./run
```

### 9. DiaROSの起動

```bash
# Pixi環境内で
cd ~/DiaROS_pixi/DiaROS_imamoto
pixi shell

# ROS2環境の設定
source DiaROS_ros/install/local_setup.bash

# DiaROSを起動
ros2 launch diaros_package sdsmod.launch.py
```

## Pixiコマンドリファレンス

```bash
# 環境に入る
pixi shell

# コマンドを実行
pixi run <command>

# パッケージを追加
pixi add <package>

# パッケージを削除
pixi remove <package>

# 環境情報を表示
pixi info

# プロジェクトをクリーン
pixi clean
```

## トラブルシューティング

### PyAudioエラー
```bash
# Pixi環境内で
pixi add portaudio
pip uninstall pyaudio
pip install pyaudio
```

### aubioビルドエラー（incompatible function pointer types）
```bash
# Homebrewでaubioライブラリをインストール
brew install aubio

# 環境変数を設定
export PKG_CONFIG_PATH="/opt/homebrew/lib/pkgconfig:$PKG_CONFIG_PATH"
export CFLAGS="-Wno-error=incompatible-function-pointer-types"
export LDFLAGS="-L/opt/homebrew/lib"
export CPPFLAGS="-I/opt/homebrew/include"

# aubioをインストール
pip install aubio --no-cache-dir
```

### MPSエラー
```bash
export PYTORCH_ENABLE_MPS_FALLBACK=1
```

### colconが見つからない
```bash
pixi add python-colcon-common-extensions
```

### ROS2コマンドが見つからない
```bash
# 必ずPixi環境内で実行
pixi shell
# または
pixi run ros2 <command>
```

## 利点と制限

### 利点
- ✅ macOSネイティブでROS2が動作
- ✅ 環境の分離が完全
- ✅ 依存関係の管理が簡単
- ✅ 複数バージョンの共存が可能

### 制限
- ⚠️ すべてのROS2パッケージが利用可能ではない
- ⚠️ ハードウェアドライバーは限定的
- ⚠️ Pixi環境内での実行が必要

## まとめ

PixiとRoboStackを使用することで、M1/M2/M3 MacでもROS2 Humbleを簡単にセットアップできます。
DiaROSも問題なく動作し、MPSによるGPUアクセラレーションも利用可能です。