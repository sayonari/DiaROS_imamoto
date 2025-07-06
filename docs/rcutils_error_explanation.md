# rcutilsのtruncatedエラーについて

## エラーメッセージ
```
[rcutils|error_handling.c:65] an error string (message, file name, or formatted message) will be truncated
```

## 原因
このエラーは、ROS2のrcutilsライブラリがエラーメッセージを出力する際に、メッセージが256文字の制限を超えているために発生します。

主な原因：
1. **長いファイルパス**: プロジェクトが深いディレクトリ構造にある
   - 例: `/Users/sayonari/_data/_DiaROS_mac/DiaROS_pixi/DiaROS_imamoto/...`
2. **ROS2のrcutilsの制限**: エラーメッセージバッファが256文字に制限されている

## 影響
- **システムへの影響**: なし（警告メッセージのみ）
- **ログの視認性**: 多数のtruncatedメッセージでログが見づらくなる

## 対策

### 1. 新しい起動ファイルを使用（推奨）
```bash
# rcutilsエラーを抑制した起動スクリプト
./scripts/launch/launch_diaros_quiet.sh
```

### 2. 既存の起動ファイルのビルド
新しい起動ファイル（sdsmod_quiet.launch.py）を使用するには、まずビルドが必要です：
```bash
cd ~/_data/_DiaROS_mac/DiaROS_pixi/DiaROS_imamoto/DiaROS_ros
colcon build --packages-select diaros_package
source ./install/local_setup.bash
```

### 3. 環境変数による対策
起動前に以下の環境変数を設定：
```bash
export RCUTILS_LOGGING_SEVERITY_THRESHOLD='ERROR'
export RCUTILS_COLORIZED_OUTPUT='0'
export ROS_LOG_DIR='/tmp/ros_logs'
```

## 根本的な解決策（将来的な改善案）
1. **プロジェクトを浅いディレクトリに配置**
   - 例: `/home/user/DiaROS/` など
2. **ROS2のrcutilsライブラリの改修**
   - バッファサイズを拡張（ROS2コミュニティへの提案）

## 注意事項
- このエラーは**システムの動作に影響しません**
- 単なる警告メッセージであり、無視しても問題ありません
- 対策により、ログの可読性が向上します