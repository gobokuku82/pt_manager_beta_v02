# Service Agent 아키텍처 분석 보고서

## 1. 전체 구조 개요

service_agent는 **LangGraph 기반의 멀티 에이전트 시스템**으로, 부동산 도메인에 특화된 AI 상담 서비스를 제공합니다.

### 1.1 핵심 아키텍처 패턴

```
┌─────────────────────────────────────────────────────────────┐
│                    TeamBasedSupervisor                      │
│          (메인 오케스트레이터 - LangGraph 워크플로우)           │
└─────────────┬───────────────────────────────────────────────┘
              │
              ├─── Planning Agent (의도 분석 + 실행 계획)
              │    └─── Query Decomposer (복합 질문 분해)
              │
              ├─── Search Executor (검색 팀)
              │    ├─── Legal Search Tool
              │    ├─── Market Data Tool
              │    ├─── Real Estate Search Tool
              │    └─── Loan Data Tool
              │
              ├─── Analysis Executor (분석 팀)
              │    ├─── Contract Analysis Tool
              │    ├─── Market Analysis Tool
              │    ├─── ROI Calculator Tool
              │    └─── Loan Simulator Tool
              │
              └─── Document Executor (문서 팀)
                   ├─── Lease Contract Generator
                   └─── Contract Review Tool
```

---

## 2. 폴더 구조 및 역할

### 2.1 Foundation (핵심 인프라)

**필수 복사 파일:**

| 파일 | 역할 | 재사용성 |
|------|------|---------|
| `config.py` | 시스템 설정 (DB 경로, 모델, 타임아웃) | ⭐⭐⭐ 높음 |
| `context.py` | LLM/Agent 컨텍스트 정의 (LangGraph 0.6+) | ⭐⭐⭐ 높음 |
| `agent_registry.py` | Agent 동적 등록/관리 시스템 | ⭐⭐⭐ 높음 |
| `agent_adapter.py` | Agent 실행 어댑터 | ⭐⭐ 중간 |
| `checkpointer.py` | LangGraph 체크포인팅 (PostgreSQL) | ⭐⭐ 중간 |
| `separated_states.py` | State 정의 (TypedDict) | ⭐ 낮음 (도메인 의존) |
| `decision_logger.py` | LLM 의사결정 로깅 | ⭐⭐ 중간 |
| `simple_memory_service.py` | Long-term Memory (PostgreSQL) | ⭐⭐ 중간 |

**핵심 포인트:**
- `config.py`, `context.py`, `agent_registry.py`는 거의 모든 프로젝트에서 재사용 가능
- `separated_states.py`는 도메인별로 새로 정의 필요 (부동산 → 다른 도메인)

---

### 2.2 Cognitive Agents (계획/의도 분석)

**핵심 파일:**

| 파일 | 역할 | 재사용성 |
|------|------|---------|
| `planning_agent.py` | 의도 분석 + 실행 계획 수립 | ⭐⭐⭐ 높음 |
| `query_decomposer.py` | 복합 질문 분해 (Phase 1 Enhancement) | ⭐⭐⭐ 높음 |
| `execution_orchestrator.py` | 실행 조율 (현재 미사용) | ⭐ 낮음 |

**핵심 포인트:**
- `planning_agent.py`는 프롬프트만 수정하면 다른 도메인 적용 가능
- `query_decomposer.py`는 범용적 (복합 질문 → 하위 작업 분해)

---

### 2.3 Execution Agents (실행 팀)

**팀 구조:**

| 팀 | 파일 | 역할 |
|----|------|------|
| **Search Team** | `search_executor.py` | 법률/시세/대출 검색 |
| **Document Team** | `document_executor.py` | 계약서 작성/검토 |
| **Analysis Team** | `analysis_executor.py` | 데이터 분석/인사이트 |

**핵심 포인트:**
- 각 팀은 독립적인 **LangGraph 서브그래프**
- 도메인별로 팀 구성 변경 필요 (예: 의료 → Diagnosis Team, Treatment Team)

---

### 2.4 Tools (도구)

**검색 도구:**
- `hybrid_legal_search.py` - 법률 검색 (FAISS + SQLite)
- `market_data_tool.py` - 부동산 시세
- `real_estate_search_tool.py` - 개별 매물 검색
- `loan_data_tool.py` - 대출 상품

**분석 도구:**
- `contract_analysis_tool.py` - 계약서 분석
- `market_analysis_tool.py` - 시장 분석
- `roi_calculator_tool.py` - ROI 계산
- `loan_simulator_tool.py` - 대출 시뮬레이션

**문서 도구:**
- `lease_contract_generator_tool.py` - 임대차 계약서 생성

