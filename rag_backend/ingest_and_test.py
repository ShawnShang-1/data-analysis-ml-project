#!/usr/bin/env python3
"""
将课程文档导入 ChromaDB 向量库
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from vector_search import get_vector_search

def main():
    vs = get_vector_search()

    print("📚 开始导入课程文档到 ChromaDB...")
    results = vs.ingest_directory()

    total = sum(results.values())
    print(f"\n导入结果:")
    for fname, count in results.items():
        status = f"新增 {count} 个切片" if count > 0 else "已存在（跳过）"
        print(f"  {fname}: {status}")

    print(f"\n总计新增: {total} 个文本切片")

    stats = vs.stats()
    print(f"向量库总切片数: {stats['total_chunks']}")

    # 测试检索
    print("\n🔍 测试检索...")
    test_queries = [
        "什么是支持向量机？",
        "决策树的信息增益怎么计算？",
        "深度学习中如何解决梯度消失问题？",
    ]

    for q in test_queries:
        results = vs.search(q, top_k=2)
        print(f"\n查询: {q}")
        for i, r in enumerate(results, 1):
            print(f"  [{i}] 相关度={r['relevance_score']}, 来源={r['source']}")
            print(f"      内容: {r['content'][:80]}...")


if __name__ == "__main__":
    main()
