# rcutilsエラーメッセージ調査レポート

## 問題の概要
ROS2ノード実行時に以下のエラーメッセージが出力される：
```
rcutils|error_handling.c:65] an error string (message, file name, or formatted message) will be truncated
```

## 影響を受けるノード
- ros2_speech_input
- ros2_acoustic_analysis
- ros2_natural_language_understanding
- ros2_dialog_management
- ros2_automatic_speech_recognition
- ros2_back_channel
- ros2_turn_taking
- ros2_speech_synthesis

## 原因
ROS2のrcutilsライブラリは、エラーメッセージが256文字を超えると自動的に切り詰めます。この警告は以下の場合に発生します：

1. **長いファイルパス**: 深いディレクトリ構造（例：`/Users/sayonari/_data/_DiaROS_mac/DiaROS_pixi/DiaROS_imamoto/...`）
2. **詳細なエラーメッセージ**: Pythonのトレースバックや例外メッセージ
3. **ログメッセージ**: デバッグ情報を含む長いログ出力

## 既存の対策
各ノードの`main()`関数で以下の環境変数を設定済み：
```python
os.environ['RCUTILS_LOGGING_SEVERITY_THRESHOLD'] = 'ERROR'
os.environ['RCUTILS_COLORIZED_OUTPUT'] = '0'
```

しかし、これらの設定は完全にはエラーを抑制できていません。

## 解決策

### 1. 起動ファイルでの環境変数設定（推奨）
新しい起動ファイル `sdsmod_quiet.launch.py` を作成しました：
```python
from launch.actions import SetEnvironmentVariable

env_vars = [
    SetEnvironmentVariable('RCUTILS_LOGGING_SEVERITY_THRESHOLD', 'ERROR'),
    SetEnvironmentVariable('RCUTILS_COLORIZED_OUTPUT', '0'),
    SetEnvironmentVariable('RCUTILS_CONSOLE_OUTPUT_FORMAT', '[{severity}] [{name}]: {message}')
]
```

使用方法：
```bash
ros2 launch diaros_package sdsmod_quiet.launch.py
```

### 2. 起動スクリプトでの環境変数設定
新しい起動スクリプト `launch_diaros_quiet.sh` を作成しました：
```bash
export RCUTILS_LOGGING_SEVERITY_THRESHOLD=ERROR
export RCUTILS_COLORIZED_OUTPUT=0
export RCUTILS_CONSOLE_OUTPUT_FORMAT='[{severity}] [{name}]: {message}'
export RCUTILS_LOGGING_MAX_MESSAGE_LENGTH=255
```

使用方法：
```bash
./scripts/launch/launch_diaros_quiet.sh
```

### 3. 根本的な対策（今後の改善案）
1. **ファイルパスの短縮**: シンボリックリンクを使用して短いパスを作成
2. **エラーメッセージの簡潔化**: 例外処理で簡潔なメッセージを使用
3. **ログレベルの調整**: 本番環境ではDEBUGログを無効化

## 影響
このエラーは警告メッセージであり、システムの動作には影響しません。ただし、ログが見づらくなるため、上記の対策を実施することを推奨します。

## 参考情報
- rcutilsのデフォルトメッセージ長制限: 256文字
- ROS2 Humbleでの既知の問題
- 長いパスを使用するプロジェクトで頻繁に発生