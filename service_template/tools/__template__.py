"""
Tool Template
도구 개발 시 이 파일을 복사하여 시작하세요
"""

import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class ToolTemplate:
    """
    Tool 템플릿 클래스

    개발 가이드:
    1. 클래스명 변경: ToolTemplate → YourTool (예: DatabaseSearchTool)
    2. __init__() 수정: 필요한 리소스 초기화 (DB 연결, API 클라이언트 등)
    3. search() 또는 execute() 구현: 핵심 로직
    4. 에러 핸들링: try-except로 안전하게
    5. 반환 형식 통일: {"status": "success/error", "data": [...]}
    """

    def __init__(self):
        """
        초기화

        TODO: 필요한 리소스 초기화
        - DB 연결
        - API 클라이언트
        - 설정 로드
        """
        # 예시:
        # self.db_connection = self._connect_to_database()
        # self.api_client = self._initialize_api_client()

        logger.info("ToolTemplate initialized")

    async def search(
        self,
        query: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        검색 실행 (메인 메서드)

        Args:
            query: 검색 쿼리
            params: 검색 파라미터 (선택적)
                예시:
                {
                    "limit": 10,
                    "filters": {...},
                    "sort_by": "relevance"
                }

        Returns:
            {
                "status": "success" | "error",
                "data": [...],  # 결과 리스트
                "metadata": {   # 메타데이터 (선택적)
                    "total_count": 100,
                    "query_time_ms": 123,
                    "source": "database"
                },
                "error": str    # 에러 발생 시만
            }

        TODO: 검색 로직 구현
        """
        try:
            # 파라미터 파싱
            params = params or {}
            limit = params.get("limit", 10)
            filters = params.get("filters", {})

            # TODO: 검색 로직 구현
            # 예시:
            # results = await self._execute_search(query, filters, limit)

            # 임시 결과 (구현 전)
            results = []

            # 성공 응답
            return {
                "status": "success",
                "data": results,
                "metadata": {
                    "total_count": len(results),
                    "query": query,
                    "source": "template_tool"
                }
            }

        except Exception as e:
            logger.error(f"Search failed: {e}")
            return {
                "status": "error",
                "data": [],
                "error": str(e)
            }

    async def execute(
        self,
        action: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        범용 실행 메서드 (검색 외 작업용)

        Args:
            action: 실행할 작업 (예: "create", "update", "delete")
            params: 작업 파라미터

        Returns:
            {
                "status": "success" | "error",
                "result": {...},
                "error": str  # 에러 발생 시만
            }

        TODO: 작업별 로직 구현
        """
        try:
            params = params or {}

            # TODO: 작업별 분기
            if action == "create":
                result = await self._create(params)
            elif action == "update":
                result = await self._update(params)
            elif action == "delete":
                result = await self._delete(params)
            else:
                raise ValueError(f"Unknown action: {action}")

            return {
                "status": "success",
                "result": result
            }

        except Exception as e:
            logger.error(f"Execute failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    # ==============================================================================
    # Private Methods (내부 구현)
    # ==============================================================================

    async def _create(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        생성 작업

        TODO: 구현
        """
        logger.info("Create operation")
        return {"message": "Not implemented"}

    async def _update(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        업데이트 작업

        TODO: 구현
        """
        logger.info("Update operation")
        return {"message": "Not implemented"}

    async def _delete(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        삭제 작업

        TODO: 구현
        """
        logger.info("Delete operation")
        return {"message": "Not implemented"}

    def _validate_params(self, params: Dict[str, Any], required_fields: List[str]) -> None:
        """
        파라미터 검증 유틸리티

        Args:
            params: 검증할 파라미터
            required_fields: 필수 필드 목록

        Raises:
            ValueError: 필수 필드 누락 시
        """
        missing = [field for field in required_fields if field not in params]
        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}")

    def _format_result(self, raw_data: Any) -> Dict[str, Any]:
        """
        결과 포맷 변환 유틸리티

        Args:
            raw_data: 원본 데이터

        Returns:
            포맷팅된 결과

        TODO: 도메인별 포맷 정의
        """
        # 예시: DB 결과 → 표준 포맷
        return {
            "id": raw_data.get("id"),
            "title": raw_data.get("title"),
            "content": raw_data.get("content"),
            # ...
        }


# ==============================================================================
# 사용 예시 (테스트 코드)
# ==============================================================================

if __name__ == "__main__":
    async def test_tool():
        """Tool 테스트"""

        # Tool 초기화
        tool = ToolTemplate()

        # 검색 테스트
        result = await tool.search(
            query="테스트 쿼리",
            params={
                "limit": 5,
                "filters": {}
            }
        )

        print(f"Status: {result['status']}")
        print(f"Data count: {len(result['data'])}")

        # 실행 테스트
        result = await tool.execute(
            action="create",
            params={"name": "테스트"}
        )

        print(f"Status: {result['status']}")

    import asyncio
    asyncio.run(test_tool())
