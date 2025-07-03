#!/usr/bin/env python3
"""
DiaROS応答生成テストスクリプト
システム修正後の動作確認用
"""

import subprocess
import time
import threading
import sys
from datetime import datetime

class DiaROSResponseTester:
    def __init__(self):
        self.test_results = []
        
    def check_ros2_nodes(self):
        """ROS2ノード起動確認"""
        print("🔍 ROS2ノード状況確認...")
        try:
            result = subprocess.run(["ros2", "node", "list"], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                nodes = result.stdout.strip().split('\n')
                diaros_nodes = [n for n in nodes if any(x in n for x in [
                    'speech_input', 'acoustic_analysis', 'automatic_speech_recognition',
                    'dialog_management', 'speech_synthesis', 'turn_taking', 'back_channel'
                ])]
                print(f"✅ DiaROSノード: {len(diaros_nodes)}/8 起動中")
                for node in diaros_nodes:
                    print(f"  - {node}")
                return len(diaros_nodes) >= 6  # 最低6ノード必要
            else:
                print("❌ ROS2ノード取得失敗")
                return False
        except Exception as e:
            print(f"❌ ノード確認エラー: {e}")
            return False
    
    def monitor_topic_for_response(self, topic, timeout=30):
        """指定トピックでの応答監視"""
        print(f"📡 トピック {topic} を {timeout}秒間監視...")
        messages = []
        
        def monitor():
            try:
                cmd = ["timeout", str(timeout), "ros2", "topic", "echo", topic, "--no-arr"]
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, 
                                         stderr=subprocess.PIPE, 
                                         universal_newlines=True)
                
                while True:
                    line = process.stdout.readline()
                    if not line:
                        break
                    if line.strip():
                        messages.append(line.strip())
                        print(f"  📨 {topic}: {line.strip()}")
                        
            except Exception as e:
                print(f"❌ 監視エラー {topic}: {e}")
        
        monitor_thread = threading.Thread(target=monitor)
        monitor_thread.daemon = True
        monitor_thread.start()
        monitor_thread.join(timeout + 2)
        
        return len(messages) > 0, messages
    
    def test_asr_to_dm_flow(self):
        """ASR→DM通信テスト"""
        print("\n🔬 ASR→DM通信フローテスト")
        print("音声入力を5秒間待機します...")
        
        has_messages, messages = self.monitor_topic_for_response("ASRtoDM", 10)
        
        if has_messages:
            print("✅ ASR→DM通信確認")
            # ASR結果の内容確認
            for msg in messages[-3:]:  # 最新3件
                if "you:" in msg and len(msg) > 10:
                    print(f"  📝 認識結果: {msg}")
            return True
        else:
            print("❌ ASR→DM通信なし")
            return False
    
    def test_dm_to_nlg_flow(self):
        """DM→NLG通信テスト"""
        print("\n🔬 DM→NLG通信フローテスト")
        
        has_messages, messages = self.monitor_topic_for_response("DMtoNLG", 5)
        
        if has_messages:
            print("✅ DM→NLG通信確認")
            for msg in messages[-2:]:  # 最新2件
                print(f"  📤 送信データ: {msg}")
            return True
        else:
            print("❌ DM→NLG通信なし（応答生成されていない可能性）")
            return False
    
    def test_nlg_to_ss_flow(self):
        """NLG→SS通信テスト"""
        print("\n🔬 NLG→SS通信フローテスト")
        
        has_messages, messages = self.monitor_topic_for_response("NLGtoSS", 5)
        
        if has_messages:
            print("✅ NLG→SS通信確認")
            for msg in messages[-2:]:  # 最新2件
                print(f"  💬 生成応答: {msg}")
            return True
        else:
            print("❌ NLG→SS通信なし")
            return False
    
    def check_tmp_audio_files(self):
        """音声合成ファイル生成確認"""
        print("\n🔬 音声合成ファイル生成確認")
        
        import os
        tmp_dir = "/Users/sayonari/_data/_DiaROS_mac/DiaROS_pixi/DiaROS_imamoto/DiaROS_ros/tmp"
        
        if os.path.exists(tmp_dir):
            wav_files = [f for f in os.listdir(tmp_dir) if f.endswith('.wav')]
            if wav_files:
                print(f"✅ 音声ファイル生成確認: {len(wav_files)}件")
                for file in wav_files[-3:]:  # 最新3件
                    file_path = os.path.join(tmp_dir, file)
                    size = os.path.getsize(file_path)
                    print(f"  🎵 {file} ({size} bytes)")
                return True
            else:
                print("❌ 音声ファイル未生成")
                return False
        else:
            print("❌ tmpディレクトリ未存在")
            return False
    
    def run_comprehensive_test(self):
        """包括的応答テスト"""
        print("=" * 60)
        print("🎯 DiaROS応答生成包括テスト")
        print("=" * 60)
        print("手順: マイクに向かって「こんにちは」または「明日の天気を教えて」と話してください")
        print("30秒間で応答生成フローを確認します...")
        print()
        
        if not self.check_ros2_nodes():
            print("❌ DiaROSが正常に起動していません")
            return False
        
        # 段階的テスト
        test_results = []
        
        print("\n--- Phase 1: 音声認識確認 ---")
        asr_ok = self.test_asr_to_dm_flow()
        test_results.append(("ASR→DM", asr_ok))
        
        if asr_ok:
            print("\n--- Phase 2: 対話管理応答判定確認 ---")
            dm_ok = self.test_dm_to_nlg_flow()
            test_results.append(("DM→NLG", dm_ok))
            
            if dm_ok:
                print("\n--- Phase 3: 自然言語生成確認 ---")
                nlg_ok = self.test_nlg_to_ss_flow()
                test_results.append(("NLG→SS", nlg_ok))
                
                print("\n--- Phase 4: 音声合成ファイル確認 ---")
                ss_ok = self.check_tmp_audio_files()
                test_results.append(("音声合成", ss_ok))
        
        # 結果サマリー
        print("\n" + "=" * 60)
        print("📊 テスト結果サマリー")
        print("=" * 60)
        
        for test_name, result in test_results:
            status = "✅ OK" if result else "❌ NG"
            print(f"{test_name:15} : {status}")
        
        success_rate = sum(1 for _, result in test_results if result) / len(test_results)
        print(f"\n成功率: {success_rate:.1%}")
        
        if success_rate >= 0.75:
            print("🎉 DiaROS応答システムは良好に動作しています！")
        else:
            print("⚠️  修正が必要な問題があります")
            
        return success_rate >= 0.75


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "quick":
        tester = DiaROSResponseTester()
        if tester.check_ros2_nodes():
            print("✅ DiaROSノード確認OK")
        else:
            print("❌ DiaROSが起動していません")
    else:
        tester = DiaROSResponseTester()
        tester.run_comprehensive_test()

if __name__ == "__main__":
    main()