**핵심 포인트:**
- 도구는 **도메인 의존적** → 새 도메인에서는 처음부터 작성 필요
- Tool 인터페이스는 일관성 유지: `search(query, params)` → `{"status": "success", "data": [...]}`

---

### 2.5 LLM Manager (LLM 통합)

| 파일 | 역할 |
|------|------|
| `llm_service.py` | LLM 호출 통합 (OpenAI, Azure 등) |
| `prompt_manager.py` | 프롬프트 템플릿 관리 |

**핵심 포인트:**
- `llm_service.py`는 재사용 가능 (프롬프트만 교체)
- 프롬프트는 `reports/prompts/` 폴더에 분리 저장

---

### 2.6 Supervisor (메인 오케스트레이터)

**핵심 파일:**
- `team_supervisor.py` - 전체 워크플로우 조율

**워크플로우 순서:**
```
1. initialize_node      → 초기화
2. planning_node        → 의도 분석 + 계획 수립 (PlanningAgent)
3. execute_teams_node   → 팀 실행 (Search/Document/Analysis)
4. aggregate_results_node → 결과 집계
5. generate_response_node → 최종 응답 생성 (LLM)
```

**핵심 포인트:**
- LangGraph의 `StateGraph`로 구성
- Checkpointing 지원 (PostgreSQL)
- WebSocket을 통한 실시간 진행 상황 전송

---

## 3. 핵심 디자인 패턴

### 3.1 멀티 에이전트 협업

**Registry 패턴:**
```python
# Agent 등록
AgentRegistry.register(
    name="search_agent",
    agent_class=SearchExecutor,
    team="search",
    capabilities=...,
    priority=10
)

# Agent 동적 생성
agent = AgentRegistry.create_agent("search_agent", llm_context=...)
```

**핵심 포인트:**
- 중앙화된 Agent 관리 → 동적 로딩/언로딩 가능
- Capability 기반 검색 가능

---

### 3.2 State 분리 설계

**State 계층:**
```
MainSupervisorState          (최상위)
├─ SharedState              (팀 간 공유)
├─ PlanningState           (계획 단계)
├─ SearchTeamState         (검색 팀)
├─ DocumentTeamState       (문서 팀)
└─ AnalysisTeamState       (분석 팀)
```

**핵심 포인트:**
- TypedDict로 타입 안정성 확보
- 팀별 State 격리 → 병렬 실행 시 안전

---

### 3.3 LLM 기반 의사결정

**의사결정 포인트:**
1. **Intent Analysis** (`planning_agent.py`)
   - 사용자 의도 파악 (법률상담, 시세조회, 대출상담 등)
   - LLM: `gpt-4o-mini` (빠른 분석)

2. **Tool Selection** (`search_executor.py`)
   - 쿼리 분석 → 필요한 도구 선택
   - LLM: `gpt-4o-mini` (저렴한 모델)

3. **Response Generation** (`team_supervisor.py`)
   - 검색 결과 통합 → 최종 답변 생성
   - LLM: `gpt-4o` (고품질 응답)

**핵심 포인트:**
- 작업별 다른 모델 사용 (비용 최적화)
- Fallback 전략 (LLM 실패 시 규칙 기반)

---

### 3.4 Long-term Memory 통합

**Memory 흐름:**
```
planning_node (시작)
  → load_recent_memories()      # 과거 대화 로드
  → analyze_intent()            # 문맥 반영한 의도 분석
  ...
generate_response_node (종료)
  → save_conversation()         # 대화 저장
```

**핵심 포인트:**
- PostgreSQL 기반 (chat_sessions, chat_messages 테이블)
- MEMORY_LOAD_LIMIT로 범위 제어 (세션별 격리 vs 전체 공유)

---

## 4. 가져가야 할 코드 우선순위

### 4.1 필수 (⭐⭐⭐)

**Foundation:**
- `config.py` - 시스템 설정
- `context.py` - LLM/Agent 컨텍스트
- `agent_registry.py` - Agent 관리 시스템

**Cognitive:**
- `planning_agent.py` - 의도 분석 + 계획
- `query_decomposer.py` - 복합 질문 분해

**LLM:**
- `llm_service.py` - LLM 통합
- `prompt_manager.py` - 프롬프트 관리

**Supervisor:**
- `team_supervisor.py` - 메인 워크플로우

---

### 4.2 중요 (⭐⭐)

**Foundation:**
- `agent_adapter.py` - Agent 실행 어댑터
- `checkpointer.py` - 체크포인팅
- `decision_logger.py` - 의사결정 로깅
- `simple_memory_service.py` - Long-term Memory

**Execution:**
- `search_executor.py` - 검색 팀 템플릿
- `analysis_executor.py` - 분석 팀 템플릿

---

### 4.3 선택 (⭐)

