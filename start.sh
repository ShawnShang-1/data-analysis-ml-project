#!/usr/bin/env python3
"""服务器启动脚本 — 修复 Python 3.13 Anaconda 版本解析问题"""
import sys

# 必须在任何其他 import 之前修复 sys.version
if "| packaged by Anaconda" in sys.version:
    import re
    sys.version = re.sub(r'\s*\|\s*packaged by Anaconda, Inc\.\s*\|\s*', '', sys.version)

# 正常启动
if __name__ == "__main__":
    import uvicorn
    from rag_backend.main import app
    uvicorn.run(app, host="0.0.0.0", port=8000)