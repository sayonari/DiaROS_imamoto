# DiaROS 高速日本語LLMガイド

## 概要
DiaROSのnaturalLanguageGenerationモジュールが、高速な日本語LLMモデルをサポートしました。
応答時間500ms以内を目標として、複数の軽量モデルから選択可能です。

## 対応モデル

### 1. rinna/japanese-gpt2-small（デフォルト・推奨）
- **サイズ**: 約100MB
- **応答時間**: 50-200ms（GPU）、200-400ms（CPU）
- **特徴**: 最速・最軽量、基本的な対話に十分
- **設定**: `export DIAROS_LLM_MODEL=rinna-small`

### 2. rinna/japanese-gpt-neox-small
- **サイズ**: 約560MB
- **応答時間**: 200-400ms（GPU）、400-800ms（CPU）
- **特徴**: より自然な応答、高品質
- **設定**: `export DIAROS_LLM_MODEL=rinna-neox`

### 3. cyberagent/open-calm-small
- **サイズ**: 約400MB
- **応答時間**: 150-350ms（GPU）、350-700ms（CPU）
- **特徴**: バランス型、安定した品質
- **設定**: `export DIAROS_LLM_MODEL=calm-small`

### 4. line-corporation/japanese-large-lm-1.7b
- **サイズ**: 約3.4GB
- **応答時間**: 400-800ms（GPU）、800-2000ms（CPU）
- **特徴**: 最高品質、メモリ消費大
- **設定**: `export DIAROS_LLM_MODEL=line-small`

## 使用方法

### 1. モデル選択
```bash
# 最速モデルを使用（推奨）
export DIAROS_LLM_MODEL=rinna-small

# 高品質モデルを使用
export DIAROS_LLM_MODEL=rinna-neox

# APIキーが設定されていない場合、自動的にローカルモデルを使用
unset OPENAI_API_KEY
```

### 2. デバイス設定
```bash
# Apple Silicon Mac（MPS使用）
export DIAROS_DEVICE=mps

# NVIDIA GPU（CUDA使用）
export DIAROS_DEVICE=cuda

# CPU使用（自動選択）
export DIAROS_DEVICE=cpu
```

### 3. DiaROS起動
```bash
# 通常の起動
./scripts/launch_diaros.sh

# または個別起動
ros2 launch diaros_package sdsmod.launch.py
```

## パフォーマンステスト

同梱のテストスクリプトで各モデルの性能を確認できます：

```bash
# モデル性能テスト
python3 scripts/test_fast_llm.py
```

テスト結果例：
```
テスト結果サマリー
============================================================
1. rinna-small: 150ms ✓
2. calm-small: 280ms ✓
3. rinna-neox: 350ms ✓

推奨設定:
export DIAROS_LLM_MODEL=rinna-small
（最速: 150ms）
```

## 最適化のポイント

### 1. モデル選択
- **リアルタイム対話**: `rinna-small`（最速）
- **品質重視**: `rinna-neox`または`calm-small`
- **研究用途**: `line-small`（最高品質）

### 2. ハードウェア最適化
- **Apple Silicon Mac**: MPSを使用（`export DIAROS_DEVICE=mps`）
- **NVIDIA GPU**: CUDA + float16で高速化
- **CPU**: スレッド数を調整（`export OMP_NUM_THREADS=4`）

### 3. 応答長さ調整
モデルは自動的に15-30文字程度の短い応答を生成するよう最適化されています。

### 4. 初回起動の高速化
- 初回起動時にモデルのダウンロードが発生します（数分程度）
- 2回目以降はキャッシュから高速ロード
- ウォームアップ処理により、初回応答も高速化

## トラブルシューティング

### モデルロードエラー
```bash
# Hugging Faceログイン（制限付きモデルの場合）
huggingface-cli login

# キャッシュクリア
rm -rf ~/.cache/huggingface/
```

### メモリ不足
```bash
# より軽量なモデルを使用
export DIAROS_LLM_MODEL=rinna-small

# またはAPI使用に切り替え
export OPENAI_API_KEY="your-key"
```

### 応答が遅い場合
1. より軽量なモデルに切り替え
2. GPUを使用（可能な場合）
3. API使用を検討（ChatGPT/Claude）

## API使用との比較

| 方式 | 応答時間 | コスト | オフライン | 品質 |
|------|----------|--------|-----------|------|
| ローカルLLM | 50-500ms | 無料 | ✓ | 中 |
| ChatGPT API | 200-800ms | 有料 | ✗ | 高 |
| Claude API | 300-1000ms | 有料 | ✗ | 高 |

## まとめ

- **速度優先**: `DIAROS_LLM_MODEL=rinna-small`を使用
- **品質優先**: API使用（`OPENAI_API_KEY`設定）
- **オフライン**: ローカルモデルを選択
- **バランス**: `rinna-neox`または`calm-small`

対話システムの要求に応じて、最適な設定を選択してください。