**Foundation:**
- `separated_states.py` - State 정의 (도메인별 재작성)

**Tools:**
- Tool 파일들 (도메인별 완전 재작성)

---

## 5. 새 앱 개발 시 수정 가이드

### 5.1 도메인 변경 (부동산 → X)

**수정 필요:**
1. `separated_states.py` - State 정의 재작성
2. `planning_agent.py` - Intent 타입 재정의
   ```python
   class IntentType(Enum):
       # 부동산 예시
       LEGAL_CONSULT = "법률상담"
       MARKET_INQUIRY = "시세조회"

       # 의료 예시로 변경
       DIAGNOSIS = "진단"
       TREATMENT = "치료"
       PRESCRIPTION = "처방"
   ```

3. Execution Agents - 팀 재구성
   - Search Team → Data Collection Team
   - Analysis Team → Diagnosis Team
   - Document Team → Report Team

4. Tools - 완전 재작성
   - 도메인별 API/DB 연결

---

### 5.2 프롬프트 커스터마이징

**위치:** `reports/prompts/`

**파일:**
- `intent_analysis.md` - 의도 분석 프롬프트
- `agent_selection.md` - Agent 선택 프롬프트
- `tool_selection_search.md` - Tool 선택 프롬프트
- `keyword_extraction.md` - 키워드 추출 프롬프트
- `response_synthesis.md` - 응답 생성 프롬프트

**수정 방법:**
1. 도메인 용어 교체 (부동산 → 의료)
2. 예시 질문 교체
3. Tool/Agent 리스트 교체

---

### 5.3 LLM 모델 변경

**위치:** `foundation/config.py`

```python
LLM_DEFAULTS = {
    "models": {
        "intent_analysis": "gpt-4o-mini",      # 빠른 분석
        "plan_generation": "gpt-4o-mini",      # 계획
        "response_synthesis": "gpt-4o",        # 고품질 응답
    }
}
```

---

## 6. 새 앱 개발 체크리스트

### 6.1 Phase 1: Foundation 구축

- [ ] `foundation/` 폴더 복사
- [ ] `config.py` 수정 (DB 경로, 모델 설정)
- [ ] `context.py` 검토 (필요시 필드 추가)
- [ ] `agent_registry.py` 검토 (그대로 사용 가능)

### 6.2 Phase 2: LLM 통합

- [ ] `llm_manager/` 폴더 복사
- [ ] 프롬프트 파일 작성 (`reports/prompts/`)
- [ ] `llm_service.py` 테스트

### 6.3 Phase 3: Planning Agent

- [ ] `planning_agent.py` 복사
- [ ] `IntentType` 재정의
- [ ] Intent 패턴 수정
- [ ] Agent 선택 로직 수정

### 6.4 Phase 4: Execution Agents

- [ ] 팀 구조 설계 (3~5개 팀)
- [ ] 각 팀별 Executor 작성
- [ ] Tool 개발 (도메인 API 연결)
- [ ] State 정의 (`separated_states.py`)

### 6.5 Phase 5: Supervisor 통합

- [ ] `team_supervisor.py` 복사
- [ ] 워크플로우 노드 수정
- [ ] 팀 연결
- [ ] 테스트

---

## 7. 핵심 교훈

### 7.1 아키텍처 강점

✅ **모듈화:** Foundation을 여러 프로젝트에서 재사용 가능
✅ **확장성:** Agent/Tool 추가가 쉬움 (Registry 패턴)
✅ **타입 안정성:** TypedDict로 State 정의
✅ **유연성:** LLM 기반 의사결정 + 규칙 기반 Fallback
✅ **추적성:** Decision Logger로 LLM 판단 기록

### 7.2 개선 포인트

⚠️ **도메인 의존성:** Tools/States는 도메인별 재작성 필수
⚠️ **복잡성:** 초기 학습 곡선 높음 (LangGraph + 멀티 에이전트)
⚠️ **비용:** LLM 호출 많음 → 프롬프트 최적화 필요

---

## 8. 결론

`service_agent`는 **LangGraph 기반의 강력한 멀티 에이전트 프레임워크**입니다.

**재사용 전략:**
1. **Foundation + LLM Manager + Supervisor**: 거의 그대로 사용
2. **Planning Agent**: 프롬프트만 수정
3. **Execution Agents + Tools**: 도메인별 재작성

**새 앱 개발 시간:**
- Foundation 재사용: ~2일
- Planning Agent 커스터마이징: ~1일
- Execution Agents + Tools 개발: ~5~7일
- 통합 테스트: ~2일

**총 예상 기간: 10~12일** (부동산 도메인 지식 활용 시)

---

**작성일:** 2025-10-20
**작성자:** Claude Code Assistant
**버전:** 1.0
