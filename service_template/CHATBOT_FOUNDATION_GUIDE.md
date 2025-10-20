# 기초 챗봇 구조 - 범용 적용 가이드

**다양한 회사와 상황에 적용 가능한 챗봇 기초 구조**

---

## 🎯 설계 목표

이 템플릿은 **어떤 도메인에도 적용 가능한 범용 챗봇 기초 구조**를 제공합니다.

### 핵심 원칙
1. **도메인 독립성** - 비즈니스 로직과 인프라 분리
2. **확장성** - 새로운 기능 쉽게 추가
3. **재사용성** - 80% 코드 재사용, 20%만 커스터마이징
4. **표준화** - 일관된 아키텍처 패턴

---

## 📦 핵심 구성 요소

### 1. Foundation (100% 재사용)
**어떤 도메인에서도 그대로 사용**

```
foundation/
├── config.py              # 시스템 설정 (DB 경로만 수정)
├── context.py             # LLM/Agent 컨텍스트 (그대로 사용)
├── agent_registry.py      # Agent 관리 (그대로 사용)
├── agent_adapter.py       # Agent 실행 (그대로 사용)
├── checkpointer.py        # 대화 이력 저장 (그대로 사용)
├── decision_logger.py     # 의사결정 로깅 (그대로 사용)
└── simple_memory_service.py  # Long-term Memory (그대로 사용)
```

**수정 불필요!** 설정 파일에서 DB 경로만 변경

---

### 2. LLM Manager (100% 재사용)
**프롬프트만 교체하면 사용**

```
llm_manager/
├── llm_service.py         # LLM 호출 통합 (그대로 사용)
└── prompt_manager.py      # 프롬프트 로딩 (그대로 사용)
```

**할 일:**
- `reports/prompts/` 폴더에 도메인별 프롬프트 작성
- 프롬프트 파일만 교체하면 끝

---

### 3. Main Supervisor (90% 재사용)
**팀 연결만 수정**

```
main_supervisor/
└── team_supervisor.py     # 워크플로우 조율
```

**수정 포인트:**
```python
# 1. 팀 초기화 (20줄)
self.teams = {
    "team1": Team1Executor(llm_context),  # 도메인별 이름
    "team2": Team2Executor(llm_context),
}

# 나머지는 그대로 사용!
```

---

### 4. Cognitive Agents (80% 재사용)
**IntentType만 수정**

```
cognitive_agents/
├── planning_agent.py      # 의도 분석 + 계획
└── query_decomposer.py    # 복합 질문 분해 (그대로 사용)
```

**수정 포인트:**
```python
# IntentType 정의 (10줄)
class IntentType(Enum):
    # 부동산 → 의료로 변경
    DIAGNOSIS = "진단"           # 기존: LEGAL_CONSULT
    TREATMENT = "치료"           # 기존: MARKET_INQUIRY
    MEDICATION = "약물정보"      # 기존: LOAN_CONSULT
    # ...
```

---

### 5. Execution Agents (새로 작성)
**도메인 로직 구현**

```
execution_agents/
├── __template__.py        # 복사하여 시작
├── search_executor.py     # 참고용 (부동산 검색)
├── analysis_executor.py   # 참고용 (부동산 분석)
└── your_executor.py       # 도메인별 신규 작성
```

**작성 비율:** 새로 작성 (템플릿 기반)

---

### 6. Tools (새로 작성)
**도메인 API/DB 연결**

```
tools/
├── __template__.py        # 복사하여 시작
└── your_tool.py           # 도메인별 신규 작성
```

**작성 비율:** 새로 작성 (템플릿 기반)

---

### 7. States (도메인 정의)
**도메인별 State 정의**

```
models/
├── states.py              # State 정의
└── (foundation/separated_states.py 참고)
```

**작성 방법:** `separated_states.py` 참고하여 작성

---

## 🏗️ 도메인 적응 프로세스

### 전체 흐름
```
1. DB 준비 (1일)
   └─> 2. IntentType 정의 (1시간)
       └─> 3. 프롬프트 작성 (1일)
           └─> 4. Tools 개발 (3~5일)
               └─> 5. Execution Agents (2~3일)
                   └─> 6. 통합 테스트 (2일)
```

**총 예상 기간: 9~13일**

---

## 📋 도메인별 커스터마이징 체크리스트

