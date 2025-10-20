# 헬스장 회원 관리 시스템 - 구조 분석 및 확장 가이드

**LangGraph 0.6 기반 멀티 에이전트 챗봇 시스템**

작성일: 2025-10-20
기반: service_template v1.0 (부동산 도메인 → 헬스장 도메인 전환)

---

## 목차

1. [현재 시스템 구조 분석](#1-현재-시스템-구조-분석)
2. [헬스장 도메인 적용 계획](#2-헬스장-도메인-적용-계획)
3. [핵심 기능별 설계](#3-핵심-기능별-설계)
4. [데이터베이스 스키마 설계](#4-데이터베이스-스키마-설계)
5. [에이전트 팀 구성](#5-에이전트-팀-구성)
6. [Tool 설계](#6-tool-설계)
7. [Intent 정의](#7-intent-정의)
8. [State 설계](#8-state-설계)
9. [단계별 구현 로드맵](#9-단계별-구현-로드맵)
10. [확장 시나리오](#10-확장-시나리오)

---

## 1. 현재 시스템 구조 분석

### 1.1 아키텍처 개요

현재 템플릿은 **LangGraph 0.6** 기반의 **멀티 에이전트 시스템**입니다.

```
┌─────────────────────────────────────────────────────────────┐
│                     Main Supervisor                          │
│  (워크플로우 조율 - 계획 수립 및 팀 실행 관리)               │
└────────────────┬────────────────────────────────────────────┘
                 │
    ┌────────────┼────────────┐
    │            │            │
┌───▼───┐  ┌────▼────┐  ┌───▼────┐
│Search │  │Document │  │Analysis│
│ Team  │  │  Team   │  │  Team  │
└───────┘  └─────────┘  └────────┘
    │            │            │
    └────────────┼────────────┘
                 │
         ┌───────▼────────┐
         │  LLM Service   │
         │ (중앙화된 호출)│
         └────────────────┘
```

### 1.2 핵심 구성 요소

#### A. **Foundation (100% 재사용)** ⭐⭐⭐

완전히 재사용 가능한 인프라 계층:

| 파일명 | 용도 | 수정 필요 |
|--------|------|----------|
| `config.py` | 시스템 설정 (DB 경로, LLM 모델) | DB 경로만 |
| `context.py` | LLM/Agent 컨텍스트 정의 | 없음 |
| `agent_registry.py` | Agent 동적 등록 및 관리 | 없음 |
| `agent_adapter.py` | Agent 실행 어댑터 | 없음 |
| `checkpointer.py` | LangGraph Checkpointing | 없음 |
| `decision_logger.py` | LLM 의사결정 로깅 | 없음 |
| `simple_memory_service.py` | Long-term Memory | 없음 |

**특징:**
- 도메인 독립적 설계
- PostgreSQL & LangGraph 통합
- LLM 호출 중앙화 (OpenAI)
- 재시도 & 에러 핸들링 내장

#### B. **LLM Manager (100% 재사용)** ⭐⭐⭐

```python
# 중앙화된 LLM 호출 시스템
class LLMService:
    def complete_json_async(prompt_name, variables):
        """프롬프트 이름 기반 LLM 호출"""
        # 1. 프롬프트 로드 (reports/prompts/{prompt_name}.md)
        # 2. OpenAI API 호출 (JSON 모드)
        # 3. 재시도 & 로깅
        # 4. JSON 파싱 및 반환
```

**장점:**
- 프롬프트 외부 파일 관리 (Markdown)
- 자동 변수 치환 (`{query}`, `{keywords}` 등)
- 모델별 자동 선택 (intent_analysis → gpt-4o-mini)

#### C. **Main Supervisor (90% 재사용)** ⭐⭐⭐

워크플로우 오케스트레이터:

```python
class TeamBasedSupervisor:
    def __init__(self):
        self.planning_agent = PlanningAgent()

        # 팀 초기화 (여기만 수정!)
        self.teams = {
            "search": SearchExecutor(),
            "document": DocumentExecutor(),
            "analysis": AnalysisExecutor()
        }
```

**워크플로우:**
```
START → Initialize → Planning → Execute Teams → Aggregate → Response → END
                         │
                         ├─ (IRRELEVANT) → Response (안내 메시지)
                         └─ (RELEVANT) → Execute Teams
```

#### D. **Cognitive Agents (80% 재사용)** ⭐⭐

**Planning Agent** - 의도 분석 및 계획 수립:

```python
class IntentType(Enum):
    """의도 타입 (이 부분만 수정!)"""
    LEGAL_CONSULT = "법률상담"      # → 회원 정보 조회
    MARKET_INQUIRY = "시세조회"     # → 상담 예약
    LOAN_CONSULT = "대출상담"       # → 트레이너 스케줄 조회
    # ...
```

**수정 필요 부분:**
- `IntentType` 정의 (10줄)
- Intent 패턴 키워드 (20줄)

**재사용 부분:**
- LLM 기반 의도 분석
- 실행 계획 생성
- 복합 질문 분해
- 병렬/순차 실행 전략

#### E. **Execution Agents (새로 작성)** 🔧

도메인 로직 구현:

```python
class SearchExecutor:
    """검색 팀 (참고용)"""
    def execute(self, shared_state):
        # 1. LLM 기반 Tool 선택
        # 2. Tool 병렬 실행
        # 3. 결과 집계
```

**템플릿 제공:**
- `__template__.py` - 복사하여 시작
- 참고 구현: `search_executor.py`, `analysis_executor.py`

---

## 2. 헬스장 도메인 적용 계획

### 2.1 도메인 정의

**헬스장 회원 관리 시스템 (PT Manager)**

**핵심 기능:**
1. **회원 관리** - 회원 정보 조회, 등록, 수정
2. **1:1 상담** - 상담 예약, 내역 조회, 상담 노트
3. **접수 관리** - 입장 기록, 출석 관리
4. **트레이너 스케줄** - 스케줄 조회, 예약 가능 시간 확인
5. **회원 데이터 분석** - 출석률, 운동 기록, 리포트 생성

### 2.2 사용자 질문 예시

**회원 관리:**
- "홍길동 회원 정보 알려줘"
- "최근 등록한 회원 목록 보여줘"
- "회원번호 1234 만료일 언제야?"

**1:1 상담:**
- "김철수 트레이너 내일 상담 가능한 시간 있어?"
- "오늘 상담 예약 내역 보여줘"
- "홍길동 회원 지난 상담 내용 확인해줘"

**접수 관리:**
- "이름이 '김' 으로 시작하는 회원 오늘 출석했어?"
- "오늘 출석률 얼마나 돼?"

**트레이너 스케줄:**
- "이번 주 박지성 트레이너 스케줄 보여줘"
- "내일 오전 10시에 빈 트레이너 있어?"

**데이터 분석:**
- "지난달 평균 출석률 분석해줘"
- "회원 이용 패턴 리포트 만들어줘"
- "회원 1234번 운동 기록 분석해줘"

### 2.3 도메인 매핑

| 기존 (부동산) | 새 도메인 (헬스장) | 비고 |
|--------------|------------------|------|
| 법률 검색 | 회원 정보 조회 | 데이터베이스 쿼리 |
| 시세 조회 | 스케줄 조회 | 일정 관리 |
| 대출 상담 | 상담 예약 | 예약 시스템 |
| 계약서 작성 | 리포트 생성 | 문서 생성 |
| 리스크 분석 | 데이터 분석 | 통계 및 인사이트 |

---

## 3. 핵심 기능별 설계

### 3.1 회원 관리 (Member Management)

**Intent:** `MEMBER_INQUIRY`

**처리 흐름:**
```
User Query → Planning Agent (Intent: MEMBER_INQUIRY)
           → Member Search Team
           → Database Query Tool (members 테이블)
           → Result Aggregation
           → Response Generation
```

**Tool:**
- `MemberSearchTool` - 회원 정보 조회 (이름, ID, 전화번호 검색)

**DB 테이블:**
- `members` - 회원 기본 정보
- `memberships` - 회원권 정보

### 3.2 1:1 상담 (Consultation)

**Intent:** `CONSULTATION_BOOKING`, `CONSULTATION_INQUIRY`

**처리 흐름:**
```
User Query → Planning Agent
           → Consultation Team
           → Schedule Check Tool + Booking Tool
           → Database Update (consultations 테이블)
           → Confirmation Response
```

**Tool:**
- `ConsultationScheduleTool` - 상담 가능 시간 조회
- `ConsultationBookingTool` - 상담 예약 생성
- `ConsultationHistoryTool` - 상담 내역 조회

**DB 테이블:**
- `consultations` - 상담 예약 정보
- `consultation_notes` - 상담 노트

### 3.3 접수 관리 (Check-in)

**Intent:** `CHECKIN_INQUIRY`, `ATTENDANCE_CHECK`

**처리 흐름:**
```
User Query → Planning Agent
           → CheckIn Team
           → Attendance Query Tool
           → Statistics Calculation
           → Response with Summary
```

**Tool:**
- `CheckInTool` - 출석 기록 생성
- `AttendanceQueryTool` - 출석 내역 조회
- `AttendanceStatsTool` - 출석 통계 계산

**DB 테이블:**
- `attendance` - 출석 기록

### 3.4 트레이너 스케줄 (Trainer Schedule)

**Intent:** `TRAINER_SCHEDULE_INQUIRY`

**처리 흐름:**
```
User Query → Planning Agent
           → Schedule Team
           → Trainer Schedule Tool
           → Available Slot Calculation
           → Response with Calendar View
```

**Tool:**
- `TrainerScheduleTool` - 트레이너 스케줄 조회
- `SlotAvailabilityTool` - 예약 가능 시간대 계산

**DB 테이블:**
- `trainer_schedules` - 트레이너 스케줄
- `trainers` - 트레이너 정보

### 3.5 회원 데이터 분석 (Member Data Analysis)

**Intent:** `DATA_ANALYSIS`, `REPORT_GENERATION`

**처리 흐름:**
```
User Query → Planning Agent
           → Analysis Team
           → Data Collection (Multiple Tools)
           → Statistical Analysis
           → Insight Generation (LLM)
           → Report Formatting
```

**Tool:**
- `AttendanceAnalysisTool` - 출석률 분석
- `WorkoutRecordTool` - 운동 기록 조회
- `MemberInsightTool` - 회원 패턴 분석

**DB 테이블:**
- `workout_logs` - 운동 기록
- `body_measurements` - 체성분 측정 기록

---

## 4. 데이터베이스 스키마 설계

### 4.1 필수 테이블 (Core)

#### A. Users (시스템 사용자 - 트레이너/관리자)

```sql
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'trainer', -- admin, trainer, staff
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
```

#### B. Chat Sessions (챗봇 대화 세션)

```sql
CREATE TABLE chat_sessions (
    session_id VARCHAR(100) PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL DEFAULT '새 대화',
    last_message TEXT,
    message_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    metadata JSONB
);

CREATE INDEX idx_chat_sessions_user_id ON chat_sessions(user_id);
CREATE INDEX idx_chat_sessions_updated_at ON chat_sessions(updated_at);
```

#### C. Chat Messages (대화 메시지)

```sql
CREATE TABLE chat_messages (
    id BIGSERIAL PRIMARY KEY,
    session_id VARCHAR(100) NOT NULL REFERENCES chat_sessions(session_id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL, -- user, assistant, system
    content TEXT NOT NULL,
    structured_data JSONB, -- 섹션별 응답 구조
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_chat_messages_session_id ON chat_messages(session_id);
CREATE INDEX idx_chat_messages_created_at ON chat_messages(created_at);
```

### 4.2 헬스장 도메인 테이블

#### A. Members (회원 정보)

```sql
CREATE TABLE members (
    id BIGSERIAL PRIMARY KEY,
    member_code VARCHAR(20) UNIQUE NOT NULL, -- M2025001234
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) UNIQUE NOT NULL,
    email VARCHAR(100),
    birth_date DATE,
    gender VARCHAR(10), -- male, female, other
    address TEXT,
    emergency_contact VARCHAR(20),
    emergency_contact_name VARCHAR(100),
    profile_photo_url TEXT,
    notes TEXT,
    status VARCHAR(20) DEFAULT 'active', -- active, inactive, suspended
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_members_name ON members(name);
CREATE INDEX idx_members_phone ON members(phone);
CREATE INDEX idx_members_status ON members(status);
CREATE INDEX idx_members_created_at ON members(created_at);
```

#### B. Memberships (회원권)

```sql
CREATE TABLE memberships (
    id BIGSERIAL PRIMARY KEY,
    member_id BIGINT NOT NULL REFERENCES members(id) ON DELETE CASCADE,
    membership_type VARCHAR(50) NOT NULL, -- 일반, PT, 필라테스, 요가
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    total_sessions INTEGER DEFAULT 0, -- PT 세션 수 (PT 회원권인 경우)
    used_sessions INTEGER DEFAULT 0,
    remaining_sessions INTEGER DEFAULT 0,
    price DECIMAL(10, 2) NOT NULL,
    payment_status VARCHAR(20) DEFAULT 'paid', -- paid, pending, refunded
    status VARCHAR(20) DEFAULT 'active', -- active, expired, suspended
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_memberships_member_id ON memberships(member_id);
CREATE INDEX idx_memberships_status ON memberships(status);
CREATE INDEX idx_memberships_end_date ON memberships(end_date);
```

#### C. Trainers (트레이너)

```sql
CREATE TABLE trainers (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id) ON DELETE SET NULL,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(100),
    specialties TEXT[], -- ["근력", "다이어트", "재활"]
    bio TEXT,
    profile_photo_url TEXT,
    hire_date DATE NOT NULL,
    status VARCHAR(20) DEFAULT 'active', -- active, on_leave, resigned
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_trainers_status ON trainers(status);
CREATE INDEX idx_trainers_user_id ON trainers(user_id);
```

#### D. Consultations (상담 예약)

```sql
CREATE TABLE consultations (
    id BIGSERIAL PRIMARY KEY,
    member_id BIGINT NOT NULL REFERENCES members(id) ON DELETE CASCADE,
    trainer_id BIGINT NOT NULL REFERENCES trainers(id) ON DELETE CASCADE,
    consultation_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    type VARCHAR(50) DEFAULT 'general', -- general, initial, follow_up, pt_consultation
    status VARCHAR(20) DEFAULT 'scheduled', -- scheduled, completed, cancelled, no_show
    created_by BIGINT REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_consultations_member_id ON consultations(member_id);
CREATE INDEX idx_consultations_trainer_id ON consultations(trainer_id);
CREATE INDEX idx_consultations_date ON consultations(consultation_date);
CREATE INDEX idx_consultations_status ON consultations(status);
```

#### E. Consultation Notes (상담 노트)

```sql
CREATE TABLE consultation_notes (
    id BIGSERIAL PRIMARY KEY,
    consultation_id BIGINT NOT NULL REFERENCES consultations(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    goals TEXT, -- 목표
    recommendations TEXT, -- 추천사항
    next_steps TEXT, -- 다음 단계
    written_by BIGINT REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_consultation_notes_consultation_id ON consultation_notes(consultation_id);
```

#### F. Attendance (출석 기록)

```sql
CREATE TABLE attendance (
    id BIGSERIAL PRIMARY KEY,
    member_id BIGINT NOT NULL REFERENCES members(id) ON DELETE CASCADE,
    check_in_time TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    check_out_time TIMESTAMP WITH TIME ZONE,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_attendance_member_id ON attendance(member_id);
CREATE INDEX idx_attendance_check_in_time ON attendance(check_in_time);
```

#### G. Trainer Schedules (트레이너 스케줄)

```sql
CREATE TABLE trainer_schedules (
    id BIGSERIAL PRIMARY KEY,
    trainer_id BIGINT NOT NULL REFERENCES trainers(id) ON DELETE CASCADE,
    schedule_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    is_available BOOLEAN DEFAULT TRUE,
    event_type VARCHAR(50) DEFAULT 'pt_session', -- pt_session, consultation, break, meeting
    member_id BIGINT REFERENCES members(id) ON DELETE SET NULL, -- 예약된 회원
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_trainer_schedules_trainer_id ON trainer_schedules(trainer_id);
CREATE INDEX idx_trainer_schedules_date ON trainer_schedules(schedule_date);
CREATE INDEX idx_trainer_schedules_available ON trainer_schedules(is_available);
```

#### H. Workout Logs (운동 기록)

```sql
CREATE TABLE workout_logs (
    id BIGSERIAL PRIMARY KEY,
    member_id BIGINT NOT NULL REFERENCES members(id) ON DELETE CASCADE,
    trainer_id BIGINT REFERENCES trainers(id) ON DELETE SET NULL,
    workout_date DATE NOT NULL,
    duration_minutes INTEGER,
    exercises JSONB, -- [{"name": "스쿼트", "sets": 3, "reps": 10, "weight": 50}]
    intensity VARCHAR(20), -- low, medium, high
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_workout_logs_member_id ON workout_logs(member_id);
CREATE INDEX idx_workout_logs_workout_date ON workout_logs(workout_date);
```

#### I. Body Measurements (체성분 측정)

```sql
CREATE TABLE body_measurements (
    id BIGSERIAL PRIMARY KEY,
    member_id BIGINT NOT NULL REFERENCES members(id) ON DELETE CASCADE,
    measurement_date DATE NOT NULL,
    weight DECIMAL(5, 2), -- kg
    height DECIMAL(5, 2), -- cm
    body_fat_percentage DECIMAL(4, 2),
    muscle_mass DECIMAL(5, 2), -- kg
    bmi DECIMAL(4, 2),
    notes TEXT,
    measured_by BIGINT REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_body_measurements_member_id ON body_measurements(member_id);
CREATE INDEX idx_body_measurements_date ON body_measurements(measurement_date);
```

### 4.3 SQLAlchemy 모델 예시

```python
# app/models/gym.py
from sqlalchemy import Column, Integer, String, Date, Time, Boolean, DECIMAL, Text, ARRAY
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
from app.db.postgre_db import Base

class Member(Base):
    __tablename__ = "members"

    id = Column(Integer, primary_key=True, autoincrement=True)
    member_code = Column(String(20), unique=True, nullable=False)
    name = Column(String(100), nullable=False, index=True)
    phone = Column(String(20), unique=True, nullable=False, index=True)
    email = Column(String(100))
    birth_date = Column(Date)
    gender = Column(String(10))
    address = Column(Text)
    emergency_contact = Column(String(20))
    emergency_contact_name = Column(String(100))
    profile_photo_url = Column(Text)
    notes = Column(Text)
    status = Column(String(20), default='active', index=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relationships
    memberships = relationship("Membership", back_populates="member", cascade="all, delete-orphan")
    consultations = relationship("Consultation", back_populates="member")
    attendance_records = relationship("Attendance", back_populates="member")
    workout_logs = relationship("WorkoutLog", back_populates="member")
    body_measurements = relationship("BodyMeasurement", back_populates="member")

class Membership(Base):
    __tablename__ = "memberships"

    id = Column(Integer, primary_key=True, autoincrement=True)
    member_id = Column(Integer, ForeignKey("members.id", ondelete="CASCADE"), nullable=False, index=True)
    membership_type = Column(String(50), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False, index=True)
    total_sessions = Column(Integer, default=0)
    used_sessions = Column(Integer, default=0)
    remaining_sessions = Column(Integer, default=0)
    price = Column(DECIMAL(10, 2), nullable=False)
    payment_status = Column(String(20), default='paid')
    status = Column(String(20), default='active', index=True)
    notes = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relationships
    member = relationship("Member", back_populates="memberships")

# ... 나머지 모델들도 유사하게 정의
```

---

## 5. 에이전트 팀 구성

### 5.1 팀 구조

```python
# main_supervisor/team_supervisor.py

class GymManagementSupervisor:
    def __init__(self, llm_context=None):
        self.llm_context = llm_context
        self.planning_agent = PlanningAgent(llm_context)

        # 팀 초기화 (헬스장 도메인)
        self.teams = {
            "member_search": MemberSearchTeam(llm_context),
            "schedule": ScheduleTeam(llm_context),
            "analysis": AnalysisTeam(llm_context)
        }
```

### 5.2 Member Search Team (회원 검색 팀)

**역할:** 회원 정보 조회, 출석 기록, 회원권 조회

```python
# execution_agents/member_search_team.py

class MemberSearchTeam:
    def __init__(self, llm_context=None):
        self.llm_context = llm_context
        self.llm_service = LLMService(llm_context)

        # Tools 초기화
        self.member_tool = MemberSearchTool()
        self.attendance_tool = AttendanceQueryTool()
        self.membership_tool = MembershipTool()

    async def execute(self, shared_state):
        """팀 실행 로직"""
        query = shared_state["query"]

        # 1. LLM 기반 Tool 선택
        selected_tools = await self._select_tools_with_llm(query)

        # 2. Tools 병렬 실행
        results = await self._execute_tools_parallel(selected_tools, query)

        # 3. 결과 집계
        return {
            "status": "completed",
            "member_data": results.get("member", {}),
            "attendance_data": results.get("attendance", []),
            "membership_data": results.get("membership", {})
        }
```

### 5.3 Schedule Team (스케줄 관리 팀)

**역할:** 상담 예약, 트레이너 스케줄 조회, 예약 가능 시간 확인

```python
# execution_agents/schedule_team.py

class ScheduleTeam:
    def __init__(self, llm_context=None):
        self.llm_context = llm_context
        self.llm_service = LLMService(llm_context)

        # Tools
        self.consultation_schedule_tool = ConsultationScheduleTool()
        self.consultation_booking_tool = ConsultationBookingTool()
        self.trainer_schedule_tool = TrainerScheduleTool()

    async def execute(self, shared_state, booking_info=None):
        """스케줄 조회 또는 예약 실행"""
        query = shared_state["query"]

        # 예약 정보가 있으면 예약 생성
        if booking_info:
            result = await self.consultation_booking_tool.create_booking(booking_info)
            return {"status": "completed", "booking": result}

        # 스케줄 조회
        schedules = await self.trainer_schedule_tool.get_schedules(query)
        return {"status": "completed", "schedules": schedules}
```

### 5.4 Analysis Team (데이터 분석 팀)

**역할:** 출석률 분석, 운동 기록 분석, 인사이트 생성

```python
# execution_agents/analysis_team.py

class AnalysisTeam:
    def __init__(self, llm_context=None):
        self.llm_context = llm_context
        self.llm_service = LLMService(llm_context)

        # Tools
        self.attendance_analysis_tool = AttendanceAnalysisTool()
        self.workout_analysis_tool = WorkoutAnalysisTool()
        self.body_measurement_tool = BodyMeasurementTool()

    async def execute(self, shared_state, analysis_type="comprehensive"):
        """데이터 분석 실행"""
        query = shared_state["query"]

        # 1. 데이터 수집
        attendance_data = await self.attendance_analysis_tool.get_stats(query)
        workout_data = await self.workout_analysis_tool.get_records(query)
        body_data = await self.body_measurement_tool.get_measurements(query)

        # 2. LLM 기반 인사이트 생성
        insights = await self._generate_insights(
            query, attendance_data, workout_data, body_data
        )

        return {
            "status": "completed",
            "attendance_stats": attendance_data,
            "workout_summary": workout_data,
            "body_progress": body_data,
            "insights": insights
        }
```

---

## 6. Tool 설계

### 6.1 Member Search Tool

```python
# tools/member_search_tool.py

class MemberSearchTool:
    """회원 정보 검색 도구"""

    async def search(self, query: str, params: dict) -> dict:
        """
        회원 검색

        Args:
            query: 검색어 (이름, 전화번호, 회원번호)
            params: 검색 파라미터
                - search_type: 'name', 'phone', 'member_code', 'all'
                - status: 'active', 'inactive', 'all'
                - limit: 결과 개수 제한

        Returns:
            {
                "status": "success",
                "data": [
                    {
                        "id": 1,
                        "member_code": "M2025001234",
                        "name": "홍길동",
                        "phone": "010-1234-5678",
                        "status": "active",
                        "membership": {
                            "type": "PT",
                            "end_date": "2025-12-31",
                            "remaining_sessions": 10
                        }
                    }
                ],
                "count": 1
            }
        """
        async with get_async_db() as db:
            # SQLAlchemy 쿼리 작성
            from sqlalchemy import select, or_
            from app.models.gym import Member, Membership

            query_builder = select(Member)

            # 검색 조건 추가
            search_type = params.get("search_type", "all")
            if search_type == "name":
                query_builder = query_builder.where(Member.name.ilike(f"%{query}%"))
            elif search_type == "phone":
                query_builder = query_builder.where(Member.phone.ilike(f"%{query}%"))
            elif search_type == "member_code":
                query_builder = query_builder.where(Member.member_code == query)
            else:  # all
                query_builder = query_builder.where(
                    or_(
                        Member.name.ilike(f"%{query}%"),
                        Member.phone.ilike(f"%{query}%"),
                        Member.member_code.ilike(f"%{query}%")
                    )
                )

            # 상태 필터
            status = params.get("status", "active")
            if status != "all":
                query_builder = query_builder.where(Member.status == status)

            # 제한
            limit = params.get("limit", 10)
            query_builder = query_builder.limit(limit)

            # 실행
            result = await db.execute(query_builder)
            members = result.scalars().all()

            # 결과 포맷팅 (회원권 정보 포함)
            data = []
            for member in members:
                member_data = {
                    "id": member.id,
                    "member_code": member.member_code,
                    "name": member.name,
                    "phone": member.phone,
                    "email": member.email,
                    "status": member.status,
                    "created_at": member.created_at.isoformat()
                }

                # 현재 활성 회원권 조회
                membership_query = (
                    select(Membership)
                    .where(Membership.member_id == member.id)
                    .where(Membership.status == 'active')
                    .order_by(Membership.end_date.desc())
                    .limit(1)
                )
                membership_result = await db.execute(membership_query)
                membership = membership_result.scalars().first()

                if membership:
                    member_data["membership"] = {
                        "type": membership.membership_type,
                        "start_date": membership.start_date.isoformat(),
                        "end_date": membership.end_date.isoformat(),
                        "total_sessions": membership.total_sessions,
                        "used_sessions": membership.used_sessions,
                        "remaining_sessions": membership.remaining_sessions,
                        "status": membership.status
                    }

                data.append(member_data)

            return {
                "status": "success",
                "data": data,
                "count": len(data)
            }
```

### 6.2 Consultation Schedule Tool

```python
# tools/consultation_schedule_tool.py

class ConsultationScheduleTool:
    """상담 스케줄 조회 도구"""

    async def get_available_slots(
        self,
        trainer_id: int,
        date: str,  # YYYY-MM-DD
        duration_minutes: int = 60
    ) -> dict:
        """
        트레이너의 예약 가능 시간대 조회

        Returns:
            {
                "status": "success",
                "trainer": {"id": 1, "name": "김철수"},
                "date": "2025-10-21",
                "available_slots": [
                    {"start_time": "10:00", "end_time": "11:00"},
                    {"start_time": "14:00", "end_time": "15:00"}
                ]
            }
        """
        async with get_async_db() as db:
            from sqlalchemy import select, and_
            from app.models.gym import Trainer, TrainerSchedule, Consultation
            from datetime import datetime, time, timedelta

            # 트레이너 정보 조회
            trainer_result = await db.execute(
                select(Trainer).where(Trainer.id == trainer_id)
            )
            trainer = trainer_result.scalars().first()

            if not trainer:
                return {"status": "error", "message": "트레이너를 찾을 수 없습니다."}

            # 해당 날짜의 예약된 시간 조회
            consultations_result = await db.execute(
                select(Consultation)
                .where(
                    and_(
                        Consultation.trainer_id == trainer_id,
                        Consultation.consultation_date == date,
                        Consultation.status.in_(['scheduled', 'completed'])
                    )
                )
            )
            consultations = consultations_result.scalars().all()

            # 예약된 시간대 수집
            booked_slots = [
                (c.start_time, c.end_time) for c in consultations
            ]

            # 운영 시간 (예: 09:00 ~ 21:00)
            operating_start = time(9, 0)
            operating_end = time(21, 0)

            # 예약 가능 시간대 계산
            available_slots = []
            current_time = datetime.combine(datetime.today(), operating_start)
            end_datetime = datetime.combine(datetime.today(), operating_end)
            slot_duration = timedelta(minutes=duration_minutes)

            while current_time + slot_duration <= end_datetime:
                slot_start = current_time.time()
                slot_end = (current_time + slot_duration).time()

                # 충돌 체크
                is_available = True
                for booked_start, booked_end in booked_slots:
                    if not (slot_end <= booked_start or slot_start >= booked_end):
                        is_available = False
                        break

                if is_available:
                    available_slots.append({
                        "start_time": slot_start.strftime("%H:%M"),
                        "end_time": slot_end.strftime("%H:%M")
                    })

                current_time += slot_duration

            return {
                "status": "success",
                "trainer": {
                    "id": trainer.id,
                    "name": trainer.name
                },
                "date": date,
                "available_slots": available_slots
            }
```

### 6.3 Attendance Analysis Tool

```python
# tools/attendance_analysis_tool.py

class AttendanceAnalysisTool:
    """출석 데이터 분석 도구"""

    async def get_stats(self, params: dict) -> dict:
        """
        출석 통계 조회

        Args:
            params:
                - member_id: 특정 회원 (optional)
                - start_date: 시작일
                - end_date: 종료일
                - stat_type: 'daily', 'weekly', 'monthly'

        Returns:
            {
                "status": "success",
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
        async with get_async_db() as db:
            from sqlalchemy import select, func, extract
            from app.models.gym import Attendance, Member
            from datetime import datetime

            start_date = params.get("start_date")
            end_date = params.get("end_date")
            member_id = params.get("member_id")

            # 기본 쿼리
            query = select(Attendance).where(
                Attendance.check_in_time.between(start_date, end_date)
            )

            if member_id:
                query = query.where(Attendance.member_id == member_id)

            # 전체 출석 기록
            result = await db.execute(query)
            attendances = result.scalars().all()

            total_visits = len(attendances)
            unique_members = len(set(a.member_id for a in attendances))

            # 일별 통계
            by_date = {}
            for attendance in attendances:
                date_key = attendance.check_in_time.date().isoformat()
                by_date[date_key] = by_date.get(date_key, 0) + 1

            by_date_list = [
                {"date": date, "count": count}
                for date, count in sorted(by_date.items())
            ]

            # 시간대별 통계 (피크 시간 분석)
            by_hour = {}
            for attendance in attendances:
                hour = attendance.check_in_time.hour
                by_hour[hour] = by_hour.get(hour, 0) + 1

            # 상위 3개 피크 시간
            peak_hours = sorted(by_hour.items(), key=lambda x: x[1], reverse=True)[:3]
            peak_hours_formatted = [
                f"{hour:02d}:00-{hour+1:02d}:00" for hour, _ in peak_hours
            ]

            # 평균 계산
            days_count = len(by_date)
            average_visits_per_day = total_visits / days_count if days_count > 0 else 0

            return {
                "status": "success",
                "period": {
                    "start": start_date,
                    "end": end_date
                },
                "total_visits": total_visits,
                "unique_members": unique_members,
                "average_visits_per_day": round(average_visits_per_day, 2),
                "peak_hours": peak_hours_formatted,
                "by_date": by_date_list
            }
```

---

## 7. Intent 정의

### 7.1 IntentType 정의

```python
# cognitive_agents/planning_agent.py

class IntentType(Enum):
    """헬스장 도메인 의도 타입"""

    # 회원 관리
    MEMBER_INQUIRY = "회원조회"           # 회원 정보 검색
    MEMBER_REGISTRATION = "회원등록"      # 신규 회원 등록
    MEMBER_UPDATE = "회원정보수정"        # 회원 정보 수정

    # 상담 관리
    CONSULTATION_BOOKING = "상담예약"     # 상담 예약 생성
    CONSULTATION_INQUIRY = "상담조회"     # 상담 내역 조회
    CONSULTATION_CANCEL = "상담취소"      # 상담 취소

    # 출석 관리
    CHECKIN = "출석체크"                  # 출석 기록
    ATTENDANCE_INQUIRY = "출석조회"       # 출석 내역 조회

    # 스케줄 관리
    TRAINER_SCHEDULE_INQUIRY = "트레이너스케줄조회"  # 트레이너 스케줄 조회
    SCHEDULE_AVAILABILITY = "스케줄가능시간"        # 예약 가능 시간 조회

    # 데이터 분석
    DATA_ANALYSIS = "데이터분석"          # 출석률, 운동 기록 분석
    REPORT_GENERATION = "리포트생성"      # 회원 리포트 생성
    MEMBER_INSIGHT = "회원인사이트"       # 회원 패턴 분석

    # 기타
    UNCLEAR = "unclear"                   # 불명확한 질문
    IRRELEVANT = "irrelevant"             # 기능 외 질문
    ERROR = "error"                       # 에러
```

### 7.2 Intent 패턴 키워드

```python
def _initialize_intent_patterns(self) -> Dict[IntentType, List[str]]:
    """의도 패턴 초기화"""
    return {
        IntentType.MEMBER_INQUIRY: [
            "회원", "정보", "조회", "찾아줘", "검색", "누구", "확인",
            "이름", "전화번호", "회원번호", "회원권", "만료일", "남은"
        ],
        IntentType.MEMBER_REGISTRATION: [
            "등록", "신규", "회원가입", "가입", "추가", "새로운"
        ],
        IntentType.MEMBER_UPDATE: [
            "수정", "변경", "업데이트", "갱신"
        ],
        IntentType.CONSULTATION_BOOKING: [
            "상담", "예약", "잡아줘", "가능한", "시간", "언제"
        ],
        IntentType.CONSULTATION_INQUIRY: [
            "상담", "내역", "기록", "지난", "이전"
        ],
        IntentType.CONSULTATION_CANCEL: [
            "상담", "취소", "삭제", "없애줘"
        ],
        IntentType.CHECKIN: [
            "체크인", "출석", "입장", "들어왔", "왔어"
        ],
        IntentType.ATTENDANCE_INQUIRY: [
            "출석", "내역", "기록", "얼마나", "몇번", "다녔"
        ],
        IntentType.TRAINER_SCHEDULE_INQUIRY: [
            "트레이너", "스케줄", "일정", "언제", "시간표"
        ],
        IntentType.SCHEDULE_AVAILABILITY: [
            "가능한", "시간", "빈", "예약", "언제"
        ],
        IntentType.DATA_ANALYSIS: [
            "분석", "통계", "평균", "얼마나", "패턴", "추이"
        ],
        IntentType.REPORT_GENERATION: [
            "리포트", "보고서", "정리", "요약"
        ],
        IntentType.MEMBER_INSIGHT: [
            "인사이트", "패턴", "특징", "경향"
        ]
    }
```

---

## 8. State 설계

### 8.1 Main Supervisor State

```python
# models/states.py

from typing import TypedDict, List, Dict, Any, Optional
from datetime import datetime

class MainSupervisorState(TypedDict):
    """메인 Supervisor 상태"""

    # 기본 정보
    query: str                          # 사용자 질문
    session_id: str                     # 세션 ID
    chat_session_id: Optional[str]      # 채팅 세션 ID
    request_id: str                     # 요청 ID
    user_id: Optional[int]              # 사용자 ID (트레이너/관리자)

    # Planning State
    planning_state: Optional[Dict]      # 계획 수립 상태
    execution_plan: Optional[Dict]      # 실행 계획

    # Team States (헬스장 도메인)
    member_search_team_state: Optional[Dict]  # 회원 검색 팀 상태
    schedule_team_state: Optional[Dict]       # 스케줄 팀 상태
    analysis_team_state: Optional[Dict]       # 분석 팀 상태

    # Execution Tracking
    current_phase: str                  # 현재 단계
    active_teams: List[str]             # 활성 팀 목록
    completed_teams: List[str]          # 완료된 팀 목록
    failed_teams: List[str]             # 실패한 팀 목록

    # Results
    team_results: Dict[str, Any]        # 팀별 결과
    aggregated_results: Dict[str, Any]  # 집계된 결과
    final_response: Optional[Dict]      # 최종 응답

    # Timing
    start_time: Optional[datetime]      # 시작 시간
    end_time: Optional[datetime]        # 종료 시간
    total_execution_time: Optional[float]  # 총 실행 시간

    # Status & Errors
    status: str                         # 상태
    error_log: List[Dict[str, Any]]     # 에러 로그

    # Memory (선택적)
    loaded_memories: Optional[List[Dict]]      # 로드된 메모리
    user_preferences: Optional[Dict]           # 사용자 선호도
    memory_load_time: Optional[str]            # 메모리 로드 시간
```

### 8.2 Team States

```python
class MemberSearchTeamState(TypedDict):
    """회원 검색 팀 상태"""
    team_name: str
    status: str
    shared_context: Dict

    # Input
    search_query: str
    search_type: str  # 'name', 'phone', 'member_code'

    # Execution
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    execution_time: Optional[float]

    # Results
    members: List[Dict]  # 검색된 회원 목록
    attendance_records: List[Dict]  # 출석 기록
    memberships: List[Dict]  # 회원권 정보

    # Status
    total_results: int
    error: Optional[str]

class ScheduleTeamState(TypedDict):
    """스케줄 팀 상태"""
    team_name: str
    status: str
    shared_context: Dict

    # Input
    trainer_id: Optional[int]
    target_date: Optional[str]
    booking_info: Optional[Dict]  # 예약 정보 (예약 생성 시)

    # Execution
    start_time: Optional[datetime]
    end_time: Optional[datetime]

    # Results
    trainer_schedules: List[Dict]  # 트레이너 스케줄
    available_slots: List[Dict]  # 예약 가능 시간
    booking_result: Optional[Dict]  # 예약 결과
    consultations: List[Dict]  # 상담 내역

    # Status
    error: Optional[str]

class AnalysisTeamState(TypedDict):
    """분석 팀 상태"""
    team_name: str
    status: str
    shared_context: Dict

    # Input
    analysis_type: str  # 'attendance', 'workout', 'comprehensive'
    target_member_id: Optional[int]
    period: Dict  # {"start_date": "...", "end_date": "..."}

    # Execution
    start_time: Optional[datetime]
    end_time: Optional[datetime]

    # Results
    attendance_stats: Optional[Dict]  # 출석 통계
    workout_summary: Optional[Dict]  # 운동 기록 요약
    body_progress: Optional[Dict]  # 체성분 변화
    insights: List[str]  # LLM이 생성한 인사이트

    # Report
    report: Optional[Dict]  # 생성된 리포트

    # Status
    error: Optional[str]
```

---

## 9. 단계별 구현 로드맵

### Phase 0: 도메인 정의 및 준비 (1일)

**목표:** 프로젝트 범위 확정 및 환경 설정

- [ ] 헬스장 요구사항 문서화
- [ ] 주요 질문 유형 30개 샘플 작성
- [ ] 팀 구조 최종 확정 (3~5개 팀)
- [ ] PostgreSQL 설치 및 DB 생성
- [ ] `.env` 파일 설정
- [ ] LangGraph 0.6 설치 확인

### Phase 1: 데이터베이스 구축 (2일)

**목표:** 헬스장 도메인 DB 스키마 완성

- [ ] 필수 테이블 생성 (users, chat_sessions, chat_messages)
- [ ] 헬스장 도메인 테이블 생성 (9개 테이블)
- [ ] 인덱스 설정
- [ ] SQLAlchemy 모델 작성
- [ ] Alembic 마이그레이션 설정
- [ ] 샘플 데이터 삽입 (회원 10명, 트레이너 3명)

### Phase 2: Intent 정의 (1일)

**목표:** 헬스장 도메인 의도 타입 정의

- [ ] `IntentType` Enum 정의 (12개)
- [ ] Intent 패턴 키워드 작성
- [ ] `planning_agent.py` 수정
- [ ] 테스트 쿼리 30개로 의도 분석 테스트

### Phase 3: 프롬프트 작성 (2일)

**목표:** 헬스장 도메인 프롬프트 작성

```
reports/prompts/
├── intent_analysis.md          # 의도 분석 프롬프트
├── agent_selection.md          # 에이전트 선택 프롬프트
├── tool_selection_member.md    # Member Search 팀 Tool 선택
├── tool_selection_schedule.md  # Schedule 팀 Tool 선택
├── tool_selection_analysis.md  # Analysis 팀 Tool 선택
└── response_synthesis.md       # 응답 생성 프롬프트
```

**프롬프트 예시:**

```markdown
# intent_analysis.md

당신은 헬스장 회원 관리 시스템의 의도 분석 전문가입니다.

사용자의 질문을 분석하여 다음 정보를 JSON 형식으로 반환하세요:

**질문:** {query}

**이전 대화:**
{chat_history}

**의도 타입 (intent):**
- member_inquiry: 회원 정보 조회
- consultation_booking: 상담 예약
- attendance_inquiry: 출석 조회
- trainer_schedule_inquiry: 트레이너 스케줄 조회
- data_analysis: 데이터 분석
- irrelevant: 기능 외 질문

**JSON 응답 형식:**
```json
{
  "intent": "member_inquiry",
  "confidence": 0.9,
  "keywords": ["홍길동", "회원", "정보"],
  "entities": {
    "member_name": "홍길동",
    "search_type": "name"
  },
  "reasoning": "회원 정보 조회 요청으로 판단"
}
```

- [ ] 6개 프롬프트 작성 및 검증
- [ ] 변수 치환 테스트 (`{query}`, `{keywords}` 등)

### Phase 4: Tools 개발 (5일)

**목표:** 헬스장 도메인 Tool 구현

**우선순위 1 (2일):**
- [ ] `MemberSearchTool` - 회원 정보 조회
- [ ] `AttendanceQueryTool` - 출석 내역 조회
- [ ] `MembershipTool` - 회원권 정보 조회

**우선순위 2 (2일):**
- [ ] `ConsultationScheduleTool` - 상담 스케줄 조회
- [ ] `ConsultationBookingTool` - 상담 예약 생성
- [ ] `TrainerScheduleTool` - 트레이너 스케줄 조회

**우선순위 3 (1일):**
- [ ] `AttendanceAnalysisTool` - 출석 통계 분석
- [ ] `WorkoutAnalysisTool` - 운동 기록 분석
- [ ] `BodyMeasurementTool` - 체성분 데이터 조회

**테스트:**
- [ ] 각 Tool 단위 테스트 작성
- [ ] 통합 테스트 (여러 Tool 조합)

### Phase 5: Execution Agents 개발 (3일)

**목표:** 헬스장 도메인 팀 구현

**팀 1: Member Search Team (1일)**
- [ ] `member_search_team.py` 작성
- [ ] Tool 선택 로직 구현
- [ ] 결과 집계 로직
- [ ] 서브그래프 구성
- [ ] 테스트

**팀 2: Schedule Team (1일)**
- [ ] `schedule_team.py` 작성
- [ ] 예약 가능 시간 계산 로직
- [ ] 예약 생성 로직
- [ ] 테스트

**팀 3: Analysis Team (1일)**
- [ ] `analysis_team.py` 작성
- [ ] LLM 기반 인사이트 생성
- [ ] 리포트 포맷팅
- [ ] 테스트

### Phase 6: State 정의 (1일)

**목표:** 헬스장 도메인 State 정의

- [ ] `models/states.py` 작성
- [ ] `MainSupervisorState` 정의
- [ ] Team States 정의 (3개)
- [ ] `StateManager` 유틸리티 작성
- [ ] TypedDict 검증

### Phase 7: Supervisor 통합 (1일)

**목표:** 팀 연결 및 워크플로우 구성

- [ ] `main_supervisor/gym_supervisor.py` 작성
- [ ] 팀 초기화 (3개 팀 연결)
- [ ] 워크플로우 그래프 검증
- [ ] LangGraph Checkpointing 활성화
- [ ] 통합 테스트

### Phase 8: 응답 생성 최적화 (2일)

**목표:** 사용자 응답 품질 향상

- [ ] `response_synthesis.md` 프롬프트 최적화
- [ ] 섹션별 응답 구조 설계
- [ ] structured_data JSONB 활용
- [ ] 10개 샘플 질문으로 응답 테스트
- [ ] A/B 테스트 (프롬프트 버전별)

### Phase 9: 엔드투엔드 테스트 (2일)

**목표:** 전체 시스템 검증

- [ ] 30개 테스트 쿼리 실행
- [ ] 성능 측정 (응답 시간)
- [ ] 에러 케이스 확인
- [ ] Long-term Memory 테스트
- [ ] WebSocket 실시간 통신 테스트

### Phase 10: 문서화 및 배포 준비 (1일)

**목표:** 운영 준비 완료

- [ ] API 문서 작성
- [ ] 관리자 매뉴얼 작성
- [ ] 트러블슈팅 가이드
- [ ] 모니터링 대시보드 설정
- [ ] 배포 체크리스트

**총 예상 기간: 21일 (약 3주)**

---

## 10. 확장 시나리오

### 10.1 추가 기능 확장

#### A. 결제 관리 기능

**Intent 추가:**
```python
class IntentType(Enum):
    PAYMENT_INQUIRY = "결제조회"       # 결제 내역 조회
    PAYMENT_PROCESS = "결제처리"       # 결제 실행
    REFUND_REQUEST = "환불요청"        # 환불 처리
```

**새 테이블:**
```sql
CREATE TABLE payments (
    id BIGSERIAL PRIMARY KEY,
    member_id BIGINT REFERENCES members(id),
    membership_id BIGINT REFERENCES memberships(id),
    amount DECIMAL(10, 2) NOT NULL,
    payment_method VARCHAR(50),
    payment_date TIMESTAMP WITH TIME ZONE,
    status VARCHAR(20) DEFAULT 'pending'
);
```

**새 Tool:**
- `PaymentProcessTool` - 결제 처리
- `PaymentHistoryTool` - 결제 내역 조회
- `RefundTool` - 환불 처리

#### B. 운동 프로그램 추천

**Intent 추가:**
```python
class IntentType(Enum):
    WORKOUT_RECOMMENDATION = "운동추천"  # 맞춤 운동 추천
    PROGRAM_INQUIRY = "프로그램조회"     # 운동 프로그램 정보
```

**새 테이블:**
```sql
CREATE TABLE workout_programs (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    difficulty_level VARCHAR(20),
    target_goals TEXT[],
    duration_weeks INTEGER,
    exercises JSONB
);

CREATE TABLE member_programs (
    id BIGSERIAL PRIMARY KEY,
    member_id BIGINT REFERENCES members(id),
    program_id BIGINT REFERENCES workout_programs(id),
    start_date DATE,
    end_date DATE,
    progress JSONB
);
```

**새 팀:**
- `RecommendationTeam` - LLM 기반 맞춤 추천

#### C. 알림 및 리마인더

**Intent 추가:**
```python
class IntentType(Enum):
    REMINDER_SET = "알림설정"          # 알림 설정
    NOTIFICATION_INQUIRY = "알림조회"  # 알림 내역 조회
```

**새 테이블:**
```sql
CREATE TABLE notifications (
    id BIGSERIAL PRIMARY KEY,
    member_id BIGINT REFERENCES members(id),
    notification_type VARCHAR(50),
    message TEXT,
    scheduled_time TIMESTAMP WITH TIME ZONE,
    sent_time TIMESTAMP WITH TIME ZONE,
    status VARCHAR(20) DEFAULT 'pending'
);
```

**새 Tool:**
- `NotificationTool` - 알림 발송
- `ReminderTool` - 리마인더 설정

### 10.2 멀티 지점 확장

여러 헬스장 지점을 관리하는 경우:

**테이블 수정:**
```sql
-- 지점 테이블 추가
CREATE TABLE gyms (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    location VARCHAR(200),
    phone VARCHAR(20),
    manager_id BIGINT REFERENCES users(id)
);

-- 기존 테이블에 gym_id 추가
ALTER TABLE members ADD COLUMN gym_id BIGINT REFERENCES gyms(id);
ALTER TABLE trainers ADD COLUMN gym_id BIGINT REFERENCES gyms(id);
```

**Intent 수정:**
```python
# 지점 필터링 추가
entities = {
    "member_name": "홍길동",
    "gym_id": 1,  # 특정 지점
    "gym_name": "강남점"
}
```

### 10.3 모바일 앱 연동

**REST API 추가:**
```python
# app/api/gym_chat.py

@router.post("/chat/stream")
async def chat_stream(
    request: ChatRequest,
    user: User = Depends(get_current_user)
):
    """WebSocket 대신 SSE 스트리밍"""
    async def event_generator():
        async for event in supervisor.process_query_streaming(
            query=request.query,
            user_id=user.id
        ):
            yield f"data: {json.dumps(event)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )
```

### 10.4 다국어 지원

**프롬프트 다국어화:**
```
reports/prompts/
├── ko/  # 한국어
│   ├── intent_analysis.md
│   └── response_synthesis.md
├── en/  # 영어
│   ├── intent_analysis.md
│   └── response_synthesis.md
└── ja/  # 일본어
    ├── intent_analysis.md
    └── response_synthesis.md
```

**언어 감지:**
```python
# Language detection
from langdetect import detect

language = detect(query)  # 'ko', 'en', 'ja'
prompt_name = f"{language}/intent_analysis"
```

---

## 11. 성능 최적화 전략

### 11.1 데이터베이스 최적화

**인덱스 전략:**
```sql
-- 복합 인덱스
CREATE INDEX idx_members_status_created ON members(status, created_at DESC);
CREATE INDEX idx_attendance_member_date ON attendance(member_id, check_in_time);

-- JSONB 인덱스 (GIN)
CREATE INDEX idx_workout_logs_exercises ON workout_logs USING GIN (exercises);
```

**쿼리 최적화:**
- Eager Loading (SQLAlchemy `joinedload`)
- 페이지네이션 (LIMIT/OFFSET)
- 데이터베이스 연결 풀 관리

### 11.2 LLM 호출 최적화

**캐싱:**
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_intent_from_cache(query: str) -> IntentResult:
    """자주 묻는 질문 캐싱"""
    pass
```

**모델 선택:**
- 간단한 작업: `gpt-4o-mini` (빠르고 저렴)
- 복잡한 분석: `gpt-4o` (정확함)

**배치 처리:**
- 여러 Tool 선택을 1회 LLM 호출로 통합

### 11.3 비동기 처리

**병렬 Tool 실행:**
```python
async def execute_tools_parallel(self, tools):
    tasks = [tool.execute() for tool in tools]
    results = await asyncio.gather(*tasks)
    return results
```

---

## 12. 모니터링 및 유지보수

### 12.1 로깅 전략

**Decision Logger 활용:**
```python
# LLM 의사결정 로깅
decision_id = decision_logger.log_tool_decision(
    agent_type="member_search",
    query=query,
    selected_tools=["member_tool", "attendance_tool"],
    reasoning="회원 정보와 출석 기록 필요",
    confidence=0.9
)
```

**성능 메트릭:**
- 평균 응답 시간
- Tool별 실행 시간
- Intent 분류 정확도
- 사용자 만족도

### 12.2 에러 핸들링

**다층 Fallback:**
```python
try:
    # LLM 기반 Tool 선택
    tools = await self._select_tools_with_llm(query)
except:
    # Fallback: 규칙 기반
    tools = self._select_tools_with_rules(query)
```

**Graceful Degradation:**
- Tool 실패 시 다른 Tool로 대체
- 부분 결과라도 반환

---

## 13. 보안 고려사항

### 13.1 데이터 접근 제어

**Role-based Access Control (RBAC):**
```python
# 트레이너는 자신의 담당 회원만 조회
if user.role == "trainer":
    query = query.where(Member.trainer_id == user.id)
```

### 13.2 개인정보 보호

**민감 정보 마스킹:**
```python
def mask_phone(phone: str) -> str:
    """전화번호 마스킹: 010-****-5678"""
    return f"{phone[:3]}-****-{phone[-4:]}"
```

**GDPR 준수:**
- 회원 정보 삭제 요청 처리
- 데이터 다운로드 기능

---

## 14. 결론

### 14.1 재사용률 요약

| 구성 요소 | 재사용률 | 작업량 |
|----------|---------|--------|
| Foundation | 100% | DB 경로만 변경 |
| LLM Manager | 100% | 프롬프트만 작성 |
| Main Supervisor | 90% | 팀 연결 (20줄) |
| Cognitive Agents | 80% | IntentType (10줄) |
| Execution Agents | 0% | 새로 작성 (템플릿 기반) |
| Tools | 0% | 새로 작성 (9개) |
| Models | 20% | State 정의 (참고) |
| **평균** | **55~60%** | **21일 개발** |

### 14.2 핵심 강점

1. **강력한 기반 인프라** - Foundation 100% 재사용
2. **LLM 중앙화** - 프롬프트 외부 관리로 빠른 수정
3. **확장 가능한 팀 구조** - 새 팀 추가 용이
4. **LangGraph 0.6 최신 기술** - Checkpointing, 상태 관리
5. **PostgreSQL 통합** - JSONB, 인덱스, 트랜잭션

### 14.3 다음 단계

1. **Phase 0 시작** - 도메인 정의 및 요구사항 확정
2. **DB 스키마 검토** - 헬스장 요구사항에 맞게 조정
3. **샘플 데이터 준비** - 테스트용 회원/트레이너 데이터
4. **Phase 1~3 집중** - DB, Intent, 프롬프트 완성
5. **반복적 개선** - 프롬프트 최적화 (10~20회 반복)

---

**문의:** 추가 질문이나 특정 기능 확장에 대한 상세 설계가 필요하면 알려주세요!

**작성:** Claude (Anthropic)
**날짜:** 2025-10-20
**버전:** 1.0
