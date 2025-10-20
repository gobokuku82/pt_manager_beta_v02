"""
Main Supervisor Template
메인 Supervisor 개발 시 이 파일을 사용하세요
"""

import logging
import json
from typing import Dict, Any, List, Optional, Callable, Awaitable
from datetime import datetime
from langgraph.graph import StateGraph, START, END

import sys
from pathlib import Path
backend_dir = Path(__file__).parent.parent.parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# TODO: State 임포트 (models/states.py)
# from app.service_template.models.states import MainSupervisorState, SharedState, StateManager

# TODO: Planning Agent 임포트
# from app.service_template.cognitive_agents.planning_agent import PlanningAgent

# TODO: Execution Agents 임포트
# from app.service_template.execution_agents.team1 import Team1Executor
# from app.service_template.execution_agents.team2 import Team2Executor

from app.service_template.foundation.context import LLMContext, create_default_llm_context
from app.service_template.foundation.agent_registry import AgentRegistry

logger = logging.getLogger(__name__)


class MainSupervisor:
    """
    메인 Supervisor 템플릿

    개발 가이드:
    1. Planning Agent 연결
    2. Execution Agents (팀) 초기화
    3. 워크플로우 노드 구현
    4. 라우팅 로직 구현
    5. 응답 생성 로직 구현
    """

    def __init__(self, llm_context: LLMContext = None, enable_checkpointing: bool = True):
        """
        초기화

        Args:
            llm_context: LLM 컨텍스트
            enable_checkpointing: Checkpointing 활성화 여부
        """
        self.llm_context = llm_context or create_default_llm_context()
        self.enable_checkpointing = enable_checkpointing

        # Agent 시스템 초기화
        # TODO: Agent 등록 (필요시)
        # AgentRegistry.register(...)

        # TODO: Planning Agent 초기화
        # self.planning_agent = PlanningAgent(llm_context=llm_context)

        # TODO: 팀 초기화
        self.teams = {
            # "team1": Team1Executor(llm_context=llm_context),
            # "team2": Team2Executor(llm_context=llm_context),
        }

        # 워크플로우 구성
        self.app = None
        self._build_graph()

        logger.info(f"MainSupervisor initialized with {len(self.teams)} teams")

    def _build_graph(self):
        """
        워크플로우 그래프 구성

        TODO: State 타입 지정 및 노드 연결
        """
        # TODO: State 타입 지정
        # workflow = StateGraph(MainSupervisorState)

        # 노드 추가
        # workflow.add_node("initialize", self.initialize_node)
        # workflow.add_node("planning", self.planning_node)
        # workflow.add_node("execute_teams", self.execute_teams_node)
        # workflow.add_node("aggregate", self.aggregate_results_node)
        # workflow.add_node("generate_response", self.generate_response_node)

        # 엣지 구성
        # workflow.add_edge(START, "initialize")
        # workflow.add_edge("initialize", "planning")
        # workflow.add_conditional_edges(
        #     "planning",
        #     self._route_after_planning,
        #     {
        #         "execute": "execute_teams",
        #         "respond": "generate_response"
        #     }
        # )
        # workflow.add_edge("execute_teams", "aggregate")
        # workflow.add_edge("aggregate", "generate_response")
        # workflow.add_edge("generate_response", END)

        # self.app = workflow.compile()
        # logger.info("Main workflow graph built successfully")
        pass

    def _route_after_planning(self, state: Dict[str, Any]) -> str:
        """
        계획 후 라우팅

        Args:
            state: 메인 상태

        Returns:
            다음 노드 이름 ("execute" 또는 "respond")

        TODO: 라우팅 로직 구현
        """
        # 예시: 실행 계획이 있으면 실행, 없으면 바로 응답
        planning_state = state.get("planning_state")

        if planning_state and planning_state.get("execution_steps"):
            return "execute"
        else:
            return "respond"

    async def initialize_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        초기화 노드

        Args:
            state: 메인 상태

        Returns:
            업데이트된 상태

        TODO: 초기화 로직 구현
        """
        logger.info("[MainSupervisor] Initializing")

        state["start_time"] = datetime.now()
        state["status"] = "initialized"
        state["current_phase"] = "initialization"
        state["active_teams"] = []
        state["completed_teams"] = []
        state["failed_teams"] = []
        state["team_results"] = {}
        state["error_log"] = []

        return state

    async def planning_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        계획 수립 노드

        Args:
            state: 메인 상태

        Returns:
            업데이트된 상태

        TODO: Planning Agent 호출 및 실행 계획 생성
        """
        logger.info("[MainSupervisor] Planning phase")

        state["current_phase"] = "planning"

        # TODO: Planning Agent로 의도 분석
        # query = state.get("query", "")
        # intent_result = await self.planning_agent.analyze_intent(query)

        # TODO: 실행 계획 생성
        # execution_plan = await self.planning_agent.create_execution_plan(intent_result)

        # TODO: Planning State 저장
        # state["planning_state"] = {...}
        # state["execution_plan"] = {...}

        return state

    async def execute_teams_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        팀 실행 노드

        Args:
            state: 메인 상태

        Returns:
            업데이트된 상태

        TODO: 팀 실행 로직 구현
        """
        logger.info("[MainSupervisor] Executing teams")

        state["current_phase"] = "executing"

        # TODO: 실행 전략에 따라 팀 실행 (순차 또는 병렬)
        execution_strategy = state.get("execution_plan", {}).get("strategy", "sequential")
        active_teams = state.get("active_teams", [])

        # TODO: 공유 상태 생성
        # shared_state = StateManager.create_shared_state(...)

        # TODO: 팀 실행
        # if execution_strategy == "parallel":
        #     results = await self._execute_teams_parallel(active_teams, shared_state, state)
        # else:
        #     results = await self._execute_teams_sequential(active_teams, shared_state, state)

        # TODO: 결과 저장
        # for team_name, team_result in results.items():
        #     state = StateManager.merge_team_results(state, team_name, team_result)

        return state

    async def aggregate_results_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        결과 집계 노드

        Args:
            state: 메인 상태

        Returns:
            업데이트된 상태

        TODO: 팀 결과 집계 로직 구현
        """
        logger.info("[MainSupervisor] Aggregating results")

        state["current_phase"] = "aggregation"

        # TODO: 팀 결과 집계
        # aggregated = {}
        # team_results = state.get("team_results", {})
        # for team_name, team_data in team_results.items():
        #     aggregated[team_name] = {...}

        # state["aggregated_results"] = aggregated

        return state

    async def generate_response_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        응답 생성 노드

        Args:
            state: 메인 상태

        Returns:
            업데이트된 상태

        TODO: 최종 응답 생성 로직 구현
        """
        logger.info("[MainSupervisor] Generating response")

        state["current_phase"] = "response_generation"

        # TODO: LLM을 사용한 응답 생성 또는 간단한 응답 생성
        # if self.planning_agent.llm_service:
        #     response = await self._generate_llm_response(state)
        # else:
        #     response = self._generate_simple_response(state)

        # state["final_response"] = response
        state["status"] = "completed"

        # 실행 시간 계산
        if state.get("start_time"):
            state["end_time"] = datetime.now()
            state["total_execution_time"] = (state["end_time"] - state["start_time"]).total_seconds()

        return state

    async def _generate_llm_response(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        LLM을 사용한 응답 생성

        Args:
            state: 메인 상태

        Returns:
            응답 딕셔너리

        TODO: LLMService 사용하여 응답 생성
        """
        # TODO: 구현
        return {
            "type": "answer",
            "message": "LLM 응답 (구현 필요)",
            "data": {}
        }

    def _generate_simple_response(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        간단한 응답 생성 (LLM 없이)

        Args:
            state: 메인 상태

        Returns:
            응답 딕셔너리
        """
        aggregated = state.get("aggregated_results", {})

        summary_parts = []
        for team_name, team_data in aggregated.items():
            if team_data.get("status") == "success":
                summary_parts.append(f"{team_name} 팀 완료")

        return {
            "type": "summary",
            "summary": ", ".join(summary_parts) if summary_parts else "처리 완료",
            "teams_used": list(aggregated.keys()),
            "data": aggregated
        }

    async def process_query(
        self,
        query: str,
        session_id: str = "default",
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        쿼리 처리 메인 메서드

        Args:
            query: 사용자 쿼리
            session_id: 세션 ID
            user_id: 사용자 ID (선택적)

        Returns:
            처리 결과

        TODO: 초기 상태 구성 및 실행
        """
        logger.info(f"[MainSupervisor] Processing query: {query[:100]}...")

        # TODO: 초기 상태 생성 (MainSupervisorState)
        # initial_state = MainSupervisorState(
        #     query=query,
        #     session_id=session_id,
        #     user_id=user_id,
        #     ...
        # )

        # # 워크플로우 실행
        # try:
        #     final_state = await self.app.ainvoke(initial_state)
        #     return final_state
        # except Exception as e:
        #     logger.error(f"Query processing failed: {e}")
        #     return {
        #         "status": "error",
        #         "error": str(e),
        #         "final_response": {
        #             "type": "error",
        #             "message": "처리 중 오류가 발생했습니다."
        #         }
        #     }
        pass


# ==============================================================================
# 사용 예시 (테스트 코드)
# ==============================================================================

if __name__ == "__main__":
    async def test_supervisor():
        """Supervisor 테스트"""

        # Supervisor 초기화
        supervisor = MainSupervisor()

        # 테스트 쿼리
        test_queries = [
            "테스트 질문 1",
            "테스트 질문 2",
        ]

        for query in test_queries:
            print(f"\n{'='*80}")
            print(f"Query: {query}")
            print("-"*80)

            result = await supervisor.process_query(query, "test_session")

            print(f"Status: {result.get('status')}")
            print(f"Response: {result.get('final_response')}")

    import asyncio
    asyncio.run(test_supervisor())
