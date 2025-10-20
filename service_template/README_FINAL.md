# Service Template - 범용 챗봇 기초 구조

**모든 회사, 모든 상황에 적용 가능한 LangGraph 기반 챗봇 템플릿**

---

## 🎯 이 템플릿의 목적

**다양한 회사와 상황에서 사용할 수 있는 범용 챗봇 기초 구조를 제공합니다.**

- ✅ **80% 코드 재사용** - Foundation, LLM Manager, Supervisor는 그대로 사용
- ✅ **20% 커스터마이징** - IntentType, Tools, Agents만 도메인에 맞게 작성
- ✅ **9~13일 개발** - 빠르게 프로덕션 수준 챗봇 구축
- ✅ **확장 가능** - 새로운 기능 쉽게 추가

---

## 📦 전체 파일 구조 (34개 파일)

```
service_template/
├── 📄 문서 (5개)
│   ├── README_FINAL.md              # 이 파일 (시작점)
│   ├── CHATBOT_FOUNDATION_GUIDE.md  # 범용 적용 가이드 ⭐⭐⭐
│   ├── DEVELOPMENT_GUIDE.md         # 단계별 개발
│   ├── DATABASE_SCHEMA_GUIDE.md     # DB 스키마
│   └── FINAL_SUMMARY.md             # 전체 요약
│
├── 📁 foundation/ (7개 파일) - 100% 재사용 ⭐⭐⭐
│   ├── config.py                    # 시스템 설정
│   ├── context.py                   # LLM/Agent 컨텍스트
│   ├── agent_registry.py            # Agent 관리
│   ├── agent_adapter.py             # Agent 실행
│   ├── separated_states.py          # State 정의 (참고용)
│   ├── checkpointer.py              # 대화 이력 저장
│   ├── decision_logger.py           # 의사결정 로깅
│   └── simple_memory_service.py     # Long-term Memory
│
├── 📁 llm_manager/ (2개 파일) - 100% 재사용 ⭐⭐⭐
│   ├── llm_service.py               # LLM 호출 통합
│   └── prompt_manager.py            # 프롬프트 관리
│
├── 📁 cognitive_agents/ (2개 파일) - 80% 재사용 ⭐⭐
│   ├── planning_agent.py            # 의도 분석 + 계획
│   └── query_decomposer.py          # 복합 질문 분해
│
├── 📁 main_supervisor/ (2개 파일) - 90% 재사용 ⭐⭐⭐
│   ├── team_supervisor.py           # 워크플로우 조율 (실제 코드)
│   └── __template__.py              # Supervisor 템플릿
│
├── 📁 execution_agents/ (4개 파일) - 새로 작성 (템플릿 기반)
│   ├── __template__.py              # 팀 개발 템플릿
│   ├── search_executor.py           # 참고용 (부동산 검색)
│   ├── analysis_executor.py         # 참고용 (부동산 분석)
│   └── document_executor.py         # 참고용 (부동산 문서)
│
├── 📁 tools/ (1개 파일) - 새로 작성 (템플릿 기반)
│   └── __template__.py              # Tool 개발 템플릿
│
└── 📁 models/ (1개 파일) - 도메인 정의
    └── states.py                    # State 정의 템플릿
```

---

## 🚀 빠른 시작 (3단계)

### 1️⃣ 문서 읽기 순서

```
1. 이 파일 (README_FINAL.md) ← 지금 읽는 중
   └─> 2. CHATBOT_FOUNDATION_GUIDE.md ← 범용 적용 가이드 ⭐⭐⭐
       └─> 3. DATABASE_SCHEMA_GUIDE.md ← DB 준비
           └─> 4. DEVELOPMENT_GUIDE.md ← 단계별 개발
```

### 2️⃣ 템플릿 복사

```bash
# 새 프로젝트 생성
cp -r backend/app/service_template backend/app/my_chatbot
cd backend/app/my_chatbot
```

### 3️⃣ 도메인 적응 (9~13일)

```
Phase 0: 도메인 정의 (2시간)
  └─> Phase 1: DB 준비 (1일)
      └─> Phase 2: IntentType 정의 (1시간)
          └─> Phase 3: 프롬프트 작성 (1일)
              └─> Phase 4~6: Tools & Agents (5~8일)
                  └─> Phase 7~8: 통합 테스트 (2일)
```

