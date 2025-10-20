# Service Template - 전체 구조도

**범용 챗봇 기초 구조 - 완전한 파일 트리**

---

## 📁 전체 폴더 구조 (36개 파일)

```
service_template/                                     # 루트 디렉토리
│
├── 📄 문서 (7개) ⭐⭐⭐
│   ├── README_FINAL.md                              # 🎯 메인 시작점 (355줄)
│   ├── CHATBOT_FOUNDATION_GUIDE.md                  # 범용 적용 가이드 (437줄)
│   ├── DATABASE_SCHEMA_GUIDE.md                     # DB 스키마 완전 가이드
│   ├── DEVELOPMENT_GUIDE.md                         # 단계별 개발 (Phase 0~8)
│   ├── FINAL_SUMMARY.md                             # 업데이트 내역 및 요약
│   ├── PROJECT_COMPLETION.md                        # 프로젝트 완료 보고서
│   ├── STRUCTURE.md                                 # 이 파일 (구조도)
│   └── README.md                                    # 초기 빠른 가이드 (참고용)
│
├── 📁 foundation/ (9개 파일) - 100% 재사용 ⭐⭐⭐
│   ├── config.py                                    # 시스템 설정 (DB 경로, LLM 모델)
│   ├── context.py                                   # LLM/Agent 컨텍스트 정의
│   ├── agent_registry.py                            # Agent 등록 및 관리
│   ├── agent_adapter.py                             # Agent 실행 어댑터
│   ├── separated_states.py                          # ⭐ 실제 State 정의 (참고용)
│   ├── checkpointer.py                              # LangGraph Checkpointing
│   ├── decision_logger.py                           # LLM 의사결정 로깅
│   ├── simple_memory_service.py                     # Long-term Memory 서비스
│   └── __init__.py                                  # 모듈 exports
│
├── 📁 llm_manager/ (3개 파일) - 100% 재사용 ⭐⭐⭐
│   ├── llm_service.py                               # ⭐ LLM 호출 통합 (567줄)
│   ├── prompt_manager.py                            # 프롬프트 로딩 및 관리
│   └── __init__.py                                  # 모듈 exports
│
├── 📁 cognitive_agents/ (3개 파일) - 80% 재사용 ⭐⭐
│   ├── planning_agent.py                            # ⭐ 의도 분석 + 계획 (876줄)
│   │                                                # → IntentType만 수정
│   ├── query_decomposer.py                          # 복합 질문 분해
│   └── __init__.py                                  # 모듈 exports
│
├── 📁 main_supervisor/ (3개 파일) - 90% 재사용 ⭐⭐⭐
│   ├── team_supervisor.py                           # ⭐ 실제 Supervisor (1,306줄)
│   │                                                # → 팀 연결만 수정 (20줄)
│   ├── __template__.py                              # Supervisor 템플릿 (학습용)
│   └── __init__.py                                  # 모듈 exports
│
├── 📁 execution_agents/ (5개 파일) - 새로 작성 (참고용 제공)
│   ├── search_executor.py                           # 🔍 검색 팀 참고 구현 (909줄)
│   ├── analysis_executor.py                         # 📊 분석 팀 참고 구현
│   ├── document_executor.py                         # 📝 문서 팀 참고 구현
│   ├── __template__.py                              # 💡 새 팀 개발 템플릿
│   └── __init__.py                                  # 모듈 exports
│
├── 📁 tools/ (2개 파일) - 새로 작성 (템플릿 제공)
│   ├── __template__.py                              # 💡 Tool 개발 템플릿
│   └── __init__.py                                  # 모듈 exports
│
├── 📁 models/ (2개 파일) - 도메인별 작성 (템플릿 + 참고)
│   ├── states.py                                    # 💡 State 정의 템플릿
│   │                                                # → separated_states.py 참고
│   └── __init__.py                                  # 모듈 exports
│
├── 📁 reports/ (1개 파일) - 사용자가 프롬프트 작성
│   └── __init__.py                                  # 프롬프트 폴더 준비됨
│       └── (prompts/ 폴더를 여기에 생성)             # intent_analysis.md 등
│
└── __init__.py                                      # 루트 패키지 초기화

```

**총 파일 수: 36개**
- 문서: 7개
- 코드: 29개

---

## 🎯 파일별 역할 및 재사용률

### 📄 문서 (7개) - 읽기 순서

| 순서 | 파일명 | 용도 | 중요도 |
|-----|--------|------|--------|
| 1 | `README_FINAL.md` | 메인 시작점, 전체 개요 | ⭐⭐⭐ |
| 2 | `CHATBOT_FOUNDATION_GUIDE.md` | 범용 적용 전략 및 도메인 예시 | ⭐⭐⭐ |
| 3 | `DATABASE_SCHEMA_GUIDE.md` | DB 스키마 (SQL + SQLAlchemy) | ⭐⭐⭐ |
| 4 | `DEVELOPMENT_GUIDE.md` | 단계별 개발 프로세스 | ⭐⭐⭐ |
| 5 | `PROJECT_COMPLETION.md` | 프로젝트 완료 보고서 | ⭐⭐ |
| 6 | `FINAL_SUMMARY.md` | 업데이트 내역 및 체크리스트 | ⭐⭐ |
| 7 | `README.md` | 초기 빠른 가이드 (참고용) | ⭐ |

