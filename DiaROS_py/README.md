# DiaROS

## インストール

````
pip install . --user
````

## モジュール構成
* speechInput.py                音声入力mod: PyAudio
* googleSpeechAPI.py            音声認識mod: Google Speech API STT
* acousticAnalysis.py           音声解析mod: aubio
* automaticSpeechRecognition.py 音声管理mod:上記3つを合わせたもの(ROSで通信ができるようになれば不要になる)
* responseControl.py            応答制御mod(応答タイミングの制御): リアルタイム制御を取り仕切る
* dialogManager.py              応答文生成mod: A3RT Talk API
* speachSynthesis.py            音声合成mod: Windows標準音声合成

## ROS2コマンド(一部)
* Topic一覧表示
```
ros2 topic list
```
* topicのレコード(コマンドを終了するまでTopicをレコードし、終えるとレコードファイルを出力)
```
ros2 bag record topic1 topic2 ... topicN
```
* レコードの再生
```
ros2 bag play [レコードファイル名]
```