### Phase 0: 도메인 정의 (2시간)
- [ ] 도메인 선택 (의료, 금융, 교육, 고객지원 등)
- [ ] 주요 사용자 질문 유형 5~7개 정의
- [ ] 필요한 데이터 소스 리스트업 (DB, API)
- [ ] 팀 구조 설계 (3~5개 팀)

### Phase 1: DB 준비 (1일)
- [ ] PostgreSQL 설치 및 DB 생성
- [ ] 필수 테이블 생성 (users, chat_sessions, chat_messages)
- [ ] 도메인 테이블 설계 및 생성
- [ ] SQLAlchemy 모델 작성

### Phase 2: Foundation 설정 (1시간)
- [ ] `foundation/config.py`에서 DB 경로 수정
- [ ] `.env` 파일 설정

### Phase 3: IntentType 정의 (1시간)
- [ ] `cognitive_agents/planning_agent.py`에서 IntentType 수정
- [ ] Intent 패턴 키워드 수정

### Phase 4: 프롬프트 작성 (1일)
- [ ] `reports/prompts/intent_analysis.md`
- [ ] `reports/prompts/agent_selection.md`
- [ ] `reports/prompts/tool_selection.md`
- [ ] `reports/prompts/response_synthesis.md`

### Phase 5: Tools 개발 (3~5일)
- [ ] `tools/__template__.py` 복사
- [ ] 도메인 API/DB 연결 도구 개발
- [ ] 테스트 코드 작성

### Phase 6: Execution Agents (2~3일)
- [ ] `models/states.py` 작성 (separated_states.py 참고)
- [ ] `execution_agents/__template__.py` 복사
- [ ] 팀별 Executor 개발
- [ ] 팀별 테스트

### Phase 7: Supervisor 연결 (1시간)
- [ ] `main_supervisor/team_supervisor.py`에서 팀 초기화만 수정
- [ ] 워크플로우는 그대로 사용

### Phase 8: 통합 테스트 (2일)
- [ ] 전체 워크플로우 테스트
- [ ] 프롬프트 최적화
- [ ] 성능 튜닝

---

## 🌍 적용 가능한 도메인 예시

### 1. 고객 지원 챗봇 (Customer Support)
```python
class IntentType(Enum):
    PRODUCT_INQUIRY = "제품문의"
    ORDER_STATUS = "주문조회"
    RETURN_REQUEST = "반품요청"
    TECHNICAL_SUPPORT = "기술지원"
    COMPLAINT = "불만접수"
```

**팀 구조:**
- **Information Team** - FAQ, 제품정보 검색
- **Action Team** - 주문처리, 반품처리
- **Escalation Team** - 고객상담사 연결

---

### 2. 의료 상담 챗봇 (Healthcare)
```python
class IntentType(Enum):
    SYMPTOM_CHECK = "증상확인"
    DIAGNOSIS = "진단"
    TREATMENT = "치료"
    MEDICATION = "약물정보"
    APPOINTMENT = "예약"
```

**팀 구조:**
- **Data Collection Team** - 증상, 병력 수집
- **Diagnosis Team** - 질병 분석
- **Treatment Team** - 치료 계획 제시

---

### 3. 금융 상담 챗봇 (Finance)
```python
class IntentType(Enum):
    ACCOUNT_INQUIRY = "계좌조회"
    TRANSACTION = "거래내역"
    LOAN_CONSULT = "대출상담"
    INVESTMENT = "투자상담"
    FRAUD_REPORT = "사기신고"
```

**팀 구조:**
- **Account Team** - 계좌 정보 조회
- **Analysis Team** - 재무 분석
- **Recommendation Team** - 상품 추천

---

### 4. 교육 챗봇 (Education)
```python
class IntentType(Enum):
    COURSE_INQUIRY = "강의문의"
    ENROLLMENT = "수강신청"
    ASSIGNMENT_HELP = "과제도움"
    PROGRESS_CHECK = "진도확인"
    CAREER_ADVICE = "진로상담"
```

**팀 구조:**
- **Course Team** - 강의 정보 제공
- **Support Team** - 학습 지원
- **Counseling Team** - 진로 상담

---

### 5. 전자상거래 챗봇 (E-commerce)
```python
class IntentType(Enum):
    PRODUCT_SEARCH = "상품검색"
    PRICE_COMPARISON = "가격비교"
    RECOMMENDATION = "추천"
    ORDER_TRACKING = "배송조회"
    SIZE_GUIDE = "사이즈안내"
```

