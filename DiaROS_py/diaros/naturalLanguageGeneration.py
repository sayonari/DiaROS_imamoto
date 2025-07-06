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
        self.dialogue_history = []  # 対話履歴を管理
        # 環境変数で設定可能（デフォルトは6: ユーザ3発話＋システム3発話）
        self.max_dialogue_history = int(os.environ.get("DIAROS_MAX_DIALOGUE_HISTORY", "6"))
        self.user_speak_is_final = False
        self.last_reply = ""  # 生成した対話文をここに格納
        self.words = ["", "", ""]  # 追加: 履歴リスト
        # ChatGPT APIを優先使用（環境変数でOpenAI APIキーが設定されている場合）
        self.use_local_model = not bool(os.environ.get("OPENAI_API_KEY"))

        sys.stdout.write('[NLG] NaturalLanguageGeneration start up.\n')
        sys.stdout.write('[NLG] =====================================================\n')
        sys.stdout.write(f'[NLG] 対話履歴最大数: {self.max_dialogue_history}発話\n')
        
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
            sys.stdout.write('[NLG] モデル: rinna/japanese-gpt2-small (最速)\n')
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
        elif model_choice == "gemma-2b":
            # google/gemma-2-2b-it (Google Gemma 2 2B、高速)
            model_name = "google/gemma-2-2b-it"
            sys.stdout.write('Using google/gemma-2-2b-it (Gemma 2, fast, ~5GB)\n')
        elif model_choice == "gemma-9b":
            # google/gemma-2-9b-it (Google Gemma 2 9B、高品質)
            model_name = "google/gemma-2-9b-it"
            sys.stdout.write('Using google/gemma-2-9b-it (Gemma 2, high quality, ~18GB)\n')
        elif model_choice == "stablelm-2":
            # stabilityai/japanese-stablelm-2-instruct-1_6b (Japanese StableLM 2、高速)
            model_name = "stabilityai/japanese-stablelm-2-instruct-1_6b"
            sys.stdout.write('[NLG] デフォルトモデル: Japanese StableLM 2 (高速・高品質, ~3.2GB)\n')
        elif model_choice == "phi-3-mini":
            # microsoft/Phi-3-mini-4k-instruct (Phi-3-mini、超高速)
            model_name = "microsoft/Phi-3-mini-4k-instruct"
            sys.stdout.write('Using Phi-3-mini 4k (ultra-fast, ~7.6GB)\n')
        elif model_choice == "elyza-7b":
            # elyza/ELYZA-japanese-Llama-2-7b (ELYZA、高品質日本語特化)
            model_name = "elyza/ELYZA-japanese-Llama-2-7b"
            sys.stdout.write('Using ELYZA-japanese-Llama-2-7b (high quality Japanese, ~13GB)\n')
        else:
            # デフォルト
            model_name = "rinna/japanese-gpt2-small"
            sys.stdout.write(f'[NLG] Unknown model {model_choice}, using default rinna-small\n')
        
        try:
            # HuggingFaceトークンの取得（環境変数またはCLIログインから）
            hf_token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_TOKEN")
            if not hf_token:
                try:
                    from huggingface_hub import HfFolder
                    hf_token = HfFolder.get_token()
                except:
                    pass
            
            # Gemmaモデルの場合は特別な設定が必要
            if "gemma" in model_name:
                sys.stdout.write('[NLG] Gemmaモデル用の特別設定を適用中...\n')
                if not hf_token:
                    sys.stdout.write('[NLG] 警告: HuggingFaceトークンが見つかりません。\n')
                    sys.stdout.write('[NLG] huggingface-cli loginを実行するか、export HF_TOKEN=your_tokenを設定してください。\n')
                else:
                    sys.stdout.write('[NLG] HuggingFaceトークンを検出しました。\n')
                
                self.tokenizer = AutoTokenizer.from_pretrained(
                    model_name,
                    token=hf_token,
                    trust_remote_code=True
                )
            elif "Phi-3" in model_name:
                # Phi-3-miniの場合は特別な設定
                sys.stdout.write('[NLG] Phi-3-mini用の特別設定を適用中...\n')
                self.tokenizer = AutoTokenizer.from_pretrained(
                    model_name,
                    trust_remote_code=True,
                    pad_token='<|endoftext|>'
                )
            elif "elyza" in model_name.lower():
                # ELYZAモデルの場合
                sys.stdout.write('[NLG] ELYZA-japanese-Llama-2用の設定を適用中...\n')
                self.tokenizer = AutoTokenizer.from_pretrained(
                    model_name,
                    use_fast=False,  # LlamaTokenizerはfastを無効化
                    legacy=False
                )
                if self.tokenizer.pad_token is None:
                    self.tokenizer.pad_token = self.tokenizer.eos_token
            else:
                # 通常のモデル読み込み
                self.tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
            
            # モデルロード時の最適化
            if "gemma" in model_name:
                self.model = AutoModelForCausalLM.from_pretrained(
                    model_name,
                    token=hf_token,
                    torch_dtype=torch.bfloat16 if self.device.type in ["cuda", "mps"] else torch.float32,
                    low_cpu_mem_usage=True,
                    trust_remote_code=True
                )
            elif "Phi-3" in model_name:
                # Phi-3-miniは特別な設定が必要
                self.model = AutoModelForCausalLM.from_pretrained(
                    model_name,
                    torch_dtype=torch.bfloat16 if self.device.type in ["cuda", "mps"] else torch.float32,
                    low_cpu_mem_usage=True,
                    trust_remote_code=True,
                    attn_implementation="eager"  # DynamicCacheエラーを回避
                )
            elif "stablelm" in model_name:
                # StableLM 2はbfloat16を推奨
                self.model = AutoModelForCausalLM.from_pretrained(
                    model_name,
                    torch_dtype=torch.bfloat16 if self.device.type in ["cuda", "mps"] else torch.float32,
                    low_cpu_mem_usage=True,
                    trust_remote_code=True,
                    attn_implementation="flash_attention_2" if self.device.type == "cuda" else None
                )
            elif "elyza" in model_name.lower():
                # ELYZAモデルはfloat16を使用
                self.model = AutoModelForCausalLM.from_pretrained(
                    model_name,
                    torch_dtype=torch.float16 if self.device.type in ["cuda", "mps"] else torch.float32,
                    low_cpu_mem_usage=True,
                    device_map="auto" if self.device.type == "cuda" else None
                )
            else:
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
            sys.stdout.write(f'Model device: {self.device}, Model dtype: {self.model.dtype}\n')
            sys.stdout.write(f'Tokenizer info: vocab_size={self.tokenizer.vocab_size}, pad_token={self.tokenizer.pad_token}\n')
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
            # 実際の応答生成と同じ処理を実行してキャッシュをウォームアップ
            start_time = time.time()
            
            # generate_local_responseと同じプロンプト構築処理
            model_name = self.model.config._name_or_path if hasattr(self.model.config, '_name_or_path') else ""
            
            if "gemma" in model_name.lower() or "stablelm" in model_name.lower() or "Phi-3" in model_name:
                # チャットテンプレートを使用するモデル
                messages = [{"role": "user", "content": text}]
                try:
                    prompt = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
                except:
                    prompt = text
            else:
                # 通常のプロンプト
                prompt = f"ユーザ：{text}\nシステム："
            
            # トークナイズ
            inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # 生成
            with torch.no_grad():
                if "Phi-3" in model_name:
                    # Phi-3の場合はキャッシュを無効化
                    outputs = self.model.generate(
                        **inputs,
                        max_new_tokens=25,
                        temperature=0.7,
                        top_p=0.9,
                        do_sample=True,
                        pad_token_id=self.tokenizer.pad_token_id,
                        eos_token_id=self.tokenizer.eos_token_id,
                        use_cache=False
                    )
                else:
                    outputs = self.model.generate(
                        **inputs,
                        max_new_tokens=25,
                        temperature=0.7,
                        top_p=0.9,
                        do_sample=True,
                        pad_token_id=self.tokenizer.pad_token_id,
                        eos_token_id=self.tokenizer.eos_token_id
                    )
            
            # デコード（実際の処理と同じ）
            generated_ids = outputs[0][inputs['input_ids'].shape[1]:]
            response = self.tokenizer.decode(generated_ids, skip_special_tokens=True)
            
            elapsed_ms = (time.time() - start_time) * 1000
            sys.stdout.write(f'Model warmup completed in {elapsed_ms:.0f}ms\n')
            
        except Exception as e:
            sys.stdout.write(f'Warmup failed (non-critical): {e}\n')
    
    def generate_local_response(self, query, role=None):
        """高速化された応答生成メソッド"""
        
        # モデルに応じた最適なプロンプト設定
        model_name = self.model.config._name_or_path if hasattr(self.model.config, '_name_or_path') else ""
        
        # デフォルトの役割設定
        if role is None:
            role = """あなたは音声対話システムのシステム側エージェントです。本音声対話システムはリアルタイムに動作し、円滑にテンポ・リズムの良い音声対話を実現させるものです。ユーザは雑談や軽い楽しい対話を行う目的で、システムに話しかけます。ですので、長い応答ではなく、手短に、しかしユーザを喜ばせるような楽しい応答をするように心がけてください。

対話例）
ユーザ：こんにちは
システム：こんにちはー

ユーザ：今日の東京の天気はどんな感じかな？
システム：どうかなー？わからないけど良くなるといいね！

ユーザ：あなたは誰ですか？
システム：音声対話システムっていうらしい。名前は無いから決めてよ！"""
        
        if "rinna" in model_name:
            # rinnaモデル用の最適化されたプロンプト
            # 対話履歴を含めたプロンプトを構築
            prompt = f"{role}\n\n"
            
            # 対話履歴を追加
            for i, hist in enumerate(self.dialogue_history):
                if hist.startswith("ユーザ："):
                    prompt += hist + "\n"
                elif hist.startswith("システム："):
                    prompt += hist + "\n"
            
            # 現在のクエリを追加
            prompt += f"ユーザ：{query}\nシステム："
        elif "calm" in model_name.lower():
            # OpenCALM用のプロンプト
            prompt = f"{role}\n\n"
            for hist in self.dialogue_history:
                prompt += hist + "\n"
            prompt = f"{prompt}ユーザ：{query}\nシステム："
        elif "line" in model_name.lower():
            # LINE LLM用のプロンプト
            prompt = f"{role}\n\n"
            for hist in self.dialogue_history:
                if hist.startswith("ユーザ："):
                    prompt += hist.replace("ユーザ：", "Human: ") + "\n"
                elif hist.startswith("システム："):
                    prompt += hist.replace("システム：", "Assistant: ") + "\n"
            prompt += f"Human: {query}\nAssistant:"
        elif "gemma" in model_name.lower():
            # Gemmaモデル用のチャットテンプレート形式（日本語指示を含む）
            system_prompt = """あなたは日本語の音声対話システムです。以下の指示に従ってください：
1. 必ず日本語で応答してください
2. 15-30文字程度の短い応答を心がけてください
3. 親しみやすい話し方をしてください
4. 天気の質問には「ごめんなさい、天気予報はわからないです」と答えてください"""
            
            messages = []
            # システムプロンプトを最初に追加
            messages.append({"role": "user", "content": system_prompt})
            messages.append({"role": "assistant", "content": "はい、わかりました。日本語で短く親しみやすく応答します。"})
            
            # 対話履歴をメッセージ形式に変換
            for i in range(0, len(self.dialogue_history), 2):
                if i < len(self.dialogue_history):
                    user_msg = self.dialogue_history[i].replace("ユーザ：", "")
                    messages.append({"role": "user", "content": user_msg})
                if i+1 < len(self.dialogue_history):
                    sys_msg = self.dialogue_history[i+1].replace("システム：", "")
                    messages.append({"role": "assistant", "content": sys_msg})
            # 現在のクエリを追加
            messages.append({"role": "user", "content": query})
            
            # Gemmaのチャットテンプレートを使用
            try:
                prompt = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            except:
                # フォールバック（チャットテンプレートが使えない場合）
                prompt = f"<bos><start_of_turn>user\n日本語で応答してください: {query}<end_of_turn>\n<start_of_turn>model\n"
        elif "stablelm" in model_name.lower():
            # Japanese StableLM 2用のプロンプト
            system_prompt = """あなたは親切で知的な日本語の音声対話アシスタントです。
以下の点に注意して応答してください：
- 必ず日本語で応答する
- 簡潔で親しみやすい表現を使う（20文字程度）
- 絵文字は使わない"""
            
            messages = []
            messages.append({"role": "system", "content": system_prompt})
            
            # 対話履歴を追加
            for i in range(0, len(self.dialogue_history), 2):
                if i < len(self.dialogue_history):
                    user_msg = self.dialogue_history[i].replace("ユーザ：", "")
                    messages.append({"role": "user", "content": user_msg})
                if i+1 < len(self.dialogue_history):
                    sys_msg = self.dialogue_history[i+1].replace("システム：", "")
                    messages.append({"role": "assistant", "content": sys_msg})
            
            # 現在のクエリを追加
            messages.append({"role": "user", "content": query})
            
            # StableLMのチャットテンプレートを適用
            try:
                prompt = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
                sys.stdout.write(f"[NLG StableLM DEBUG] Applied chat template (length: {len(prompt)})\n")
            except:
                # フォールバック
                prompt = f"### 指示:\n{system_prompt}\n\n### 入力:\n{query}\n\n### 応答:\n"
        elif "Phi-3" in model_name:
            # Phi-3-mini用のプロンプト
            system_prompt = """You are a friendly Japanese conversational assistant. 
Rules:
- ALWAYS respond in Japanese
- Keep responses short (15-30 characters)
- Be friendly and casual
- No emojis"""
            
            messages = []
            messages.append({"role": "system", "content": system_prompt})
            
            # 対話履歴を追加
            for i in range(0, len(self.dialogue_history), 2):
                if i < len(self.dialogue_history):
                    user_msg = self.dialogue_history[i].replace("ユーザ：", "")
                    messages.append({"role": "user", "content": user_msg})
                if i+1 < len(self.dialogue_history):
                    sys_msg = self.dialogue_history[i+1].replace("システム：", "")
                    messages.append({"role": "assistant", "content": sys_msg})
            
            # 現在のクエリを追加
            messages.append({"role": "user", "content": query})
            
            # Phi-3のチャットテンプレートを適用
            try:
                prompt = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
                sys.stdout.write(f"[NLG Phi-3 DEBUG] Applied chat template (length: {len(prompt)})\n")
            except:
                # フォールバック
                prompt = f"<|system|>\n{system_prompt}<|end|>\n<|user|>\n{query}<|end|>\n<|assistant|>\n"
        elif "elyza" in model_name.lower():
            # ELYZA-japanese-Llama-2用のプロンプト
            system_prompt = """あなたは親切な日本語の音声対話アシスタントです。
以下のルールに従って応答してください：
- 必ず日本語で応答する
- 20文字以内の短い応答を心がける
- 親しみやすい口調で話す
- 絵文字は使わない"""
            
            # Llama-2形式のプロンプト
            prompt = f"""<s>[INST] <<SYS>>
{system_prompt}
<</SYS>>

{query} [/INST]"""
        else:
            # デフォルトプロンプト
            prompt = f"{role}\n\n"
            for hist in self.dialogue_history:
                prompt += hist + "\n"
            prompt = f"{prompt}ユーザ：{query}\nシステム："
        
        # 高速化のためのトークナイズ最適化
        tokenized = self.tokenizer(
            prompt,
            return_tensors="pt",
            max_length=256,  # 入力を短くして高速化
            truncation=True,
            padding=False  # パディングは不要
        )
        
        # Phi-3モデルの場合はattention_maskを明示的に設定
        if "Phi-3" in model_name:
            inputs = tokenized.input_ids.to(self.device)
            attention_mask = tokenized.attention_mask.to(self.device)
        else:
            inputs = tokenized.input_ids.to(self.device)
            attention_mask = None
        
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
        elif "gemma" in model_name.lower():
            # Gemmaモデル用の最適化
            generation_config["temperature"] = 0.5  # より確定的に
            generation_config["top_k"] = 30       # 候補をさらに制限
            generation_config["max_new_tokens"] = 30  # 応答が途切れないよう少し増やす
        elif "Phi-3" in model_name:
            # Phi-3モデル用の最適化（DynamicCacheエラー回避）
            generation_config["temperature"] = 0.7
            generation_config["top_k"] = 40
            generation_config["use_cache"] = False  # キャッシュを無効化してエラー回避
        elif "elyza" in model_name.lower():
            # ELYZAモデル用の最適化
            generation_config["temperature"] = 0.6
            generation_config["top_k"] = 30
            generation_config["top_p"] = 0.9
            generation_config["repetition_penalty"] = 1.15  # 繰り返しを防ぐ
        
        # 生成
        with torch.no_grad():
            # Phi-3モデルの場合はattention_maskを含める
            if "Phi-3" in model_name and attention_mask is not None:
                if self.device.type == "mps":
                    # MPS最適化
                    with torch.autocast("mps", dtype=torch.bfloat16):
                        outputs = self.model.generate(
                            inputs, 
                            attention_mask=attention_mask,
                            **generation_config
                        )
                else:
                    outputs = self.model.generate(
                        inputs,
                        attention_mask=attention_mask,
                        **generation_config
                    )
            elif self.device.type == "mps":
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
        
        # デバッグ: 生成結果の詳細
        sys.stdout.write(f"[NLG LOCAL DEBUG] prompt length: {len(prompt)}, generated_ids: {len(generated_ids)}, raw response: '{response}'\n")
        sys.stdout.flush()
        
        # 後処理（モデル特有の処理）
        # プレフィックスの除去（"システム："などが含まれる場合）
        prefixes_to_remove = ["システム：", "システム:", "アシスタント：", "アシスタント:", "Assistant:", "assistant:", 
                             "System:", "system:", "ユーザ：", "ユーザ:", "User:", "user:"]
        for prefix in prefixes_to_remove:
            if response.startswith(prefix):
                response = response[len(prefix):].strip()
                break
        
        # 文中の"システム:"パターンも除去
        import re
        response = re.sub(r'システム[:：]\s*', ' ', response)
        response = re.sub(r'ユーザ[:：]\s*', ' ', response)
        response = re.sub(r'アシスタント[:：]\s*', ' ', response)
        
        # 不要な記号や改行を除去
        response = response.replace("\n", " ").strip()
        response = response.replace("　", " ")  # 全角スペースを半角に
        
        # 連続する句読点を修正
        response = response.replace("。。", "。")
        response = response.replace("！！", "！")
        response = response.replace("？？", "？")
        response = response.replace("、、", "、")
        
        # 括弧内の内容を除去（システムの思考や説明が含まれることがある）
        import re
        response = re.sub(r'（[^）]*）', '', response)
        response = re.sub(r'\([^)]*\)', '', response)
        response = re.sub(r'\[[^\]]*\]', '', response)
        
        # 長さ制限（30文字以内に調整）
        if len(response) > 30:
            # 句読点で区切る
            sentences = re.split(r'[。！？]', response)
            if sentences and sentences[0]:
                # 最初の文を使用
                response = sentences[0]
                # 末尾に句読点を追加
                if not response.endswith(('。', '！', '？', '〜', 'ー')):
                    response += "。"
            else:
                # 句読点がない場合は単純に切る
                response = response[:28] + "…"
        
        # 短すぎる場合の処理
        if len(response) < 2:
            # 短すぎる場合のフォールバック応答
            fallback_responses = ["はい！", "そうだね！", "なるほど〜", "ふむふむ", "了解！"]
            import random
            response = random.choice(fallback_responses)
        
        # 最終的な空白の除去
        response = response.strip()
        
        return response

    def update(self, words):
        # wordsはリスト型
        if not words or not any(w and w.strip() for w in words):
            print("[DEBUG NLG] 空のwordsを受信。処理をスキップします。")
            return
        
        # 短すぎる発話（全て2文字未満）も除外
        valid_words = [w for w in words if w and w.strip() and len(w.strip()) >= 2]
        if not valid_words:
            print(f"[DEBUG NLG] 短すぎる発話を検出: {words}。処理をスキップします。")
            return
        
        self.words = valid_words
        self.query = valid_words[0] if valid_words else ""
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
                # デバッグ: 応答内容の詳細確認
                sys.stdout.write(f"[NLG DEBUG] query: '{query}' → res: '{res}' (length: {len(res)})\n")
                sys.stdout.flush()
                
                # 対話履歴を更新
                self.dialogue_history.append(f"ユーザ：{query}")
                self.dialogue_history.append(f"システム：{res}")
                
                # 履歴の最大数を超えたら古いものから削除
                if len(self.dialogue_history) > self.max_dialogue_history:
                    # 古い発話ペアを削除（2つずつ削除）
                    self.dialogue_history = self.dialogue_history[-self.max_dialogue_history:]
                
                # デバッグ: 対話履歴の状態
                sys.stdout.write(f"[NLG DEBUG] 対話履歴数: {len(self.dialogue_history)}\n")
                if len(self.dialogue_history) > 0:
                    sys.stdout.write(f"[NLG DEBUG] 最新履歴: {self.dialogue_history[-2:]}\n")
                
                # 空の応答をチェックして、フォールバック応答を使用
                if not res or res.strip() == "":
                    sys.stdout.write("[NLG WARNING] 空の応答を検出しました。フォールバック応答を使用します。\n")
                    res = "はい、そうですね。"
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