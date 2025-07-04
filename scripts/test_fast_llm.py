#!/usr/bin/env python3
"""
高速日本語LLMモデルのテストスクリプト
使用可能なモデルをテストして応答時間を計測
"""

import os
import sys
import time
import torch
from datetime import datetime

# DiaROSパスを追加
sys.path.append(os.path.join(os.path.dirname(__file__), '../DiaROS_py'))

def test_model(model_name):
    """指定されたモデルをテストして応答時間を計測"""
    print(f"\n{'='*60}")
    print(f"テスト開始: {model_name}")
    print('='*60)
    
    # 環境変数を設定
    os.environ["DIAROS_LLM_MODEL"] = model_name
    
    # NLGモジュールをインポート（毎回新規作成）
    from diaros.naturalLanguageGeneration import NaturalLanguageGeneration
    
    try:
        # モジュール初期化
        print("モジュール初期化中...")
        start_init = time.time()
        nlg = NaturalLanguageGeneration()
        nlg.use_local_model = True  # 強制的にローカルモデルを使用
        nlg.init_local_model()
        init_time = time.time() - start_init
        print(f"初期化時間: {init_time:.2f}秒")
        
        # テスト発話リスト
        test_queries = [
            "こんにちは",
            "今日はいい天気ですね",
            "疲れました",
            "明日の予定は？",
            "ありがとう"
        ]
        
        print("\n応答テスト:")
        print("-" * 60)
        
        total_time = 0
        response_times = []
        
        for query in test_queries:
            print(f"\n入力: {query}")
            
            # 応答生成
            start_time = time.time()
            response = nlg.generate_local_response(query)
            elapsed_time = time.time() - start_time
            elapsed_ms = elapsed_time * 1000
            
            print(f"応答: {response}")
            print(f"時間: {elapsed_ms:.0f}ms")
            
            total_time += elapsed_time
            response_times.append(elapsed_ms)
            
            # 少し待機
            time.sleep(0.1)
        
        # 統計情報
        avg_time = total_time / len(test_queries) * 1000
        min_time = min(response_times)
        max_time = max(response_times)
        
        print("\n" + "="*60)
        print("統計情報:")
        print(f"  平均応答時間: {avg_time:.0f}ms")
        print(f"  最小応答時間: {min_time:.0f}ms")
        print(f"  最大応答時間: {max_time:.0f}ms")
        
        if avg_time <= 500:
            print("  ✓ 目標達成: 平均500ms以内")
        else:
            print("  ⚠️ 目標未達: 平均500ms超過")
        
        # メモリ使用量（概算）
        if hasattr(nlg, 'model'):
            param_count = sum(p.numel() for p in nlg.model.parameters())
            model_size_mb = param_count * 4 / 1024 / 1024  # float32想定
            print(f"  モデルサイズ: 約{model_size_mb:.0f}MB")
        
        # クリーンアップ
        del nlg
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        return avg_time
        
    except Exception as e:
        print(f"エラー発生: {e}")
        return float('inf')

def main():
    """メイン処理"""
    print("DiaROS 高速日本語LLMモデル テスト")
    print("="*60)
    
    # デバイス情報を表示
    try:
        from diaros import device_utils
        device = device_utils.get_optimal_device(verbose=True)
    except:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Device: {device}")
    
    # テストするモデルリスト
    models_to_test = [
        ("rinna-small", "最速・最軽量"),
        ("rinna-neox", "高品質・やや重い"),
        ("calm-small", "バランス型"),
        # ("line-small", "最高品質・重い")  # オプション
    ]
    
    results = {}
    
    # 各モデルをテスト
    for model_id, description in models_to_test:
        print(f"\n\n[モデル: {model_id}] {description}")
        avg_time = test_model(model_id)
        results[model_id] = avg_time
        
        # メモリクリア
        time.sleep(1)
    
    # 結果サマリー
    print("\n\n" + "="*60)
    print("テスト結果サマリー")
    print("="*60)
    
    sorted_results = sorted(results.items(), key=lambda x: x[1])
    
    for i, (model_id, avg_time) in enumerate(sorted_results):
        if avg_time == float('inf'):
            print(f"{i+1}. {model_id}: エラー")
        else:
            status = "✓" if avg_time <= 500 else "△" if avg_time <= 1000 else "✗"
            print(f"{i+1}. {model_id}: {avg_time:.0f}ms {status}")
    
    # 推奨設定
    print("\n推奨設定:")
    if sorted_results[0][1] <= 500:
        print(f"export DIAROS_LLM_MODEL={sorted_results[0][0]}")
        print(f"（最速: {sorted_results[0][1]:.0f}ms）")
    else:
        print("export DIAROS_LLM_MODEL=rinna-small")
        print("（デフォルト推奨）")
    
    # API使用の推奨
    print("\nより高速な応答が必要な場合:")
    print("export OPENAI_API_KEY='your-api-key'  # ChatGPT APIを使用")
    print("export ANTHROPIC_API_KEY='your-api-key'  # Claude APIを使用")

if __name__ == "__main__":
    main()