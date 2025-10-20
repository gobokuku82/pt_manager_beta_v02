# Service Template

**LangGraph 기반 멀티 에이전트 시스템 템플릿**

이 템플릿은 `service_agent`의 핵심 아키텍처를 재사용 가능한 형태로 추출한 것입니다.

---

## 폴더 구조

```
service_template/
├─ foundation/           # 핵심 인프라 (재사용 가능)
│  ├─ config.py         # 시스템 설정
│  ├─ context.py        # LLM/Agent 컨텍스트
│  ├─ agent_registry.py # Agent 관리 시스템
│  └─ agent_adapter.py  # Agent 실행 어댑터
│
├─ cognitive_agents/     # 계획/의도 분석 (프롬프트 수정)
│  ├─ planning_agent.py # 의도 분석 + 실행 계획
│  └─ query_decomposer.py # 복합 질문 분해
│
├─ execution_agents/     # 실행 팀 (도메인별 재작성)
│  ├─ __template__.py   # 팀 템플릿
│  └─ README.md         # 팀 개발 가이드
│
├─ llm_manager/         # LLM 통합 (재사용 가능)
│  ├─ llm_service.py    # LLM 호출 서비스
│  └─ prompt_manager.py # 프롬프트 관리
│
├─ supervisor/          # 메인 오케스트레이터 (팀 연결만 수정)
│  └─ __template__.py   # Supervisor 템플릿
│
├─ tools/               # 도구 (도메인별 완전 재작성)
│  ├─ __template__.py   # Tool 템플릿
│  └─ README.md         # Tool 개발 가이드
│
└─ models/              # State 정의 (도메인별 재작성)
   └─ states.py         # TypedDict State 정의
```

---

## 빠른 시작

### 1. 도메인 정의

먼저 당신의 도메인을 정의하세요:

- **도메인 이름**: (예: 의료, 금융, 교육)
- **주요 의도 타입**: (예: 진단, 치료, 처방)
- **필요한 팀**: (예: Data Collection, Diagnosis, Treatment)

---

### 2. 설정 파일 수정

#### `foundation/config.py`

```python
# 데이터베이스 경로 수정
DATABASES = {
    "your_domain_data": DB_DIR / "your_domain" / "data.db",
    # ...
}

# LLM 모델 설정
DEFAULT_MODELS = {
    "intent": "gpt-4o-mini",      # 의도 분석 (빠름)
    "planning": "gpt-4o",          # 계획 수립 (정확함)
}
```

---

### 3. Intent 타입 정의

#### `cognitive_agents/planning_agent.py`

```python
class IntentType(Enum):
    """의도 타입 정의 - 도메인별로 수정"""

    # 예시: 의료 도메인
    DIAGNOSIS = "진단"
    TREATMENT = "치료"
    PRESCRIPTION = "처방"
    CONSULTATION = "상담"
    EMERGENCY = "응급"
    UNCLEAR = "unclear"
    IRRELEVANT = "irrelevant"
```

---

### 4. 팀 구조 설계

#### `execution_agents/` 폴더에 팀 추가

각 팀은 `__template__.py`를 복사하여 시작:

```bash
cp execution_agents/__template__.py execution_agents/data_collection_team.py
cp execution_agents/__template__.py execution_agents/diagnosis_team.py
cp execution_agents/__template__.py execution_agents/treatment_team.py
```

#### 팀별 역할:

- **Data Collection Team**: 정보 수집 (검색, API 호출)
- **Diagnosis Team**: 데이터 분석 및 진단
- **Treatment Team**: 처방/치료 계획 수립

---

### 5. Tool 개발

#### `tools/` 폴더에 도구 추가

```python
# tools/medical_database_tool.py

class MedicalDatabaseTool:
    """의료 데이터베이스 검색 도구"""

    async def search(self, query: str, params: dict) -> dict:
        """
        의료 정보 검색

        Args:
            query: 검색 쿼리
            params: 검색 파라미터

        Returns:
            {"status": "success", "data": [...]}
        """
        # 구현...
        pass
```

