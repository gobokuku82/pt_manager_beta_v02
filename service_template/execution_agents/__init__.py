"""
Execution Agents Module - 실행 레이어
각 Executor는 독립적으로 작업을 실행하는 Agent

기본 제공:
- SearchExecutor (검색 팀 - 참고용)
- DocumentExecutor (문서 팀 - 참고용)
- AnalysisExecutor (분석 팀 - 참고용)

도메인별로 새로운 Executor 추가:
- __template__.py 복사하여 시작
"""

# 참고용 Executor (service_agent에서 복사됨)
from .search_executor import SearchExecutor
from .document_executor import DocumentExecutor
from .analysis_executor import AnalysisExecutor

__all__ = [
    "SearchExecutor",
    "DocumentExecutor",
    "AnalysisExecutor"
]
