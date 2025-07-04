#!/bin/bash
# launch_diaros_quiet.sh - rcutilsエラーを抑制した起動スクリプト
# 
# このスクリプトは、rcutilsのtruncatedエラーメッセージを抑制して
# DiaROSを起動します。

# スクリプトのディレクトリを取得
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
SCRIPT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "=== DiaROS quiet launcher ==="
echo "🔇 rcutilsエラーメッセージを抑制してDiaROSを起動します"
echo ""

# 環境変数を設定してrcutilsエラーを抑制
export RCUTILS_LOGGING_SEVERITY_THRESHOLD='ERROR'
export RCUTILS_COLORIZED_OUTPUT='0'
export RCUTILS_CONSOLE_OUTPUT_FORMAT='[{severity}] [{name}]: {message}'
export ROS_LOG_DIR='/tmp/ros_logs'

# OS検出
OS_TYPE=$(uname -s)

if [[ "$OS_TYPE" == "Darwin" ]]; then
    # macOSの場合、Pixi環境で実行
    # 相対パスでdiaros_workspaceを探す
    PARENT_DIR="$(cd "$SCRIPT_ROOT/.." && pwd)"
    PIXI_DIR="$PARENT_DIR/diaros_workspace"
    
    if [ ! -d "$PIXI_DIR" ]; then
        echo "❌ Pixi環境が見つかりません: $PIXI_DIR"
        echo "📍 現在のディレクトリ: $SCRIPT_ROOT"
        exit 1
    fi
    
    echo "🔧 Pixi環境でDiaROSを起動します..."
    echo "🔇 rcutilsエラー抑制: 有効"
    echo ""
    
    # Pixi環境内で実行するための一時スクリプトを作成
    TEMP_SCRIPT=$(mktemp)
    cat > "$TEMP_SCRIPT" << EOF
#!/bin/bash
set -x  # デバッグ出力を有効化

# 環境変数を再設定（Pixi環境内でも確実に設定）
export RCUTILS_LOGGING_SEVERITY_THRESHOLD='ERROR'
export RCUTILS_COLORIZED_OUTPUT='0'
export RCUTILS_CONSOLE_OUTPUT_FORMAT='[{severity}] [{name}]: {message}'
export ROS_LOG_DIR='/tmp/ros_logs'

# DiaROSディレクトリに移動
cd "$SCRIPT_ROOT/DiaROS_ros"

# 環境変数の設定
export DIAROS_DEVICE=mps
export AMENT_PREFIX_PATH="$SCRIPT_ROOT/DiaROS_ros/install/diaros_package:$SCRIPT_ROOT/DiaROS_ros/install/interfaces:\$AMENT_PREFIX_PATH"
export PYTHONPATH="$SCRIPT_ROOT/DiaROS_ros/install/diaros_package/lib/python3.9/site-packages:$SCRIPT_ROOT/DiaROS_ros/install/interfaces/lib/python3.9/site-packages:\$PYTHONPATH"

# macOSでのライブラリパス設定
export DYLD_LIBRARY_PATH="$SCRIPT_ROOT/DiaROS_ros/install/interfaces/lib:\$DYLD_LIBRARY_PATH"

echo "Environment variables set:"
echo "  DIAROS_DEVICE=\$DIAROS_DEVICE"
echo "  RCUTILS_LOGGING_SEVERITY_THRESHOLD=\$RCUTILS_LOGGING_SEVERITY_THRESHOLD"

# ROS2起動（sdsmod_quiet.launch.pyを使用）
exec ros2 launch diaros_package sdsmod_quiet.launch.py
EOF
    
    chmod +x "$TEMP_SCRIPT"
    
    # Pixi環境で実行
    cd "$PIXI_DIR"
    pixi run bash "$TEMP_SCRIPT"
    
    # 一時ファイルを削除
    rm -f "$TEMP_SCRIPT"
    
else
    # Linuxの場合
    echo "🐧 Linux環境でDiaROSを起動します..."
    echo "🔇 rcutilsエラー抑制: 有効"
    echo ""
    
    # ROS2環境の設定
    if [ -f "/opt/ros/humble/setup.bash" ]; then
        source /opt/ros/humble/setup.bash
    else
        echo "❌ ROS2 Humbleが見つかりません"
        exit 1
    fi
    
    # DiaROSパッケージの設定
    DIAROS_ROS_DIR="$SCRIPT_ROOT/DiaROS_ros"
    if [ -f "$DIAROS_ROS_DIR/install/local_setup.bash" ]; then
        source "$DIAROS_ROS_DIR/install/local_setup.bash"
    fi
    
    # DiaROSディレクトリに移動
    cd "$DIAROS_ROS_DIR"
    
    # ROS2起動（sdsmod_quiet.launch.pyを使用）
    exec ros2 launch diaros_package sdsmod_quiet.launch.py
fi