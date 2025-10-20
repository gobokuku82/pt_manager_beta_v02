"""
State Definitions (TypedDict)
도메인별로 State를 정의하세요
"""

from typing import TypedDict, List, Dict, Any, Optional
from datetime import datetime


# ==============================================================================
# Main Supervisor State
# ==============================================================================

class MainSupervisorState(TypedDict):
    """
    메인 Supervisor 상태

    TODO: 도메인별로 필드 수정
    """
    # ========== 기본 정보 ==========
    query: str                          # 사용자 질문
    session_id: str                     # 세션 ID
    chat_session_id: Optional[str]      # 채팅 세션 ID
    request_id: str                     # 요청 ID
    user_id: Optional[int]              # 사용자 ID

    # ========== Planning State ==========
    planning_state: Optional[Dict]      # 계획 수립 상태
    execution_plan: Optional[Dict]      # 실행 계획

    # ========== Team States (도메인별로 수정) ==========
    team1_state: Optional[Dict]         # TODO: 팀1 상태 (예: data_collection_state)
    team2_state: Optional[Dict]         # TODO: 팀2 상태 (예: diagnosis_state)
    team3_state: Optional[Dict]         # TODO: 팀3 상태 (예: treatment_state)

    # ========== Execution Tracking ==========
    current_phase: str                  # 현재 단계
    active_teams: List[str]             # 활성 팀 목록
    completed_teams: List[str]          # 완료된 팀 목록
    failed_teams: List[str]             # 실패한 팀 목록

    # ========== Results ==========
    team_results: Dict[str, Any]        # 팀별 결과
    aggregated_results: Dict[str, Any]  # 집계된 결과
    final_response: Optional[Dict]      # 최종 응답

    # ========== Timing ==========
    start_time: Optional[datetime]      # 시작 시간
    end_time: Optional[datetime]        # 종료 시간
    total_execution_time: Optional[float]  # 총 실행 시간

    # ========== Status & Errors ==========
    status: str                         # 상태 (initialized, in_progress, completed, failed)
    error_log: List[Dict[str, Any]]     # 에러 로그

    # ========== Memory (선택적) ==========
    loaded_memories: Optional[List[Dict]]      # 로드된 메모리
    user_preferences: Optional[Dict]           # 사용자 선호도
    memory_load_time: Optional[str]            # 메모리 로드 시간


# ==============================================================================
# Shared State (팀 간 공유)
# ==============================================================================

class SharedState(TypedDict):
    """
    팀 간 공유 상태

    TODO: 공유할 정보 정의
    """
    query: str                          # 사용자 질문
    user_query: str                     # 원본 질문
    session_id: str                     # 세션 ID
    user_id: Optional[int]              # 사용자 ID

    # TODO: 도메인별 공유 정보 추가
    # 예시:
    # patient_id: Optional[int]         # 환자 ID (의료 도메인)
    # transaction_id: Optional[str]     # 거래 ID (금융 도메인)


# ==============================================================================
# Planning State
# ==============================================================================

class PlanningState(TypedDict):
    """
    계획 수립 상태

    TODO: 도메인별로 수정
    """
    raw_query: str                      # 원본 질문
    analyzed_intent: Dict[str, Any]     # 분석된 의도
    intent_confidence: float            # 의도 신뢰도

    # Agent 정보
    available_agents: List[str]         # 사용 가능한 Agent
    available_teams: List[str]          # 사용 가능한 팀

    # 실행 계획
    execution_steps: List[Dict]         # 실행 단계 목록
    execution_strategy: str             # 실행 전략 (sequential, parallel, pipeline)
    parallel_groups: List[List[str]]    # 병렬 실행 그룹

    # 검증
    plan_validated: bool                # 계획 검증 여부
    validation_errors: List[str]        # 검증 에러

    # 예상 시간
    estimated_total_time: float         # 예상 총 실행 시간


# ==============================================================================
# Team States (팀별 State 템플릿)
# ==============================================================================

