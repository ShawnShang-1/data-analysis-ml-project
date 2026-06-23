"""
FastAPI 主服务 — 提供 RAG 对话、图谱查询、文档导入、数字人等 API
"""
import json
import sys
import asyncio
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import Literal
from sse_starlette.sse import EventSourceResponse

from config import HOST, PORT, CORS_ORIGINS, NEO4J_URI, OLLAMA_BASE_URL, CHROMA_DIR, MAX_QUESTION_LENGTH
from rag_engine import get_rag_engine
from graph_query import get_graph_querier
from vector_search import get_vector_search

# 添加数字人模块路径
sys.path.insert(0, str(Path(__file__).parent.parent))
from digital_human import router as digital_human_router


# ── 生命周期管理 ──

@asynccontextmanager
async def lifespan(app: FastAPI):
    """启动和关闭时的资源管理"""
    # 启动
    print("🚀 RAG 服务启动中...")
    print(f"   Neo4j: {NEO4J_URI}")
    print(f"   Ollama: {OLLAMA_BASE_URL}")
    print(f"   ChromaDB: {CHROMA_DIR}")
    print(f"   CORS origins: {CORS_ORIGINS}")

    # 启动文件清理后台任务
    from digital_human.file_cleanup import start_cleanup_background
    start_cleanup_background()

    yield
    # 关闭
    querier = get_graph_querier()
    querier.close()
    print("👋 RAG 服务已关闭")


app = FastAPI(
    title="ML知识问答 RAG 系统",
    description="基于知识图谱 + 向量检索的机器学习课程智能问答",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS 中间件（限制允许的前端来源）
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# 注册数字人路由
app.include_router(digital_human_router)

# 前端静态文件（如果存在）
frontend_dir = Path(__file__).parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/ui", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")


# ── 请求/响应模型 ──

class ChatRequest(BaseModel):
    question: str = Field(..., max_length=MAX_QUESTION_LENGTH, description="用户问题")
    stream: bool = True

class ChatResponse(BaseModel):
    question: str
    answer: str
    sources: list[str]
    graph_context: str

class IngestResponse(BaseModel):
    results: dict
    total: int

class GraphQueryRequest(BaseModel):
    query_type: Literal["search", "prerequisites", "related", "chapter", "path", "task_algorithms"]
    params: dict = Field(default_factory=dict)


# ── API 路由 ──

@app.get("/")
async def root():
    return {
        "status": "running",
        "service": "ML知识问答 RAG 系统",
        "endpoints": [
            "/chat", "/chat/stream", "/graph/query", "/ingest", "/stats",
            "/digital_human/speak", "/digital_human/tts", "/digital_human/voices",
            "/digital_human/expressions", "/digital_human/viseme_map",
        ],
    }


@app.post("/chat")
async def chat(req: ChatRequest):
    """
    非流式对话接口 — 返回完整回答
    """
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="问题不能为空")

    try:
        engine = get_rag_engine()
        result = engine.generate(req.question)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成失败: {str(e)}")


@app.post("/chat/stream")
async def chat_stream(req: ChatRequest):
    """
    SSE 流式对话接口 — 逐步返回 token
    前端通过 EventSource 接收
    """
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="问题不能为空")

    engine = get_rag_engine()

    async def event_generator():
        try:
            async for chunk in engine.generate_stream(req.question):
                yield {
                    "event": chunk["type"],
                    "data": json.dumps(chunk, ensure_ascii=False),
                }
        except Exception as e:
            yield {
                "event": "error",
                "data": json.dumps({"error": str(e)}, ensure_ascii=False),
            }

    return EventSourceResponse(event_generator())


@app.post("/graph/query")
async def graph_query(req: GraphQueryRequest):
    """
    知识图谱查询接口
    query_type: search | prerequisites | related | chapter | path | task_algorithms
    """
    querier = get_graph_querier()
    qt = req.query_type
    p = req.params

    try:
        if qt == "search":
            return querier.search_concepts(p.get("keyword", ""), p.get("limit", 5))
        elif qt == "prerequisites":
            return querier.get_prerequisites(p["concept"], p.get("depth", 2))
        elif qt == "related":
            return querier.get_related_concepts(p["concept"], p.get("limit", 3))
        elif qt == "chapter":
            return querier.get_chapter_content(p["chapter"])
        elif qt == "path":
            return querier.get_learning_path(p["start"], p["end"])
        elif qt == "task_algorithms":
            return querier.get_algorithms_for_task(p["task"])
        else:
            raise HTTPException(status_code=400, detail=f"未知查询类型: {qt}")
    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"缺少参数: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")


@app.post("/ingest")
async def ingest_documents():
    """
    导入课程文档到向量库
    扫描 data/textbooks/ 目录下的所有 .txt/.md 文件
    """
    try:
        vs = get_vector_search()
        results = vs.ingest_directory()
        total = sum(results.values())
        return {"results": results, "total": total, "vector_stats": vs.stats()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导入失败: {str(e)}")


@app.get("/stats")
async def stats():
    """系统状态统计"""
    from config import LLM_MODEL, EMBEDDING_MODEL
    vs = get_vector_search()
    return {
        "vector_db": vs.stats(),
        "neo4j": "connected",
        "llm_model": LLM_MODEL,
        "embedding_model": EMBEDDING_MODEL,
    }


# ── 启动入口 ──

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT, reload=False)
