"""LLM API client service with tool calling support."""

import json
import sys
from typing import Any

import httpx

from services.lms_client import LMSClient


def get_tool_definitions(lms_client: LMSClient) -> list[dict[str, Any]]:
    """Get the list of tool definitions for the LLM.

    Args:
        lms_client: The LMS client instance to use for tool execution.

    Returns:
        List of tool definitions in OpenAI-compatible format.
    """
    return [
        {
            "type": "function",
            "function": {
                "name": "get_items",
                "description": "Get all labs and tasks. Use this to list available labs or find a lab by name.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_pass_rates",
                "description": "Get per-task pass rates and attempt counts for a specific lab.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {
                            "type": "string",
                            "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                        },
                    },
                    "required": ["lab"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_scores",
                "description": "Get score distribution (4 buckets: 0-25, 26-50, 51-75, 76-100) for a lab.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {
                            "type": "string",
                            "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                        },
                    },
                    "required": ["lab"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_timeline",
                "description": "Get submissions per day for a lab to see activity over time.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {
                            "type": "string",
                            "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                        },
                    },
                    "required": ["lab"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_groups",
                "description": "Get per-group performance (average score and student count) for a lab.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {
                            "type": "string",
                            "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                        },
                    },
                    "required": ["lab"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_top_learners",
                "description": "Get top N learners by average score for a lab.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {
                            "type": "string",
                            "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Number of top learners to return (default: 10)",
                            "default": 10,
                        },
                    },
                    "required": ["lab"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_completion_rate",
                "description": "Get completion rate (percentage of learners who scored >= 60) for a lab.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {
                            "type": "string",
                            "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                        },
                    },
                    "required": ["lab"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_learners",
                "description": "Get all enrolled learners and their groups.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "trigger_sync",
                "description": "Trigger ETL sync to refresh data from autochecker. Use when user asks to update data.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
        },
    ]


async def execute_tool(
    name: str, arguments: dict[str, Any], lms_client: LMSClient
) -> Any:
    """Execute a tool and return the result.

    Args:
        name: The tool name.
        arguments: The tool arguments.
        lms_client: The LMS client instance.

    Returns:
        The tool execution result.
    """
    if name == "get_items":
        return await lms_client.get_items()
    elif name == "get_pass_rates":
        lab = arguments.get("lab", "")
        results = await lms_client.get_pass_rates(lab)
        return [{"task": r.task, "avg_score": r.avg_score, "attempts": r.attempts} for r in results]
    elif name == "get_scores":
        lab = arguments.get("lab", "")
        return await lms_client.get_scores(lab)
    elif name == "get_timeline":
        lab = arguments.get("lab", "")
        return await lms_client.get_timeline(lab)
    elif name == "get_groups":
        lab = arguments.get("lab", "")
        return await lms_client.get_groups(lab)
    elif name == "get_top_learners":
        lab = arguments.get("lab", "")
        limit = arguments.get("limit", 10)
        return await lms_client.get_top_learners(lab, limit)
    elif name == "get_completion_rate":
        lab = arguments.get("lab", "")
        return await lms_client.get_completion_rate(lab)
    elif name == "get_learners":
        return await lms_client.get_learners()
    elif name == "trigger_sync":
        return await lms_client.trigger_sync()
    else:
        return {"error": f"Unknown tool: {name}"}