---

## 📊 코드 재사용률

| 구성 요소 | 재사용률 | 작업량 |
|----------|---------|--------|
| Foundation | 100% | 설정만 변경 |
| LLM Manager | 100% | 프롬프트만 작성 |
| Main Supervisor | 90% | 팀 연결 (20줄) |
| Cognitive Agents | 80% | IntentType (10줄) |
| Execution Agents | 0% | 새로 작성 (템플릿 기반) |
| Tools | 0% | 새로 작성 (템플릿 기반) |

**평균 재사용률: 55~60%**

---

## 🌍 적용 가능한 도메인

### 고객 지원 (Customer Support)
- 제품 문의, 주문 조회, 반품 처리
- **팀**: Information, Action, Escalation

### 의료 (Healthcare)
- 증상 확인, 진단, 치료 계획
- **팀**: Data Collection, Diagnosis, Treatment

### 금융 (Finance)
- 계좌 조회, 거래 내역, 대출 상담
- **팀**: Account, Analysis, Recommendation

### 교육 (Education)
- 강의 문의, 수강 신청, 과제 도움
- **팀**: Course, Support, Counseling

### 전자상거래 (E-commerce)
- 상품 검색, 가격 비교, 추천
- **팀**: Search, Recommendation, Order

**→ [CHATBOT_FOUNDATION_GUIDE.md](./CHATBOT_FOUNDATION_GUIDE.md)에서 더 많은 예시 확인**

---

## 🔑 핵심 파일 설명

### 필수 실행 코드 (그대로 사용)
- **`main_supervisor/team_supervisor.py`** - 전체 워크플로우 (1,306줄)
- **`cognitive_agents/planning_agent.py`** - 의도 분석 (876줄)
- **`llm_manager/llm_service.py`** - LLM 통합 (567줄)
- **`foundation/separated_states.py`** - State 정의 참고

### 템플릿 (복사하여 사용)
- **`execution_agents/__template__.py`** - 팀 개발 템플릿
- **`tools/__template__.py`** - Tool 개발 템플릿
- **`models/states.py`** - State 정의 템플릿

### 참고 코드 (service_agent 실제 구현)
- **`execution_agents/search_executor.py`** - 검색 팀 예시
- **`execution_agents/analysis_executor.py`** - 분석 팀 예시
- **`execution_agents/document_executor.py`** - 문서 팀 예시

---

## 📝 개발 체크리스트

### Phase 0: 준비 (2시간)
- [ ] 도메인 선택 (의료, 금융, 교육 등)
- [ ] 주요 질문 유형 5~7개 정의
- [ ] 팀 구조 설계 (3~5개 팀)

### Phase 1: DB (1일)
- [ ] PostgreSQL 설치
- [ ] 필수 테이블 생성 (DATABASE_SCHEMA_GUIDE.md)
- [ ] 도메인 테이블 설계

### Phase 2: IntentType (1시간)
- [ ] `planning_agent.py`에서 IntentType 수정 (10줄)

### Phase 3: 프롬프트 (1일)
- [ ] `reports/prompts/` 폴더 생성
- [ ] 4개 프롬프트 파일 작성

### Phase 4: Tools (3~5일)
- [ ] `__template__.py` 복사
- [ ] 도메인 API/DB 연결

### Phase 5: Agents (2~3일)
- [ ] `models/states.py` 작성
- [ ] 팀별 Executor 개발

### Phase 6: 통합 (2일)
- [ ] 전체 워크플로우 테스트
- [ ] 프롬프트 최적화

---

## 💡 핵심 개념

### 1. 도메인 독립성
**비즈니스 로직과 인프라를 완전히 분리**

```
Infrastructure (100% 재사용)
  ↓
Planning Layer (80% 재사용, IntentType만 수정)
  ↓
Execution Layer (새로 작성, 템플릿 기반)
```

### 2. 표준 패턴
**4가지 표준 챗봇 패턴 제공**

