"""
ALSAエラーメッセージを抑制するユーティリティモジュール
"""
import os
import sys
import ctypes
from contextlib import contextmanager

# ALSAエラーメッセージを抑制
def suppress_alsa_lib_error_messages():
    """プラットフォーム別にALSAエラーメッセージを抑制"""
    import platform
    
    # macOS環境の場合
    if platform.system() == 'Darwin':
        # macOSではPyAudio環境変数でALSA警告を抑制
        os.environ['PYAUDIO_DEBUG'] = '0'
        os.environ['PULSE_CRASH_ON_ERROR'] = '0'
        # CoreAudio関連の警告を抑制
        os.environ['CA_DISABLE_LOGGING'] = '1'
        return True
    
    # Linux環境の場合（従来のコード）
    try:
        # libasound.so.2をロード
        asound = ctypes.cdll.LoadLibrary('libasound.so.2')
        
        # エラーハンドラ関数の型定義
        # typedef void (*snd_lib_error_handler_t)(const char *file, int line, const char *function, int err, const char *format, ...);
        ERROR_HANDLER_FUNC = ctypes.CFUNCTYPE(None, ctypes.c_char_p, ctypes.c_int,
                                              ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p)
        
        # 空のエラーハンドラ（何もしない）
        def null_error_handler(filename, line, function, err, format):
            # エラーメッセージを無視
            pass
        
        # エラーハンドラを登録
        c_null_handler = ERROR_HANDLER_FUNC(null_error_handler)
        asound.snd_lib_error_set_handler(c_null_handler)
        
        # ハンドラへの参照を保持（ガベージコレクションを防ぐ）
        suppress_alsa_lib_error_messages._handler = c_null_handler
        
        return True
    except Exception as e:
        # libasoundが見つからない場合や互換性がない場合
        # 環境変数によるフォールバック抑制を試行
        os.environ['ALSA_CARD'] = '0'
        os.environ['PULSE_RUNTIME_PATH'] = '/dev/null'
        return False

@contextmanager
def suppress_stdout_stderr():
    """標準出力と標準エラー出力を一時的に抑制するコンテキストマネージャ"""
    with open(os.devnull, 'w') as devnull:
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = devnull
        sys.stderr = devnull
        try:
            yield
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr