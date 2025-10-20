# Service Template 개발 가이드

**단계별 개발 프로세스**

---

## 개발 단계 개요

```
Phase 1: 도메인 정의 및 설정 (1~2일)
  └─> Phase 2: Planning Agent (1일)
      └─> Phase 3: Tools 개발 (3~5일)
          └─> Phase 4: Execution Agents (2~3일)
              └─> Phase 5: Supervisor 통합 (1~2일)
                  └─> Phase 6: 테스트 및 최적화 (2일)
```

**총 예상 기간: 10~15일**

---

## Phase 1: 도메인 정의 및 설정

### 1.1 도메인 분석

먼저 당신의 도메인을 명확히 정의하세요:

**질문 체크리스트:**
- [ ] 어떤 도메인인가? (예: 의료, 금융, 교육, 전자상거래)
- [ ] 사용자가 물어볼 수 있는 주요 질문 유형은? (3~7개)
- [ ] 어떤 데이터 소스가 필요한가? (DB, API, 파일)
- [ ] 어떤 작업을 수행해야 하는가? (검색, 분석, 생성)

**예시 (의료 도메인):**
```
도메인: 의료 진단 보조
주요 질문 유형:
  - 증상 분석 (SYMPTOM_ANALYSIS)
  - 진단 추천 (DIAGNOSIS)
  - 치료 계획 (TREATMENT)
  - 약물 정보 (MEDICATION)
  - 검사 해석 (TEST_INTERPRETATION)

데이터 소스:
  - 의료 데이터베이스 (증상, 질병)
  - 약물 정보 API
  - 임상 가이드라인 문서

작업:
  - 증상 기반 질병 검색
  - 진단 결과 분석
  - 치료 계획 생성
```

### 1.2 설정 파일 수정

#### `foundation/config.py`

```python
# 1. 데이터베이스 경로 수정
DATABASES = {
    "medical_symptoms": DB_DIR / "medical" / "symptoms.db",
    "medical_diseases": DB_DIR / "medical" / "diseases.db",
    "medication": DB_DIR / "medical" / "medication.db",
}

# 2. LLM 모델 설정 (비용 최적화)
DEFAULT_MODELS = {
    "intent": "gpt-4o-mini",           # 의도 분석 (빠름, 저렴)
    "planning": "gpt-4o-mini",         # 계획 수립
    "diagnosis": "gpt-4o",             # 진단 (정확함, 비쌈)
    "analysis": "gpt-4o",              # 분석
}

# 3. 타임아웃 설정
TIMEOUTS = {
    "agent": 45,      # Agent 타임아웃 (의료는 더 오래 걸릴 수 있음)
    "llm": 30,        # LLM 타임아웃
}
```

### 1.3 프롬프트 폴더 생성

```bash
mkdir -p reports/prompts
```

**필수 프롬프트 파일:**
- `intent_analysis.md` - 의도 분석
- `agent_selection.md` - Agent 선택
- `tool_selection.md` - Tool 선택
- `response_synthesis.md` - 응답 생성

---

## Phase 2: Planning Agent 개발

### 2.1 Intent 타입 정의

#### `cognitive_agents/planning_agent.py`

```python
class IntentType(Enum):
    """의도 타입 정의 - 의료 도메인"""

    # 주요 의도
    SYMPTOM_ANALYSIS = "증상분석"
    DIAGNOSIS = "진단"
    TREATMENT = "치료"
    MEDICATION = "약물정보"
    TEST_INTERPRETATION = "검사해석"

    # 일반 의도
    GENERAL_INQUIRY = "일반문의"
    UNCLEAR = "unclear"
    IRRELEVANT = "irrelevant"
```

### 2.2 Intent 패턴 수정

```python
def _initialize_intent_patterns(self) -> Dict[IntentType, List[str]]:
    """의도 패턴 초기화 - 의료 도메인"""
    return {
        IntentType.SYMPTOM_ANALYSIS: [
            "증상", "아프", "통증", "열", "기침", "두통"
        ],
        IntentType.DIAGNOSIS: [
            "진단", "병명", "질병", "무슨병", "어떤병"
        ],
        IntentType.TREATMENT: [
            "치료", "치료법", "어떻게", "방법"
        ],
        IntentType.MEDICATION: [
            "약", "처방", "복용", "의약품"
        ],
        # ...
    }
```

### 2.3 프롬프트 작성

#### `reports/prompts/intent_analysis.md`

```markdown
당신은 의료 상담 AI의 의도 분석 전문가입니다.

사용자 질문: {{query}}

다음 의도 타입 중 하나를 선택하세요:
- SYMPTOM_ANALYSIS: 증상 분석
- DIAGNOSIS: 진단
- TREATMENT: 치료 계획
- MEDICATION: 약물 정보
- TEST_INTERPRETATION: 검사 결과 해석
- GENERAL_INQUIRY: 일반 문의
- UNCLEAR: 불명확
- IRRELEVANT: 무관

JSON 형식으로 응답:
{
  "intent": "SYMPTOM_ANALYSIS",
  "confidence": 0.9,
  "keywords": ["두통", "열", "기침"],
  "reasoning": "증상 관련 질문입니다.",
  "entities": {
    "symptoms": ["두통", "열"]
  }
}
```