- 정보 제공형 (재사용 90%)
- 분석 제공형 (재사용 85%)
- 작업 실행형 (재사용 80%)
- 복합형 (재사용 75%)

### 3. 점진적 확장
**작은 것부터 시작하여 확장**

```
1~2개 Intent → 테스트 → 3~4개 추가 → 테스트 → ...
```

---

## 📚 문서 가이드

### 반드시 읽어야 할 문서 (⭐⭐⭐)
1. **[CHATBOT_FOUNDATION_GUIDE.md](./CHATBOT_FOUNDATION_GUIDE.md)**
   - 범용 적용 가이드
   - 도메인별 예시
   - 코드 재사용률

2. **[DATABASE_SCHEMA_GUIDE.md](./DATABASE_SCHEMA_GUIDE.md)**
   - DB 스키마 (SQL + SQLAlchemy)
   - 필수/선택 테이블
   - 마이그레이션 가이드

3. **[DEVELOPMENT_GUIDE.md](./DEVELOPMENT_GUIDE.md)**
   - 단계별 개발 프로세스 (Phase 1~6)
   - 실제 코드 예시
   - 테스트 방법

### 참고 문서
4. **[FINAL_SUMMARY.md](./FINAL_SUMMARY.md)**
   - 전체 파일 목록
   - 업데이트 내역

5. **[../../reports/service_agent_architecture_analysis.md](../../reports/service_agent_architecture_analysis.md)**
   - 아키텍처 상세 분석
   - 디자인 패턴 설명

---

## 🎯 성공 사례 흐름

### 예시: 의료 상담 챗봇 개발 (12일)

**Day 1**: 도메인 정의 + DB 준비
```
- 5개 IntentType 정의 (증상확인, 진단, 치료, 약물, 예약)
- PostgreSQL 테이블 생성 (users, chat_sessions, symptoms, diseases)
```

**Day 2**: IntentType + 프롬프트
```
- planning_agent.py 수정 (10줄)
- 4개 프롬프트 파일 작성
```

**Day 3-7**: Tools 개발 (5일)
```
- SymptomDatabaseTool
- DiseaseDatabaseTool
- MedicationSearchTool
- DiagnosisAnalyzerTool
```

**Day 8-10**: Execution Agents (3일)
```
- DataCollectionTeam
- DiagnosisTeam
- TreatmentTeam
```

**Day 11-12**: 통합 테스트
```
- 전체 워크플로우 테스트
- 프롬프트 최적화
```

**결과**: 프로덕션 수준 의료 상담 챗봇 완성!

---

## 🚨 주의사항

### 하지 말아야 할 것
- ❌ Foundation 코드 수정 (99% 불필요)
- ❌ Supervisor 워크플로우 변경 (팀 연결만)
- ❌ 처음부터 모든 기능 구현

### 해야 할 것
- ✅ CHATBOT_FOUNDATION_GUIDE.md 먼저 읽기
- ✅ 1~2개 Intent부터 시작
- ✅ 참고 코드 활용 (search_executor.py 등)
- ✅ 프롬프트 반복 개선 (10~20번)

---

## 🤝 도움말

### 막힐 때
1. **참고 코드 확인**
   - `team_supervisor.py` - 워크플로우
   - `search_executor.py` - 검색 로직
   - `planning_agent.py` - 의도 분석

2. **문서 재확인**
   - CHATBOT_FOUNDATION_GUIDE.md - 도메인 적용
   - DEVELOPMENT_GUIDE.md - 개발 단계

3. **로깅 활용**
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

---

## 🎉 시작하기

```bash
# 1. 범용 가이드 읽기
cat CHATBOT_FOUNDATION_GUIDE.md

# 2. 템플릿 복사
cp -r . ../my_company_chatbot
cd ../my_company_chatbot

# 3. DB 준비
cat DATABASE_SCHEMA_GUIDE.md

# 4. 개발 시작
cat DEVELOPMENT_GUIDE.md
```

---

**목표**: 모든 회사, 모든 상황에 적용 가능한 범용 챗봇 기초 구조

**개발 기간**: 9~13일

**코드 재사용률**: 55~60%

**작성일**: 2025-10-20

**버전**: 3.0 (범용 챗봇 기초 구조)
