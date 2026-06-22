"""
图谱查询模块 — 从 Neo4j 知识图谱中检索结构化知识
"""
from neo4j import GraphDatabase
from config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD


class GraphQuerier:
    """封装 Neo4j 图谱查询，为 RAG 提供结构化知识检索"""

    def __init__(self):
        self.driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

    def close(self):
        self.driver.close()

    # ── 核心查询方法 ──

    def search_concepts(self, keyword: str, limit: int = 5) -> list[dict]:
        """
        根据关键词模糊搜索知识点（不区分大小写）
        返回匹配的节点及其基本信息
        """
        query = """
        MATCH (n)
        WHERE toLower(n.name) CONTAINS toLower($keyword)
           OR toLower(n.description) CONTAINS toLower($keyword)
        RETURN labels(n)[0] AS type, n.name AS name,
               n.description AS description, n.chapter AS chapter
        ORDER BY CASE WHEN n.name = $keyword THEN 0 ELSE 1 END
        LIMIT $limit
        """
        with self.driver.session() as session:
            result = session.run(query, keyword=keyword, limit=limit)
            return [dict(record) for record in result]

    def get_prerequisites(self, concept_name: str, depth: int = 2) -> list[dict]:
        """
        查询某知识点的前置知识链（递归查找 PREREQUISITE_OF 的反向关系）
        """
        query = """
        MATCH path = (pre)-[:PREREQUISITE_OF*1..%d]->(target {name: $name})
        WITH pre, length(path) AS dist
        RETURN DISTINCT labels(pre)[0] AS type, pre.name AS name,
               pre.description AS description, dist AS distance
        ORDER BY dist
        """ % depth
        with self.driver.session() as session:
            result = session.run(query, name=concept_name)
            return [dict(record) for record in result]

    def get_related_concepts(self, concept_name: str, limit: int = 3) -> list[dict]:
        """
        查询与某知识点直接关联的所有概念（双向关系）
        包括 COMPARE_WITH、PART_OF、USED_IN 等关系
        """
        query = """
        MATCH (n {name: $name})-[r]-(m)
        WHERE type(r) IN ['COMPARE_WITH', 'PART_OF', 'USED_IN', 'EVALUATED_BY']
        RETURN DISTINCT type(r) AS relation, labels(m)[0] AS type,
               m.name AS name, m.description AS description
        LIMIT $limit
        """
        with self.driver.session() as session:
            result = session.run(query, name=concept_name, limit=limit * 3)
            return [dict(record) for record in result][:limit]

    def get_chapter_content(self, chapter_name: str) -> list[dict]:
        """
        查询某章节包含的所有知识点
        """
        query = """
        MATCH (c:Chapter {name: $chapter})-[:CONTAINS]->(n)
        RETURN labels(n)[0] AS type, n.name AS name, n.description AS description
        ORDER BY type, name
        """
        with self.driver.session() as session:
            result = session.run(query, chapter=chapter_name)
            return [dict(record) for record in result]

    def get_learning_path(self, start: str, end: str) -> list[dict]:
        """
        查询两个知识点之间的最短学习路径
        """
        query = """
        MATCH path = shortestPath(
            (a {name: $start})-[*..10]-(b {name: $end})
        )
        RETURN [node IN nodes(path) | {
            name: node.name,
            type: labels(node)[0],
            description: node.description
        }] AS path
        """
        with self.driver.session() as session:
            result = session.run(query, start=start, end=end)
            record = result.single()
            return record["path"] if record else []

    def get_algorithms_for_task(self, task_name: str) -> list[dict]:
        """
        查询适用于某任务类型的所有算法
        """
        query = """
        MATCH (a)-[:USED_IN]->(t:Task {name: $task})
        RETURN labels(a)[0] AS type, a.name AS name, a.description AS description
        """
        with self.driver.session() as session:
            result = session.run(query, task=task_name)
            return [dict(record) for record in result]

    # ── RAG 专用：综合图谱检索 ──

    def _get_all_concept_names(self) -> list[str]:
        """
        从图谱中获取所有知识点名称（按长度降序排列，优先匹配长名称）
        缓存在实例变量中避免重复查询
        """
        if not hasattr(self, '_concept_names_cache'):
            query = """
            MATCH (n)
            WHERE labels(n)[0] IN ['Concept', 'Algorithm', 'Method', 'Metric', 'Task', 'Chapter']
            RETURN n.name AS name
            ORDER BY size(n.name) DESC
            """
            with self.driver.session() as session:
                result = session.run(query)
                self._concept_names_cache = [r["name"] for r in result]
        return self._concept_names_cache

    def _extract_concepts_from_query(self, query_text: str) -> list[str]:
        """
        智能提取：将查询文本与图谱中所有已知概念名称做子串匹配
        优先匹配长名称（如"支持向量机"优先于"支持"）
        """
        names = self._get_all_concept_names()
        matched = []
        remaining = query_text

        for name in names:
            if len(name) < 2:
                continue
            if name in remaining:
                matched.append(name)
                # 从剩余文本中移除已匹配的部分，避免子串重复匹配
                remaining = remaining.replace(name, "", 1)

        return matched

    def retrieve_for_rag(self, query_text: str, top_k: int = 3) -> str:
        """
        RAG 图谱检索入口（优化版）：
        1. 用子串匹配从查询中提取图谱中的已知概念
        2. 获取每个匹配概念的描述、前置知识和关联概念
        3. 组装为结构化文本返回
        """
        matched_concepts = self._extract_concepts_from_query(query_text)

        all_knowledge = []
        seen_names = set()

        for concept_name in matched_concepts:
            # 查找该概念的完整信息
            concepts = self.search_concepts(concept_name, limit=1)
            for c in concepts:
                if c["name"] not in seen_names:
                    seen_names.add(c["name"])
                    all_knowledge.append(c)

                    # 获取前置知识
                    prereqs = self.get_prerequisites(c["name"], depth=1)
                    for p in prereqs[:2]:
                        if p["name"] not in seen_names:
                            seen_names.add(p["name"])
                            all_knowledge.append({
                                "type": p["type"],
                                "name": p["name"],
                                "description": f"[前置知识] {p['description']}",
                                "chapter": "",
                            })

                    # 获取关联概念（对比、组成、应用等）
                    related = self.get_related_concepts(c["name"], limit=3)
                    for r in related:
                        if r["name"] not in seen_names:
                            seen_names.add(r["name"])
                            all_knowledge.append({
                                "type": r["type"],
                                "name": r["name"],
                                "description": f"[{r['relation']}] {r['description']}",
                                "chapter": "",
                            })

            if len(all_knowledge) >= top_k * 4:
                break

        # 格式化为文本
        if not all_knowledge:
            return "（图谱中未找到直接相关的结构化知识）"

        lines = ["【知识图谱结构化知识】"]
        for i, k in enumerate(all_knowledge[:top_k * 4], 1):
            chap_info = f"（第{k['chapter']}章）" if k.get("chapter") else ""
            lines.append(f"{i}. [{k['type']}] {k['name']}{chap_info}：{k['description']}")

        return "\n".join(lines)


# 便捷函数
_querier = None

def get_graph_querier() -> GraphQuerier:
    global _querier
    if _querier is None:
        _querier = GraphQuerier()
    return _querier
