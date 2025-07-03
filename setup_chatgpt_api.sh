#!/bin/bash
# ChatGPT API設定スクリプト
# DiaROS音声対話システム用OpenAI API設定

echo "============================================================"
echo "🤖 DiaROS ChatGPT API 設定"
echo "============================================================"

# APIキーの確認
if [ -n "$OPENAI_API_KEY" ]; then
    echo "✅ OpenAI API キーが既に設定されています"
    echo "   現在のAPIキー: ${OPENAI_API_KEY:0:15}..."
    echo ""
    read -p "新しいAPIキーを設定しますか？ (y/N): " replace_key
    if [[ ! "$replace_key" =~ ^[Yy]$ ]]; then
        echo "🎯 既存の設定を使用します"
        exit 0
    fi
fi

echo ""
echo "📋 OpenAI API キー設定手順："
echo "1. https://platform.openai.com/api-keys にアクセス"
echo "2. ログインまたはアカウント作成"
echo "3. 「Create new secret key」をクリック"
echo "4. 生成されたAPIキーをコピー（sk-proj-で始まる文字列）"
echo ""

read -p "OpenAI API キーを入力してください: " api_key

# APIキーの形式確認
if [[ ! "$api_key" =~ ^sk- ]]; then
    echo "❌ 無効なAPIキー形式です。APIキーは 'sk-' で始まります"
    exit 1
fi

# 環境変数設定
export OPENAI_API_KEY="$api_key"

# 永続化設定の確認
echo ""
echo "🔧 環境変数の永続化設定:"
echo ""

# macOSのシェル判定
if [[ "$SHELL" == *"zsh"* ]]; then
    PROFILE_FILE="$HOME/.zshrc"
    echo "zsh シェルを検出しました"
elif [[ "$SHELL" == *"bash"* ]]; then
    PROFILE_FILE="$HOME/.bash_profile"
    echo "bash シェルを検出しました"
else
    echo "⚠️  シェルを自動検出できませんでした"
    read -p "使用しているシェルを入力してください (zsh/bash): " shell_type
    if [[ "$shell_type" == "zsh" ]]; then
        PROFILE_FILE="$HOME/.zshrc"
    else
        PROFILE_FILE="$HOME/.bash_profile"
    fi
fi

echo "設定ファイル: $PROFILE_FILE"

# 既存設定の確認
if grep -q "OPENAI_API_KEY" "$PROFILE_FILE" 2>/dev/null; then
    echo "⚠️  既存のOPENAI_API_KEY設定が見つかりました"
    read -p "既存設定を更新しますか？ (y/N): " update_existing
    if [[ "$update_existing" =~ ^[Yy]$ ]]; then
        # 既存行を削除
        grep -v "OPENAI_API_KEY" "$PROFILE_FILE" > "${PROFILE_FILE}.tmp" && mv "${PROFILE_FILE}.tmp" "$PROFILE_FILE"
        echo "export OPENAI_API_KEY=\"$api_key\"" >> "$PROFILE_FILE"
        echo "✅ 既存設定を更新しました"
    fi
else
    echo "export OPENAI_API_KEY=\"$api_key\"" >> "$PROFILE_FILE"
    echo "✅ 新規設定を追加しました"
fi

echo ""
echo "🧪 API接続テスト実行中..."

# API接続テスト
python3 -c "
import openai
import os
openai.api_key = os.environ.get('OPENAI_API_KEY')
try:
    response = openai.chat.completions.create(
        model='gpt-3.5-turbo',
        messages=[
            {'role': 'system', 'content': 'テスト用の短い応答をしてください。'},
            {'role': 'user', 'content': 'こんにちは'}
        ],
        max_tokens=20
    )
    print(f'✅ API接続成功: {response.choices[0].message.content}')
except Exception as e:
    print(f'❌ API接続失敗: {e}')
    print('APIキーを確認してください')
"

echo ""
echo "============================================================"
echo "📖 DiaROS での ChatGPT API 使用方法"
echo "============================================================"
echo ""
echo "1. 現在のセッションで使用する場合:"
echo "   export OPENAI_API_KEY=\"$api_key\""
echo ""
echo "2. 新しいターミナルで設定を反映する場合:"
echo "   source $PROFILE_FILE"
echo ""
echo "3. DiaROS起動方法:"
echo "   cd /Users/sayonari/_data/_DiaROS_mac/DiaROS_pixi/DiaROS_imamoto"
echo "   ./scripts/launch_diaros.sh"
echo ""
echo "4. APIキー確認方法:"
echo "   echo \$OPENAI_API_KEY"
echo ""
echo "============================================================"
echo "🎯 重要事項"
echo "============================================================"
echo ""
echo "• APIキーは絶対に他人と共有しないでください"
echo "• GitHub等の公開リポジトリにコミットしないでください"
echo "• 使用量に応じて料金が発生します"
echo "• 会話1回あたり約0.001-0.01ドル程度です"
echo ""
echo "✅ ChatGPT API設定が完了しました！"
echo "これでDiaROSが動的な音声応答を生成できます。"