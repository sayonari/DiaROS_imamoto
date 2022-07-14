import requests
import json
import sys
import os

class DialogManagement:
    def __init__(self):
        # read API key
        with open(os.environ['A3RT_APIKEY'],encoding='utf-8') as f:
            self.key = f.readline().strip()
        self.url = "https://api.a3rt.recruit.co.jp/talk/v1/smalltalk" # エンドポイントURL
        self.rc = { "word": "" }
        sys.stdout.write('DialogManagement start up.\n')
        sys.stdout.write('=====================================================\n')

    def response(self, query):
        try:
            if query == "dummy":
                return "はい"
            res = requests.post( self.url, {'apikey': self.key, 'query': query } )
            data = res.json()
            if data['status'] == 0:
                reply = data['results'][0]['reply'] # レスポンス結果
                return reply
            else: # レスポンスに不備あり
                return f"リクエストエラー (status: {str(data['status'])}, message: {data['message']})"
        except Exception as e:
            return f"不明なエラー：{e.args}"


if __name__ == '__main__': 
    api = DialogManagement()

    while True:
        text = input('input:')
        print(f'API: {api.response(text)}')


