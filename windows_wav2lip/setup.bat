@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ============================================================
echo    Wav2Lip Windows 部署脚本 v1.0
echo    适用于: RTX 3050 Laptop GPU (4GB VRAM)
echo ============================================================
echo.

:: ===== 第一步：检查 Python =====
echo [1/5] 检查 Python 环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未找到 Python！请先安装 Python 3.9
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)
python --version
echo [OK] Python 已安装
echo.

:: ===== 第二步：检查/安装 CUDA =====
echo [2/5] 检查 CUDA 环境...
set CUDA_OK=0
nvcc --version >nul 2>&1
if %errorlevel% equ 0 (
    nvcc --version | findstr "release"
    echo [OK] CUDA 已安装
    set CUDA_OK=1
) else (
    echo [警告] 未检测到 nvcc
    echo 请确保已安装 CUDA Toolkit 11.8:
    echo https://developer.nvidia.com/cuda-11-8-0-download-archive
    echo.
    :: 即使没有 nvcc，也可能有 CUDA 运行时
    echo 尝试继续...（如果 PyTorch 检测不到 CUDA 会报错）
    set CUDA_OK=1
)
echo.

:: ===== 第三步：安装 Python 依赖 =====
echo [3/5] 安装 Python 依赖...
echo 这可能需要 5-10 分钟，请耐心等待...

:: 先升级 pip
python -m pip install --upgrade pip --quiet

:: 安装 PyTorch (CUDA 11.8)
echo   - 安装 PyTorch CUDA 11.8 版本...
pip install torch==2.0.1+cu118 torchvision==0.15.2+cu118 --index-url https://download.pytorch.org/whl/cu118 --quiet
if %errorlevel% neq 0 (
    echo [错误] PyTorch 安装失败！
    echo 请检查网络连接，或手动安装:
    echo pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
    pause
    exit /b 1
)

echo   - 安装其他依赖...
pip install numpy==1.24.4 opencv-python==4.8.1.78 scipy==1.10.1 scikit-image==0.21.0 --quiet
pip install librosa==0.9.2 face-alignment==1.3.5 tqdm==4.66.1 --quiet
pip install fastapi==0.104.1 "uvicorn[standard]==0.24.0" python-multipart aiofiles --quiet
pip install soundfile imageio imageio-ffmpeg matplotlib --quiet

echo [OK] 依赖安装完成
echo.

:: ===== 第四步：克隆 Wav2Lip 并下载模型 =====
echo [4/5] 下载 Wav2Lip 模型...

cd /d "%~dp0"

if not exist "Wav2Lip" (
    echo   - 克隆 Wav2Lip 仓库...
    git clone https://github.com/Rudrabha/Wav2Lip.git
    if %errorlevel% neq 0 (
        echo [警告] git clone 失败，尝试使用镜像...
        git clone https://gitclone.com/github.com/Rudrabha/Wav2Lip.git
    )
)

if not exist "Wav2Lip\checkpoints" mkdir "Wav2Lip\checkpoints"

if not exist "Wav2Lip\checkpoints\wav2lip_gan.pth" (
    echo   - 下载 Wav2Lip GAN 模型 (约 380MB)...
    echo   - 下载地址: https://iiitaphyd-my.sharepoint.com/personal/radrabha_m_research_iiit_ac_in/_layouts/15/onedrive.aspx?id=%%2Fpersonal%%2Fradrabha_m_research_iiit_ac_in%%2FDocuments%%2FWav2Lip_Models%%2Fwav2lip_gan.pth
    echo.
    echo   [手动操作] 请打开以下链接下载模型文件:
    echo   https://drive.google.com/drive/folders/1tBkqi4yuFgsmduxq3qNnN0itaqoJ_Bb0
    echo.
    echo   下载后，将 wav2lip_gan.pth 放到:
    echo   %~dp0Wav2Lip\checkpoints\wav2lip_gan.pth
    echo.
    echo   如果无法访问 Google Drive，可以用以下备用链接:
    echo   https://github.com/Rudrabha/Wav2Lip?tab=readme-ov-file#getting-the-weights
    echo.
    echo   [按任意键继续...]
    pause >nul
) else (
    echo [OK] Wav2Lip 模型已存在
)

:: 检查 face_detection 模型
if not exist "Wav2Lip\face_detection\detection\sfd\s3fd.pth" (
    echo   - 下载人脸检测模型...
    echo   请访问: https://www.adrianbulat.com/downloads/python-fan/s3fd-619a316812.pth
    echo   下载后重命名为 s3fd.pth，放到:
    echo   %~dp0Wav2Lip\face_detection\detection\sfd\s3fd.pth
    echo.
    echo   [按任意键继续...]
    pause >nul
) else (
    echo [OK] 人脸检测模型已存在
)

echo.
echo ============================================================
echo   安装完成！
echo ============================================================
echo.
echo 启动服务:
echo   python wav2lip_server.py --port 8001
echo.
echo 测试:
echo   curl http://localhost:8001/
echo.
echo 如果使用 Tailscale，服务地址为:
echo   http://100.x.x.x:8001  (Windows 的 Tailscale IP)
echo ============================================================
pause