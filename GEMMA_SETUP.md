# Gemma 2モデルセットアップガイド

DiaROSでGemma 2モデル（google/gemma-2-2b-it）を使用するための設定手順です。

## 前提条件
- Pixi環境がセットアップ済み
- インターネット接続（5GBのモデルダウンロード）
- HuggingFaceアカウント

## セットアップ手順

### 1. Pixi環境に入る
```bash
cd ~/_data/_DiaROS_mac/DiaROS_pixi/diaros_workspace
pixi shell
```

### 2. HuggingFace認証状態を確認
```bash
../DiaROS_imamoto/scripts/setup/check_hf_auth.sh
```

### 3. Gemma 2へのアクセス許可を取得
1. 以下のURLにアクセス：
   https://huggingface.co/google/gemma-2-2b-it
2. HuggingFaceアカウントでログイン
3. 「Agree and access repository」ボタンをクリック

### 4. HuggingFace CLIでログイン
```bash
huggingface-cli login
```
ブラウザに表示されるトークンをコピーして貼り付け

### 5. モデルをダウンロード
```bash
python3 ../DiaROS_imamoto/scripts/setup/download_gemma_model.py
```
※ 約5GBのダウンロードのため、時間がかかります

### 6. DiaROSを起動
```bash
../DiaROS_imamoto/scripts/launch/launch_diaros_local.sh
```

## トラブルシューティング

### エラー: "Access to model google/gemma-2-2b-it is restricted"
→ 手順3のアクセス許可が完了していません

### エラー: "HF_TOKENが設定されていません"
→ 手順4のCLIログインが必要です

### ダウンロードが遅い
→ 安定したインターネット接続で再実行してください

## 代替モデル
Gemmaが使用できない場合は、以下のコマンドで軽量モデルに切り替え可能：
```bash
export DIAROS_LLM_MODEL=rinna-small
../DiaROS_imamoto/scripts/launch/launch_diaros_local.sh
```