import os
import matplotlib.pyplot as plt

# 获取当前文件所在的目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# 项目根目录
ROOT_DIR = os.path.dirname(BASE_DIR)

class ModelServiceConfig:
    MODEL_PATH = os.path.join(ROOT_DIR, "models", "chatglm-6b-4bit")
    DIFFICULTY_LEVELS = ["初级", "中级", "高级"]
    DIFFICULTY_THRESHOLDS = {'upgrade': 80, 'downgrade': 60}
    KEYWORD_TOP_K = 5
    DEBUG_MODE = False
    PLT_FONT_CONFIG = {
        "font.family": "Microsoft YaHei",
        "axes.unicode_minus": False
    }

class DataConfig:
    TECH_DICT_PATH = os.path.join(ROOT_DIR, "data", "tech_dict.txt")
    STOPWORDS_PATH = os.path.join(ROOT_DIR, "data", "stopwords.txt")
    RAW_DATASET_PATH = os.path.join(ROOT_DIR, "data", "raw_dataset.json")
    REFERENCE_ANSWERS_PATH = os.path.join(ROOT_DIR, "data", "reference_answers.json")
    PROCESSED_DATA_DIR = os.path.join(ROOT_DIR, "data", "processed")

# 初始化字体配置
plt.rcParams.update(ModelServiceConfig.PLT_FONT_CONFIG)