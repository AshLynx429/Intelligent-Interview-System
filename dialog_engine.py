from enum import Enum, auto
import json
from pathlib import Path
from model_service import ModelService


def get_data_path(filename: str) -> Path:
    """获取 data 文件夹下的文件路径"""
    return Path(__file__).resolve().parent.parent / "data" / filename


class InterviewState(Enum):
    INITIAL = auto()
    GREETING = auto()
    QUESTIONING = auto()
    ANSWERING = auto()
    PROBING = auto()
    FEEDBACK = auto()
    TERMINATED = auto()


class InterviewDialogEngine:
    def __init__(self):
        self.current_state = InterviewState.INITIAL  # 从初始状态开始
        self.session_data = {  # 会话数据（记录面试全过程）
            "qa_records": [],   # 问答记录（问题、答案、评分）
            "questions": [],  # 题目列表
            "probing_map": {},  # 追问映射（哪些问题有追问）
            "position": "",  # 应聘职位
            "prob_count": 0  # 已追问次数
        }
        self.model_service = ModelService()  # 创建评分器
        self._init_user_info()  # 收集姓名、职位
        self._init_questions()  # 加载题目

    def _init_user_info(self):
        print("=== 智能面试系统 ===")
        name = input("请输入您的姓名：")
        self.session_data["position"] = input("请输入应聘职位：")
        print(f"\n{name}你好，欢迎参加本次面试！")

    def _init_questions(self):
        # 1. 加载题库
        json_path = get_data_path("reference_answers.json")
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # 2. 根据职位关键词，自动匹配技能领域
        position = self.session_data["position"]
        matched_categories = []

        # 规则匹配：如果职位包含"Python"，就加Python相关的题
        if "Python" in position or "算法" in position or "开发" in position:
            matched_categories.append("Python")
        if "系统" in position or "架构" in position or "分布式" in position:
            matched_categories.append("分布式系统")
        if "数据" in position or "数据库" in position:
            matched_categories.append("数据库")

        # 如果没有匹配到任何领域，默认取前两个
        if not matched_categories:
            matched_categories = list(data.keys())[:2]

        # 3. 从匹配的领域里取题目
        self.session_data["questions"] = []
        for category in matched_categories:
            if category in data:
                questions = list(data[category].keys())
                self.session_data["questions"].extend(questions[:3])  # 每个领域取前3道

        self.session_data["questions"] = self.session_data["questions"][:6]  # 总共不超过6道

    def start_interview(self):
        while self.current_state != InterviewState.TERMINATED:
            self._handle_state()

    def _handle_state(self):
        if self.current_state == InterviewState.INITIAL:
            self._transition(InterviewState.GREETING)

        elif self.current_state == InterviewState.GREETING:
            self._transition(InterviewState.QUESTIONING)

        elif self.current_state == InterviewState.QUESTIONING:
            answered = len([r for r in self.session_data["qa_records"] if not r.get("is_probing")])
            if answered < len(self.session_data["questions"]):
                question = self.session_data["questions"][answered]
                print(f"\n[问题 {answered + 1}] {question}")
                self.session_data["qa_records"].append({
                    "question": question,
                    "answer": None,
                    "is_probing": False
                })
                self._transition(InterviewState.ANSWERING)
            else:
                self._transition(InterviewState.FEEDBACK)

        elif self.current_state == InterviewState.ANSWERING:
            answer = input("\n请输入回答：").strip()
            current_qa = self.session_data["qa_records"][-1]
            current_qa["answer"] = answer

            result = self.model_service.process_evaluation(
                answer,
                self._get_question_category(current_qa["question"]),
                current_qa["question"]
            )
            current_qa["evaluation"] = result
            print(f"\n[系统] 得分：{result['metrics']['composite_score']}，难度：{result['new_difficulty']}")

            if (result['metrics']['composite_score'] < 80 and self.session_data["prob_count"] < 2):
                # 动态生成追问
                probing_question = self.model_service.generate_probing_question(
                    current_qa["question"],
                    answer
                )
                # 记录到 probing_map
                self.session_data["probing_map"][current_qa["question"]] = probing_question
                self._transition(InterviewState.PROBING)

        elif self.current_state == InterviewState.PROBING:
            last_question = self.session_data["qa_records"][-1]["question"]
            probing_question = self.session_data["probing_map"].get(last_question)
            if probing_question:
                print(f"\n[追问] {probing_question}")
                self.session_data["qa_records"].append({
                    "question": probing_question,
                    "answer": None,
                    "is_probing": True
                })
                self.session_data["prob_count"] += 1
                self._transition(InterviewState.ANSWERING)
            else:
                self._transition(InterviewState.QUESTIONING)

        elif self.current_state == InterviewState.FEEDBACK:
            print("\n=== 面试结束 ===")
            self._transition(InterviewState.TERMINATED)

    def _get_question_category(self, question: str) -> str:
        json_path = get_data_path("reference_answers.json")
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        for category, questions in data.items():
            if question in questions:
                return category
        return "分布式系统"

    def _transition(self, new_state: InterviewState):
        self.current_state = new_state