---

## Phase 3: Tools 개발

### 3.1 Tool 구조 설계

**Tool 목록 예시 (의료 도메인):**

1. **SymptomDatabaseTool** - 증상 검색
2. **DiseaseDatabaseTool** - 질병 검색
3. **MedicationSearchTool** - 약물 정보 검색
4. **DiagnosisAnalyzerTool** - 진단 분석
5. **TreatmentPlannerTool** - 치료 계획 생성

### 3.2 Tool 개발 (예시)

#### `tools/symptom_database_tool.py`

```python
"""
증상 데이터베이스 검색 도구
"""

import logging
from typing import Dict, Any, List, Optional
import sqlite3

logger = logging.getLogger(__name__)


class SymptomDatabaseTool:
    """증상 기반 질병 검색 도구"""

    def __init__(self):
        """DB 연결 초기화"""
        from app.service_template.foundation.config import Config

        self.db_path = Config.DATABASES["medical_symptoms"]
        logger.info(f"SymptomDatabaseTool initialized with DB: {self.db_path}")

    async def search(
        self,
        query: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        증상 기반 질병 검색

        Args:
            query: 검색 쿼리 (증상 설명)
            params: 검색 파라미터
                - symptoms: List[str] - 증상 목록
                - limit: int - 결과 개수 (기본 10)

        Returns:
            {
                "status": "success",
                "data": [
                    {
                        "disease_id": 1,
                        "disease_name": "감기",
                        "matching_symptoms": ["열", "기침"],
                        "confidence": 0.8
                    }
                ]
            }
        """
        try:
            params = params or {}
            symptoms = params.get("symptoms", [])
            limit = params.get("limit", 10)

            # DB 쿼리 (예시 - 실제 스키마에 맞게 수정)
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # SQL 쿼리 (증상과 매칭되는 질병 검색)
            # TODO: 실제 DB 스키마에 맞게 수정
            cursor.execute("""
                SELECT
                    d.disease_id,
                    d.disease_name,
                    COUNT(s.symptom_id) as match_count
                FROM diseases d
                JOIN disease_symptoms ds ON d.disease_id = ds.disease_id
                JOIN symptoms s ON ds.symptom_id = s.symptom_id
                WHERE s.symptom_name IN ({})
                GROUP BY d.disease_id
                ORDER BY match_count DESC
                LIMIT ?
            """.format(','.join('?' * len(symptoms))), symptoms + [limit])

            results = []
            for row in cursor.fetchall():
                results.append({
                    "disease_id": row[0],
                    "disease_name": row[1],
                    "match_count": row[2],
                    "confidence": min(row[2] / len(symptoms), 1.0)
                })

            conn.close()

            return {
                "status": "success",
                "data": results,
                "metadata": {
                    "total_count": len(results),
                    "query_symptoms": symptoms
                }
            }

        except Exception as e:
            logger.error(f"Symptom search failed: {e}")
            return {
                "status": "error",
                "data": [],
                "error": str(e)
            }
```

### 3.3 Tool 테스트

```python
# tools/test_symptom_tool.py

async def test_symptom_tool():
    tool = SymptomDatabaseTool()

    result = await tool.search(
        query="두통과 열이 있습니다",
        params={
            "symptoms": ["두통", "열", "기침"],
            "limit": 5
        }
    )

    print(f"Status: {result['status']}")
    print(f"Found {len(result['data'])} diseases")
    for disease in result['data']:
        print(f"  - {disease['disease_name']} (confidence: {disease['confidence']:.2f})")

import asyncio
asyncio.run(test_symptom_tool())
```

---

## Phase 4: Execution Agents 개발

### 4.1 팀 구조 설계

**팀 목록 예시 (의료 도메인):**

1. **Data Collection Team** - 증상/질병 데이터 수집
2. **Diagnosis Team** - 진단 분석
3. **Treatment Team** - 치료 계획 수립

### 4.2 State 정의

#### `models/states.py`

```python
class DataCollectionState(TypedDict):
    """데이터 수집 팀 상태"""
    team_name: str
    status: str
    shared_context: SharedState

    # 수집 결과
    collected_symptoms: List[Dict]
    matched_diseases: List[Dict]
    medication_data: List[Dict]

    # 메타데이터
    data_sources: List[str]
    collection_time: Optional[float]
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    error: Optional[str]


class DiagnosisState(TypedDict):
    """진단 팀 상태"""
    team_name: str
    status: str
    shared_context: SharedState

    # 입력 데이터 (Data Collection Team 결과)
    input_data: Optional[Dict]

    # 진단 결과
    diagnosis_result: Optional[Dict]
    confidence_score: float
    risk_factors: List[str]
    recommended_tests: List[str]

    # 타이밍
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    error: Optional[str]
```

