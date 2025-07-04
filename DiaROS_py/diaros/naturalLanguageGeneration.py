# 一旦履歴諦め

import requests
import json
import sys
import os
import time
from datetime import datetime
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None
    import openai
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import warnings
warnings.filterwarnings('ignore')

class NaturalLanguageGeneration:
    def __init__(self):
        self.rc = { "word": "" }
        
        self.query = ""
        self.update_flag = False
        self.dialogue_history = []
        self.user_speak_is_final = False
        self.last_reply = ""  # 生成した対話文をここに格納
        self.words = ["", "", ""]  # 追加: 履歴リスト
        # ChatGPT APIを優先使用（環境変数でOpenAI APIキーが設定されている場合）
        self.use_local_model = not bool(os.environ.get("OPENAI_API_KEY"))

        sys.stdout.write('NaturalLanguageGeneration  start up.\n')
        sys.stdout.write('=====================================================\n')
        
        # 使用するAPIの設定
        self.api_type = self.detect_api_type()
        
        # ローカルモデルの初期化
        if self.use_local_model:
            self.init_local_model()
        else:
            # APIキーを環境変数から設定
            if self.api_type == "openai":
                if OpenAI:
                    # 新しいOpenAI SDK形式
                    self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
                else:
                    # 古いopenai形式
                    openai.api_key = os.environ.get("OPENAI_API_KEY")
                sys.stdout.write('OpenAI APIを使用します\n')
            elif self.api_type == "anthropic":
                sys.stdout.write('Claude API設定を確認中...\n')
                # Anthropic APIは別途実装可能
            else:
                sys.stdout.write('APIキーが設定されていません。ローカルモデルを使用します。\n')
                self.use_local_model = True
                self.init_local_model()
    
    def detect_api_type(self):
        """使用可能なAPIを検出"""
        # OpenAI APIキーの確認
        if os.environ.get("OPENAI_API_KEY"):
            return "openai"
        # Anthropic APIキーの確認
        elif os.environ.get("ANTHROPIC_API_KEY"):
            return "anthropic"
        else:
            return None
    
    def init_local_model(self):
        sys.stdout.write('Loading local language model...\n')
        
        # デバイス選択（MPS/CUDA/CPU自動選択）
        try:
            from . import device_utils
            self.device = device_utils.get_optimal_device(verbose=True)
        except:
            # フォールバック
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        sys.stdout.write(f'Using device: {self.device}\n')
        
        # 高速な日本語モデルの選択（環境変数で指定可能）
        model_choice = os.environ.get("DIAROS_LLM_MODEL", "rinna-small")
        
        # モデル選択ロジック
        if model_choice == "rinna-small":
            # rinna/japanese-gpt2-small (最も軽量、最速)
            model_name = "rinna/japanese-gpt2-small"
            sys.stdout.write('Using rinna/japanese-gpt2-small (fastest, ~100MB)\n')
        elif model_choice == "rinna-neox":
            # rinna/japanese-gpt-neox-small (高品質、やや重い)
            model_name = "rinna/japanese-gpt-neox-small"
            sys.stdout.write('Using rinna/japanese-gpt-neox-small (better quality, ~560MB)\n')
        elif model_choice == "calm-small":
            # cyberagent/open-calm-small (バランス型)
            model_name = "cyberagent/open-calm-small"
            sys.stdout.write('Using cyberagent/open-calm-small (balanced, ~400MB)\n')
        elif model_choice == "line-small":
            # line-corporation/japanese-large-lm-1.7b (最高品質、重い)
            model_name = "line-corporation/japanese-large-lm-1.7b"
            sys.stdout.write('Using LINE japanese-large-lm-1.7b (best quality, ~3.4GB)\n')
        else:
            # デフォルト
            model_name = "rinna/japanese-gpt2-small"
            sys.stdout.write(f'Unknown model {model_choice}, using default rinna/japanese-gpt2-small\n')
        
        try:
            # トークナイザーとモデルの読み込み
            self.tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
            
            # モデルロード時の最適化
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float16 if self.device.type in ["cuda", "mps"] else torch.float32,
                low_cpu_mem_usage=True,
                trust_remote_code=True
            )
            
            # モデルをデバイスに移動
            self.model.to(self.device)
            self.model.eval()
            
            # 推論高速化のための設定
            if hasattr(self.model, 'config'):
                self.model.config.use_cache = True  # KVキャッシュを有効化
            
            # パディングトークンを設定
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # 初回ウォームアップ（初回推論の遅延を避ける）
            sys.stdout.write('Warming up model...\n')
            warmup_text = "こんにちは"
            self._warmup_model(warmup_text)
            
            sys.stdout.write(f'Local model {model_name} loaded successfully.\n')
            sys.stdout.flush()
            
        except Exception as e:
            sys.stdout.write(f'Error loading {model_name}: {e}\n')
            sys.stdout.write('Falling back to rinna/japanese-gpt2-small\n')
            # フォールバック
            self.tokenizer = AutoTokenizer.from_pretrained("rinna/japanese-gpt2-small")
            self.model = AutoModelForCausalLM.from_pretrained("rinna/japanese-gpt2-small")
            self.model.to(self.device)
            self.model.eval()
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
    
    def _warmup_model(self, text):
        """モデルのウォームアップ（初回推論の遅延を避ける）"""
        try:
            inputs = self.tokenizer.encode(text, return_tensors="pt", max_length=128, truncation=True)
            inputs = inputs.to(self.device)
            with torch.no_grad():
                _ = self.model.generate(
                    inputs,
                    max_new_tokens=10,
                    temperature=0.8,
                    do_sample=False,
                    pad_token_id=self.tokenizer.pad_token_id
                )
        except Exception as e:
            sys.stdout.write(f'Warmup failed (non-critical): {e}\n')
    
    def generate_local_response(self, query, role=None):
        """高速化された応答生成メソッド"""
        
        # モデルに応じた最適なプロンプト設定
        model_name = self.model.config._name_or_path if hasattr(self.model.config, '_name_or_path') else ""
        
        if "rinna" in model_name:
            # rinnaモデル用の最適化されたプロンプト
            if role is None:
                role = "ユーザー: {query}\nシステム:"
            prompt = role.format(query=query) if "{query}" in role else f"{role}\nユーザー: {query}\nシステム:"
        elif "calm" in model_name.lower():
            # OpenCALM用のプロンプト
            if role is None:
                role = "以下は、ユーザーとアシスタントの会話です。\n"
            prompt = f"{role}ユーザー: {query}\nアシスタント:"
        elif "line" in model_name.lower():
            # LINE LLM用のプロンプト
            if role is None:
                role = ""
            prompt = f"{role}Human: {query}\nAssistant:"
        else:
            # デフォルトプロンプト
            if role is None:
                role = "優しい性格のアンドロイドとして、相手を労るような返答を２０文字以内でしてください。"
            prompt = f"{role}\n質問: {query}\n回答:"
        
        # 高速化のためのトークナイズ最適化
        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            max_length=256,  # 入力を短くして高速化
            truncation=True,
            padding=False  # パディングは不要
        ).input_ids.to(self.device)
        
        # 生成パラメータの最適化（高速化重視）
        generation_config = {
            "max_new_tokens": 25,  # 短い応答で高速化
            "min_new_tokens": 5,   # 最小文字数を減らして高速化
            "temperature": 0.7,    # やや確定的にして高速化
            "do_sample": True,
            "top_k": 50,          # top_kを追加して候補を制限
            "top_p": 0.85,        # top_pをやや下げて高速化
            "repetition_penalty": 1.1,
            "pad_token_id": self.tokenizer.pad_token_id,
            "eos_token_id": self.tokenizer.eos_token_id,
            "use_cache": True,    # KVキャッシュを明示的に有効化
            "num_beams": 1,       # ビームサーチを無効化して高速化
        }
        
        # 特定のモデルに対する調整
        if "neox" in model_name.lower():
            generation_config["temperature"] = 0.8
            generation_config["top_p"] = 0.9
        elif "calm" in model_name.lower():
            generation_config["temperature"] = 0.6
            generation_config["top_k"] = 40
        
        # 生成
        with torch.no_grad():
            if self.device.type == "mps":
                # MPS最適化
                with torch.autocast("mps", dtype=torch.float16):
                    outputs = self.model.generate(inputs, **generation_config)
            elif self.device.type == "cuda":
                # CUDA最適化
                with torch.cuda.amp.autocast():
                    outputs = self.model.generate(inputs, **generation_config)
            else:
                # CPU
                outputs = self.model.generate(inputs, **generation_config)
        
        # デコード（高速化のため部分的にデコード）
        generated_ids = outputs[0][inputs.shape[-1]:]  # 入力部分を除外
        response = self.tokenizer.decode(generated_ids, skip_special_tokens=True).strip()
        
        # 後処理（モデル特有の処理）
        if ":" in response and response.index(":") < 10:
            response = response.split(":", 1)[1].strip()
        
        # 改行や余分な空白を除去
        response = response.replace("\n", " ").strip()
        
        # 最初の句読点で切る（自然な終了）
        for delimiter in ["。", "！", "？", "、"]:
            if delimiter in response:
                parts = response.split(delimiter)
                if len(parts[0]) >= 5:  # 最低5文字は保持
                    response = parts[0] + delimiter
                    break
        
        # 長さ制限（30文字以内に調整）
        if len(response) > 30:
            # 文節の区切りで切る
            if "、" in response[:30]:
                response = response[:response.index("、", 0, 30)] + "。"
            else:
                response = response[:28] + "。"
        elif len(response) < 3:
            # 短すぎる場合のフォールバック
            response = "はい。"
        
        return response

    def update(self, words):
        # wordsはリスト型
        self.words = words
        self.query = words[0] if words else ""
        self.update_flag = True
    # def generate_dialogue(self, query):
    #     sys.stdout.write('対話履歴作成\n')
    #     sys.stdout.flush()
    #     response_res = self.response(query)
    #     dialogue_res = response_res
    #     if ":" in dialogue_res:
    #         dialogue_res = dialogue_res.split(":")[1]
    #     self.dialogue_history.append("usr:" + query)
    #     self.dialogue_history.append("sys:" + dialogue_res)
    #     # self.dialogue_historyの最後から４つの要素を保存
    #     if len(self.dialogue_history) > 5:
    #         self.dialogue_history = self.dialogue_history[-4:]
    #     sys.stdout.write('対話履歴作成\n')
    #     sys.stdout.flush()
    #     return response_res
    
    def run(self):
        DEBUG = True
        response_cnt = 0
        while True:
            if self.update_flag and self.words:
                # 最新・3つ前・6つ前の履歴を使う
                query_list = self.words
                query = query_list[0] if len(query_list) > 0 else ""
                # 必要に応じて3つ前・6つ前も利用可能
                # sys.stdout.write(f"input:{text_input}\n")
                # sys.stdout.flush()
                start_time = datetime.now()
                # ローカルモデル用の簡潔なプロンプト（高速化のため）
                if self.use_local_model:
                    # モデルに応じた最適なプロンプトを自動選択
                    res = self.generate_local_response(query)
                else:
                    # API用の詳細なプロンプト
                    role = """あなたは音声対話システムです。以下の点を守って応答してください：

1. 雑談対話にふさわしい、手短な1文程度（15-30文字）で応答
2. 自然で親しみやすい話し方
3. 相手の発言に対して適切に反応
4. 長すぎる説明は避ける
5. 質問には簡潔に答える

例：
- ユーザー: 「おはよう」→「おはようございます！」
- ユーザー: 「今日は暑いね」→「本当に暑いですね。」
- ユーザー: 「明日の天気は？」→「すみません、天気予報は分からないです。」

相手の発言に対して、自然で簡潔な応答をしてください。"""
                    
                    # APIを使用（高速応答最適化）
                    if self.api_type == "openai":
                        try:
                            # ChatGPT-3.5-turbo使用、音声対話向け最適化
                            if hasattr(self, 'client') and self.client:
                                # 新しいOpenAI SDK形式
                                chat_response = self.client.chat.completions.create(
                                    model="gpt-3.5-turbo",
                                    messages=[
                                        {"role": "system", "content": role},
                                        {"role": "user", "content": f"ユーザーの発言: {query}"}
                                    ],
                                    max_tokens=60,  # 短めの応答用
                                    temperature=0.7,  # 適度な創造性
                                    top_p=0.9,
                                    frequency_penalty=0.1,
                                    presence_penalty=0.1,
                                    timeout=3.0  # タイムアウトを3秒に延長
                                )
                            else:
                                # 古いopenai形式
                                chat_response = openai.chat.completions.create(
                                    model="gpt-3.5-turbo",
                                    messages=[
                                        {"role": "system", "content": role},
                                        {"role": "user", "content": f"ユーザーの発言: {query}"}
                                    ],
                                    max_tokens=60,  # 短めの応答用
                                    temperature=0.7,  # 適度な創造性
                                    top_p=0.9,
                                    frequency_penalty=0.1,
                                    presence_penalty=0.1,
                                    timeout=3.0  # タイムアウトを3秒に延長
                                )
                            res = chat_response.choices[0].message.content.strip()
                            
                            # 応答が長すぎる場合は最初の文のみ使用
                            if len(res) > 50:
                                sentences = res.split('。')
                                if len(sentences) > 1:
                                    res = sentences[0] + '。'
                                else:
                                    res = res[:50]
                            
                            sys.stdout.write(f"[ChatGPT API] 応答生成成功: {res}\n")
                            
                        except Exception as e:
                            sys.stdout.write(f"[ERROR] ChatGPT API エラー: {e}\n")
                            # フォールバック：文脈に応じた固定応答
                            fallback_responses = [
                                "そうですね。",
                                "なるほど。", 
                                "はい、分かりました。",
                                "ありがとうございます。"
                            ]
                            import random
                            res = random.choice(fallback_responses)
                            sys.stdout.write(f"[FALLBACK] 固定応答使用: {res}\n")
                    else:
                        # その他のAPI（将来的にClaude等）
                        res = "申し訳ございません。"
                sys.stdout.write("res: " + res + "\n")
                sys.stdout.flush()
                elapsed_time = datetime.now() - start_time
                response_time_sec = elapsed_time.total_seconds()
                response_time_ms = response_time_sec * 1000
                sys.stdout.write(f"[NLG] 応答時間: {response_time_ms:.0f}ms ({response_time_sec:.3f}秒)\n")
                
                # 応答時間の警告閾値をモード別に設定
                if self.use_local_model:
                    # ローカルモデル使用時は500ms以内が目標
                    if response_time_ms > 500:
                        sys.stdout.write(f"⚠️ 警告: ローカルモデルの応答時間が500msを超えました ({response_time_ms:.0f}ms)\n")
                        if response_time_ms > 1000:
                            sys.stdout.write("対話リズムが遅くなっています。より軽量なモデルへの切り替えを検討してください。\n")
                            sys.stdout.write("推奨: export DIAROS_LLM_MODEL=rinna-small\n")
                    else:
                        sys.stdout.write(f"✓ 高速応答達成: {response_time_ms:.0f}ms\n")
                else:
                    # API使用時は1500ms以内が目標
                    if response_time_sec > 1.5:
                        sys.stdout.write(f"⚠️ 警告: API応答時間が1.5秒を超えました ({response_time_sec:.3f}秒)\n")
                        sys.stdout.write("対話リズムが遅くなっています。API応答の最適化が必要です。\n")
                sys.stdout.flush()
                if ":" in res:
                    res = res.split(":", 1)[1]
                if self.user_speak_is_final:
                    self.dialogue_history.append("usr:" + query)
                    self.dialogue_history.append("sys:" + res)
                    self.user_speak_is_final = False
                    if len(self.dialogue_history) > 5:
                        self.dialogue_history = self.dialogue_history[-4:]
                    sys.stdout.write('対話履歴完了\n')
                    sys.stdout.flush()
                self.last_reply = res  # ここに生成文を格納
                # 生成文を標準出力
                print(f"[NLG生成文] {res}")
                sys.stdout.flush()
                self.update_flag = False
            # last_replyが空でない場合のみros2_natural_language_generation.pyで送信される
            time.sleep(0.01)