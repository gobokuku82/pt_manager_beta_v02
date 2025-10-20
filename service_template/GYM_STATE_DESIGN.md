# 헬스장 회원 관리 시스템 - State 설계 완전 가이드

**TypedDict 기반 State 아키텍처 상세 분석**

작성일: 2025-10-20
기반: separated_states.py 완전 분석

---

## 목차

1. [State 아키텍처 개요](#1-state-아키텍처-개요)
2. [부동산 → 헬스장 State 매핑](#2-부동산--헬스장-state-매핑)
3. [헬스장 State 완전 정의](#3-헬스장-state-완전-정의)
4. [State 관리 유틸리티](#4-state-관리-유틸리티)
5. [실전 코드 예시](#5-실전-코드-예시)

---

## 1. State 아키텍처 개요

### 1.1 State 계층 구조

```
┌─────────────────────────────────────────────────────────────┐
│                  MainSupervisorState                        │
│  (전체 시스템 상태)                                          │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ - query, session_id, user_id                          │ │
│  │ - planning_state (PlanningState)                      │ │
│  │ - team_results (팀별 결과)                            │ │
│  │ - final_response                                      │ │
│  └───────────────────────────────────────────────────────┘ │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
┌───────▼──────┐ ┌──▼─────────┐ ┌▼────────────┐
│ MemberSearch │ │  Schedule  │ │  Analysis   │
│ TeamState    │ │  TeamState │ │  TeamState  │
└──────────────┘ └────────────┘ └─────────────┘
        │            │            │
        │            │            │
   ┌────▼────┐  ┌───▼────┐  ┌───▼─────┐
   │Shared   │  │Shared  │  │Shared   │
   │State    │  │State   │  │State    │
   └─────────┘  └────────┘  └─────────┘
```

### 1.2 핵심 원칙

#### A. State 분리 (Separation of Concerns)
```python
# ✅ 좋은 예: 팀별 독립적인 State
class MemberSearchTeamState(TypedDict):
    team_name: str
    shared_context: SharedState  # 공유 데이터만
    members: List[Dict]           # 팀 전용 데이터
    # ...

# ❌ 나쁜 예: 전역 State에 모든 데이터
class GlobalState(TypedDict):
    members: List[Dict]           # Member 팀 데이터
    schedules: List[Dict]         # Schedule 팀 데이터
    analysis: Dict                # Analysis 팀 데이터
    # → State pollution 발생
```

#### B. TypedDict 활용 (타입 안정성)
```python
from typing import TypedDict

class MemberSearchTeamState(TypedDict):
    """타입 체크 가능"""
    team_name: str
    members: List[Dict[str, Any]]

# IDE 자동완성 + 타입 체크
state: MemberSearchTeamState = {
    "team_name": "member_search",
    "members": [...]  # 타입 검증됨
}
```

#### C. Optional vs Required
```python
class MainSupervisorState(TypedDict, total=False):
    """total=False → 모든 필드 선택적"""
    query: str                    # 필수처럼 보이지만 선택적
    session_id: str
    final_response: Optional[Dict]

# 장점: State 점진적 구성 가능
state = {}
state["query"] = "홍길동 회원 정보"
state["session_id"] = "sess_123"
# final_response는 나중에 추가
```

---

## 2. 부동산 → 헬스장 State 매핑

### 2.1 MainSupervisorState 비교

#### 부동산 도메인 (기존)
```python
class MainSupervisorState(TypedDict, total=False):
    # 기본 정보
    query: str
    session_id: str
    user_id: Optional[int]

    # Planning
    planning_state: Optional[PlanningState]
    execution_plan: Optional[Dict[str, Any]]

    # 팀 States (부동산 도메인)
    search_team_state: Optional[Dict[str, Any]]      # 법률/부동산/대출 검색
    document_team_state: Optional[Dict[str, Any]]    # 계약서 작성/검토
    analysis_team_state: Optional[Dict[str, Any]]    # 시세/리스크 분석

    # 실행 추적
    active_teams: List[str]
    completed_teams: List[str]
    failed_teams: List[str]

    # 결과
    team_results: Dict[str, Any]
    final_response: Optional[Dict[str, Any]]
```

#### 헬스장 도메인 (새로 정의)
```python
class GymMainSupervisorState(TypedDict, total=False):
    """헬스장 메인 Supervisor State"""

    # 기본 정보 (그대로 재사용)
    query: str
    session_id: str
    chat_session_id: Optional[str]
    request_id: str
    user_id: Optional[int]  # 트레이너/관리자 ID

    # Planning (그대로 재사용)
    planning_state: Optional[PlanningState]
    execution_plan: Optional[Dict[str, Any]]

    # 팀 States (헬스장 도메인 - 이름만 변경)
    member_search_team_state: Optional[Dict[str, Any]]  # 회원 검색
    schedule_team_state: Optional[Dict[str, Any]]       # 상담/스케줄 관리
    analysis_team_state: Optional[Dict[str, Any]]       # 출석/운동 분석

    # 실행 추적 (그대로 재사용)
    current_phase: str
    active_teams: List[str]
    completed_teams: List[str]
    failed_teams: List[str]

    # 결과 (그대로 재사용)
    team_results: Dict[str, Any]
    aggregated_results: Dict[str, Any]
    final_response: Optional[Dict[str, Any]]

    # Timing (그대로 재사용)
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    total_execution_time: Optional[float]

    # 에러 (그대로 재사용)
    status: str
    error_log: List[Dict[str, Any]]

    # Long-term Memory (그대로 재사용)
    loaded_memories: Optional[List[Dict[str, Any]]]
    user_preferences: Optional[Dict[str, Any]]
    memory_load_time: Optional[str]
```

**변경 사항:**
- ✅ 팀 State 이름만 변경 (3줄)
- ✅ 나머지 100% 재사용

---

### 2.2 팀별 State 비교

#### A. Search Team → Member Search Team

**기존 (부동산):**
```python
class SearchTeamState(TypedDict):
    team_name: str
    status: str
    shared_context: Dict[str, Any]

    # 검색 키워드
    keywords: Optional[SearchKeywords]  # legal, real_estate, loan

    # 검색 결과
    legal_results: List[Dict[str, Any]]
    real_estate_results: List[Dict[str, Any]]
    loan_results: List[Dict[str, Any]]
    aggregated_results: Dict[str, Any]
```

**새로운 (헬스장):**
```python
class MemberSearchTeamState(TypedDict):
    """회원 검색 팀 State"""
    team_name: str
    status: str
    shared_context: SharedState

    # 검색 입력
    search_query: str
    search_type: str  # 'name', 'phone', 'member_code'
    filters: Dict[str, Any]

    # 검색 결과
    members: List[Dict[str, Any]]           # 회원 목록
    attendance_records: List[Dict[str, Any]] # 출석 기록
    memberships: List[Dict[str, Any]]       # 회원권 정보

    # 메타데이터
    total_results: int
    search_time: float
    sources_used: List[str]

    # 실행 추적
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    execution_time: Optional[float]
    error: Optional[str]
```

#### B. Document Team → Schedule Team

**기존 (부동산):**
```python
class DocumentTeamState(TypedDict):
    team_name: str
    status: str

    # 문서 타입
    document_type: str  # "lease_contract", "sales_contract"

    # 생성 결과
    template: Optional[DocumentTemplate]
    document_content: Optional[DocumentContent]
    review_result: Optional[ReviewResult]
    final_document: Optional[str]
```

**새로운 (헬스장):**
```python
class ScheduleTeamState(TypedDict):
    """스케줄 관리 팀 State"""
    team_name: str
    status: str
    shared_context: SharedState

    # 입력
    trainer_id: Optional[int]
    target_date: Optional[str]  # YYYY-MM-DD
    booking_info: Optional[Dict[str, Any]]

    # 결과
    trainer_schedules: List[Dict[str, Any]]  # 트레이너 스케줄
    available_slots: List[Dict[str, Any]]    # 예약 가능 시간
    consultations: List[Dict[str, Any]]      # 상담 내역
    booking_result: Optional[Dict[str, Any]] # 예약 생성 결과

    # 실행 추적
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    error: Optional[str]
```

#### C. Analysis Team (거의 동일)

**기존 (부동산):**
```python
class AnalysisTeamState(TypedDict):
    team_name: str
    status: str

    # 분석 타입
    analysis_type: str  # "market", "risk", "comprehensive"

    # 분석 결과
    raw_analysis: Dict[str, Any]
    metrics: Dict[str, float]
    insights: List[str]
    report: Dict[str, Any]
    recommendations: List[str]
```

**새로운 (헬스장):**
```python
class AnalysisTeamState(TypedDict):
    """데이터 분석 팀 State"""
    team_name: str
    status: str
    shared_context: SharedState

    # 분석 입력
    analysis_type: str  # "attendance", "workout", "comprehensive"
    target_member_id: Optional[int]
    period: Dict[str, str]  # {"start_date": "...", "end_date": "..."}

    # 분석 결과
    attendance_stats: Optional[Dict[str, Any]]  # 출석 통계
    workout_summary: Optional[Dict[str, Any]]   # 운동 기록 요약
    body_progress: Optional[Dict[str, Any]]     # 체성분 변화
    insights: List[str]                         # LLM 인사이트

    # 리포트
    report: Optional[Dict[str, Any]]

    # 실행 추적
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    error: Optional[str]
```

---

## 3. 헬스장 State 완전 정의

### 3.1 SharedState (모든 팀 공유)

```python
# models/gym_states.py

from typing import TypedDict, Optional, Literal

class SharedState(TypedDict):
    """
    모든 팀이 공유하는 최소한의 상태
    - 필수 필드만 포함
    - 팀 간 통신의 기본 단위
    """
    user_query: str                     # 사용자 질문
    session_id: str                     # 세션 ID
    user_id: Optional[int]              # 사용자 ID (트레이너/관리자)
    timestamp: str                      # ISO 8601 형식
    language: str                       # 언어 (기본: "ko")
    status: Literal["pending", "processing", "completed", "error"]
    error_message: Optional[str]
```

**사용 예시:**
```python
shared_state = SharedState(
    user_query="홍길동 회원 정보 알려줘",
    session_id="sess_12345",
    user_id=1,  # 트레이너 ID
    timestamp="2025-10-20T10:00:00",
    language="ko",
    status="processing",
    error_message=None
)

# 팀에 전달
member_search_team_state = {
    "team_name": "member_search",
    "shared_context": shared_state,
    "members": []
}
```

---

### 3.2 PlanningState (그대로 재사용)

```python
class ExecutionStepState(TypedDict):
    """실행 단계 (TODO 아이템)"""
    step_id: str                    # "step_0", "step_1"
    step_type: str                  # 'search', 'schedule', 'analysis'
    agent_name: str                 # "member_search_team"
    team: str                       # "member_search"

    task: str                       # "회원 정보 검색"
    description: str                # "홍길동 회원의 정보를 조회합니다"

    status: Literal["pending", "in_progress", "completed", "failed", "skipped"]
    progress_percentage: int        # 0-100

    started_at: Optional[str]       # ISO 8601
    completed_at: Optional[str]     # ISO 8601

    result: Optional[Dict[str, Any]]
    error: Optional[str]


class PlanningState(TypedDict):
    """계획 수립 State (100% 재사용)"""
    raw_query: str
    analyzed_intent: Dict[str, Any]     # Intent 분석 결과
    intent_confidence: float

    available_agents: List[str]
    available_teams: List[str]

    execution_steps: List[ExecutionStepState]  # TODO 아이템들
    execution_strategy: str                    # "sequential", "parallel"
    parallel_groups: Optional[List[List[str]]]

    plan_validated: bool
    validation_errors: List[str]
    estimated_total_time: float
```

---

### 3.3 팀별 State 완전 정의

#### A. MemberSearchTeamState

```python
class MemberSearchTeamState(TypedDict):
    """
    회원 검색 팀 State

    담당:
    - 회원 정보 조회 (이름, 전화번호, 회원번호)
    - 출석 기록 조회
    - 회원권 정보 조회
    """
    # === 기본 정보 ===
    team_name: str                  # "member_search"
    status: str                     # "initialized", "running", "completed", "failed"
    shared_context: SharedState     # 공유 State

    # === 검색 입력 ===
    search_query: str               # 검색어 (예: "홍길동", "010-1234-5678")
    search_type: str                # 'name', 'phone', 'member_code', 'all'
    filters: Dict[str, Any]         # 추가 필터 (status, membership_type 등)

    # === Tool 선택 ===
    selected_tools: List[str]       # ["member_tool", "attendance_tool"]
    tool_selection_reasoning: Optional[str]

    # === 검색 결과 ===
    members: List[Dict[str, Any]]           # 회원 목록
    """
    회원 데이터 구조:
    {
        "id": 1,
        "member_code": "M2025001234",
        "name": "홍길동",
        "phone": "010-1234-5678",
        "email": "hong@example.com",
        "status": "active",
        "membership": {
            "type": "PT",
            "end_date": "2025-12-31",
            "remaining_sessions": 10
        }
    }
    """

    attendance_records: List[Dict[str, Any]]  # 출석 기록
    """
    출석 데이터 구조:
    {
        "id": 1,
        "member_id": 1,
        "check_in_time": "2025-10-20T10:00:00",
        "check_out_time": "2025-10-20T12:00:00"
    }
    """

    memberships: List[Dict[str, Any]]        # 회원권 정보
    """
    회원권 데이터 구조:
    {
        "id": 1,
        "membership_type": "PT",
        "start_date": "2025-01-01",
        "end_date": "2025-12-31",
        "total_sessions": 20,
        "used_sessions": 10,
        "remaining_sessions": 10,
        "status": "active"
    }
    """

    # === 메타데이터 ===
    total_results: int              # 검색 결과 총 개수
    search_time: float              # 검색 소요 시간 (초)
    sources_used: List[str]         # 사용된 Tool 목록
    search_progress: Dict[str, str] # Tool별 진행 상태

    # === 실행 추적 ===
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    execution_time: Optional[float]
    current_search: Optional[str]   # 현재 실행 중인 Tool
    execution_strategy: Optional[str]  # "parallel", "sequential"

    # === 에러 ===
    error: Optional[str]
```

#### B. ScheduleTeamState

```python
class ScheduleTeamState(TypedDict):
    """
    스케줄 관리 팀 State

    담당:
    - 상담 예약 조회/생성/취소
    - 트레이너 스케줄 조회
    - 예약 가능 시간 계산
    """
    # === 기본 정보 ===
    team_name: str                  # "schedule"
    status: str
    shared_context: SharedState

    # === 입력 ===
    action_type: str                # "query", "booking", "cancel"
    trainer_id: Optional[int]       # 트레이너 ID
    member_id: Optional[int]        # 회원 ID
    target_date: Optional[str]      # YYYY-MM-DD
    booking_info: Optional[Dict[str, Any]]  # 예약 생성 시 정보
    """
    booking_info 구조:
    {
        "trainer_id": 1,
        "member_id": 1,
        "consultation_date": "2025-10-21",
        "start_time": "10:00",
        "end_time": "11:00",
        "type": "initial"
    }
    """

    # === Tool 선택 ===
    selected_tools: List[str]       # ["consultation_schedule_tool", "booking_tool"]

    # === 결과 ===
    trainer_schedules: List[Dict[str, Any]]  # 트레이너 스케줄
    """
    스케줄 데이터 구조:
    {
        "id": 1,
        "trainer_id": 1,
        "schedule_date": "2025-10-21",
        "start_time": "10:00",
        "end_time": "11:00",
        "is_available": false,
        "event_type": "pt_session",
        "member_id": 1
    }
    """

    available_slots: List[Dict[str, Any]]    # 예약 가능 시간
    """
    시간대 데이터 구조:
    {
        "start_time": "10:00",
        "end_time": "11:00"
    }
    """

    consultations: List[Dict[str, Any]]      # 상담 내역
    """
    상담 데이터 구조:
    {
        "id": 1,
        "member_id": 1,
        "trainer_id": 1,
        "consultation_date": "2025-10-20",
        "start_time": "10:00",
        "end_time": "11:00",
        "type": "initial",
        "status": "completed"
    }
    """

    booking_result: Optional[Dict[str, Any]]  # 예약 생성/취소 결과
    """
    예약 결과 구조:
    {
        "success": true,
        "consultation_id": 1,
        "message": "예약이 완료되었습니다"
    }
    """

    # === 메타데이터 ===
    total_schedules: int
    total_consultations: int

    # === 실행 추적 ===
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    error: Optional[str]
```

#### C. AnalysisTeamState

```python
class AnalysisTeamState(TypedDict):
    """
    데이터 분석 팀 State

    담당:
    - 출석률 통계 분석
    - 운동 기록 분석
    - 체성분 변화 추이
    - LLM 기반 인사이트 생성
    """
    # === 기본 정보 ===
    team_name: str                  # "analysis"
    status: str
    shared_context: SharedState

    # === 분석 입력 ===
    analysis_type: str              # "attendance", "workout", "body", "comprehensive"
    target_member_id: Optional[int] # 특정 회원 분석 시
    period: Dict[str, str]          # {"start_date": "2025-10-01", "end_date": "2025-10-31"}
    filters: Dict[str, Any]         # 추가 필터

    # === Tool 선택 ===
    selected_tools: List[str]       # ["attendance_analysis_tool", "workout_tool"]

    # === 분석 결과 ===
    attendance_stats: Optional[Dict[str, Any]]  # 출석 통계
    """
    출석 통계 구조:
    {
        "period": {"start": "2025-10-01", "end": "2025-10-31"},
        "total_visits": 45,
        "unique_members": 30,
        "average_visits_per_day": 1.5,
        "peak_hours": ["18:00-19:00", "19:00-20:00"],
        "by_date": [
            {"date": "2025-10-01", "count": 25},
            {"date": "2025-10-02", "count": 30}
        ]
    }
    """

    workout_summary: Optional[Dict[str, Any]]   # 운동 기록 요약
    """
    운동 요약 구조:
    {
        "total_workouts": 20,
        "total_duration_minutes": 1200,
        "average_intensity": "medium",
        "favorite_exercises": ["스쿼트", "벤치프레스"],
        "progress": {
            "squat_weight": {"start": 50, "end": 70, "increase": 40}
        }
    }
    """

    body_progress: Optional[Dict[str, Any]]     # 체성분 변화
    """
    체성분 변화 구조:
    {
        "measurements": [
            {
                "date": "2025-10-01",
                "weight": 70.0,
                "body_fat_percentage": 20.0,
                "muscle_mass": 30.0
            }
        ],
        "trends": {
            "weight": {"change": -2.0, "direction": "down"},
            "muscle_mass": {"change": +1.5, "direction": "up"}
        }
    }
    """

    insights: List[str]                         # LLM이 생성한 인사이트
    """
    인사이트 예시:
    [
        "출석률이 지난 달 대비 15% 증가했습니다",
        "스쿼트 중량이 꾸준히 증가하는 긍정적인 추세입니다",
        "체지방률이 감소하고 근육량이 증가하는 이상적인 변화입니다"
    ]
    """

    # === 리포트 ===
    report: Optional[Dict[str, Any]]
    """
    리포트 구조:
    {
        "title": "홍길동 회원 10월 리포트",
        "summary": "전반적으로 긍정적인 진행...",
        "sections": [
            {
                "title": "출석 현황",
                "content": "...",
                "charts": [...]
            }
        ],
        "recommendations": [
            "주 3회 이상 출석을 유지하세요",
            "하체 운동 비중을 늘리는 것을 추천합니다"
        ]
    }
    """

    # === 메타데이터 ===
    confidence_score: float         # 분석 신뢰도 (0.0 ~ 1.0)
    data_completeness: float        # 데이터 완전성 (0.0 ~ 1.0)

    # === 실행 추적 ===
    analysis_progress: Dict[str, str]  # Tool별 진행 상태
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    analysis_time: Optional[float]
    error: Optional[str]
```

---

## 4. State 관리 유틸리티

### 4.1 StateManager

```python
# foundation/separated_states.py:353-498

class StateManager:
    """State 변환 및 관리 유틸리티"""

    @staticmethod
    def update_step_status(
        planning_state: PlanningState,
        step_id: str,
        new_status: Literal["pending", "in_progress", "completed", "failed"],
        progress: Optional[int] = None,
        error: Optional[str] = None
    ) -> PlanningState:
        """
        execution_step 상태 업데이트

        WebSocket을 통해 Frontend에 실시간 전송됨
        """
        for step in planning_state["execution_steps"]:
            if step["step_id"] == step_id:
                step["status"] = new_status

                if progress is not None:
                    step["progress_percentage"] = progress

                if new_status == "in_progress":
                    step["started_at"] = datetime.now().isoformat()

                if new_status in ["completed", "failed"]:
                    step["completed_at"] = datetime.now().isoformat()

                if error:
                    step["error"] = error

                break

        return planning_state
```

**사용 예시:**
```python
# Member Search Team 시작
planning_state = StateManager.update_step_status(
    planning_state=state["planning_state"],
    step_id="step_0",
    new_status="in_progress",
    progress=0
)

# 50% 진행
planning_state = StateManager.update_step_status(
    planning_state=state["planning_state"],
    step_id="step_0",
    new_status="in_progress",
    progress=50
)

# 완료
planning_state = StateManager.update_step_status(
    planning_state=state["planning_state"],
    step_id="step_0",
    new_status="completed",
    progress=100
)
```

### 4.2 create_shared_state

```python
@staticmethod
def create_shared_state(
    query: str,
    session_id: str,
    user_id: Optional[int] = None,
    language: str = "ko"
) -> SharedState:
    """공유 State 생성"""
    return SharedState(
        user_query=query,
        session_id=session_id,
        user_id=user_id,
        timestamp=datetime.now().isoformat(),
        language=language,
        status="pending",
        error_message=None
    )
```

### 4.3 merge_team_results

```python
@staticmethod
def merge_team_results(
    main_state: MainSupervisorState,
    team_name: str,
    team_result: Dict[str, Any]
) -> MainSupervisorState:
    """팀 결과를 메인 State에 병합"""

    # 결과 저장
    main_state["team_results"][team_name] = team_result

    # 완료 팀 추가
    if team_result.get("status") == "completed":
        if team_name not in main_state["completed_teams"]:
            main_state["completed_teams"].append(team_name)
    else:
        if team_name not in main_state["failed_teams"]:
            main_state["failed_teams"].append(team_name)

    # 활성 팀에서 제거
    if team_name in main_state["active_teams"]:
        main_state["active_teams"].remove(team_name)

    return main_state
```

---

## 5. 실전 코드 예시

### 5.1 전체 실행 흐름

```python
# main_supervisor/gym_supervisor.py

async def process_query(self, query: str, session_id: str, user_id: int):
    """쿼리 처리 전체 흐름"""

    # 1. 초기 State 생성
    state: GymMainSupervisorState = {
        "query": query,
        "session_id": session_id,
        "user_id": user_id,
        "request_id": f"req_{uuid.uuid4().hex[:8]}",
        "status": "initialized",
        "active_teams": [],
        "completed_teams": [],
        "failed_teams": [],
        "team_results": {},
        "error_log": []
    }

    # 2. LangGraph 실행
    result = await self.app.ainvoke(state)

    return result["final_response"]
```

### 5.2 Member Search Team 실행

```python
# execution_agents/member_search_team.py

class MemberSearchTeam:
    async def invoke(self, shared_state: SharedState) -> Dict[str, Any]:
        """팀 실행"""

        # 1. 팀 State 초기화
        team_state: MemberSearchTeamState = {
            "team_name": "member_search",
            "status": "running",
            "shared_context": shared_state,
            "search_query": shared_state["user_query"],
            "search_type": "all",
            "filters": {},
            "members": [],
            "attendance_records": [],
            "memberships": [],
            "total_results": 0,
            "search_time": 0.0,
            "sources_used": [],
            "search_progress": {},
            "start_time": datetime.now(),
            "end_time": None,
            "execution_time": None,
            "current_search": None,
            "execution_strategy": "parallel",
            "error": None
        }

        # 2. LLM 기반 Tool 선택
        selected_tools = await self._select_tools_with_llm(
            query=team_state["search_query"]
        )
        team_state["selected_tools"] = selected_tools

        # 3. Tools 병렬 실행
        start = datetime.now()
        results = await self._execute_tools_parallel(selected_tools, team_state)
        team_state["search_time"] = (datetime.now() - start).total_seconds()

        # 4. 결과 병합
        team_state["members"] = results.get("members", [])
        team_state["attendance_records"] = results.get("attendance", [])
        team_state["memberships"] = results.get("memberships", [])
        team_state["total_results"] = len(team_state["members"])

        # 5. 완료 처리
        team_state["status"] = "completed"
        team_state["end_time"] = datetime.now()
        team_state["execution_time"] = (
            team_state["end_time"] - team_state["start_time"]
        ).total_seconds()

        return team_state
```

### 5.3 State 디버깅

```python
# 디버깅 유틸리티

def print_state_summary(state: GymMainSupervisorState):
    """State 요약 출력"""
    print(f"=== State Summary ===")
    print(f"Query: {state['query']}")
    print(f"Status: {state['status']}")
    print(f"Active Teams: {state.get('active_teams', [])}")
    print(f"Completed Teams: {state.get('completed_teams', [])}")
    print(f"Failed Teams: {state.get('failed_teams', [])}")

    # Planning State
    if state.get("planning_state"):
        ps = state["planning_state"]
        print(f"\nPlanning:")
        print(f"  Intent: {ps['analyzed_intent'].get('intent_type')}")
        print(f"  Confidence: {ps['intent_confidence']}")
        print(f"  Steps: {len(ps['execution_steps'])}")

        for step in ps["execution_steps"]:
            print(f"    - {step['step_id']}: {step['status']} ({step['progress_percentage']}%)")

    # 팀 결과
    if state.get("team_results"):
        print(f"\nTeam Results:")
        for team_name, result in state["team_results"].items():
            print(f"  {team_name}: {result.get('status')}")
```

---

## 결론

### 재사용률 요약

| State 구성 요소 | 재사용률 | 변경 사항 |
|----------------|---------|----------|
| MainSupervisorState | 95% | 팀 이름 3줄 |
| SharedState | 100% | 없음 |
| PlanningState | 100% | 없음 |
| ExecutionStepState | 100% | 없음 |
| 팀별 State | 0% | 새로 정의 (템플릿 참고) |
| StateManager | 100% | 없음 |
| StateValidator | 100% | 없음 |

**전체 평균: 82% 재사용**

### 다음 단계

1. [models/gym_states.py](./models/gym_states.py) 작성
2. 팀별 State 정의 완료
3. StateManager 통합 테스트
4. 실제 데이터로 검증

---

**다음 문서:** [GYM_IMPLEMENTATION_GUIDE.md](./GYM_IMPLEMENTATION_GUIDE.md) - 실제 구현 가이드
