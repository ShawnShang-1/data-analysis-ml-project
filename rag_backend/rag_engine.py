"""
RAG 引擎 v2 — 优化版
改进：更好的 Prompt、LLM 重排序、引用追踪、Qwen3 适配
"""
import json
import httpx
from config import (
    OLLAMA_BASE_URL, LLM_MODEL, TOP_K_VECTOR, TOP_K_GRAPH,
    TOP_K_RERANK, MAX_CONTEXT_TOKENS, ENABLE_RERANK,
    RERANK_TIMEOUT, GENERATE_TIMEOUT,
)
from vector_search import get_vector_search
from graph_query import get_graph_querier


# ── System Prompt（优化版） ──

SYSTEM_PROMPT = """你是一位资深的机器学习课程助教"小智老师"，正在为大学生解答机器学习相关问题。

## 回答规范
1. **基于资料回答**：严格基于下方提供的参考资料（知识图谱 + 课程文档）。可以补充你的专业知识，但核心定义和公式必须与资料一致
2. **结构化回答**：先给出核心定义，再展开细节。如有公式请用 LaTeX 格式
3. **对比说明**：当问题涉及多个概念时，主动做对比分析（如 SVM vs 逻辑回归）
4. **前置知识**：如果回答涉及前置概念，简要提及并建议学生先学习
5. **诚实边界**：资料不足时明确告知，并建议查阅教材的具体章节
6. **语言**：中文

## 参考资料

### 一、知识图谱（结构化知识）
{graph_context}

### 二、课程文档（详细内容）
{vector_context}

---

## 学生问题
{question}

请基于以上参考资料，给出准确、清晰的回答。如果引用了特定章节内容，请在回答末尾标注来源。"""


# ── 重排序 Prompt ──

RERANK_PROMPT = """你是一个文档相关性评估专家。给定一个查询和多个文档片段，请按相关性从高到低排序，只返回排序后的文档编号列表。

查询：{query}

文档列表：
{documents}

请按相关性从高到低排列，只输出编号，用逗号分隔。例如：3,1,4,2"""


class RAGEngine:
    """双通道 RAG 引擎 v2：向量检索 + 图谱检索 + 重排序"""

    def __init__(self):
        self.vector_search = get_vector_search()
        self.graph_querier = get_graph_querier()

    def retrieve(self, question: str) -> dict:
        """双通道检索"""
        vector_results = self.vector_search.search(question, top_k=TOP_K_VECTOR)
        graph_context = self.graph_querier.retrieve_for_rag(question, top_k=TOP_K_GRAPH)
        return {
            "vector_raw": vector_results,
            "graph_context": graph_context,
        }

    def rerank(self, question: str, documents: list[dict]) -> list[dict]:
        """
        用 LLM 对检索结果做轻量级重排序
        当文档数量较多时，通过 LLM 判断哪些最相关
        """
        if not ENABLE_RERANK or len(documents) <= TOP_K_RERANK:
            return documents[:TOP_K_RERANK]

        # 构建重排序请求
        doc_list = []
        for i, d in enumerate(documents, 1):
            snippet = d["content"][:200]  # 只取前200字做判断
            doc_list.append(f"[{i}] {snippet}...")

        prompt = RERANK_PROMPT.format(
            query=question,
            documents="\n".join(doc_list),
        )

        try:
            response = httpx.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": LLM_MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.0,
                        "num_predict": 50,
                    },
                },
                timeout=RERANK_TIMEOUT,
            )
            response.raise_for_status()
            result_text = response.json().get("response", "").strip()

            # 解析排序结果（如 "3,1,4,2"）
            import re
            numbers = re.findall(r'\d+', result_text)
            ranked_indices = []
            for n in numbers:
                idx = int(n) - 1
                if 0 <= idx < len(documents) and idx not in ranked_indices:
                    ranked_indices.append(idx)

            # 按重排序结果重新排列，取 Top-K
            reranked = [documents[i] for i in ranked_indices[:TOP_K_RERANK]]
            # 补充未排到的（防止解析不全）
            seen = set(ranked_indices[:TOP_K_RERANK])
            for i, d in enumerate(documents):
                if i not in seen and len(reranked) < TOP_K_RERANK:
                    reranked.append(d)
            return reranked

        except Exception:
            # 重排序失败时降级为原始排序
            return documents[:TOP_K_RERANK]

    def build_prompt(self, question: str, retrieval: dict) -> str:
        """组装优化版 Prompt"""
        # 图谱上下文
        graph_ctx = retrieval["graph_context"]

        # 向量上下文（已重排序）
        reranked_docs = self.rerank(question, retrieval["vector_raw"])

        if reranked_docs:
            vector_lines = []
            for i, r in enumerate(reranked_docs, 1):
                vector_lines.append(
                    f"【片段 {i}】来源: {r['source']}，相关度: {r['relevance_score']}\n{r['content']}"
                )
            vector_ctx = "\n\n".join(vector_lines)
        else:
            vector_ctx = "（未检索到相关文档片段）"

        return SYSTEM_PROMPT.format(
            graph_context=graph_ctx,
            vector_context=vector_ctx,
            question=question,
        )

    def generate(self, question: str) -> dict:
        """完整的 RAG 生成流程（同步版）"""
        # 1. 双通道检索
        retrieval = self.retrieve(question)

        # 2. 组装 Prompt
        prompt = self.build_prompt(question, retrieval)

        # 3. 调用 Qwen3.5（关闭思考模式以加快响应）
        response = httpx.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": LLM_MODEL,
                "prompt": prompt,
                "stream": False,
                "think": False,  # 关闭 Qwen3.5 的思考模式，直接生成回答
                "options": {
                    "temperature": 0.3,
                    "top_p": 0.9,
                    "num_predict": 2048,
                },
            },
            timeout=GENERATE_TIMEOUT,
        )
        response.raise_for_status()
        result = response.json()

        # 清理 Qwen3 的 <think>...</think> 标签
        answer = result.get("response", "")
        answer = _strip_think_tags(answer)

        return {
            "question": question,
            "answer": answer,
            "sources": list(set(r["source"] for r in retrieval["vector_raw"])),
            "graph_context": retrieval["graph_context"],
        }

    async def generate_stream(self, question: str):
        """流式生成（SSE）"""
        retrieval = self.retrieve(question)
        prompt = self.build_prompt(question, retrieval)

        yield {
            "type": "metadata",
            "sources": list(set(r["source"] for r in retrieval["vector_raw"])),
            "graph_context": retrieval["graph_context"],
        }

        async with httpx.AsyncClient(timeout=GENERATE_TIMEOUT) as client:
            async with client.stream(
                "POST",
                f"{OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": LLM_MODEL,
                    "prompt": prompt,
                    "stream": True,
                    "think": False,
                    "options": {
                        "temperature": 0.3,
                        "top_p": 0.9,
                        "num_predict": 2048,
                    },
                },
            ) as response:
                async for line in response.aiter_lines():
                    if line:
                        data = json.loads(line)
                        if "response" in data:
                            yield {
                                "type": "token",
                                "content": data["response"],
                            }
                        if data.get("done"):
                            yield {"type": "done"}
                            break


def _strip_think_tags(text: str) -> str:
    """清理 Qwen3 的 <think>...</think> 思考过程标签"""
    import re
    return re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()


# 便捷函数
_engine = None

def get_rag_engine() -> RAGEngine:
    global _engine
    if _engine is None:
        _engine = RAGEngine()
    return _engine
