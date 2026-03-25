"""LLM API client service."""

import httpx


class LLMClient:
    """Client for interacting with the LLM API for intent routing."""

    def __init__(self, api_key: str) -> None:
        """Initialize the LLM client.

        Args:
            api_key: API key for the LLM service.
        """
        self.api_key = api_key

    async def detect_intent(self, message: str) -> str:
        """Detect the intent of a user message.

        Args:
            message: The user's message text.

        Returns:
            The detected intent (e.g., 'start', 'help', 'health', 'labs', 'scores').
        """
        if not self.api_key:
            return self._fallback_intent(message)

        # TODO: Implement actual LLM API call
        # For now, use simple keyword matching
        return self._fallback_intent(message)

    def _fallback_intent(self, message: str) -> str:
        """Fallback intent detection using keyword matching.

        Args:
            message: The user's message text.

        Returns:
            The detected intent.
        """
        message_lower = message.lower()

        if any(word in message_lower for word in ["привет", "start", "начать"]):
            return "start"
        if any(word in message_lower for word in ["помощь", "help", "команд"]):
            return "help"
        if any(word in message_lower for word in ["health", "статус", "здоров"]):
            return "health"
        if any(word in message_lower for word in ["lab", "лаборатор", "список"]):
            return "labs"
        if any(word in message_lower for word in ["score", "оценк", "балл"]):
            return "scores"

        return "unknown"
