# Intelligent-Interview-System (智能面试系统)

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![Model](https://img.shields.io/badge/LLM-ChatGLM--6B--4bit-red.svg)](https://huggingface.co/THUDM/chatglm-6b)
[![Database](https://img.shields.io/badge/VectorDB-ChromaDB-green.svg)](https://www.trychroma.com/)

## 📌 项目简介
本项目是一款基于 **ChatGLM-6B** 大规模语言模型的智能面试系统。通过集成 **RAG (检索增强生成)** 技术与 **4-bit 量化部署**，实现了从职位提问、多维打分到动态追问的全链路面试自动化。

## 🌟 核心亮点
- **5维度评估体系**：设计了包含准确性、完整性、逻辑性、表达性、响应速度在内的评分维度，通过 Prompt Engineering 实现自动化量化评分，评估一致性达 **85%**。
- **RAG 驱动的动态追问**：基于 **ChromaDB** 与 **sentence-transformers** 构建自研知识库。经对比实验优化 Top-k 参数，使面试追问的相关度较基准提升 **40%**。
- **高性能 4-bit 量化**：利用 `bitsandbytes` 对模型进行 NF4 量化，首字响应延迟（RT）显著降低至 **0.9s**，支持在消费级 GPU 上流畅运行。
- **多 Agent 协作架构**：解耦提问官、评估官、追问官与报告官角色，实现面试流程的高度自动化与结构化报告产出。

## 🏗️ 系统架构
```text
[用户回答] -> [Qwen-3ASR (语音转文本)] -> [对话引擎]
                                          |
        +---------------------------------+---------------------------------+
        |                                 |                                 |
 [RAG 检索 (ChromaDB)]           [5维度评估官 (ChatGLM)]           [追问官 Agent]
        |                                 |                                 |
 [参考答案匹配] <-----------------> [Prompt 打分] <------------------> [动态生成追问]
                                          |
                                 [报告官: 生成结构化报告]
📊 评估指标定义
维度	计算策略	权重
准确性 (Accuracy)	基于 RAG 检索结果的关键词命中率 + 模型语义匹配	30%
完整性 (Completeness)	候选人回答对参考要点的覆盖范围长度占比	25%
逻辑性 (Logic)	针对连接词、因果推理结构的语法连贯性分析	20%
表达性 (Expression)	语言流畅度、句子平均长度及语义清晰度评分	15%
响应速度 (Performance)	系统推理时延与用户交互反馈效率	10%
🚀 快速开始
1. 环境准备
git clone https://github.com/AshLynx429/Intelligent-Interview-System.git
cd Intelligent-Interview-System
pip install -r requirements.txt
2. 模型下载
请将 chatglm-6b-int4 模型放置于 models/ 目录下。

3. 运行面试系统
python main.py
📈 实验报告示例
系统会自动在 reports/ 目录下生成：

结构化文本报告：包含每一轮对话的分项得分与建议。
可视化雷达图：直观展示候选人的各项能力分布（如下图示例）。
<img src="https://via.placeholder.com/600x300?text=Radar+Chart+Example" width="500">
🛠️ 技术栈
LLM: ChatGLM-6B (Int4)
Vector DB: ChromaDB
Embedding: Sentence-Transformers (paraphrase-multilingual-MiniLM-L12-v2)
Quantization: BitsAndBytes / Accelerate
NLP Tools: Jieba, PyTorch
Visualization: Matplotlib, Numpy