# 一旦履歴諦め

import requests
import json
import sys
import os
import time
from datetime import datetime
import openai

class NaturalLanguageGeneration:
    def __init__(self):
        self.rc = { "word": "" }
        
        self.query = ""
        self.update_flag = False
        self.dialogue_history = []
        self.user_speak_is_final = False
        self.last_reply = ""  # 生成した対話文をここに格納

        sys.stdout.write('NaturalLanguageGeneration  start up.\n')
        sys.stdout.write('=====================================================\n')
        # OpenAI APIキーを環境変数から設定
        openai.api_key = os.environ.get("OPENAI_API_KEY")

    def update(self, query):
        self.query = query
        self.update_flag = True
        sys.stdout.write(f"[NLG] update() called with query: {query}\n")
        sys.stdout.flush()


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
            if self.update_flag and self.query:
                query = self.query  # 修正: self.queryを使う
                try:
                    if query == "dummy":
                        res = "はい"
                    else:
                        if query in ("user_speak_is_final"):
                            sys.stdout.write('対話履歴作成\n')
                            sys.stdout.flush()
                            self.user_speak_is_final = True
                            query = query.replace("user_speak_is_final", "", 1)
                        if ":" in query:
                            response_cnt = int(query.split(":", 1)[0])
                            query = query.split(":", 1)[1]
                        sys.stdout.write(f"[NLG] query: {query}\n")

                        text_input = query
                        sys.stdout.write(f"[NLG] input {text_input}\n")
                        sys.stdout.flush()
                        start_time = datetime.now()
                        role = "優しい性格のアンドロイドとして、相手を労るような返答を２０文字以内でしてください。"
                        # openai>=1.0.0対応
                        chat_response = openai.chat.completions.create(
                            model="gpt-3.5-turbo-0125",
                            messages=[
                                {"role": "system","content": role},
                                {"role": "user","content": text_input},
                            ],
                        )
                        res = chat_response.choices[0].message.content
                        sys.stdout.write("[NLG生成文] " + res + "\n")
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
                except Exception as e:
                    self.last_reply = ""  # エラー時はlast_replyを空にすることで音声合成に反映しない
                    sys.stdout.write(f"[NLG ERROR] {e}\n")
                    sys.stdout.flush()
                self.update_flag = False
            # last_replyが空でない場合のみros2_natural_language_generation.pyで送信される
            time.sleep(0.01)