# DiaROS デバッグ・開発ツールガイド

このドキュメントでは、DiaROSプロジェクトで利用可能なデバッグツールと開発支援スクリプトについて説明します。

## 📋 目次

- [環境設定ツール](#環境設定ツール)
- [起動スクリプト](#起動スクリプト)
- [デバッグ・監視ツール](#デバッグ監視ツール)
- [テストツール](#テストツール)
- [ユーティリティツール](#ユーティリティツール)

---

## 環境設定ツール

### 🔧 ROS2環境設定
- **`scripts/setup/setup_ros2_env.sh`**
  - ROS2環境を一発で設定するスクリプト
  - macOS/Linux自動判別、Pixi環境対応
  ```bash
  source scripts/setup/setup_ros2_env.sh
  # 環境確認
  check_ros2_env
  ```

### 🔑 API設定
- **`scripts/setup/setup_chatgpt_api.sh`**
  - OpenAI APIキーの対話型設定スクリプト
  ```bash
  ./scripts/setup/setup_chatgpt_api.sh
  ```

### 📦 Pixi/ROS2セットアップ
- **`scripts/setup/setup_pixi_ros2.sh`**
  - Pixi環境でROS2 Humbleをセットアップ
  - macOS用の環境構築スクリプト

### 🐳 Docker音声設定
- **`scripts/setup/docker_audio_setup.sh`**
  - Docker環境での音声デバイス設定
  - PulseAudioの設定を自動化

---

## 起動スクリプト

### 🚀 メイン起動スクリプト
- **`scripts/launch/launch_diaros.sh`**
  - DiaROSの統合起動スクリプト
  - VOICEVOX自動起動、環境設定込み
  ```bash
  ./scripts/launch/launch_diaros.sh
  ```

### ⚡ クイックスタート
- **`scripts/launch/pixi_diaros_quick_start.sh`**
  - Pixi環境でのクイックスタート
  - 初回セットアップチェック付き

### 🏃 標準起動
- **`scripts/launch/start_diaros.sh`**
  - 基本的なDiaROS起動スクリプト
  - Docker環境向け

---

## デバッグ・監視ツール

### 🐛 対話フローデバッガー
- **`scripts/debug/debug_diaros_flow.py`**
  - リアルタイムで対話フローを監視
  - 各モジュール間の通信を可視化
  ```bash
  ./scripts/debug/debug_diaros_flow.sh  # 環境設定付き実行
  ```

  **機能：**
  - 音声入力、認識、応答生成の流れを追跡
  - 各モジュールの状態をリアルタイム表示
  - 重要イベントの即時通知

### 📊 統合モニタリング
- **`scripts/debug/monitor.sh`**
  - DiaROS専用の包括的モニタリングツール
  - Docker/ネイティブ環境両対応
  ```bash
  ./scripts/debug/monitor.sh
  ```

  **提供機能：**
  - ROS2基本ツール（rqt、rqt_graph等）
  - 対話フロー監視
  - パフォーマンス測定
  - システムリソース監視

---

## テストツール

### 🧪 応答テスト
- **`scripts/test/test_diaros_response.py`**
  - DiaROSシステムの応答フローをテスト
  - ノード起動状態、トピック通信を検証
  ```bash
  ./scripts/test/test_diaros_response.sh  # 環境設定付き実行
  ```

### 🎤 音声テスト
- **`scripts/test/test_audio_simple.py`**
  - 簡易音声入力テスト
  - PyAudioデバイス検出と音声レベル表示
  ```bash
  python3 scripts/test/test_audio_simple.py
  ```

- **`scripts/test/test_pyaudio_pulse.py`**
  - PulseAudio環境での音声テスト
  - Docker環境向け

---

## ユーティリティツール

### 🎙️ マイク設定
- **`scripts/utils/set_default_mic.py`**
  - インタラクティブな音声デバイス設定
  - デバイステストと設定保存
  ```bash
  python3 scripts/utils/set_default_mic.py
  ```

### 🍎 macOSネイティブ実行
- **`scripts/utils/run_diaros_native_macos.py`**
  - macOS環境でのネイティブ実行
  - Apple Silicon GPU (MPS) 活用

### 🛠️ ROS2ツール実行
- **`scripts/utils/run_ros2_tool.sh`**
  - 任意のROS2コマンドを環境設定付きで実行
  ```bash
  ./scripts/utils/run_ros2_tool.sh ros2 topic list
  ./scripts/utils/run_ros2_tool.sh python3 my_script.py
  ```

---

## 使用例

### 1. 初回セットアップ
```bash
# Pixi環境のセットアップ（macOS）
./scripts/setup/setup_pixi_ros2.sh

# APIキーの設定
./scripts/setup/setup_chatgpt_api.sh

# ROS2環境の確認
source scripts/setup/setup_ros2_env.sh
check_ros2_env
```

### 2. DiaROSの起動とデバッグ
```bash
# DiaROSを起動
./scripts/launch/launch_diaros.sh

# 別ターミナルでフローを監視
./scripts/debug/debug_diaros_flow.sh

# システム全体のモニタリング
./scripts/debug/monitor.sh
```

### 3. テストの実行
```bash
# 音声デバイスのテスト
python3 scripts/test/test_audio_simple.py

# システム応答のテスト
./scripts/test/test_diaros_response.sh
```

---

## トラブルシューティング

### ROS2コマンドが見つからない
```bash
source scripts/setup/setup_ros2_env.sh
```

### Pythonモジュールが見つからない
```bash
# 環境変数の確認
check_ros2_env

# または汎用実行ツールを使用
./scripts/utils/run_ros2_tool.sh python3 your_script.py
```

### 音声デバイスの問題
```bash
# デバイス設定ツールを使用
python3 scripts/utils/set_default_mic.py
```

---

詳細な情報は各スクリプトのヘッダーコメントを参照してください。