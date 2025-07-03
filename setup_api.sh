#!/bin/bash
# DiaROS API設定スクリプト
# 高速応答生成のためのAPI設定

echo "=================================="
echo "DiaROS 高速応答API設定"
echo "=================================="
echo ""

echo "現在の設定状況:"
if [ -n "$OPENAI_API_KEY" ]; then
    echo "✅ OpenAI API: 設定済み"
else
    echo "❌ OpenAI API: 未設定"
fi

if [ -n "$ANTHROPIC_API_KEY" ]; then
    echo "✅ Claude API: 設定済み"
else
    echo "❌ Claude API: 未設定"
fi

echo ""
echo "選択してください:"
echo "1. OpenAI API設定 (ChatGPT)"
echo "2. Claude API設定 (Anthropic)"
echo "3. APIキー確認"
echo "4. 終了"
echo ""
echo -n "選択 [1-4]: "
read choice

case $choice in
    1)
        echo ""
        echo "OpenAI APIキーを設定します"
        echo "OpenAI APIキーを入力してください:"
        echo -n "sk-....: "
        read -s openai_key
        echo ""
        
        # 環境変数設定
        export OPENAI_API_KEY="$openai_key"
        
        # ~/.bashrcまたは~/.zshrcに追加
        if [ -f ~/.zshrc ]; then
            echo "export OPENAI_API_KEY=\"$openai_key\"" >> ~/.zshrc
            echo "✅ ~/.zshrcに設定を追加しました"
        elif [ -f ~/.bashrc ]; then
            echo "export OPENAI_API_KEY=\"$openai_key\"" >> ~/.bashrc
            echo "✅ ~/.bashrcに設定を追加しました"
        fi
        
        echo "設定完了。新しいターミナルで有効になります。"
        echo "現在のセッションでも使用する場合は以下を実行:"
        echo "export OPENAI_API_KEY=\"$openai_key\""
        ;;
    2)
        echo ""
        echo "Claude API (Anthropic)設定"
        echo "Anthropic APIキーを入力してください:"
        echo -n "sk-ant-....: "
        read -s anthropic_key
        echo ""
        
        # 環境変数設定
        export ANTHROPIC_API_KEY="$anthropic_key"
        
        # ~/.bashrcまたは~/.zshrcに追加
        if [ -f ~/.zshrc ]; then
            echo "export ANTHROPIC_API_KEY=\"$anthropic_key\"" >> ~/.zshrc
            echo "✅ ~/.zshrcに設定を追加しました"
        elif [ -f ~/.bashrc ]; then
            echo "export ANTHROPIC_API_KEY=\"$anthropic_key\"" >> ~/.bashrc
            echo "✅ ~/.bashrcに設定を追加しました"
        fi
        
        echo "設定完了。新しいターミナルで有効になります。"
        echo "現在のセッションでも使用する場合は以下を実行:"
        echo "export ANTHROPIC_API_KEY=\"$anthropic_key\""
        ;;
    3)
        echo ""
        echo "現在のAPIキー設定:"
        if [ -n "$OPENAI_API_KEY" ]; then
            echo "OpenAI API: ${OPENAI_API_KEY:0:8}...${OPENAI_API_KEY: -4}"
        else
            echo "OpenAI API: 未設定"
        fi
        
        if [ -n "$ANTHROPIC_API_KEY" ]; then
            echo "Claude API: ${ANTHROPIC_API_KEY:0:8}...${ANTHROPIC_API_KEY: -4}"
        else
            echo "Claude API: 未設定"
        fi
        ;;
    4)
        echo "終了します"
        exit 0
        ;;
    *)
        echo "無効な選択です"
        ;;
esac

echo ""
echo "=================================="
echo "高速応答設定説明:"
echo "=================================="
echo "• OpenAI API使用時: ~500-1000ms"
echo "• ローカルモデル使用時: ~2000-5000ms"
echo "• 対話破綻防止: 1500ms以内推奨"
echo ""
echo "DiaROS起動時に自動的に最適なAPIが選択されます。"