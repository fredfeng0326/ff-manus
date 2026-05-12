#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026-05-12 10:37
@Author  : fred.feng0326@gmail.com
@File    : base.py
"""
import inspect
from typing import Dict, Any, List, Callable

from app.domain.models.tool_result import ToolResult

"""
ff Manus tool design:
1. Concrete tools inherit BaseTool and expose a single invoke entry for methods on that tool set.
2. The @tool decorator binds name, description, and parameter schema onto _tool_name, _tool_description, _tool_schema.
3. Subclasses call get_tools to obtain a cached list of tool declarations for LLM binding and invocation.
4. Model output may hallucinate or include extra fields; before invocation, kwargs are filtered to the target method signature.
"""


def tool(
        name: str,
        description: str,
        parameters: Dict[str, Dict[str, Any]],
        required: List[str],
) -> Callable:
    """OpenAI-style function-tool decorator; attaches tool metadata and declaration to the wrapped method."""

    def decorator(func):
        """Write name, description, parameter fields, and required list onto the wrapped function."""
        # 1. Build tool declaration (keys must match OpenAI tool schema; do not localize)
        tool_schema = {
            "type": "function",
            "function": {
                "name": name,
                "description": description,
                "parameters": {
                    "type": "object",
                    "properties": parameters,
                    "required": required,
                }
            }
        }

        # 2. Attach metadata to the wrapped function
        func._tool_name = name
        func._tool_description = description
        func._tool_schema = tool_schema

        return func

    return decorator


class BaseTool:
    """Base class grouping tool methods callable by an LLM."""
    name: str = ""  # Name of this tool group / toolkit

    def __init__(self) -> None:
        """Initialize with an empty tool-declaration cache."""
        self._tools_cache = None

    @classmethod
    def _filter_parameters(cls, method: Callable, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Keep only kwargs whose keys exist on the target method signature (drop hallucinated keys)."""
        # 1. Accumulate filtered kwargs
        filtered_kwargs = {}
        sign = inspect.signature(method)

        # 2. Iterate incoming keyword arguments
        for key, value in kwargs.items():
            if key in sign.parameters:
                filtered_kwargs[key] = value

        return filtered_kwargs

    def get_tools(self) -> List[Dict[str, Any]]:
        """Return all registered tool schemas (cached) for LLM tool binding."""
        # 1. Return cache if already built
        if self._tools_cache is not None:
            return self._tools_cache

        # 2. Collect schemas from bound methods
        tools = []

        # 3. Scan instance methods for @tool metadata
        for _, method in inspect.getmembers(self, inspect.ismethod):
            if hasattr(method, "_tool_schema"):
                tools.append(getattr(method, "_tool_schema"))

        # 4. Store cache and return
        self._tools_cache = tools
        return tools

    def has_tool(self, tool_name: str) -> bool:
        """Return True if a method with the given tool name exists on this tool set."""
        for _, method in inspect.getmembers(self, inspect.ismethod):
            if hasattr(method, "_tool_name") and getattr(method, "_tool_name") == tool_name:
                return True
        return False

    async def invoke(self, tool_name: str, **kwargs) -> ToolResult:
        """Invoke the tool named tool_name with filtered kwargs and return its ToolResult."""
        # 1. Find a method whose registered tool name matches
        for _, method in inspect.getmembers(self, inspect.ismethod):
            # 2. Match _tool_name
            if hasattr(method, "_tool_name") and getattr(method, "_tool_name") == tool_name:
                # 3. Filter kwargs to the method signature
                filtered_kwargs = self._filter_parameters(method, kwargs)

                # 4. Call and return
                return await method(**filtered_kwargs)

        # 5. No matching tool
        raise ValueError(f"Tool not found: [{tool_name}]")
