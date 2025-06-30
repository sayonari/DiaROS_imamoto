#!/bin/bash

# DiaROS macOS起動スクリプト（2回目以降の起動用）
# このスクリプトはPixi環境でDiaROSを簡単に起動するためのものです

set -e

echo "==================================="
echo "DiaROS macOS 起動スクリプト"
echo "==================================="

# 設定
PIXI_WORKSPACE_DIR="$HOME/DiaROS_pixi/diaros_workspace"
DIAROS_DIR="$HOME/DiaROS_pixi/DiaROS_imamoto/DiaROS_ros"

# Pixi環境の確認
if [ ! -d "$PIXI_WORKSPACE_DIR" ]; then
    echo "エラー: Pixiワークスペースが見つかりません: $PIXI_WORKSPACE_DIR"
    echo "README.mdの手順に従ってセットアップを完了してください。"
    exit 1
fi

# DiaROSディレクトリの確認
if [ ! -d "$DIAROS_DIR" ]; then
    echo "エラー: DiaROSディレクトリが見つかりません: $DIAROS_DIR"
    echo "README.mdの手順に従ってセットアップを完了してください。"
    exit 1
fi

# VOICEVOXの起動確認
echo ""
echo "VOICEVOXの状態を確認中..."
if curl -s http://localhost:50021/version > /dev/null 2>&1; then
    echo "✅ VOICEVOXは既に起動しています"
else
    echo "❌ VOICEVOXが起動していません"
    echo ""
    echo "VOICEVOXを自動起動しますか？ [Y/n]"
    read -r answer
    
    if [[ "$answer" != "n" && "$answer" != "N" ]]; then
        VOICEVOX_DIR="$HOME/Downloads/macos-x64"
        if [ -d "$VOICEVOX_DIR" ]; then
            echo "VOICEVOXを起動中..."
            cd "$VOICEVOX_DIR"
            ./run &
            VOICEVOX_PID=$!
            
            # 起動待機
            echo -n "VOICEVOXの起動を待機中"
            for i in {1..30}; do
                if curl -s http://localhost:50021/version > /dev/null 2>&1; then
                    echo ""
                    echo "✅ VOICEVOXが起動しました"
                    break
                fi
                echo -n "."
                sleep 1
            done
            
            if ! curl -s http://localhost:50021/version > /dev/null 2>&1; then
                echo ""
                echo "エラー: VOICEVOXの起動に失敗しました"
                exit 1
            fi
        else
            echo "エラー: VOICEVOXが見つかりません: $VOICEVOX_DIR"
            echo "README.mdの手順に従ってVOICEVOXをダウンロードしてください。"
            exit 1
        fi
    else
        echo "VOICEVOXを手動で起動してから、このスクリプトを再実行してください。"
        echo "  cd ~/Downloads/macos-x64 && ./run"
        exit 1
    fi
fi

# Pixi環境でDiaROSを起動
echo "Pixi環境でDiaROSを起動中..."
cd "$PIXI_WORKSPACE_DIR"

# Pixi shellコマンドでDiaROSを起動
pixi shell << 'EOF'
# DiaROSディレクトリに移動
cd ~/DiaROS_pixi/DiaROS_imamoto/DiaROS_ros

# 環境変数の設定
export DIAROS_DEVICE=mps  # Apple Silicon GPUを使用
export AMENT_PREFIX_PATH=$PWD/install/diaros_package:$PWD/install/interfaces:$AMENT_PREFIX_PATH
export PYTHONPATH=$PWD/install/diaros_package/lib/python3.9/site-packages:$PWD/install/interfaces/lib/python3.9/site-packages:$PYTHONPATH
export DYLD_LIBRARY_PATH=$PWD/install/interfaces/lib:$DYLD_LIBRARY_PATH

# DiaROSの起動
echo "DiaROSを起動しています..."
ros2 launch diaros_package sdsmod.launch.py
EOF