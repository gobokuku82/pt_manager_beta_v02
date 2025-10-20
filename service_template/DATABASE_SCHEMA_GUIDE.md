# Database Schema Guide

**service_agent에서 사용하는 데이터베이스 스키마 가이드**

---

## 필수 테이블 (Core Tables)

새로운 서비스를 개발할 때 최소한 필요한 테이블들입니다.

---

### 1. Users (사용자)

```sql
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    full_name VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
```

**SQLAlchemy 모델:**
```python
from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP
from sqlalchemy.sql import func
from app.db.postgre_db import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    full_name = Column(String(100))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)
```

---

### 2. Chat Sessions (채팅 세션)

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
CREATE INDEX idx_chat_sessions_user_updated ON chat_sessions(user_id, updated_at);
```

**metadata JSONB 필드 구조:**
```json
{
  "conversation_summary": "대화 요약 (Long-term Memory용)",
  "last_updated": "2025-10-20T14:30:00",
  "message_count": 10,
  "custom_field_1": "...",
  "custom_field_2": "..."
}
```

**SQLAlchemy 모델:**
```python
from sqlalchemy import Column, Integer, String, Text, Boolean, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

class ChatSession(Base):
    __tablename__ = "chat_sessions"

    session_id = Column(String(100), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(200), nullable=False, default="새 대화")
    last_message = Column(Text)
    message_count = Column(Integer, default=0)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)

    # 주의: 'metadata'는 SQLAlchemy 예약어이므로 session_metadata로 매핑
    session_metadata = Column("metadata", JSONB)

    # Relationships
    user = relationship("User", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")
```

---

### 3. Chat Messages (채팅 메시지)

```sql
CREATE TABLE chat_messages (
    id BIGSERIAL PRIMARY KEY,
    session_id VARCHAR(100) NOT NULL REFERENCES chat_sessions(session_id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    structured_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_chat_messages_session_id ON chat_messages(session_id);
CREATE INDEX idx_chat_messages_created_at ON chat_messages(created_at);
```

**structured_data JSONB 필드 구조:**
```json
{
  "sections": [
    {
      "title": "핵심 답변",
      "content": "...",
      "icon": "target",
      "priority": "high",
      "expandable": false
    }
  ],
  "metadata": {
    "confidence": 0.9,
    "sources": ["database", "api"],
    "intent_type": "diagnosis"
  }
}
```

**SQLAlchemy 모델:**
```python
class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(100), ForeignKey("chat_sessions.session_id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(20), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    structured_data = Column(JSONB)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relationships
    session = relationship("ChatSession", back_populates="messages")
```

---

## 선택 테이블 (Optional - LangGraph Checkpointing)

LangGraph의 Checkpointing 기능을 사용할 경우 필요한 테이블들입니다.

### 4. Checkpoints (LangGraph용)

```sql
CREATE TABLE checkpoints (
    thread_id TEXT NOT NULL,
    checkpoint_ns TEXT NOT NULL DEFAULT '',
    checkpoint_id TEXT NOT NULL,
    parent_checkpoint_id TEXT,
    type TEXT,
    checkpoint JSONB NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}',
    PRIMARY KEY (thread_id, checkpoint_ns, checkpoint_id)
);
```

### 5. Checkpoint Blobs (LangGraph용)

```sql
CREATE TABLE checkpoint_blobs (
    thread_id TEXT NOT NULL,
    checkpoint_ns TEXT NOT NULL DEFAULT '',
    channel TEXT NOT NULL,
    version TEXT NOT NULL,
    type TEXT NOT NULL,
    blob BYTEA,
    PRIMARY KEY (thread_id, checkpoint_ns, channel, version)
);
```

### 6. Checkpoint Writes (LangGraph용)

```sql
CREATE TABLE checkpoint_writes (
    thread_id TEXT NOT NULL,
    checkpoint_ns TEXT NOT NULL DEFAULT '',
    checkpoint_id TEXT NOT NULL,
    task_id TEXT NOT NULL,
    idx INTEGER NOT NULL,
    channel TEXT NOT NULL,
    type TEXT,
    blob BYTEA NOT NULL,
    PRIMARY KEY (thread_id, checkpoint_ns, checkpoint_id, task_id, idx)
);
```

**생성 방법:**
```python
# LangGraph가 자동 생성 (setup() 메서드 호출 시)
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

async with AsyncPostgresSaver.from_conn_string(DB_URI) as checkpointer:
    await checkpointer.setup()  # 테이블 자동 생성
```

---

## 도메인별 테이블 (Domain-Specific)

도메인에 따라 추가로 필요한 테이블들입니다.

### 예시: 의료 도메인

```sql
-- 증상 테이블
CREATE TABLE symptoms (
    symptom_id BIGSERIAL PRIMARY KEY,
    symptom_name VARCHAR(100) NOT NULL,
    description TEXT,
    severity_level INTEGER DEFAULT 1,
    category VARCHAR(50)
);

-- 질병 테이블
CREATE TABLE diseases (
    disease_id BIGSERIAL PRIMARY KEY,
    disease_name VARCHAR(100) NOT NULL,
    description TEXT,
    icd_code VARCHAR(20),
    category VARCHAR(50)
);

-- 질병-증상 매핑
CREATE TABLE disease_symptoms (
    disease_id BIGINT REFERENCES diseases(disease_id),
    symptom_id BIGINT REFERENCES symptoms(symptom_id),
    weight FLOAT DEFAULT 1.0,
    PRIMARY KEY (disease_id, symptom_id)
);

-- 약물 테이블
CREATE TABLE medications (
    medication_id BIGSERIAL PRIMARY KEY,
    medication_name VARCHAR(100) NOT NULL,
    description TEXT,
    dosage_info TEXT,
    side_effects TEXT
);
```

### 예시: 부동산 도메인 (service_agent 기준)

```sql
-- 부동산 매물
CREATE TABLE real_estates (
    id BIGSERIAL PRIMARY KEY,
    region VARCHAR(50),
    district VARCHAR(50),
    property_type VARCHAR(20),
    trade_type VARCHAR(20),
    area_m2 FLOAT,
    price BIGINT,
    deposit BIGINT,
    monthly_rent INTEGER,
    floor INTEGER,
    building_year INTEGER,
    description TEXT,
    location_detail TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_real_estates_region ON real_estates(region);
CREATE INDEX idx_real_estates_price ON real_estates(price);

-- 거래 내역
CREATE TABLE transactions (
    id BIGSERIAL PRIMARY KEY,
    real_estate_id BIGINT REFERENCES real_estates(id),
    transaction_date DATE,
    transaction_type VARCHAR(20),
    price BIGINT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

---

## 마이그레이션 가이드

### 1. Alembic 초기화

```bash
# Alembic 설치
pip install alembic

# 초기화
alembic init migrations
```

### 2. alembic.ini 수정

```ini
# migrations/alembic.ini
sqlalchemy.url = postgresql://user:password@localhost/dbname
```

### 3. env.py 수정

```python
# migrations/env.py
from app.db.postgre_db import Base
from app.models.users import User
from app.models.chat import ChatSession, ChatMessage
# 도메인별 모델 임포트
from app.models.your_domain import YourModel

target_metadata = Base.metadata
```

### 4. 마이그레이션 생성 및 적용

```bash
# 마이그레이션 파일 생성
alembic revision --autogenerate -m "Create initial tables"

# 마이그레이션 적용
alembic upgrade head

# 롤백
alembic downgrade -1
```

---

## Connection 설정

### 1. 환경변수 (.env)

```env
# PostgreSQL 설정
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=your_database

# Connection String
DATABASE_URL=postgresql+asyncpg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}
```

### 2. DB 연결 코드

```python
# app/db/postgre_db.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.core.config import settings

# Base 클래스
Base = declarative_base()

# Async Engine
engine = create_async_engine(
    settings.postgres_url,
    echo=False,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True
)

# Session Factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Dependency
async def get_async_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
```

---

## 체크리스트

### 필수 (모든 서비스)
- [ ] users 테이블 생성
- [ ] chat_sessions 테이블 생성
- [ ] chat_messages 테이블 생성
- [ ] SQLAlchemy 모델 작성
- [ ] Alembic 설정
- [ ] 마이그레이션 생성 및 적용

### 선택 (LangGraph Checkpointing 사용 시)
- [ ] checkpoints 테이블 생성 (자동)
- [ ] checkpoint_blobs 테이블 생성 (자동)
- [ ] checkpoint_writes 테이블 생성 (자동)

### 도메인별
- [ ] 도메인 특화 테이블 설계
- [ ] 인덱스 설정
- [ ] 관계 설정
- [ ] 샘플 데이터 삽입

---

## FAQ

### Q1: metadata vs session_metadata?

**A:** SQLAlchemy에서 `metadata`는 예약어입니다. DB 컬럼명은 `metadata`지만, Python 속성명은 `session_metadata`로 매핑합니다.

```python
# DB 컬럼: metadata
# Python 속성: session_metadata
session_metadata = Column("metadata", JSONB)
```

### Q2: session_id를 String으로 사용하는 이유?

**A:** UUID 대신 사용자 정의 형식(`session-{timestamp}-{random}`)을 사용하기 위해 VARCHAR(100)을 사용합니다.

### Q3: JSONB vs JSON?

**A:** PostgreSQL에서는 **JSONB 사용을 권장**합니다:
- 인덱싱 가능
- 쿼리 성능 우수
- 중복 키 자동 제거

### Q4: Long-term Memory는 어떻게 저장하나요?

**A:** `chat_sessions.metadata` JSONB 필드에 `conversation_summary` 키로 저장합니다:

```python
session.session_metadata = {
    "conversation_summary": "대화 요약...",
    "last_updated": datetime.now().isoformat(),
    "message_count": 10
}
```

### Q5: 도메인별 테이블은 어디에 작성하나요?

**A:** `backend/app/models/` 폴더에 도메인별 파일 생성:

```
app/models/
├── __init__.py
├── users.py           # 사용자 모델
├── chat.py            # 채팅 모델
└── your_domain.py     # 도메인 특화 모델 (새로 생성)
```

---

**작성일**: 2025-10-20
**버전**: 1.0
