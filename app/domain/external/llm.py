#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026-05-11 12:28
@Author  : fred.feng0326@gmail.com
@File    : llm.py
"""
from typing import Protocol, List, Dict, Any


class LLM(Protocol):
    """Protocol for agents to interact with an LLM."""

    async def invoke(
            self,
            messages: List[Dict[str, Any]],
            tools: List[Dict[str, Any]] = None,
            response_format: Dict[str, Any] = None,
            tool_choice: str = None,
    ) -> Dict[str, Any]:
        """Call the LLM with messages, optional tools, response format, and tool-choice policy."""
        ...

    @property
    def model_name(self) -> str:
        """Read-only: current LLM model name."""
        ...

    @property
    def temperature(self) -> float:
        """Read-only: sampling temperature."""
        ...

    @property
    def max_tokens(self) -> int:
        """Read-only: maximum number of tokens to generate."""
        ...
