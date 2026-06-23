"""
启动脚本 — 修复 Python 3.13 Anaconda 版本解析问题
"""
import sys

# 修复 sys.version，移除 Anaconda 打包信息
# 原始: "3.13.13 | packaged by Anaconda, Inc. | (main, ...)"
# 修复: "3.13.13 (main, ...)"
if "| packaged by Anaconda" in sys.version:
    import re
    fixed = re.sub(r'\s*\|\s*packaged by Anaconda, Inc\.\s*\|', '', sys.version)
    sys.version = fixed

# 正常启动
import uvicorn
from rag_backend.main import app

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)