### 4.3 팀 개발 (예시)

#### `execution_agents/data_collection_team.py`

```python
"""
Data Collection Team - 데이터 수집
"""

from app.service_template.execution_agents.__template__ import TemplateTeam
from app.service_template.models.states import DataCollectionState


class DataCollectionTeam(TemplateTeam):
    """데이터 수집 팀"""

    def __init__(self, llm_context=None):
        super().__init__(llm_context)
        self.team_name = "data_collection"

        # Tool 초기화
        from app.service_template.tools.symptom_database_tool import SymptomDatabaseTool
        from app.service_template.tools.medication_search_tool import MedicationSearchTool

        self.symptom_tool = SymptomDatabaseTool()
        self.medication_tool = MedicationSearchTool()

    async def execute_node(self, state: DataCollectionState) -> DataCollectionState:
        """데이터 수집 실행"""
        logger.info("[DataCollectionTeam] Collecting data")

        shared_context = state.get("shared_context", {})
        query = shared_context.get("query", "")

        # 1. 증상 추출 (LLM 또는 규칙 기반)
        symptoms = self._extract_symptoms(query)

        # 2. 증상 기반 질병 검색
        disease_result = await self.symptom_tool.search(
            query,
            params={"symptoms": symptoms}
        )

        state["matched_diseases"] = disease_result.get("data", [])
        state["data_sources"] = ["symptom_db"]

        return state
```

---

## Phase 5: Supervisor 통합

### 5.1 Supervisor 구성

#### `supervisor/main_supervisor.py`

```python
from app.service_template.supervisor.__template__ import MainSupervisor as BaseSupervisor
from app.service_template.cognitive_agents.planning_agent import PlanningAgent
from app.service_template.execution_agents.data_collection_team import DataCollectionTeam
from app.service_template.execution_agents.diagnosis_team import DiagnosisTeam


class MedicalSupervisor(BaseSupervisor):
    """의료 도메인 Supervisor"""

    def __init__(self, llm_context=None):
        super().__init__(llm_context)

        # Planning Agent
        self.planning_agent = PlanningAgent(llm_context=llm_context)

        # 팀 초기화
        self.teams = {
            "data_collection": DataCollectionTeam(llm_context),
            "diagnosis": DiagnosisTeam(llm_context),
        }

        # 워크플로우 재구성
        self._build_graph()
```

---

## Phase 6: 테스트 및 최적화

### 6.1 통합 테스트

```python
# tests/test_integration.py

async def test_full_workflow():
    """전체 워크플로우 테스트"""

    supervisor = MedicalSupervisor()

    test_cases = [
        {
            "query": "두통과 열이 있어요",
            "expected_intent": "SYMPTOM_ANALYSIS",
            "expected_teams": ["data_collection", "diagnosis"]
        },
        {
            "query": "감기 치료 방법은?",
            "expected_intent": "TREATMENT",
            "expected_teams": ["data_collection", "treatment"]
        }
    ]

    for case in test_cases:
        result = await supervisor.process_query(case["query"])

        assert result["status"] == "completed"
        assert result["planning_state"]["analyzed_intent"]["intent_type"] == case["expected_intent"]
        assert set(result["active_teams"]) == set(case["expected_teams"])

        print(f"✅ Test passed: {case['query']}")
```

### 6.2 성능 최적화

**체크리스트:**
- [ ] LLM 호출 최소화 (캐싱, 배칭)
- [ ] DB 쿼리 최적화 (인덱스, 쿼리 튜닝)
- [ ] 병렬 실행 활용 (독립적인 팀)
- [ ] 프롬프트 최적화 (토큰 수 감소)
- [ ] 타임아웃 조정 (팀별 특성 반영)

---

## 개발 팁

### 1. 단계별 검증

각 단계를 완료할 때마다 테스트:
```python
# Phase 2 완료 후
python -m app.service_template.cognitive_agents.planning_agent

# Phase 3 완료 후
python -m app.service_template.tools.symptom_database_tool

# Phase 4 완료 후
python -m app.service_template.execution_agents.data_collection_team
```

### 2. 로깅 활용

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# 특정 모듈만 디버그
logging.getLogger("app.service_template").setLevel(logging.DEBUG)
```

### 3. 프롬프트 반복 개선

프롬프트는 여러 번 테스트하며 개선:
1. 초기 버전 작성
2. 다양한 쿼리로 테스트
3. 잘못된 응답 분석
4. 프롬프트 수정
5. 재테스트

---

## 참고 자료

- [LangGraph 공식 문서](https://langchain-ai.github.io/langgraph/)
- [OpenAI API 문서](https://platform.openai.com/docs/)
- [서비스 에이전트 아키텍처 분석](../../reports/service_agent_architecture_analysis.md)
- [README](./README.md)

---

**작성일**: 2025-10-20
**버전**: 1.0
