"""
PyTorchデバイス選択ユーティリティ
M1/M2 Mac、CUDA、CPUを自動的に選択
"""
import torch
import os
import sys

def get_optimal_device(prefer_mps=True, verbose=True):
    """
    利用可能な最適なデバイスを選択
    
    Args:
        prefer_mps (bool): MPSが利用可能な場合に優先的に使用するか
        verbose (bool): デバイス選択情報を出力するか
        
    Returns:
        torch.device: 選択されたデバイス
    """
    # 環境変数でデバイスを強制指定可能
    force_device = os.environ.get('DIAROS_DEVICE', '').lower()
    
    if force_device:
        if force_device in ['mps', 'cuda', 'cpu']:
            if verbose:
                print(f"[Device] Forced to use: {force_device}")
            return torch.device(force_device)
    
    # MPS (Metal Performance Shaders) チェック - M1/M2 Mac
    if prefer_mps and hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
        device = torch.device("mps")
        if verbose:
            print(f"[Device] Using MPS (Metal Performance Shaders) on Apple Silicon")
        return device
    
    # CUDA チェック - NVIDIA GPU
    elif torch.cuda.is_available():
        device = torch.device("cuda")
        if verbose:
            gpu_name = torch.cuda.get_device_name(0)
            print(f"[Device] Using CUDA GPU: {gpu_name}")
        return device
    
    # CPU フォールバック
    else:
        device = torch.device("cpu")
        if verbose:
            print(f"[Device] Using CPU")
            # CPU最適化のヒント
            if sys.platform == "darwin":  # macOS
                print("[Device] Tip: For better CPU performance on Mac, ensure OMP_NUM_THREADS is set")
        return device

def move_model_to_device(model, device=None, verbose=True):
    """
    モデルを最適なデバイスに移動
    
    Args:
        model: PyTorchモデル
        device: 指定デバイス（Noneの場合は自動選択）
        verbose: 情報出力の有無
        
    Returns:
        tuple: (model, device)
    """
    if device is None:
        device = get_optimal_device(verbose=verbose)
    
    try:
        model = model.to(device)
        if verbose:
            print(f"[Device] Model successfully moved to {device}")
    except Exception as e:
        if device.type == "mps":
            # MPSエラーの場合はCPUにフォールバック
            if verbose:
                print(f"[Device] MPS failed: {e}")
                print("[Device] Falling back to CPU...")
            device = torch.device("cpu")
            model = model.to(device)
        else:
            raise e
    
    return model, device

def check_device_capabilities():
    """デバイス能力の詳細チェック（デバッグ用）"""
    print("=== Device Capabilities Check ===")
    print(f"PyTorch version: {torch.__version__}")
    print(f"Platform: {sys.platform}")
    
    # CUDA
    print(f"\nCUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"CUDA device count: {torch.cuda.device_count()}")
        for i in range(torch.cuda.device_count()):
            print(f"  GPU {i}: {torch.cuda.get_device_name(i)}")
    
    # MPS
    mps_available = hasattr(torch.backends, 'mps') and torch.backends.mps.is_available()
    print(f"\nMPS available: {mps_available}")
    if mps_available:
        print("  Running on Apple Silicon (M1/M2/M3)")
    
    # メモリ情報
    if sys.platform == "darwin":
        try:
            import subprocess
            result = subprocess.run(['sysctl', 'hw.memsize'], capture_output=True, text=True)
            if result.returncode == 0:
                mem_bytes = int(result.stdout.split(':')[1].strip())
                mem_gb = mem_bytes / (1024**3)
                print(f"\nSystem Memory: {mem_gb:.1f} GB")
        except:
            pass
    
    print("\n" + "="*30)