# DiaROS改善チェックリスト

## 実装済み改善項目

### 1. 音声再生の修正
- ✅ DialogManagement.pyに詳細なログ出力を追加
- ✅ afplayコマンドの実行結果を確認
- ✅ 相槌ファイルのパスを修正（DiaROS_ros/static_back_channel_*.wav）
- ✅ 静的応答ファイルのパスを修正（DiaROS_ros/static_response_source/）

### 2. ログ出力の最適化
- ✅ ros2_speech_synthesis.pyの重複メッセージを削減
- ✅ "publish filename"メッセージが変更時のみ出力されるよう修正

### 3. Google Gemma 2Bモデルの統合
- ✅ naturalLanguageGeneration.pyにGemmaモデルサポートを追加
- ✅ Gemma専用のプロンプトフォーマットを実装
- ✅ HuggingFaceトークン認証のサポート
- ✅ launch_diaros_local.shのデフォルトモデルをGemmaに変更
- ✅ Gemmaモデル用の生成パラメータ最適化

## テスト手順

### 1. HuggingFaceトークンの設定
```bash
# HuggingFaceにログイン（Gemmaモデルアクセスのため）
huggingface-cli login

# または環境変数で設定
export HF_TOKEN=your_huggingface_token
```

### 2. VOICEVOXの起動
```bash
# macOS
open -a "/Users/sayonari/_data/tools/VOICEVOX/VOICEVOX.app"
```

### 3. DiaROSの起動
```bash
# ローカルLLMモード（Gemma 2B）で起動
./scripts/launch/launch_diaros_local.sh
```

### 4. 動作確認ポイント
- [ ] 音声認識が正常に動作
- [ ] 200msポーズ検出で応答生成トリガー
- [ ] Gemmaモデルによる日本語応答生成
- [ ] VOICEVOXによる音声合成
- [ ] afplayによる音声再生
- [ ] 相槌機能の動作

### 5. 期待される改善
- 応答生成速度: ~100-300ms（Gemma 2B、GPU使用時）
- 応答品質: rinna-smallより大幅に向上
- 音声再生: 正常に動作

## トラブルシューティング

### Gemmaモデルが読み込めない場合
1. HuggingFaceトークンが設定されているか確認
2. インターネット接続を確認
3. 十分なメモリ（4GB以上）があるか確認

### 音声が再生されない場合
1. VOICEVOXが起動しているか確認
2. /tmp/ディレクトリの音声ファイルを確認
3. afplayコマンドが使用可能か確認

### 応答が遅い場合
1. GPUが使用されているか確認（MPSまたはCUDA）
2. より軽量なモデル（rinna-small）にフォールバック