class LLMClient:
    """Client for interacting with the LLM API for intent routing."""

    def __init__(self, api_key: str, base_url: str, model: str) -> None:
        """Initialize the LLM client.

        Args:
            api_key: API key for the LLM service.
            base_url: Base URL of the LLM API.
            model: Model name to use.
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model

    async def route(
        self, message: str, lms_client: LMSClient, debug: bool = False
    ) -> str:
        """Route a user message to the appropriate tool(s) and return a response.

        Args:
            message: The user's message text.
            lms_client: The LMS client instance for tool execution.
            debug: Whether to print debug output to stderr.

        Returns:
            The LLM's response text.
        """
        if not self.api_key:
            return self._fallback_response(message)

        tools = get_tool_definitions(lms_client)
        system_prompt = (
            "You are a helpful assistant for a Learning Management System (LMS) bot. "
            "Users can ask about labs, scores, pass rates, groups, top learners, and completion rates. "
            "Use the available tools to fetch data and answer questions accurately. "
            "If you don't have enough information, ask clarifying questions. "
            "If the user's message is gibberish or unclear, politely explain what you can help with. "
            "Always provide specific data when available (percentages, counts, names). "
            "After calling tools, analyze the results and provide a clear, helpful summary."
        )

        messages: list[dict[str, Any]] = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message},
        ]

        max_iterations = 10
        for iteration in range(max_iterations):
            if debug:
                print(
                    f"[LLM] Iteration {iteration + 1}/{max_iterations}", file=sys.stderr
                )

            response = await self._call_llm(messages, tools)

            if debug:
                print(f"[LLM] Response: {response.get('choices', [])}", file=sys.stderr)

            # Check if LLM wants to call tools
            tool_calls = response.get("choices", [{}])[0].get("message", {}).get("tool_calls", [])

            if not tool_calls:
                # LLM returned final response
                content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
                return content or "I'm not sure how to help with that. Try asking about labs, scores, or pass rates."

            # Execute tool calls
            for tool_call in tool_calls:
                func_name = tool_call.get("function", {}).get("name", "")
                func_args = tool_call.get("function", {}).get("arguments", "{}")

                try:
                    args = json.loads(func_args) if isinstance(func_args, str) else func_args
                except json.JSONDecodeError:
                    args = {}

                if debug:
                    print(f"[tool] LLM called: {func_name}({args})", file=sys.stderr)

                result = await execute_tool(func_name, args, lms_client)

                if debug:
                    result_str = str(result)[:200] + "..." if len(str(result)) > 200 else str(result)
                    print(f"[tool] Result: {result_str}", file=sys.stderr)

                # Add tool result to conversation
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.get("id", ""),
                    "content": json.dumps(result, default=str),
                })

            if debug:
                print(f"[summary] Feeding {len(tool_calls)} tool result(s) back to LLM", file=sys.stderr)

        return "This request requires multiple data lookups. Please try a simpler question like 'show me scores for lab-04' or 'what labs are available?'"

    async def _call_llm(
        self, messages: list[dict[str, Any]], tools: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Call the LLM API.

        Args:
            messages: Conversation messages.
            tools: Tool definitions.

        Returns:
            LLM response.
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "tools": tools,
            "tool_choice": "auto",
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30.0,
            )
            response.raise_for_status()
            return response.json()

    def _fallback_response(self, message: str) -> str:
        """Generate a fallback response without LLM.

        Args:
            message: The user's message text.

        Returns:
            A simple response based on keywords.
        """
        msg_lower = message.lower()

        if any(word in msg_lower for word in ["привет", "hello", "hi", "start"]):
            return "👋 Привет! Я LMS Bot. Я могу показать список лабораторных, оценки, pass rates и другую статистику. Спросите меня о чём-нибудь!"

        if any(word in msg_lower for word in ["help", "помощь", "команд"]):
            return "📚 Я понимаю такие запросы:\n- 'какие лабы есть?'\n- 'покажи оценки для lab-04'\n- 'какая лаба самая сложная?'\n- 'кто лучшие студенты?'"

        if any(word in msg_lower for word in ["lab", "лабор", "лабы"]):
            return "📋 Я могу показать список лабораторных работ. Используйте команду /labs или спросите 'какие лабы есть?'"

        if any(word in msg_lower for word in ["score", "оценк", "балл"]):
            return "📊 Я могу показать оценки для конкретной лабы. Используйте /scores <lab_id> или спросите 'покажи оценки для lab-04'"

        return "❓ Я не совсем понял ваш запрос. Попробуйте спросить о лабораторных работах, оценках или статистике. Или используйте /help для списка команд."
