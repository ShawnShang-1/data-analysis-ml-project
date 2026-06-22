"""
FastAPI 主服务 — 提供 RAG 对话、图谱查询、文档导入等 API
"""
import json
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from config import HOST, PORT
from rag_engine import get_rag_engine
from graph_query import get_graph_querier
from vector_search import get_vector_search


# ── 生命周期管理 ──

@asynccontextmanager
async def lifespan(app: FastAPI):
    """启动和关闭时的资源管理"""
    # 启动
    print("🚀 RAG 服务启动中...")
    print(f"   Neo4j: bolt://localhost:7687")
    print(f"   Ollama: http://localhost:11434")
    print(f"   ChromaDB: ./chroma_db")
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

# CORS 中间件（允许前端跨域访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── 请求/响应模型 ──

class ChatRequest(BaseModel):
    question: str
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
    query_type: str  # search | prerequisites | related | chapter | path
    params: dict


# ── API 路由 ──

@app.get("/")
async def root():
    return {
        "status": "running",
        "service": "ML知识问答 RAG 系统",
        "endpoints": ["/chat", "/chat/stream", "/graph/query", "/ingest", "/stats"],
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
