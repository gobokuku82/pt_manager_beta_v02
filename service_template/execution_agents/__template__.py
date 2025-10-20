"""
Execution Team Template
팀 개발 시 이 파일을 복사하여 시작하세요
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from langgraph.graph import StateGraph, START, END

import sys
from pathlib import Path
backend_dir = Path(__file__).parent.parent.parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# TODO: State 정의 임포트 (models/states.py에서 정의)
# from app.service_template.models.states import YourTeamState, SharedState

from app.service_template.foundation.agent_registry import AgentRegistry
from app.service_template.foundation.agent_adapter import AgentAdapter
# from app.service_template.llm_manager import LLMService  # LLM 필요시

logger = logging.getLogger(__name__)


class TemplateTeam:
    """
    팀 템플릿 클래스

    개발 가이드:
    1. 클래스명 변경: TemplateTeam → YourTeam (예: DataCollectionTeam)
    2. State 정의: models/states.py에 YourTeamState 정의
    3. 노드 구현: prepare, execute, aggregate, finalize
    4. Tool 연결: tools/ 폴더의 도구 임포트
    5. 서브그래프 구성: _build_subgraph() 수정
    """

    def __init__(self, llm_context=None):
        """
        초기화

        Args:
            llm_context: LLM 컨텍스트 (선택적)
        """
        self.llm_context = llm_context
        self.team_name = "template"  # TODO: 팀 이름 변경

        # LLM Service (필요시)
        # self.llm_service = LLMService(llm_context=llm_context)

        # Agent 초기화 (Registry 사용)
        self.available_agents = self._initialize_agents()

        # Tool 초기화 (도메인별로 구현)
        self._initialize_tools()

        # 서브그래프 구성
        self.app = None
        self._build_subgraph()

    def _initialize_agents(self) -> Dict[str, bool]:
        """
        사용 가능한 Agent 확인

        Returns:
            Agent 이름 → 사용 가능 여부 매핑
        """
        # TODO: 필요한 Agent 목록 정의
        agent_types = ["your_agent"]
        available = {}

        for agent_name in agent_types:
            available[agent_name] = agent_name in AgentRegistry.list_agents(enabled_only=True)

        logger.info(f"{self.team_name} Team available agents: {available}")
        return available

    def _initialize_tools(self):
        """
        Tool 초기화

        TODO: 도메인별 Tool 임포트 및 초기화
        """
        # 예시:
        # try:
        #     from app.service_template.tools.your_tool import YourTool
        #     self.your_tool = YourTool()
        #     logger.info("YourTool initialized successfully")
        # except Exception as e:
        #     logger.warning(f"YourTool initialization failed: {e}")
        #     self.your_tool = None
        pass

    def _build_subgraph(self):
        """
        서브그래프 구성

        TODO: 팀별 워크플로우 정의
        """
        # TODO: State 타입 지정
        # workflow = StateGraph(YourTeamState)

        # 노드 추가
        # workflow.add_node("prepare", self.prepare_node)
        # workflow.add_node("execute", self.execute_node)
        # workflow.add_node("aggregate", self.aggregate_results_node)
        # workflow.add_node("finalize", self.finalize_node)

        # 엣지 구성
        # workflow.add_edge(START, "prepare")
        # workflow.add_edge("prepare", "execute")
        # workflow.add_edge("execute", "aggregate")
        # workflow.add_edge("aggregate", "finalize")
        # workflow.add_edge("finalize", END)

        # self.app = workflow.compile()
        # logger.info(f"{self.team_name} Team subgraph built successfully")
        pass

    async def prepare_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        준비 노드 - 입력 처리 및 초기화

        Args:
            state: 팀 상태

        Returns:
            업데이트된 상태

        TODO: 팀별 준비 로직 구현
        """
        logger.info(f"[{self.team_name} Team] Preparing")

        state["team_name"] = self.team_name
        state["status"] = "in_progress"
        state["start_time"] = datetime.now()

        # TODO: 준비 로직 구현
        # - 입력 검증
        # - 파라미터 파싱
        # - 초기화

        return state

    async def execute_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        실행 노드 - 주요 작업 수행

        Args:
            state: 팀 상태

        Returns:
            업데이트된 상태

        TODO: 팀별 실행 로직 구현
        """
        logger.info(f"[{self.team_name} Team] Executing")

        # TODO: Tool 호출 또는 Agent 실행
        # 예시:
        # if self.your_tool:
        #     result = await self.your_tool.execute(query, params)
        #     state["results"] = result

        return state

    async def aggregate_results_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        결과 집계 노드

        Args:
            state: 팀 상태

        Returns:
            업데이트된 상태

        TODO: 결과 집계 로직 구현
        """
        logger.info(f"[{self.team_name} Team] Aggregating results")

        # TODO: 결과 집계
        # - 결과 검증
        # - 통계 계산
        # - 포맷 변환

        return state

    async def finalize_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        최종화 노드 - 상태 정리 및 완료

        Args:
            state: 팀 상태

        Returns:
            업데이트된 상태

        TODO: 완료 로직 구현
        """
        logger.info(f"[{self.team_name} Team] Finalizing")

        state["end_time"] = datetime.now()

        if state.get("start_time"):
            elapsed = (state["end_time"] - state["start_time"]).total_seconds()
            state["execution_time"] = elapsed

        # 상태 결정
        if state.get("error"):
            state["status"] = "failed"
        else:
            state["status"] = "completed"

        logger.info(f"[{self.team_name} Team] Completed with status: {state['status']}")
        return state

    async def execute(
        self,
        shared_state: Dict[str, Any],
        **kwargs
    ) -> Dict[str, Any]:
        """
        팀 실행 메인 메서드

        Args:
            shared_state: 공유 상태
            **kwargs: 추가 파라미터

        Returns:
            팀 실행 결과

        TODO: 초기 상태 구성 수정
        """
        # TODO: 초기 상태 생성 (YourTeamState 사용)
        initial_state = {
            "team_name": self.team_name,
            "status": "pending",
            "shared_context": shared_state,
            "start_time": None,
            "end_time": None,
            "error": None,
            # TODO: 팀별 필드 추가
        }

        # 서브그래프 실행
        try:
            final_state = await self.app.ainvoke(initial_state)
            return final_state
        except Exception as e:
            logger.error(f"{self.team_name} Team execution failed: {e}")
            initial_state["status"] = "failed"
            initial_state["error"] = str(e)
            return initial_state


# ==============================================================================
# 사용 예시 (테스트 코드)
# ==============================================================================

if __name__ == "__main__":
    async def test_template_team():
        """템플릿 팀 테스트"""

        # 팀 초기화
        team = TemplateTeam()

        # 공유 상태 생성
        shared_state = {
            "query": "테스트 쿼리",
            "session_id": "test_session",
            "user_query": "테스트 쿼리"
        }

        # 팀 실행
        result = await team.execute(shared_state)

        # 결과 출력
        print(f"Status: {result.get('status')}")
        print(f"Execution time: {result.get('execution_time', 0):.2f}s")

    import asyncio
    asyncio.run(test_template_team())
