# 智能面试系统

基于 ChatGLM-6b 大语言模型的智能面试系统。支持多轮对话、答案评分、动态难度调整。

## 技术栈

- Python 3.8
- PyTorch + Transformers
- ChatGLM-6b (4-bit量化)
- jieba分词
- Matplotlib

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 下载模型到 models/chatglm-6b-4bit/

# 3. 运行测试
python tests/test_model.py

# 4. 启动面试
python main.py
项目结构
text
src/                # 核心代码
├── config.py           # 配置
├── model_service.py    # 模型加载+评分
├── dialog_engine.py    # 对话流程
└── evaluation.py       # 报告生成
data/               # 数据文件
tests/              # 测试文件
reports/            # 输出报告
当前状态
模型加载与对话 ✅

关键词评分 ✅

动态难度调整 ✅

语义评分 🚧（计划优化）