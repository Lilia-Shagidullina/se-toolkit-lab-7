"""LMS API client service."""

import httpx


class LMSClient:
    """Client for interacting with the LMS backend API."""

    def __init__(self, base_url: str, api_key: str = "") -> None:
        """Initialize the LMS client.

        Args:
            base_url: Base URL of the LMS API.
            api_key: API key for authentication.
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self._headers = {}
        if api_key:
            self._headers["Authorization"] = f"Bearer {api_key}"

    async def health_check(self) -> bool:
        """Check if the LMS backend is healthy.

        Returns:
            True if the backend is healthy, False otherwise.
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/health",
                    headers=self._headers,
                    timeout=5.0,
                )
                return response.status_code == 200
        except httpx.HTTPError:
            return False

    async def get_learners(self) -> list[dict]:
        """Get all learners from the LMS.

        Returns:
            List of learner dictionaries.
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/learners",
                    headers=self._headers,
                    timeout=5.0,
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError:
            return []

    async def get_scores(self, lab_id: str) -> list[dict]:
        """Get scores for a specific lab.

        Args:
            lab_id: The lab identifier.

        Returns:
            List of score dictionaries.
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/scores/{lab_id}",
                    headers=self._headers,
                    timeout=5.0,
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError:
            return []
