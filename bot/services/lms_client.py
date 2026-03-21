"""LMS API client service."""

from dataclasses import dataclass

import httpx


@dataclass
class BackendError:
    """Represents a backend error with details."""

    message: str
    status_code: int | None = None
    details: str | None = None


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

    async def _request(self, method: str, path: str, **kwargs) -> httpx.Response | None:
        """Make an HTTP request with error handling.

        Args:
            method: HTTP method (GET, POST, etc.)
            path: API path (e.g., "/items/")
            **kwargs: Additional arguments for httpx.

        Returns:
            Response object or None if request failed.

        Raises:
            BackendError: If the request fails.
        """
        url = f"{self.base_url}{path}"
        headers = {**self._headers, **kwargs.pop("headers", {})}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.request(
                    method, url, headers=headers, timeout=10.0, **kwargs
                )
                response.raise_for_status()
                return response
        except httpx.ConnectError as e:
            raise BackendError(
                message=f"connection refused ({self.base_url})",
                details=str(e),
            ) from e
        except httpx.TimeoutException as e:
            raise BackendError(
                message=f"request timed out ({self.base_url})",
                details=str(e),
            ) from e
        except httpx.HTTPStatusError as e:
            raise BackendError(
                message=f"HTTP {e.response.status_code} {e.response.reason_phrase}",
                status_code=e.response.status_code,
                details=str(e),
            ) from e
        except httpx.HTTPError as e:
            raise BackendError(
                message=f"HTTP error: {str(e)}",
                details=str(e),
            ) from e

    async def health_check(self) -> tuple[bool, str | None]:
        """Check if the LMS backend is healthy.

        Returns:
            Tuple of (is_healthy, error_message).
            error_message is None if healthy, or contains error details if not.
        """
        try:
            response = await self._request("GET", "/items/")
            if response is not None:
                data = response.json()
                count = len(data) if isinstance(data, list) else "unknown"
                return True, f"Backend is healthy. {count} items available."
            return False, "Unknown backend state"
        except BackendError as e:
            return False, f"Backend error: {e.message}. Check that the services are running."

    async def get_items(self) -> list[dict]:
        """Get all items (labs and tasks) from the LMS.

        Returns:
            List of item dictionaries.

        Raises:
            BackendError: If the request fails.
        """
        response = await self._request("GET", "/items/")
        if response is None:
            return []
        return response.json() if isinstance(response.json(), list) else []

    async def get_learners(self) -> list[dict]:
        """Get all learners from the LMS.

        Returns:
            List of learner dictionaries.

        Raises:
            BackendError: If the request fails.
        """
        response = await self._request("GET", "/learners/")
        if response is None:
            return []
        return response.json() if isinstance(response.json(), list) else []

    async def get_pass_rates(self, lab_id: str) -> list[dict]:
        """Get pass rates for a specific lab.

        Args:
            lab_id: The lab identifier (e.g., "lab-04").

        Returns:
            List of pass rate dictionaries with task names and percentages.

        Raises:
            BackendError: If the request fails.
        """
        response = await self._request(
            "GET", "/analytics/pass-rates/", params={"lab": lab_id}
        )
        if response is None:
            return []
        data = response.json()
        return data if isinstance(data, list) else []

    async def get_scores(self, lab_id: str) -> list[dict]:
        """Get scores for a specific lab.

        Args:
            lab_id: The lab identifier.

        Returns:
            List of score dictionaries.

        Raises:
            BackendError: If the request fails.
        """
        response = await self._request(
            "GET", "/analytics/scores/", params={"lab": lab_id}
        )
        if response is None:
            return []
        return response.json() if isinstance(response.json(), list) else []
