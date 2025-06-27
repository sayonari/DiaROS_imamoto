# DiaROS
**[English ver is HERE](README.md)**

## Author
西村良太 徳島大学  
nishimura@is.tokushima-u.ac.jp

## Developer
- 西村 良太 (Ryota Nishimura)
- 森 貴大 (Takahiro Mori) https://bitbucket.org/takahiro_mori_win/

## Demo video
[<img width="300" alt="youtube" src="https://user-images.githubusercontent.com/16011609/199163853-a00c3d9b-b4ea-483f-8d22-d1affb59dcd9.png">
](https://www.youtube.com/watch?v=2EkJCJpSpS4)

## 概要
リアルタイム音声対話システムをROS2対応にさせたものです．システム自体の構成は単純で，中身も単純ですが，その分，音声対話システムのROS対応の方法が理解できると思います．基本的には，python実装された音声対話システムの各モジュール間の通信をROSでラップした構成になっています．この構成にすることで，通信内容をROSで監視することが可能となり，通信内容の確認，記録，再生が可能となるため，システム開発・デバッグの効率が格段に上がります．

## 注意事項
- まだバグが含まれています．バグ取り段階です．

## ブランチについて
- `main`: 標準ブランチ
- `deep_model`: ディープラーニングベースの音声認識・合成モデルを使用する実験的ブランチ
  - 高精度な音声認識が可能
  - より自然な音声合成を実現
  - GPU推奨（CPUでも動作可能）


# システムインストール方法
以下にシステムのインストール方法を記載します．

## 0. システム要件
- OS: Ubuntu 22.04 LTS
- Python: 3.10.x（Ubuntu 22.04のデフォルト）
- ROS2: Humble Hawksbill


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

# 音声対話システムの実行
ros2 launch diaros_package sdsmod.launch.py
```

### 4.2 システムの停止
`Ctrl+C` で終了します．


## 5. ROS2モニタリングツールの活用

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
```bash
# 入力デバイス一覧確認
pactl list short sources

# デフォルトデバイスの設定
pactl set-default-source <device_name>

# ~/.bashrcに追加して永続化
echo "pactl set-default-source <device_name>" >> ~/.bashrc
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

### 7.3 deep_modelブランチの特徴
実験的な機能として、ディープラーニングモデルを使用した高度な音声処理が可能：
- Whisper（OpenAI）による高精度音声認識
- BERT/GPTベースの対話モデル
- WaveNetやTacotron2による自然な音声合成
- GPUを推奨（CUDA対応）

使用方法：
```bash
git checkout deep_model
# 追加の依存関係をインストール
pip install -r requirements_deep.txt
```


## 8. ライセンスと謝辞
本システムは研究目的で開発されています．
各種APIの利用規約に従ってご使用ください．

### 使用している主要なライブラリ・API
- ROS2 Humble
- Hugging Face Transformers（ローカル音声認識・言語生成）
- VOICEVOX（日本語音声合成）
- PyAudio
- その他多数のオープンソースライブラリ


## 9. 付録：外部APIの使用（オプション）

DiaROSは現在、外部APIなしで完全にローカルで動作しますが、より高い精度を求める場合はクラウドベースのサービスを使用することも可能です：

### 9.1 Google Speech-to-Text API（音声認識）
1. Google Cloud Consoleでプロジェクトを作成
2. Speech-to-Text APIを有効化
3. サービスアカウントキーを作成（JSON形式）
4. 詳細手順: https://cloud.google.com/speech-to-text/docs/before-you-begin?hl=ja
5. 環境変数を設定:
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS="$HOME/secret/google_stt_key.json"
   ```

### 9.2 OpenAI API（応答生成）
1. https://platform.openai.com/ でアカウント作成
2. APIキーを作成
3. 環境変数を設定:
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```
4. `naturalLanguageGeneration.py`で`self.use_local_model = False`に変更

### 9.3 A3RT Talk API（代替応答生成）
1. APIキーを取得: https://a3rt.recruit.co.jp/product/talkAPI/
2. APIキーをテキストファイルに保存
3. 環境変数を設定:
   ```bash
   export A3RT_APIKEY="$HOME/secret/a3rt_api_key.txt"
   ```
   注：現在の実装ではOpenAI APIまたはローカルモデルが使用されています