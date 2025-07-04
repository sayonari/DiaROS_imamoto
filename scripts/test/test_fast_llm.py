#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_fast_llm.py - 高速日本語LLMモデルのパフォーマンステスト
"""

import os
import sys
import time
import statistics
from pathlib import Path

# DiaROSモジュールのパスを追加
diaros_path = Path(__file__).parent.parent.parent / "DiaROS_py"
sys.path.insert(0, str(diaros_path))

def test_models():
    """各モデルのパフォーマンステスト"""
    models = [
        ("rinna-small", "rinna/japanese-gpt2-small"),
        ("rinna-neox", "rinna/japanese-gpt-neox-small"),
        ("calm-small", "cyberagent/open-calm-small"),
    ]
    
    test_inputs = [
        ["こんにちは"],
        ["明日の天気はどうですか"],
        ["ありがとうございます"],
        ["そうですね"],
        ["おはようございます"],
    ]
    
    print("=" * 60)
    print("高速日本語LLMパフォーマンステスト")
    print("=" * 60)
    print("")
    
    # OpenAI APIキーを一時的に無効化
    original_api_key = os.environ.get("OPENAI_API_KEY", "")
    if original_api_key:
        os.environ.pop("OPENAI_API_KEY", None)
        print("⚠️  OpenAI APIキーを一時的に無効化しました")
        print("")
    
    results = {}
    
    for model_env, model_name in models:
        print(f"\n🧪 テスト中: {model_name}")
        print("-" * 60)
        
        # モデルを設定
        os.environ["DIAROS_LLM_MODEL"] = model_env
        
        try:
            # NLGモジュールをインポート（モデル変更のため毎回再インポート）
            if 'diaros.naturalLanguageGeneration' in sys.modules:
                del sys.modules['diaros.naturalLanguageGeneration']
            from diaros.naturalLanguageGeneration import NaturalLanguageGeneration
            
            nlg = NaturalLanguageGeneration()
            
            # ウォームアップ
            print("⏳ ウォームアップ中...")
            nlg.nlg(["テスト"])
            
            # パフォーマンステスト
            times = []
            
            for i, test_input in enumerate(test_inputs, 1):
                start_time = time.time()
                response = nlg.nlg(test_input)
                elapsed = (time.time() - start_time) * 1000
                times.append(elapsed)
                
                print(f"  テスト{i}: {test_input[0][:10]}... → {response[:20]}...")
                print(f"          応答時間: {elapsed:.0f}ms")
            
            # 統計情報
            avg_time = statistics.mean(times)
            min_time = min(times)
            max_time = max(times)
            
            results[model_name] = {
                "avg": avg_time,
                "min": min_time,
                "max": max_time,
                "times": times
            }
            
            print(f"\n📊 統計:")
            print(f"  平均: {avg_time:.0f}ms")
            print(f"  最小: {min_time:.0f}ms")
            print(f"  最大: {max_time:.0f}ms")
            
            if avg_time < 500:
                print(f"  ✅ 目標達成！（< 500ms）")
            else:
                print(f"  ⚠️  目標未達成（> 500ms）")
                
        except Exception as e:
            print(f"❌ エラー: {e}")
            import traceback
            traceback.print_exc()
    
    # 結果のまとめ
    print("\n" + "=" * 60)
    print("📊 総合結果")
    print("=" * 60)
    
    sorted_results = sorted(results.items(), key=lambda x: x[1]["avg"])
    
    for i, (model, stats) in enumerate(sorted_results, 1):
        print(f"\n{i}. {model}")
        print(f"   平均応答時間: {stats['avg']:.0f}ms")
        print(f"   {'✅' if stats['avg'] < 500 else '⚠️ '} {'高速' if stats['avg'] < 500 else '要改善'}")
    
    if sorted_results:
        best_model = sorted_results[0][0]
        print(f"\n🏆 推奨モデル: {best_model}")
        print(f"   平均応答時間: {sorted_results[0][1]['avg']:.0f}ms")
    
    # APIキーを復元
    if original_api_key:
        os.environ["OPENAI_API_KEY"] = original_api_key
    
    print("\n✅ テスト完了")

def main():
    try:
        test_models()
    except KeyboardInterrupt:
        print("\n\n⚠️  テスト中断")
    except Exception as e:
        print(f"\n❌ 予期しないエラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()