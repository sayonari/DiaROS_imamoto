#!/usr/bin/env python3
"""
debug_diaros_flow.py - DiaROS対話フローデバッグツール
対話システムの各モジュール間の通信をリアルタイムで監視・デバッグします。
"""

import rclpy
from rclpy.node import Node
from interfaces.msg import Iasr, Idm, Inlg, Iss, Iaa, Itt, Ibc
from std_msgs.msg import Float32MultiArray
import time
from datetime import datetime
import sys
import threading

class DiaROSFlowDebugger(Node):
    def __init__(self):
        super().__init__('diaros_flow_debugger')
        
        # 各モジュールの最新データを保存
        self.latest_data = {
            'audio_input': None,
            'acoustic_analysis': None,
            'asr': None,
            'dm': None,
            'nlg': None,
            'ss': None,
            'tt': None,
            'bc': None
        }
        
        # タイムスタンプを記録
        self.timestamps = {}
        
        # 統計情報
        self.stats = {
            'audio_input_count': 0,
            'asr_count': 0,
            'dm_count': 0,
            'nlg_count': 0,
            'ss_count': 0,
            'tt_count': 0,
            'bc_count': 0
        }
        
        # サブスクライバーの設定
        self.setup_subscribers()
        
        # 定期的な表示用タイマー
        self.display_timer = self.create_timer(1.0, self.display_status)
        
        self.get_logger().info('DiaROSフローデバッガーを起動しました')
        print('\n' + '='*70)
        print('DiaROS対話フローデバッガー - リアルタイム監視')
        print('='*70)
        print('Ctrl+Cで終了します\n')
        
    def setup_subscribers(self):
        """各トピックのサブスクライバーを設定"""
        # 音声入力
        self.sub_audio = self.create_subscription(
            Float32MultiArray, 'mic_audio_float32', 
            lambda msg: self.audio_callback(msg), 10)
        
        # 音響分析
        self.sub_aa = self.create_subscription(
            Iaa, 'AAtoDM', 
            lambda msg: self.aa_callback(msg), 10)
        
        # 音声認識
        self.sub_asr = self.create_subscription(
            Iasr, 'ASRtoDM', 
            lambda msg: self.asr_callback(msg), 10)
        
        # 対話管理からNLG
        self.sub_dm_to_nlg = self.create_subscription(
            Idm, 'DMtoNLG', 
            lambda msg: self.dm_to_nlg_callback(msg), 10)
        
        # NLGから対話管理
        self.sub_nlg = self.create_subscription(
            Inlg, 'NLGtoDM', 
            lambda msg: self.nlg_callback(msg), 10)
        
        # 音声合成
        self.sub_ss = self.create_subscription(
            Iss, 'SStoDM', 
            lambda msg: self.ss_callback(msg), 10)
        
        # ターンテイキング
        self.sub_tt = self.create_subscription(
            Itt, 'TTtoDM', 
            lambda msg: self.tt_callback(msg), 10)
        
        # バックチャンネル
        self.sub_bc = self.create_subscription(
            Ibc, 'BCtoDM', 
            lambda msg: self.bc_callback(msg), 10)
    
    def audio_callback(self, msg):
        """音声入力のコールバック"""
        self.stats['audio_input_count'] += 1
        audio_data = msg.data[:10] if len(msg.data) > 10 else msg.data
        self.latest_data['audio_input'] = f"長さ: {len(msg.data)}, 先頭: {audio_data[0] if audio_data else 'N/A':.3f}"
        self.timestamps['audio_input'] = datetime.now()
    
    def aa_callback(self, msg):
        """音響分析のコールバック"""
        self.latest_data['acoustic_analysis'] = f"F0: {msg.f0:.1f}, Power: {msg.power:.1f}, ZC: {msg.zerocross}"
        self.timestamps['acoustic_analysis'] = datetime.now()
    
    def asr_callback(self, msg):
        """音声認識のコールバック"""
        self.stats['asr_count'] += 1
        self.latest_data['asr'] = f"'{msg.you}' (final: {msg.is_final})"
        self.timestamps['asr'] = datetime.now()
        # 重要なイベントは即座に表示
        if msg.you:
            print(f"\n🎤 [ASR] 認識結果: '{msg.you}' (final: {msg.is_final})")
    
    def dm_to_nlg_callback(self, msg):
        """対話管理→NLGのコールバック"""
        self.stats['dm_count'] += 1
        # Idm.msgはstring[]型のwordsフィールドを持つ
        words = msg.words if msg.words else []
        # 空でない要素のみフィルタリング
        non_empty_words = [w for w in words if w and w.strip()]
        self.latest_data['dm'] = f"Words: {non_empty_words}"
        self.timestamps['dm'] = datetime.now()
        if non_empty_words:
            print(f"\n💭 [DM→NLG] 生成要求: {non_empty_words}")
        else:
            print(f"\n💭 [DM→NLG] 空の生成要求")
    
    def nlg_callback(self, msg):
        """NLGのコールバック"""
        self.stats['nlg_count'] += 1
        self.latest_data['nlg'] = f"'{msg.response}'"
        self.timestamps['nlg'] = datetime.now()
        print(f"\n🤖 [NLG] 応答生成: '{msg.response}'")
    
    def ss_callback(self, msg):
        """音声合成のコールバック"""
        self.stats['ss_count'] += 1
        self.latest_data['ss'] = f"File: {msg.filename}, Time: {msg.timestamp}"
        self.timestamps['ss'] = datetime.now()
        print(f"\n🔊 [SS] 音声合成完了: {msg.filename}")
    
    def tt_callback(self, msg):
        """ターンテイキングのコールバック"""
        self.stats['tt_count'] += 1
        self.latest_data['tt'] = f"Confidence: {msg.confidence:.3f}"
        self.timestamps['tt'] = datetime.now()
        if msg.confidence > 0.5:
            print(f"\n🔄 [TT] ターン交代検出: {msg.confidence:.3f}")
    
    def bc_callback(self, msg):
        """バックチャンネルのコールバック"""
        self.stats['bc_count'] += 1
        self.latest_data['bc'] = f"'{msg.response}'"
        self.timestamps['bc'] = datetime.now()
        print(f"\n😊 [BC] 相槌: '{msg.response}'")
    
    def display_status(self):
        """定期的にステータスを表示"""
        # カーソルを上に移動してステータスを更新
        print('\033[H\033[J', end='')  # 画面クリア
        print('='*70)
        print('DiaROS対話フローデバッガー - リアルタイム監視')
        print('='*70)
        print(f'更新時刻: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        print('-'*70)
        
        # 各モジュールの状態を表示
        modules = [
            ('音声入力', 'audio_input', '🎙️'),
            ('音響分析', 'acoustic_analysis', '📊'),
            ('音声認識', 'asr', '🎤'),
            ('対話管理', 'dm', '💭'),
            ('応答生成', 'nlg', '🤖'),
            ('音声合成', 'ss', '🔊'),
            ('ターン管理', 'tt', '🔄'),
            ('相槌', 'bc', '😊')
        ]
        
        for name, key, icon in modules:
            data = self.latest_data.get(key, 'データなし')
            timestamp = self.timestamps.get(key)
            if timestamp:
                elapsed = (datetime.now() - timestamp).total_seconds()
                status = '🟢' if elapsed < 2 else ('🟡' if elapsed < 5 else '🔴')
            else:
                status = '⚫'
            
            print(f'{icon} {name:10} {status} {data}')
        
        print('-'*70)
        print('統計情報:')
        print(f'  音声入力: {self.stats["audio_input_count"]:6d} | '
              f'ASR: {self.stats["asr_count"]:4d} | '
              f'DM: {self.stats["dm_count"]:4d} | '
              f'NLG: {self.stats["nlg_count"]:4d}')
        print(f'  SS: {self.stats["ss_count"]:4d} | '
              f'TT: {self.stats["tt_count"]:4d} | '
              f'BC: {self.stats["bc_count"]:4d}')
        print('='*70)
        print('\n最新イベント:')

def main():
    rclpy.init()
    debugger = DiaROSFlowDebugger()
    
    try:
        rclpy.spin(debugger)
    except KeyboardInterrupt:
        print('\n\nデバッグを終了しました。')
    finally:
        debugger.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()