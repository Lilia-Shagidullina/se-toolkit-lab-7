"""LMS API client service."""

from dataclasses import dataclass

import httpx


@dataclass
class HealthStatus:
    """Health check result."""

    is_healthy: bool
    item_count: int = 0
    error_message: str = ""


@dataclass
class PassRateResult:
    """Pass rate result for a lab."""

    task: str
    avg_score: float
    attempts: int


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

    async def health_check(self) -> HealthStatus:
        """Check if the LMS backend is healthy.

        Returns:
            HealthStatus with health information.
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/items/",
                    headers=self._headers,
                    timeout=5.0,
                )
                if response.status_code == 200:
                    items = response.json()
                    return HealthStatus(is_healthy=True, item_count=len(items))
                else:
                    return HealthStatus(
                        is_healthy=False,
                        error_message=f"HTTP {response.status_code} {response.reason_phrase}",
                    )
        except httpx.ConnectError as e:
            return HealthStatus(
                is_healthy=False,
                error_message=f"connection refused ({self.base_url}). Check that the services are running.",
            )
        except httpx.HTTPStatusError as e:
            return HealthStatus(
                is_healthy=False,
                error_message=f"HTTP {e.response.status_code} {e.response.reason_phrase}. The backend service may be down.",
            )
        except httpx.HTTPError as e:
            return HealthStatus(
                is_healthy=False,
                error_message=str(e),
            )

    async def get_items(self) -> list[dict]:
        """Get all items (labs and tasks) from the LMS.

        Returns:
            List of item dictionaries.

        Raises:
            httpx.HTTPError: If the request fails.
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/items/",
                    headers=self._headers,
                    timeout=5.0,
                )
                response.raise_for_status()
                return response.json()
        except httpx.ConnectError:
            raise RuntimeError(f"Cannot connect to backend at {self.base_url}")
        except httpx.HTTPStatusError as e:
            raise RuntimeError(f"Backend returned HTTP {e.response.status_code}")
        except httpx.TimeoutException:
            raise RuntimeError(f"Backend request timed out")

    async def get_pass_rates(self, lab_id: str) -> list[PassRateResult]:
        """Get pass rates for a specific lab.

        Args:
            lab_id: The lab identifier (e.g., "lab-04").

        Returns:
            List of PassRateResult objects.

        Raises:
            RuntimeError: If the request fails.
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/analytics/pass-rates",
                    params={"lab": lab_id},
                    headers=self._headers,
                    timeout=5.0,
                )
                response.raise_for_status()
                data = response.json()
                return [
                    PassRateResult(
                        task=item.get("task", "Unknown"),
                        avg_score=item.get("avg_score", 0.0),
                        attempts=item.get("attempts", 0),
                    )
                    for item in data
                ]
        except httpx.ConnectError:
            raise RuntimeError(f"Cannot connect to backend at {self.base_url}")
        except httpx.HTTPStatusError as e:
            raise RuntimeError(f"Backend returned HTTP {e.response.status_code}")
        except httpx.TimeoutException:
            raise RuntimeError(f"Backend request timed out")
