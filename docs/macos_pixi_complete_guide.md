# macOS (Apple Silicon) でのDiaROS完全セットアップガイド (Pixi版)

このガイドでは、M1/M2/M3 MacでPixiを使用してDiaROSを動作させるまでの全手順を記載します。

## 前提条件

- macOS 12+ (Monterey以降)
- Apple Silicon Mac (M1/M2/M3)
- 16GB以上のメモリ推奨
- 20GB以上の空き容量

## セットアップ手順

### 1. 基本ツールのインストール

```bash
# Xcodeコマンドラインツールのインストール
xcode-select --install

# Homebrewのインストール（まだの場合）
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# パスの設定（Apple Silicon Mac）
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zshrc
source ~/.zshrc

# 必要なツールのインストール
brew install portaudio ffmpeg
```

### 2. Pixiのインストールとプロジェクト作成

```bash
# Pixiのインストール
curl -fsSL https://pixi.sh/install.sh | bash
source ~/.zshrc  # または ~/.bashrc

# プロジェクトディレクトリの作成
mkdir -p ~/DiaROS_pixi && cd ~/DiaROS_pixi

# Pixiプロジェクトの初期化（RoboStackチャンネルを使用）
pixi init diaros_workspace -c robostack-humble -c conda-forge
cd diaros_workspace
```

### 3. ROS2 Humbleと開発ツールのインストール

```bash
# Python 3.9を最初に追加（重要：ROS2 HumbleはPython 3.9を要求）
pixi add python=3.9

# ROS2 Humbleのインストール（時間がかかります）
pixi add ros-humble-desktop colcon-common-extensions pip

# ビルドツールの追加
pixi add cython setuptools-scm
```

### 4. DiaROSのクローン

```bash
cd ~/DiaROS_pixi
git clone https://github.com/sayonari/DiaROS_imamoto.git
```

### 5. Pythonパッケージのインストール

```bash
# Pixi環境に入る
cd ~/DiaROS_pixi/diaros_workspace
pixi shell

# NumPyを1.xに固定（aubioとの互換性のため）
pip install numpy==1.24.3

# PyTorchと深層学習関連
pip install torch torchvision torchaudio
pip install transformers huggingface-hub

# 音声処理関連
pip install pyaudio sounddevice librosa scipy
pip install matplotlib requests pyyaml webrtcvad pyworld soundfile
```

### 6. aubioのインストール（特別な手順が必要）

macOSでaubioをビルドする際、コンパイラエラーが発生する場合があります：

```bash
# Homebrewでaubioライブラリをインストール
brew install aubio

# 環境変数の設定
export PKG_CONFIG_PATH="/opt/homebrew/lib/pkgconfig:$PKG_CONFIG_PATH"
export CFLAGS="-Wno-error=incompatible-function-pointer-types"
export LDFLAGS="-L/opt/homebrew/lib"
export CPPFLAGS="-I/opt/homebrew/include"

# aubioのPythonバインディングをインストール
pip install aubio --no-cache-dir

# インストール確認
python -c "import aubio; print(f'aubio version: {aubio.version}')"
```

### 7. ROS2パッケージのビルド

#### 7.1 interfacesパッケージのビルド

```bash
# DiaROS_rosディレクトリに移動
cd ~/DiaROS_pixi/DiaROS_imamoto/DiaROS_ros

# Python環境変数の設定（CMakeがPython 3.9を見つけられるように）
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
```

#### 7.2 DiaROSパッケージのビルド

```bash
# ROS2環境変数の設定
export ROS_DISTRO=humble
export ROS_VERSION=2
export ROS_PYTHON_VERSION=3
export AMENT_PREFIX_PATH=$PWD/install/interfaces:$CONDA_PREFIX
export CMAKE_PREFIX_PATH=$PWD/install/interfaces:$CONDA_PREFIX
export PYTHONPATH=$PWD/install/interfaces/lib/python3.9/site-packages:$PYTHONPATH

# DiaROSパッケージのビルド
colcon build --packages-select diaros_package
```