class TeamStateTemplate(TypedDict):
    """
    팀 State 템플릿

    TODO: 팀별로 복사하여 수정
    예시: DataCollectionState, DiagnosisState, TreatmentState
    """
    team_name: str                      # 팀 이름
    status: str                         # 상태 (pending, in_progress, completed, failed)
    shared_context: SharedState         # 공유 컨텍스트

    # Execution
    start_time: Optional[datetime]      # 시작 시간
    end_time: Optional[datetime]        # 종료 시간
    execution_time: Optional[float]     # 실행 시간

    # Results (팀별로 정의)
    results: Optional[Dict]             # 결과
    error: Optional[str]                # 에러 메시지

    # TODO: 팀별 필드 추가
    # 예시 (Data Collection Team):
    # collected_data: List[Dict]
    # data_sources: List[str]
    # data_quality_score: float


# ==============================================================================
# State Manager (유틸리티)
# ==============================================================================

class StateManager:
    """
    State 관리 유틸리티

    TODO: 도메인별 메서드 추가
    """

    @staticmethod
    def create_shared_state(
        query: str,
        session_id: str,
        user_id: int = None
    ) -> SharedState:
        """
        공유 상태 생성

        Args:
            query: 사용자 질문
            session_id: 세션 ID
            user_id: 사용자 ID (선택적)

        Returns:
            SharedState
        """
        return SharedState(
            query=query,
            user_query=query,
            session_id=session_id,
            user_id=user_id
        )

    @staticmethod
    def merge_team_results(
        main_state: MainSupervisorState,
        team_name: str,
        team_result: Dict
    ) -> MainSupervisorState:
        """
        팀 결과를 메인 상태에 병합

        Args:
            main_state: 메인 Supervisor 상태
            team_name: 팀 이름
            team_result: 팀 결과

        Returns:
            업데이트된 메인 상태
        """
        # 팀 결과 저장
        main_state["team_results"][team_name] = team_result

        # 완료 팀 추가
        if team_result.get("status") == "completed":
            if team_name not in main_state["completed_teams"]:
                main_state["completed_teams"].append(team_name)

        # 실패 팀 추가
        elif team_result.get("status") == "failed":
            if team_name not in main_state["failed_teams"]:
                main_state["failed_teams"].append(team_name)

        return main_state

    @staticmethod
    def update_step_status(
        planning_state: PlanningState,
        step_id: str,
        status: str,
        progress: int = None,
        error: str = None
    ) -> PlanningState:
        """
        실행 단계 상태 업데이트

        Args:
            planning_state: 계획 상태
            step_id: 단계 ID
            status: 상태 (pending, in_progress, completed, failed)
            progress: 진행률 (0-100)
            error: 에러 메시지 (선택적)

        Returns:
            업데이트된 계획 상태
        """
        for step in planning_state["execution_steps"]:
            if step["step_id"] == step_id:
                step["status"] = status

                if progress is not None:
                    step["progress_percentage"] = progress

                if status == "in_progress":
                    step["started_at"] = datetime.now().isoformat()
                elif status in ["completed", "failed"]:
                    step["completed_at"] = datetime.now().isoformat()

                if error:
                    step["error"] = error

                break

        return planning_state


# ==============================================================================
# 사용 예시
# ==============================================================================

if __name__ == "__main__":
    # Shared State 생성
    shared_state = StateManager.create_shared_state(
        query="테스트 질문",
        session_id="test_session_123",
        user_id=1
    )

    print("Shared State:")
    print(shared_state)

    # Planning State 예시
    planning_state: PlanningState = {
        "raw_query": "테스트 질문",
        "analyzed_intent": {
            "intent_type": "test",
            "confidence": 0.9
        },
        "intent_confidence": 0.9,
        "available_agents": ["agent1", "agent2"],
        "available_teams": ["team1", "team2"],
        "execution_steps": [
            {
                "step_id": "step_1",
                "status": "pending",
                "progress_percentage": 0,
                "started_at": None,
                "completed_at": None,
                "error": None
            }
        ],
        "execution_strategy": "sequential",
        "parallel_groups": [],
        "plan_validated": True,
        "validation_errors": [],
        "estimated_total_time": 10.0
    }

    # Step 상태 업데이트
    planning_state = StateManager.update_step_status(
        planning_state,
        "step_1",
        "in_progress",
        progress=50
    )

    print("\nPlanning State:")
    print(planning_state)