---

### 📁 foundation/ (9개) - 100% 재사용

| 파일명 | 용도 | 수정 필요 | 줄 수 |
|--------|------|----------|-------|
| `config.py` | 시스템 설정 | DB 경로만 | ~150 |
| `context.py` | LLM/Agent 컨텍스트 | 없음 | ~120 |
| `agent_registry.py` | Agent 관리 | 없음 | ~180 |
| `agent_adapter.py` | Agent 실행 | 없음 | ~200 |
| `separated_states.py` ⭐ | State 정의 참고용 | 참고만 | ~350 |
| `checkpointer.py` | Checkpointing | 없음 | ~100 |
| `decision_logger.py` | 의사결정 로깅 | 없음 | ~150 |
| `simple_memory_service.py` | Long-term Memory | 없음 | ~180 |
| `__init__.py` | 모듈 exports | 없음 | ~70 |

**핵심 파일:**
- **`separated_states.py`**: service_agent의 실제 State 정의. `models/states.py` 작성 시 참고

---

### 📁 llm_manager/ (3개) - 100% 재사용

| 파일명 | 용도 | 수정 필요 | 줄 수 |
|--------|------|----------|-------|
| `llm_service.py` ⭐ | LLM 호출 통합 | 없음 | ~567 |
| `prompt_manager.py` | 프롬프트 관리 | 없음 | ~120 |
| `__init__.py` | 모듈 exports | 없음 | ~10 |

**핵심 기능:**
- OpenAI API 통합
- JSON 모드 지원
- 재시도 로직
- 프롬프트 로딩 및 변수 치환

**사용법:**
```python
llm_service = LLMService(llm_context)
result = await llm_service.complete_json_async(
    prompt_name="intent_analysis",
    variables={"query": "사용자 질문"}
)
```

---

### 📁 cognitive_agents/ (3개) - 80% 재사용

| 파일명 | 용도 | 수정 필요 | 줄 수 |
|--------|------|----------|-------|
| `planning_agent.py` ⭐ | 의도 분석 + 계획 | IntentType (10줄) | ~876 |
| `query_decomposer.py` | 복합 질문 분해 | 없음 | ~250 |
| `__init__.py` | 모듈 exports | 없음 | ~20 |

**수정 포인트:**
```python
# planning_agent.py에서 IntentType만 수정
class IntentType(Enum):
    # 부동산 → 의료로 변경
    DIAGNOSIS = "진단"           # 기존: LEGAL_CONSULT
    TREATMENT = "치료"           # 기존: MARKET_INQUIRY
    MEDICATION = "약물정보"      # 기존: LOAN_CONSULT
    # ...
```

---

### 📁 main_supervisor/ (3개) - 90% 재사용

| 파일명 | 용도 | 수정 필요 | 줄 수 |
|--------|------|----------|-------|
| `team_supervisor.py` ⭐ | 실제 Supervisor | 팀 연결 (20줄) | ~1,306 |
| `__template__.py` | 템플릿 (학습용) | 참고만 | ~400 |
| `__init__.py` | 모듈 exports | 없음 | ~10 |

**수정 포인트:**
```python
# team_supervisor.py의 __init__에서 팀만 교체
def __init__(self, llm_context=None):
    self.teams = {
        "search": SearchExecutor(llm_context),      # → 도메인 팀으로 변경
        "document": DocumentExecutor(llm_context),  # → 도메인 팀으로 변경
        "analysis": AnalysisExecutor(llm_context)   # → 도메인 팀으로 변경
    }
    # 나머지는 그대로 사용!
```

---

### 📁 execution_agents/ (5개) - 새로 작성 (참고용 제공)

| 파일명 | 용도 | 재사용 | 줄 수 |
|--------|------|--------|-------|
| `search_executor.py` 🔍 | 검색 팀 참고 구현 | 참고 | ~909 |
| `analysis_executor.py` 📊 | 분석 팀 참고 구현 | 참고 | ~650 |
| `document_executor.py` 📝 | 문서 팀 참고 구현 | 참고 | ~580 |
| `__template__.py` 💡 | 새 팀 개발 템플릿 | 복사 후 수정 | ~350 |
| `__init__.py` | 모듈 exports | 수정 | ~15 |

**참고 구현 활용법:**
1. `search_executor.py` - 검색/조회 팀 개발 시 참고
2. `analysis_executor.py` - 분석/계산 팀 개발 시 참고
3. `document_executor.py` - 문서생성 팀 개발 시 참고
4. `__template__.py` - 새 팀 개발 시작점

**개발 패턴:**
```python
# __template__.py 복사
cp execution_agents/__template__.py execution_agents/diagnosis_team.py

# 도메인 로직 구현
class DiagnosisTeam:
    async def _select_tools_with_llm(self, query):
        # Tool 선택 로직

    async def invoke(self, state):
        # 팀 실행 로직
```

