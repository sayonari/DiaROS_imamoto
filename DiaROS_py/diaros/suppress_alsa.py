"""
ALSAエラーメッセージを抑制するユーティリティモジュール
"""
import os
import sys
import ctypes
from contextlib import contextmanager

# ALSAエラーメッセージを抑制
def suppress_alsa_lib_error_messages():
    """libasoundのエラーハンドラを無効化してALSAメッセージを抑制"""
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
        print(f"Warning: Could not suppress ALSA messages: {e}")
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