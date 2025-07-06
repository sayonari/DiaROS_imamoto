# DiaROS改善内容まとめ（2025年7月5日）

## 実装した改善内容

### 1. プロンプトの改善
- 音声対話システムに適したプロンプトに変更
- リアルタイム対話向けの役割設定と対話例を追加
- 短く楽しい応答を生成するよう指示

### 2. 対話履歴管理の実装
- 過去の発話を保持して文脈を考慮した応答生成が可能に
- デフォルトで6発話（ユーザ3発話＋システム3発話）を保持
- 環境変数`DIAROS_MAX_DIALOGUE_HISTORY`で設定可能

### 3. 後処理の改善
- 不要なプレフィックス（"システム："等）の自動除去
- 括弧内の内容（システムの思考）を除去
- 句読点の重複を修正
- 30文字以内への適切な調整
- 短すぎる応答のフォールバック処理

### 4. Gemma 2モデル対応
- 正しいモデル名に修正：
  - `google/gemma-2-2b-it`（2Bパラメータ、高速）
  - `google/gemma-2-9b-it`（9Bパラメータ、高品質）
- チャットテンプレートを使用した適切なプロンプト形式

## 使用方法

### 基本的な起動（Gemma 2使用）
```bash
./scripts/launch/launch_diaros_local.sh
```

### rinna-neoxを使用する場合
```bash
export DIAROS_LLM_MODEL=rinna-neox
./scripts/launch/launch_diaros_local.sh
```

### 対話履歴数の変更
```bash
export DIAROS_MAX_DIALOGUE_HISTORY=10  # 10発話まで保持
./scripts/launch/launch_diaros_local.sh
```

## Gemma 2使用時の注意点

1. **HuggingFaceへのログインが必要**
   ```bash
   huggingface-cli login
   ```

2. **必要なVRAM**
   - gemma-2-2b: 約5GB
   - gemma-2-9b: 約18GB

3. **初回実行時はモデルのダウンロードに時間がかかります**

## 期待される改善効果

1. **応答品質の向上**
   - 文脈を考慮した自然な応答
   - 対話の流れに沿った返答
   - 不自然な文字列の削除

2. **対話の継続性**
   - 前の話題を覚えている
   - 一貫性のある対話

3. **Gemma 2使用時**
   - より高品質な日本語応答
   - 多様な表現力

## パフォーマンス監視

実行時のログで以下を確認してください：
- `[NLG] 応答時間: XXXms` - 目標は500ms以下
- `[NLG DEBUG] 対話履歴数: X` - 履歴が正しく管理されているか
- `[NLG LOCAL DEBUG]` - プロンプトと生成結果の詳細