**팀 구조:**
- **Search Team** - 상품 검색
- **Recommendation Team** - 개인화 추천
- **Order Team** - 주문 관리

---

## 🔑 핵심 재사용 패턴

### 패턴 1: 정보 제공형 챗봇
**예:** FAQ, 제품정보, 고객지원

**구조:**
```
Search Team (정보 검색)
  → Analysis Team (관련성 분석) [선택적]
    → Response (답변 생성)
```

**재사용 비율:** 90%

---

### 패턴 2: 분석 제공형 챗봇
**예:** 의료진단, 재무분석, 리스크평가

**구조:**
```
Data Collection Team (데이터 수집)
  → Analysis Team (분석)
    → Recommendation Team (권고) [선택적]
      → Response (결과 제시)
```

**재사용 비율:** 85%

---

### 패턴 3: 작업 실행형 챗봇
**예:** 주문처리, 예약, 반품

**구조:**
```
Validation Team (검증)
  → Action Team (작업 실행)
    → Notification Team (알림) [선택적]
      → Response (완료 안내)
```

**재사용 비율:** 80%

---

### 패턴 4: 복합형 챗봇
**예:** 종합 비서, 플랫폼 챗봇

**구조:**
```
Planning (의도 분석)
  → Multi Teams (병렬 실행)
    → Aggregation (결과 통합)
      → Response (종합 답변)
```

**재사용 비율:** 75%

---

## 📊 코드 재사용률 요약

| 구성 요소 | 재사용률 | 수정 내용 |
|----------|---------|----------|
| **Foundation** | 100% | DB 경로만 |
| **LLM Manager** | 100% | 프롬프트만 |
| **Main Supervisor** | 90% | 팀 연결 (20줄) |
| **Cognitive Agents** | 80% | IntentType (10줄) |
| **Execution Agents** | 0% | 새로 작성 (템플릿 기반) |
| **Tools** | 0% | 새로 작성 (템플릿 기반) |
| **States** | 20% | 참고하여 작성 |

**전체 평균 재사용률: 약 55~60%**

---

## 🚀 빠른 시작 (회사별 적용)

### 1. 템플릿 복사
```bash
cp -r backend/app/service_template backend/app/my_company_chatbot
cd backend/app/my_company_chatbot
```

### 2. 도메인 정의 (2시간)
```bash
# 1. 비즈니스 요구사항 정리
# 2. 주요 질문 유형 5~7개 리스트업
# 3. 팀 구조 스케치 (3~5개 팀)
```

### 3. DB 준비 (1일)
```bash
# DATABASE_SCHEMA_GUIDE.md 참고
# - PostgreSQL 설치
# - 필수 테이블 생성
# - 도메인 테이블 설계
```

### 4. 개발 시작 (8~12일)
```bash
# DEVELOPMENT_GUIDE.md 따라 단계별 개발
# - Phase 1: Foundation 설정 (1시간)
# - Phase 2: IntentType 정의 (1시간)
# - Phase 3: 프롬프트 작성 (1일)
# - Phase 4~6: Tools & Agents 개발 (5~8일)
# - Phase 7~8: 통합 테스트 (2일)
```

---

## 💡 성공 팁

### 1. 작은 것부터 시작
- 처음에는 1~2개 Intent만 구현
- 점진적으로 확장

### 2. 참고 코드 활용
- `search_executor.py` - 검색 로직 참고
- `analysis_executor.py` - 분석 로직 참고
- `team_supervisor.py` - 워크플로우 참고

### 3. 프롬프트 반복 개선
- 초기 버전 → 테스트 → 수정 → 재테스트
- 10~20번 반복하여 최적화

### 4. 로깅 활용
- Decision Logger로 LLM 판단 추적
- 성능 병목 지점 파악

---

## 📚 관련 문서

- [README.md](./README.md) - 전체 개요
- [DEVELOPMENT_GUIDE.md](./DEVELOPMENT_GUIDE.md) - 단계별 개발
- [DATABASE_SCHEMA_GUIDE.md](./DATABASE_SCHEMA_GUIDE.md) - DB 스키마
- [FINAL_SUMMARY.md](./FINAL_SUMMARY.md) - 전체 요약
- [../../reports/service_agent_architecture_analysis.md](../../reports/service_agent_architecture_analysis.md) - 아키텍처 분석

---

**작성일**: 2025-10-20
**버전**: 1.0
**목표**: 모든 회사, 모든 상황에 적용 가능한 범용 챗봇 기초 구조
