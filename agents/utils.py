"""Agent utilities"""

import json

from configs.logging_config import get_logger
from tools.base import Tool

logger = get_logger(__name__)


def parse_function_args(response):
    message = response.choices[0].message
    if not message.tool_calls:
        return {}
    return json.loads(message.tool_calls[0].function.arguments)


def get_tool_from_response(response, tools: list[Tool]):
    tool_name = response.choices[0].message.tool_calls[0].function.name
    for t in tools:
        if t.name == tool_name:
            return t
    raise ValueError(f"Tool {tool_name} not found in tools list.")


def run_tool_from_response(response, tools: list[Tool]):
    tool = get_tool_from_response(response, tools)
    tool_kwargs = parse_function_args(response)
    return tool.run(**tool_kwargs)
