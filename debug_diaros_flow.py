#!/usr/bin/env python3
"""
DiaROS 対話フロー診断ツール
ROS2トピック通信をリアルタイム監視して問題箇所を特定します
"""

import subprocess
import time
import sys
from datetime import datetime
import threading
import queue
import signal
import os

class DiaROSFlowDebugger:
    def __init__(self):
        self.monitoring = True
        self.message_queue = queue.Queue()
        
    def monitor_topic(self, topic_name, description):
        """指定トピックの監視"""
        try:
            cmd = ["ros2", "topic", "echo", topic_name, "--no-arr"]
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, 
                                     stderr=subprocess.PIPE, 
                                     universal_newlines=True)
            
            print(f"🔍 {description} 監視開始: {topic_name}")
            
            while self.monitoring:
                try:
                    line = process.stdout.readline()
                    if line:
                        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                        self.message_queue.put(f"[{timestamp}] {description}: {line.strip()}")
                except Exception as e:
                    break
                    
        except Exception as e:
            print(f"❌ トピック監視エラー {topic_name}: {e}")

    def check_ros2_environment(self):
        """ROS2環境確認"""
        print("=" * 60)
        print("🔧 ROS2環境確認")
        print("=" * 60)
        
        try:
            # ROS2ノード一覧確認
            result = subprocess.run(["ros2", "node", "list"], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                nodes = result.stdout.strip().split('\n')
                print(f"✅ 起動中のROS2ノード数: {len(nodes)}")
                for node in nodes:
                    print(f"  - {node}")
            else:
                print("❌ ROS2ノード取得失敗")
                
        except Exception as e:
            print(f"❌ ROS2環境確認エラー: {e}")
            return False
            
        try:
            # トピック一覧確認
            result = subprocess.run(["ros2", "topic", "list"], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                topics = [t for t in result.stdout.strip().split('\n') if t]
                print(f"✅ 利用可能トピック数: {len(topics)}")
                diaros_topics = [t for t in topics if any(x in t for x in ['ASR', 'DM', 'NLG', 'SS', 'TT', 'BC'])]
                print(f"✅ DiaROS関連トピック数: {len(diaros_topics)}")
                for topic in diaros_topics:
                    print(f"  - {topic}")
            else:
                print("❌ ROS2トピック取得失敗")
                
        except Exception as e:
            print(f"❌ トピック確認エラー: {e}")
            return False
            
        return True

    def start_monitoring(self):
        """対話フロー監視開始"""
        if not self.check_ros2_environment():
            print("❌ ROS2環境の問題により監視を開始できません")
            return
            
        print("\n" + "=" * 60)
        print("🎯 DiaROS対話フロー診断開始")
        print("=" * 60)
        print("Ctrl+C で終了")
        
        # 重要なトピックの監視
        topics_to_monitor = [
            ("ASRtoDM", "音声認識→対話管理"),
            ("DMtoNLG", "対話管理→自然言語生成"),
            ("NLGtoSS", "自然言語生成→音声合成"),
            ("SStoDM", "音声合成→対話管理"),
            ("TTtoDM", "ターンテイキング→対話管理"),
            ("BCtoDM", "バックチャネル→対話管理")
        ]
        
        # 各トピックの監視スレッドを起動
        threads = []
        for topic, desc in topics_to_monitor:
            t = threading.Thread(target=self.monitor_topic, args=(topic, desc))
            t.daemon = True
            t.start()
            threads.append(t)
            time.sleep(0.1)  # スレッド起動間隔
        
        # メッセージ表示スレッド
        def display_messages():
            while self.monitoring:
                try:
                    message = self.message_queue.get(timeout=1)
                    print(message)
                except queue.Empty:
                    continue
                except Exception as e:
                    break
        
        display_thread = threading.Thread(target=display_messages)
        display_thread.daemon = True
        display_thread.start()
        
        try:
            # シグナルハンドリング
            def signal_handler(sig, frame):
                print("\n🛑 監視終了中...")
                self.monitoring = False
                sys.exit(0)
                
            signal.signal(signal.SIGINT, signal_handler)
            
            # メインループ
            print("📡 リアルタイム監視中... (メッセージが表示されない場合は通信に問題があります)")
            while self.monitoring:
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n🛑 監視を終了します")
            self.monitoring = False

    def run_quick_diagnosis(self):
        """クイック診断"""
        print("=" * 60)
        print("⚡ DiaROS クイック診断")
        print("=" * 60)
        
        # 1. ノード動作確認
        try:
            result = subprocess.run(["ros2", "node", "list"], 
                                  capture_output=True, text=True, timeout=3)
            if result.returncode == 0:
                nodes = result.stdout.strip().split('\n')
                expected_nodes = [
                    "speech_input", "acoustic_analysis", "automatic_speech_recognition",
                    "natural_language_understanding", "dialog_management", 
                    "speech_synthesis", "turn_taking", "back_channel"
                ]
                
                running_nodes = []
                for node in nodes:
                    node_name = node.strip('/')
                    if any(expected in node_name for expected in expected_nodes):
                        running_nodes.append(node_name)
                        
                print(f"✅ DiaROSノード稼働状況: {len(running_nodes)}/8")
                for node in running_nodes:
                    print(f"  ✓ {node}")
                    
                missing = [n for n in expected_nodes if not any(n in r for r in running_nodes)]
                if missing:
                    print("❌ 未起動ノード:")
                    for node in missing:
                        print(f"  ✗ {node}")
                        
        except Exception as e:
            print(f"❌ ノード診断エラー: {e}")
        
        # 2. トピック通信確認
        print("\n📡 トピック通信テスト (5秒間):")
        topics_test = ["ASRtoDM", "DMtoNLG", "NLGtoSS"]
        
        for topic in topics_test:
            try:
                result = subprocess.run(["timeout", "2", "ros2", "topic", "echo", topic, "--once"],
                                      capture_output=True, text=True)
                if result.returncode == 0 and result.stdout.strip():
                    print(f"  ✅ {topic}: 通信確認")
                else:
                    print(f"  ❌ {topic}: 通信なし")
            except Exception as e:
                print(f"  ⚠️  {topic}: テストエラー")


def main():
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python debug_diaros_flow.py monitor  # リアルタイム監視")
        print("  python debug_diaros_flow.py quick    # クイック診断")
        return
    
    debugger = DiaROSFlowDebugger()
    
    if sys.argv[1] == "monitor":
        debugger.start_monitoring()
    elif sys.argv[1] == "quick":
        debugger.run_quick_diagnosis()
    else:
        print("無効なコマンドです。monitor または quick を指定してください。")

if __name__ == "__main__":
    main()