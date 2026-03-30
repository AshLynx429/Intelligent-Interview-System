import os
import torch
import jieba
import jieba.analyse
import json
from typing import Dict, Tuple
from transformers import AutoModel, AutoTokenizer
from config import ModelServiceConfig
from pathlib import Path


def get_reference_answer(skill: str, question: str) -> str:
    """从 data/reference_answers.json 读取参考答案"""
    json_path = Path(__file__).parent.parent / "data" / "reference_answers.json"
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get(skill, {}).get(question, "无相关参考答案")
    except Exception as e:
        print(f"参考答案加载失败: {str(e)}")
        return "无相关参考答案"

# === 全局初始化 ===
os.environ["BITSANDBYTES_NOWELCOME"] = "1"  # 禁用欢迎信息
os.environ["QUANT_KERNEL_SKIP_COMPILE"] = "1"  # 跳过内核编译
os.environ["TOKENIZERS_PARALLELISM"] = "false"  # 禁用分词器并行


class AdaptiveEvaluator:
    """动态评分与难度调节引擎"""

   # 初始化时接收一份配置，给系统设置一个初始难度："中级"
    def __init__(self, config: ModelServiceConfig):
        self.config = config
        self.difficulty_level = "中级"

    def evaluate_response(self, answer: str, skill: str, question: str) -> Tuple[Dict, str]:
        reference = get_reference_answer(skill, question)  #获取参考答案
        metrics = self._calculate_metrics(answer, reference)  #计算评估指标
        new_level = self._adjust_difficulty(metrics["composite_score"])  #调整难度级别
        return metrics, new_level  #返回包含详细评分的字典和新的难度级别

    def _calculate_metrics(self, answer: str, reference: str) -> Dict[str, float]:
        # 关键词匹配（50%权重）
        keywords = []
        accuracy = 30.0  # 保底分

        if reference and reference != "无相关参考答案，请人工评估":
            keywords = jieba.analyse.extract_tags(reference, topK=self.config.KEYWORD_TOP_K)
            if keywords:
                matched = sum(1 for kw in keywords if kw in answer)
                accuracy = round(matched / len(keywords) * 50, 2)

        # 完整性计算（40%权重）
        ref_len = max(len(reference), 1) if reference else 1
        completeness = round(min(len(answer) / ref_len * 40, 40), 2)

        return {
            "accuracy": accuracy,
            "completeness": completeness,
            "response_speed": 10.0,  # 固定速度分
            "composite_score": round(accuracy + completeness + 10, 2)
        }

    def _adjust_difficulty(self, score: float) -> str:
        # 百分制难度调整
        if score >= 80:
            return "高级"
        elif score >= 60:
            return "中级"
        else:
            return "初级"


class ModelService:

    #模型服务接口
    def __init__(self):
        self.config = ModelServiceConfig()
        self.evaluator = AdaptiveEvaluator(self.config)
        self.model, self.tokenizer = self._load_model()

    def _load_model(self) -> tuple:
        # 获取模型文件夹的路径
        model_path = Path(self.config.MODEL_PATH)

        # 设置一个临时文件夹，用来放放不下的数据
        offload_dir = Path(__file__).parent.parent / "offload"
        offload_dir.mkdir(parents=True, exist_ok=True)

        # 加载分词器（把文字变成数字）
        tokenizer = AutoTokenizer.from_pretrained(
            str(model_path),
            trust_remote_code=True  # 允许运行模型自带的代码
        )
        # 加载模型本身
        model = AutoModel.from_pretrained(
            str(model_path),
            trust_remote_code=True,
            device_map="auto",  #让Pytorch自动分配GPU/CPU
            offload_folder=str(offload_dir),  # 显存不够时，临时放这里
            torch_dtype=torch.float16  # 用半精度，省显存
        ).half().cuda().eval()  # 转半精度 → 移到 GPU → 设为评估模式

        return model, tokenizer

    def process_evaluation(self, answer: str, skill: str, question: str) -> Dict:
        try:
            metrics, new_level = self.evaluator.evaluate_response(answer, skill, question)
            return {"metrics": metrics, "new_difficulty": new_level}
        except Exception as e:
            return {"error": str(e)}