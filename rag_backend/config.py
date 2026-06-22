"""
RAG 系统配置文件
"""
import os

# ── 路径配置 ──
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
TEXTBOOK_DIR = os.path.join(DATA_DIR, "textbooks")
CHROMA_DIR = os.path.join(BASE_DIR, "chroma_db")

# ── Neo4j 配置 ──
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "ml2026kg"

# ── Ollama 配置 ──
OLLAMA_BASE_URL = "http://localhost:11434"
LLM_MODEL = "qwen3.5:9b"             # Qwen3.5 9B，最新一代，推理能力更强
EMBEDDING_MODEL = "bge-m3"           # 中文 embedding 效果远优于 nomic-embed-text

# ── RAG 配置 ──
CHUNK_SIZE = 600            # 文本切片大小（字符数），增大以保留更多上下文
CHUNK_OVERLAP = 100         # 切片重叠（字符数）
TOP_K_VECTOR = 6            # 向量检索返回 Top-K 条（增大后重排序筛选）
TOP_K_GRAPH = 5             # 图谱检索返回关联概念数（增大覆盖更多相关知识）
TOP_K_RERANK = 4            # 重排序后保留的 Top-K 条文档
MAX_CONTEXT_TOKENS = 4000   # Prompt 中上下文最大 token 数
ENABLE_RERANK = False       # 是否启用 LLM 重排序（首次测试关闭，后续可开启）
RERANK_TIMEOUT = 60         # 重排序请求超时（秒）
GENERATE_TIMEOUT = 300      # 生成请求超时（秒）

# ── 服务配置 ──
HOST = "0.0.0.0"
PORT = 8000
