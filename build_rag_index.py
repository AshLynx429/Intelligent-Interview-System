import json
from pathlib import Path
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.utils import embedding_functions

# 加载数据
json_path = Path(__file__).parent / "data" / "reference_answers.json"
with open(json_path, "r", encoding="utf-8") as f:
    data = json.load(f)

# 构建文档列表：每个文档是“问题 + 参考答案”
documents = []
metadatas = []
ids = []
doc_id = 0

for category, qa_dict in data.items():
    for question, answer in qa_dict.items():
        # 文档内容：问题和答案拼接
        doc_text = f"问题：{question}\n参考答案：{answer}"
        documents.append(doc_text)
        metadatas.append({
            "category": category,
            "question": question,
            "answer": answer
        })
        ids.append(f"doc_{doc_id}")
        doc_id += 1

print(f"共加载 {len(documents)} 条文档")

# 初始化 Chroma 客户端（持久化到本地）
persist_dir = Path(__file__).parent / "rag_index"
persist_dir.mkdir(exist_ok=True)

client = chromadb.PersistentClient(path=str(persist_dir))

# 使用 sentence-transformers 作为 embedding 函数
embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

# 创建或获取 collection
collection = client.get_or_create_collection(
    name="interview_qa",
    embedding_function=embedding_fn
)

# 批量添加文档（如果 collection 已有数据，先清空）
existing = collection.get()
if existing["ids"]:
    collection.delete(ids=existing["ids"])

collection.add(
    documents=documents,
    metadatas=metadatas,
    ids=ids
)

print(f"向量库构建完成，共 {collection.count()} 条文档")