---

### 6. State 정의

#### `models/states.py`

```python
from typing import TypedDict, List, Dict, Any, Optional

class MainSupervisorState(TypedDict):
    """메인 Supervisor 상태"""
    query: str
    session_id: str
    user_id: Optional[int]

    # Planning
    planning_state: Optional[Dict]
    execution_plan: Optional[Dict]

    # Team States
    data_collection_state: Optional[Dict]
    diagnosis_state: Optional[Dict]
    treatment_state: Optional[Dict]

    # Results
    final_response: Optional[Dict]
    status: str
    # ...
```

---

### 7. Supervisor 조립

#### `supervisor/main_supervisor.py`

```python
class MainSupervisor:
    def __init__(self, llm_context=None):
        self.planning_agent = PlanningAgent(llm_context)

        # 팀 초기화
        self.teams = {
            "data_collection": DataCollectionTeam(llm_context),
            "diagnosis": DiagnosisTeam(llm_context),
            "treatment": TreatmentTeam(llm_context)
        }

        self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(MainSupervisorState)

        # 노드 추가
        workflow.add_node("initialize", self.initialize_node)
        workflow.add_node("planning", self.planning_node)
        workflow.add_node("execute_teams", self.execute_teams_node)
        workflow.add_node("aggregate", self.aggregate_results_node)
        workflow.add_node("generate_response", self.generate_response_node)

        # 엣지 연결...
        self.app = workflow.compile()
```

---

### 8. 프롬프트 작성

#### `reports/prompts/` 폴더 생성

프롬프트 파일 예시:

- `intent_analysis.md` - 의도 분석 프롬프트
- `agent_selection.md` - 에이전트 선택 프롬프트
- `tool_selection.md` - 도구 선택 프롬프트
- `response_synthesis.md` - 응답 생성 프롬프트

---

## 개발 체크리스트

### Phase 1: Foundation 설정
- [ ] `config.py` 수정 (DB 경로, 모델)
- [ ] `context.py` 검토 (필요시 필드 추가)
- [ ] 프롬프트 폴더 생성 (`reports/prompts/`)

### Phase 2: Planning Agent
- [ ] `IntentType` 재정의
- [ ] Intent 패턴 수정
- [ ] 프롬프트 작성 (`intent_analysis.md`)

### Phase 3: Execution Agents
- [ ] 팀 구조 설계 (3~5개 팀)
- [ ] 각 팀 템플릿 복사 및 수정
- [ ] State 정의 (`models/states.py`)

### Phase 4: Tools
- [ ] 도메인 API/DB 연결 도구 개발
- [ ] Tool 인터페이스 통일 (`search(query, params)`)
- [ ] 테스트 코드 작성

### Phase 5: Supervisor
- [ ] 팀 연결
- [ ] 워크플로우 노드 설정
- [ ] 통합 테스트

### Phase 6: 프롬프트 최적화
- [ ] Agent 선택 프롬프트
- [ ] Tool 선택 프롬프트
- [ ] 응답 생성 프롬프트

---

## 핵심 원칙

### 1. State 분리
- 팀별 State 격리 → 병렬 실행 안전
- TypedDict로 타입 안정성 확보

### 2. LLM 기반 의사결정
- Intent Analysis (의도 파악)
- Tool Selection (도구 선택)
- Response Generation (응답 생성)

### 3. Fallback 전략
- LLM 실패 시 규칙 기반 로직
- 안전한 기본값 제공

### 4. 로깅 및 추적
- Decision Logger로 LLM 판단 기록
- 성능 모니터링

---

## 참고 문서

- [아키텍처 분석 보고서](../../reports/service_agent_architecture_analysis.md)
- [LangGraph 공식 문서](https://langchain-ai.github.io/langgraph/)
- [OpenAI API 문서](https://platform.openai.com/docs/api-reference)

---

## 라이선스

MIT License

---

**생성일**: 2025-10-20
**버전**: 1.0
**기반**: service_agent v1.0
