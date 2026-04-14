from enum import Enum, auto
import json
from pathlib import Path
from model_service.model_service import ModelService


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
        self.current_state = InterviewState.INITIAL
        self.session_data = {
            "qa_records": [],
            "questions": [],
            "probing_map": {},
            "position": "",
            "prob_count": 0
        }
        self.model_service = ModelService()
        self._init_user_info()
        self._init_questions()

    def _init_user_info(self):
        print("=== 智能面试系统 ===")
        name = input("请输入您的姓名：")
        self.session_data["position"] = input("请输入应聘职位：")
        print(f"\n{name}你好，欢迎参加本次面试！")

    def _init_questions(self):
        position_map = {"高级系统工程师": ["分布式系统", "系统设计"]}
        json_path = get_data_path("reference_answers.json")

        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        categories = position_map.get(self.session_data["position"], [])
        self.session_data["questions"] = []
        for category in categories:
            self.session_data["questions"].extend(list(data.get(category, {}).keys())[:3])

        self.session_data["questions"] = self.session_data["questions"][:6]
        self._build_prob_map()

    def _build_prob_map(self):
        self.session_data["probing_map"] = {
            "请解释CAP定理": "请举例说明CAP定理在实际系统中的应用",
            "如何设计高并发系统？": "请详细说明缓存机制的设计要点"
        }

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

            if (result['metrics']['composite_score'] < 80
                    and self.session_data["prob_count"] < 2
                    and current_qa["question"] in self.session_data["probing_map"]):
                self._transition(InterviewState.PROBING)
            else:
                self._transition(InterviewState.QUESTIONING)

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