### 8. DiaROS Pythonモジュールのインストール

```bash
# DiaROS_pyディレクトリに移動
cd ../DiaROS_py

# Pythonバージョン要件の確認（pyproject.tomlでrequires-python = ">=3.9"であること）
# 必要に応じて編集

# インストール
pip install -e .

# インストール確認
python -c "import diaros; print('DiaROS module imported successfully')"
```

### 9. VOICEVOXの起動（別ターミナル）

```bash
# VOICEVOXをダウンロード
cd ~/Downloads
curl -L https://github.com/VOICEVOX/voicevox_engine/releases/download/0.14.0/macos-x64.zip -o voicevox.zip
unzip voicevox.zip

# 実行権限を付与
chmod +x macos-x64/run

# VOICEVOXを起動
cd macos-x64
./run
```

### 10. HuggingFaceトークンの設定（必要な場合）

一部のモデルアクセスにトークンが必要です：

```bash
# HuggingFace CLIでログイン
pip install huggingface-cli
huggingface-cli login

# または環境変数で設定
export HF_TOKEN=your_token_here
```

### 11. DiaROSの起動

```bash
# DiaROS_rosディレクトリに移動
cd ~/DiaROS_pixi/DiaROS_imamoto/DiaROS_ros

# 環境変数の設定
export DIAROS_DEVICE=mps  # Apple Silicon GPUを使用
export AMENT_PREFIX_PATH=$PWD/install/diaros_package:$PWD/install/interfaces:$AMENT_PREFIX_PATH
export PYTHONPATH=$PWD/install/diaros_package/lib/python3.9/site-packages:$PWD/install/interfaces/lib/python3.9/site-packages:$PYTHONPATH

# DiaROSの起動
ros2 launch diaros_package sdsmod.launch.py
```

## トラブルシューティング

### よくあるエラーと対処法

#### 1. "Package 'diaros_package' not found"
```bash
# AMENT_PREFIX_PATHが正しく設定されているか確認
echo $AMENT_PREFIX_PATH

# パッケージリストを確認
ros2 pkg list | grep diaros
```

#### 2. CMakeがPython 3.12を見つける
```bash
# Python 3.9を明示的に指定
export Python3_EXECUTABLE=$CONDA_PREFIX/bin/python
which python  # /Users/.../pixi/envs/default/bin/python を確認
```

#### 3. aubioビルドエラー
詳細は [macos_aubio_build_fix.md](macos_aubio_build_fix.md) を参照

#### 4. 音声デバイスが見つからない
```bash
# 利用可能なデバイスを確認
python -c "
import pyaudio
p = pyaudio.PyAudio()
for i in range(p.get_device_count()):
    info = p.get_device_info_by_index(i)
    if info['maxInputChannels'] > 0:
        print(f'{i}: {info[\"name\"]}')
"
```

#### 5. マイクアクセス権限
システム設定 → プライバシーとセキュリティ → マイク → ターミナルを許可

## 動作確認

以下のメッセージが表示されれば成功です：
- "MPS available: True" （GPU認識）
- "All DiaROS modules imported successfully"
- "Found X audio devices"
- VOICEVOXが起動している
- ros2 launchコマンドでノードが起動する

## パフォーマンス最適化

- `export DIAROS_DEVICE=mps` でApple Silicon GPUを使用
- `export OMP_NUM_THREADS=8` でCPUスレッド数を調整
- Docker環境と比較して最大10倍の高速化が可能

## 次のステップ

1. 音声認識のテスト
2. 対話システムのカスタマイズ
3. 新しい対話シナリオの追加
4. ログの確認と分析

## 参考資料

- [Pixi公式ドキュメント](https://pixi.sh/)
- [RoboStack](https://robostack.github.io/)
- [DiaROSリポジトリ](https://github.com/sayonari/DiaROS_imamoto)