---

### 📁 tools/ (2개) - 새로 작성 (템플릿 제공)

| 파일명 | 용도 | 재사용 | 줄 수 |
|--------|------|--------|-------|
| `__template__.py` 💡 | Tool 개발 템플릿 | 복사 후 수정 | ~150 |
| `__init__.py` | 모듈 exports | 수정 | ~5 |

**Tool 개발 패턴:**
```python
# __template__.py 복사
cp tools/__template__.py tools/medical_database_tool.py

# Tool 구현
class MedicalDatabaseTool:
    async def search(self, query: str, params: dict) -> dict:
        # API 호출, DB 쿼리 등
        return {
            "status": "success",
            "data": [...],
            "metadata": {...}
        }
```

---

### 📁 models/ (2개) - 도메인별 작성

| 파일명 | 용도 | 재사용 | 줄 수 |
|--------|------|--------|-------|
| `states.py` 💡 | State 정의 템플릿 | 새로 작성 | ~100 |
| `__init__.py` | 모듈 exports | 수정 | ~5 |

**State 정의 방법:**
```python
# foundation/separated_states.py를 참고하여 작성
from typing import TypedDict, Optional, Dict, Any

class MainSupervisorState(TypedDict):
    query: str
    session_id: str
    planning_state: Optional[Dict]
    team_results: Dict[str, Any]
    final_response: Optional[Dict]
    # 도메인별 필드 추가...
```

---

### 📁 reports/ (1개) - 사용자가 프롬프트 작성

| 파일명 | 용도 |
|--------|------|
| `__init__.py` | 프롬프트 폴더 표시 |

**프롬프트 작성:**
```bash
mkdir reports/prompts

# 4개 프롬프트 파일 작성
touch reports/prompts/intent_analysis.md
touch reports/prompts/agent_selection.md
touch reports/prompts/tool_selection.md
touch reports/prompts/response_synthesis.md
```

---

## 📊 재사용률 요약

```
┌─────────────────────┬──────────┬─────────────────────┐
│ 구성 요소           │ 재사용률 │ 작업량               │
├─────────────────────┼──────────┼─────────────────────┤
│ Foundation          │ 100%     │ DB 경로만 변경       │
│ LLM Manager         │ 100%     │ 프롬프트만 작성      │
│ Main Supervisor     │  90%     │ 팀 연결 (20줄)       │
│ Cognitive Agents    │  80%     │ IntentType (10줄)    │
│ Execution Agents    │   0%     │ 새로 작성 (템플릿)   │
│ Tools               │   0%     │ 새로 작성 (템플릿)   │
│ Models              │  20%     │ 참고하여 작성        │
├─────────────────────┼──────────┼─────────────────────┤
│ 평균                │ 55~60%   │ 9~13일 개발          │
└─────────────────────┴──────────┴─────────────────────┘
```

---

## 🚀 개발 시작 순서

### 1단계: 문서 읽기 (1~2시간)
```
README_FINAL.md → CHATBOT_FOUNDATION_GUIDE.md → DATABASE_SCHEMA_GUIDE.md
```

### 2단계: 템플릿 복사
```bash
cp -r service_template my_domain_chatbot
```

### 3단계: DB 준비 (1일)
```
DATABASE_SCHEMA_GUIDE.md 참고
→ PostgreSQL 설치
→ 필수 테이블 생성
→ 도메인 테이블 추가
```

### 4단계: 개발 (8~12일)
```
DEVELOPMENT_GUIDE.md 단계별 진행
→ Phase 0: 도메인 정의
→ Phase 1~2: Foundation + IntentType
→ Phase 3~6: 프롬프트 + Tools + Agents
→ Phase 7~8: 통합 테스트
```

---

## 🎯 핵심 파일 (반드시 확인)

### ⭐⭐⭐ 최우선
1. **README_FINAL.md** - 시작점
2. **foundation/separated_states.py** - State 정의 참고
3. **main_supervisor/team_supervisor.py** - Supervisor 구현
4. **cognitive_agents/planning_agent.py** - 의도 분석
5. **llm_manager/llm_service.py** - LLM 통합

### ⭐⭐ 중요
6. **CHATBOT_FOUNDATION_GUIDE.md** - 범용 적용
7. **DATABASE_SCHEMA_GUIDE.md** - DB 스키마
8. **DEVELOPMENT_GUIDE.md** - 개발 단계
9. **execution_agents/search_executor.py** - 팀 구현 참고

### ⭐ 참고
10. **execution_agents/__template__.py** - 팀 템플릿
11. **tools/__template__.py** - Tool 템플릿
12. **models/states.py** - State 템플릿

---

## 📚 외부 문서

```
../../reports/
└── service_agent_architecture_analysis.md    # 아키텍처 상세 분석
```

---

**생성일**: 2025-10-20
**버전**: 3.0
**총 파일 수**: 36개
**상태**: ✅ 프로덕션 준비 완료
