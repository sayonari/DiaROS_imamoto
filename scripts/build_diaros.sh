#!/bin/bash
# build_diaros.sh - DiaROSパッケージのビルドスクリプト
# 
# このスクリプトは、DiaROSパッケージをビルドし、
# 新しい起動ファイル（sdsmod_quiet.launch.py）を含めて更新します。

# スクリプトのディレクトリを取得
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
SCRIPT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "=== DiaROS Builder ==="
echo "🔨 DiaROSパッケージをビルドします"
echo ""

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
    
    echo "🔧 Pixi環境でビルドを実行します..."
    echo ""
    
    # Pixi環境内で実行するための一時スクリプトを作成
    TEMP_SCRIPT=$(mktemp)
    cat > "$TEMP_SCRIPT" << EOF
#!/bin/bash
set -e  # エラーで停止

# 環境変数の設定
export DIAROS_DEVICE=mps
export Python3_ROOT_DIR=\$CONDA_PREFIX
export Python3_EXECUTABLE=\$CONDA_PREFIX/bin/python
export Python3_INCLUDE_DIR=\$CONDA_PREFIX/include/python3.9
export Python3_LIBRARY=\$CONDA_PREFIX/lib/libpython3.9.dylib

# DiaROSディレクトリに移動
cd "$SCRIPT_ROOT/DiaROS_ros"

echo "📂 現在のディレクトリ: \$(pwd)"
echo ""

# 既存のビルドをクリーン（オプション）
if [ "\$1" == "clean" ]; then
    echo "🧹 既存のビルドをクリーンアップしています..."
    rm -rf build install log
    echo "✅ クリーンアップ完了"
    echo ""
fi

# インターフェースのビルド
echo "1️⃣ インターフェースをビルドしています..."
colcon build --cmake-args -DCMAKE_C_FLAGS=-fPIC -DPython3_FIND_STRATEGY=LOCATION --packages-select interfaces
if [ \$? -ne 0 ]; then
    echo "❌ インターフェースのビルドに失敗しました"
    exit 1
fi
source ./install/local_setup.bash

# DiaROSパッケージのビルド
echo ""
echo "2️⃣ DiaROSパッケージをビルドしています..."
colcon build --packages-select diaros_package
if [ \$? -ne 0 ]; then
    echo "❌ DiaROSパッケージのビルドに失敗しました"
    exit 1
fi
source ./install/local_setup.bash

# ビルド結果の確認
echo ""
echo "3️⃣ ビルド結果を確認しています..."
if [ -f "install/diaros_package/share/diaros_package/sdsmod.launch.py" ]; then
    echo "✅ sdsmod.launch.py: OK"
else
    echo "❌ sdsmod.launch.py: 見つかりません"
fi

if [ -f "install/diaros_package/share/diaros_package/sdsmod_quiet.launch.py" ]; then
    echo "✅ sdsmod_quiet.launch.py: OK"
else
    echo "⚠️  sdsmod_quiet.launch.py: 見つかりません (新規ファイル)"
fi

# Pythonモジュールのインストール
echo ""
echo "4️⃣ Pythonモジュールをインストールしています..."
cd "$SCRIPT_ROOT/DiaROS_py"
pip install -e . --quiet
if [ \$? -eq 0 ]; then
    echo "✅ Pythonモジュールのインストール完了"
else
    echo "❌ Pythonモジュールのインストールに失敗しました"
    exit 1
fi

echo ""
echo "🎉 ビルドが完了しました！"
echo ""
echo "次のコマンドでDiaROSを起動できます："
echo "  通常版: ./scripts/launch/launch_diaros.sh"
echo "  静音版: ./scripts/launch/launch_diaros_quiet.sh"
EOF
    
    chmod +x "$TEMP_SCRIPT"
    
    # Pixi環境で実行
    cd "$PIXI_DIR"
    pixi run bash "$TEMP_SCRIPT" "$@"
    
    # 一時ファイルを削除
    rm -f "$TEMP_SCRIPT"
    
else
    # Linuxの場合
    echo "🐧 Linux環境でビルドを実行します..."
    echo ""
    
    # ROS2環境の設定
    if [ -f "/opt/ros/humble/setup.bash" ]; then
        source /opt/ros/humble/setup.bash
    else
        echo "❌ ROS2 Humbleが見つかりません"
        exit 1
    fi
    
    # DiaROSディレクトリに移動
    cd "$SCRIPT_ROOT/DiaROS_ros"
    
    # 既存のビルドをクリーン（オプション）
    if [ "$1" == "clean" ]; then
        echo "🧹 既存のビルドをクリーンアップしています..."
        rm -rf build install log
        echo "✅ クリーンアップ完了"
        echo ""
    fi
    
    # インターフェースのビルド
    echo "1️⃣ インターフェースをビルドしています..."
    colcon build --cmake-args -DCMAKE_C_FLAGS=-fPIC --packages-select interfaces
    source ./install/local_setup.bash
    
    # DiaROSパッケージのビルド
    echo ""
    echo "2️⃣ DiaROSパッケージをビルドしています..."
    colcon build --packages-select diaros_package
    source ./install/local_setup.bash
    
    # Pythonモジュールのインストール
    echo ""
    echo "3️⃣ Pythonモジュールをインストールしています..."
    cd "$SCRIPT_ROOT/DiaROS_py"
    pip install -e . --user --quiet
    
    echo ""
    echo "🎉 ビルドが完了しました！"
fi