# 一旦履歴諦め

import requests
import json
import sys
import os
import time
from datetime import datetime
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
        self.use_local_model = True  # ローカルモデルを使用

        sys.stdout.write('NaturalLanguageGeneration  start up.\n')
        sys.stdout.write('=====================================================\n')
        
        # ローカルモデルの初期化
        if self.use_local_model:
            self.init_local_model()
        else:
            # OpenAI APIキーを環境変数から設定
            openai.api_key = os.environ.get("OPENAI_API_KEY")
    
    def init_local_model(self):
        sys.stdout.write('Loading local language model...\n')
        # 日本語対応の軽量モデルを使用（rinna/japanese-gpt2-small）
        model_name = "rinna/japanese-gpt2-small"
        
        # デバイスの設定
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        sys.stdout.write(f'Using device: {self.device}\n')
        
        # トークナイザーとモデルの読み込み
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name)
        self.model.to(self.device)
        self.model.eval()
        
        # パディングトークンを設定
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        sys.stdout.write('Local model loaded successfully.\n')
        sys.stdout.flush()
    
    def generate_local_response(self, query, role="優しい性格のアンドロイドとして、相手を労るような返答を２０文字以内でしてください。"):
        # プロンプトの作成
        prompt = f"{role}\n質問: {query}\n回答:"
        
        # トークナイズ
        inputs = self.tokenizer.encode(prompt, return_tensors="pt", max_length=512, truncation=True)
        inputs = inputs.to(self.device)
        
        # 生成
        with torch.no_grad():
            outputs = self.model.generate(
                inputs,
                max_new_tokens=30,  # 20文字程度の応答を生成
                min_length=10,
                temperature=0.8,
                do_sample=True,
                top_p=0.9,
                repetition_penalty=1.2,
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.eos_token_id
            )
        
        # デコード
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # プロンプト部分を除去
        if "回答:" in response:
            response = response.split("回答:")[-1].strip()
        else:
            # プロンプトの長さ分を除去
            prompt_length = len(self.tokenizer.decode(inputs[0], skip_special_tokens=True))
            response = response[prompt_length:].strip()
        
        # 最初の句読点または改行で切る（20文字制限のため）
        for delimiter in ["。", "！", "？", "\n"]:
            if delimiter in response:
                response = response.split(delimiter)[0] + delimiter
                break
        
        # 20文字を超える場合は切り詰める
        if len(response) > 20:
            response = response[:20]
        
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
                role = "優しい性格のアンドロイドとして、相手を労るような返答を２０文字以内でしてください。"
                
                if self.use_local_model:
                    # ローカルモデルを使用
                    res = self.generate_local_response(query, role)
                else:
                    # OpenAI APIを使用
                    # openai>=1.0.0対応
                    chat_response = openai.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system","content": role},
                            {"role": "user","content": query},
                        ],
                    )
                    res = chat_response.choices[0].message.content
                sys.stdout.write("res: " + res + "\n")
                sys.stdout.flush()
                elapsed_time = datetime.now() - start_time
                sys.stdout.write(f"time: {elapsed_time.total_seconds()}秒\n")
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