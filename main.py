# -*- coding: utf-8 -*-
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from dialog_engine import InterviewDialogEngine
from evaluation.evaluation import EvaluationReport

if __name__ == "__main__":
    engine = InterviewDialogEngine()
    engine.start_interview()

    report = EvaluationReport.generate_report(engine.session_data["qa_records"])
    print(report)