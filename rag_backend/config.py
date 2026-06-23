"""
RAG 系统配置文件
所有敏感信息从环境变量读取，支持 .env 文件
"""
import os

# 尝试加载 .env 文件（开发环境用）
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ── 路径配置 ──
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
TEXTBOOK_DIR = os.path.join(DATA_DIR, "textbooks")
CHROMA_DIR = os.path.join(BASE_DIR, "chroma_db")

# ── Neo4j 配置（从环境变量读取） ──
NEO4J_URI = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.environ.get("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "ml2026kg")

# ── Ollama 配置 ──
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
LLM_MODEL = os.environ.get("LLM_MODEL", "qwen3.5:9b")
EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", "bge-m3")

# ── RAG 配置 ──
CHUNK_SIZE = int(os.environ.get("CHUNK_SIZE", "600"))
CHUNK_OVERLAP = int(os.environ.get("CHUNK_OVERLAP", "100"))
TOP_K_VECTOR = int(os.environ.get("TOP_K_VECTOR", "6"))
TOP_K_GRAPH = int(os.environ.get("TOP_K_GRAPH", "5"))
TOP_K_RERANK = int(os.environ.get("TOP_K_RERANK", "4"))
MAX_CONTEXT_TOKENS = int(os.environ.get("MAX_CONTEXT_TOKENS", "4000"))
ENABLE_RERANK = os.environ.get("ENABLE_RERANK", "false").lower() == "true"
RERANK_TIMEOUT = int(os.environ.get("RERANK_TIMEOUT", "60"))
GENERATE_TIMEOUT = int(os.environ.get("GENERATE_TIMEOUT", "300"))

# ── 服务配置 ──
HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", "8000"))

# ── CORS 配置 ──
# 允许的前端来源（逗号分隔），默认允许本地开发
CORS_ORIGINS = os.environ.get(
    "CORS_ORIGINS",
    "http://localhost:8000,http://127.0.0.1:8000,http://localhost:3000"
).split(",")

# ── Wav2Lip 远程推理 (Windows + RTX 3050) ──
WAV2LIP_SERVER_URL = os.environ.get("WAV2LIP_SERVER_URL", None)

# ── 输入限制 ──
MAX_QUESTION_LENGTH = int(os.environ.get("MAX_QUESTION_LENGTH", "2000"))
MAX_TTS_LENGTH = int(os.environ.get("MAX_TTS_LENGTH", "5000"))