"""
向量检索模块 v2 — bge-m3 + 改进切片策略
改进：章节感知切片、元数据增强、bge-m3 中文 embedding
"""
import os
import re
import hashlib
import chromadb
from chromadb.utils import embedding_functions
from config import (
    CHROMA_DIR, OLLAMA_BASE_URL, EMBEDDING_MODEL,
    CHUNK_SIZE, CHUNK_OVERLAP, TEXTBOOK_DIR, TOP_K_VECTOR,
)


class VectorSearch:
    """封装 ChromaDB 向量数据库操作（v2 优化版）"""

    def __init__(self):
        self.client = chromadb.PersistentClient(path=CHROMA_DIR)
        self.embed_fn = embedding_functions.OllamaEmbeddingFunction(
            url=f"{OLLAMA_BASE_URL}/api/embeddings",
            model_name=EMBEDDING_MODEL,
        )
        # 使用 embedding model 名称作为 collection 后缀，切换模型时自动重建
        collection_name = f"ml_docs_{EMBEDDING_MODEL.replace('-', '_')}"
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embed_fn,
            metadata={"hnsw:space": "cosine"},
        )

    # ── 文档处理 ──

    @staticmethod
    def _extract_sections(text: str) -> list[dict]:
        """
        将文本按 Markdown 标题拆分为多个段落（section）
        每个 section 包含标题和内容
        """
        sections = []
        current_title = ""
        current_content = []

        for line in text.split("\n"):
            # 匹配 # / ## / ### 标题
            heading_match = re.match(r'^(#{1,3})\s+(.+)', line)
            if heading_match:
                # 保存上一个 section
                if current_content:
                    sections.append({
                        "title": current_title,
                        "content": "\n".join(current_content).strip(),
                    })
                current_title = heading_match.group(2).strip()
                current_content = []
            else:
                current_content.append(line)

        # 保存最后一个 section
        if current_content:
            sections.append({
                "title": current_title,
                "content": "\n".join(current_content).strip(),
            })

        return sections if sections else [{"title": "", "content": text}]

    @staticmethod
    def chunk_text(text: str, chunk_size: int = CHUNK_SIZE,
                   overlap: int = CHUNK_OVERLAP) -> list[dict]:
        """
        章节感知切片：
        1. 先按标题拆分 section
        2. 每个 section 内按段落聚合，超过 chunk_size 时按句子拆分
        3. 每个 chunk 携带 section 标题作为上下文前缀
        返回 list[dict]，每项含 content、section_title
        """
        sections = VectorSearch._extract_sections(text)
        chunks = []

        for section in sections:
            title = section["title"]
            body = section["content"]
            if not body.strip():
                continue

            # 按段落拆分
            paragraphs = [p.strip() for p in body.split("\n\n") if p.strip()]

            current_chunk = ""
            for para in paragraphs:
                if len(para) > chunk_size:
                    # 长段落按句子拆分
                    sentences = re.split(r'(?<=[。！？；\.\!\?;])', para)
                    for sent in sentences:
                        sent = sent.strip()
                        if not sent:
                            continue
                        if len(current_chunk) + len(sent) <= chunk_size:
                            current_chunk += sent
                        else:
                            if current_chunk:
                                chunks.append({
                                    "content": current_chunk.strip(),
                                    "section_title": title,
                                })
                            current_chunk = sent
                else:
                    if len(current_chunk) + len(para) + 2 <= chunk_size:
                        current_chunk += ("\n\n" + para) if current_chunk else para
                    else:
                        if current_chunk:
                            chunks.append({
                                "content": current_chunk.strip(),
                                "section_title": title,
                            })
                        current_chunk = para

            if current_chunk.strip():
                chunks.append({
                    "content": current_chunk.strip(),
                    "section_title": title,
                })

        # 添加上下文前缀（section 标题）和重叠
        result = []
        for i, chunk in enumerate(chunks):
            # 添加 section 标题作为上下文
            prefix = f"[{chunk['section_title']}] " if chunk["section_title"] else ""
            content = prefix + chunk["content"]

            # 重叠：将前一个 chunk 的尾部追加到当前 chunk
            if overlap > 0 and i > 0:
                prev_content = chunks[i - 1]["content"]
                prev_tail = prev_content[-overlap:] if len(prev_content) > overlap else prev_content
                content = prev_tail + "\n" + content

            result.append({
                "content": content.strip(),
                "section_title": chunk["section_title"],
            })

        return result

    def ingest_file(self, filepath: str) -> int:
        """
        读取文件并切片存入 ChromaDB
        返回新增的 chunk 数量
        """
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()

        filename = os.path.basename(filepath)
        # 从文件名提取章节信息（如 "06_支持向量机.txt"）
        chapter_match = re.match(r'(\d+)_(.+)\.txt', filename)
        chapter_num = chapter_match.group(1) if chapter_match else ""
        chapter_name = chapter_match.group(2) if chapter_match else filename

        chunks = self.chunk_text(text)
        if not chunks:
            return 0

        ids = []
        documents = []
        metadatas = []

        for i, chunk in enumerate(chunks):
            doc_id = hashlib.md5(
                f"{EMBEDDING_MODEL}:{filepath}:{i}:{chunk['content'][:50]}".encode()
            ).hexdigest()
            ids.append(doc_id)
            documents.append(chunk["content"])
            metadatas.append({
                "source": filename,
                "chapter": chapter_name,
                "chapter_num": chapter_num,
                "section": chunk["section_title"],
                "chunk_index": i,
                "total_chunks": len(chunks),
            })

        # 幂等导入
        existing = self.collection.get(ids=ids)
        existing_ids = set(existing["ids"]) if existing["ids"] else set()

        new_ids = [id for id in ids if id not in existing_ids]
        if not new_ids:
            return 0

        # O(1) 查找：先构建 {id: index} 字典
        id_to_idx = {id: i for i, id in enumerate(ids)}
        new_indices = [id_to_idx[id] for id in new_ids]
        self.collection.add(
            ids=[ids[i] for i in new_indices],
            documents=[documents[i] for i in new_indices],
            metadatas=[metadatas[i] for i in new_indices],
        )
        return len(new_ids)

    def ingest_directory(self, dirpath: str = TEXTBOOK_DIR) -> dict:
        """递归扫描目录下所有 .txt / .md 文件并导入"""
        results = {}
        for root, _, files in os.walk(dirpath):
            for fname in sorted(files):
                if fname.endswith((".txt", ".md")):
                    fpath = os.path.join(root, fname)
                    count = self.ingest_file(fpath)
                    results[fname] = count
        return results

    # ── 检索 ──

    def search(self, query: str, top_k: int = TOP_K_VECTOR) -> list[dict]:
        """语义检索：返回与查询最相关的文档切片"""
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )

        output = []
        if results and results["documents"]:
            for doc, meta, dist in zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0],
            ):
                output.append({
                    "content": doc,
                    "source": meta.get("source", "unknown"),
                    "chapter": meta.get("chapter", ""),
                    "section": meta.get("section", ""),
                    "chunk_index": meta.get("chunk_index", -1),
                    "relevance_score": round(1 - dist, 4),
                })
        return output

    def stats(self) -> dict:
        """返回向量库统计信息"""
        count = self.collection.count()
        return {
            "total_chunks": count,
            "collection": self.collection.name,
            "embedding_model": EMBEDDING_MODEL,
        }


# 便捷函数
_vs = None

def get_vector_search() -> VectorSearch:
    global _vs
    if _vs is None:
        _vs = VectorSearch()
    return _vs
