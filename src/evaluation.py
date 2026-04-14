import matplotlib.pyplot as plt
import os
from datetime import datetime
from config import ModelServiceConfig
from pathlib import Path

class EvaluationReport:
    @staticmethod
    def generate_report(qa_records: list, report_dir=None) -> str:
        # 应用字体配置
        plt.rcParams.update(ModelServiceConfig.PLT_FONT_CONFIG)

        # 设置报告目录
        if not report_dir:
            report_dir = Path(__file__).parent.parent / "reports"

        # 确保报告目录存在
        os.makedirs(report_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        txt_path = os.path.join(report_dir, f"report_{timestamp}.txt")
        img_path = os.path.join(report_dir, f"chart_{timestamp}.png")

        # 生成文本报告
        text = "=== 面试评估报告 ===\n"
        for i, record in enumerate(qa_records):
            text += f"问题{i + 1}: {record['question']}\n得分: {record['evaluation']['metrics']['composite_score']}\n"

        # 生成可视化图表
        if len(qa_records) > 0:
            plt.figure(figsize=(10, 5))
            scores = [r["evaluation"]["metrics"]["composite_score"] for r in qa_records]
            plt.bar(range(len(scores)), scores, color='skyblue')
            plt.title("面试评分趋势")
            plt.xlabel("问题序号")
            plt.ylabel("得分")
            plt.ylim(0, 100)
            plt.savefig(img_path)
            plt.close()
        else:
            img_path = "无评分数据，未生成图表"

        # 保存文本报告
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(text + f"\n可视化报告: {img_path}")

        return text + f"\n完整报告已保存至: {txt_path}"