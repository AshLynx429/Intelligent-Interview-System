from pathlib import Path
import chromadb
from chromadb.utils import embedding_functions

# 初始化 Chroma 客户端
persist_dir = Path(__file__).parent / "rag_index"
client = chromadb.PersistentClient(path=str(persist_dir))

# 使用相同的 embedding 函数
embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

collection = client.get_collection(
    name="interview_qa",
    embedding_function=embedding_fn
)


def search(query: str, top_k: int = 3):
    results = collection.query(
        query_texts=[query],
        n_results=top_k
    )

    print(f"\n查询：{query}\n")
    for i, (doc, meta, dist) in enumerate(zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0]
    )):
        # 距离越小越相似，转换为相似度分数
        similarity = 1 - dist
        print(f"结果 {i + 1} (相似度: {similarity:.3f})")
        print(f"  分类: {meta['category']}")
        print(f"  问题: {meta['question']}")
        print(f"  参考答案: {meta['answer'][:100]}...")
        print()


if __name__ == "__main__":
    # 示例查询
    query = input("请输入你的问题: ")
    search(query)