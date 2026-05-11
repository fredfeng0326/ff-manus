#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026-05-11 12:33
@Author  : fred.feng0326@gmail.com
@File    : openai_llm.py
"""
import logging
from typing import List, Dict, Any

from openai import AsyncOpenAI

from app.application.errors.exceptions import ServerRequestsError
from app.domain.external.llm import LLM
from app.domain.models.app_config import LLMConfig

logger = logging.getLogger(__name__)


class OpenAILLM(LLM):
    """LLM client using the OpenAI SDK (OpenAI-compatible API)."""

    def __init__(self, llm_config: LLMConfig, **kwargs) -> None:
        """Create the async OpenAI client and store model parameters."""
        # 1. Initialize async client
        self._client = AsyncOpenAI(
            base_url=str(llm_config.base_url),
            api_key=llm_config.api_key,
            **kwargs,
        )

        # 2. Store model settings
        self._model_name = llm_config.model_name
        self._temperature = llm_config.temperature
        self._max_tokens = llm_config.max_tokens
        self._timeout = 3600

    @property
    def model_name(self) -> str:
        return self._model_name

    @property
    def temperature(self) -> float:
        return self._temperature

    @property
    def max_tokens(self) -> int:
        return self._max_tokens

    async def invoke(
            self,
            messages: List[Dict[str, Any]],
            tools: List[Dict[str, Any]] = None,
            response_format: Dict[str, Any] = None,
            tool_choice: str = None,
    ) -> Dict[str, Any]:
        """Call the LLM via the async OpenAI client (non-streaming; can be switched to streaming later)."""
        try:
            # 1. Branch on whether tools are provided
            if tools:
                logger.info(f"Calling LLM with tools via OpenAI client, model={self._model_name}")
                response = await self._client.chat.completions.create(
                    model=self._model_name,
                    temperature=self._temperature,
                    max_tokens=self._max_tokens,
                    messages=messages,
                    response_format=response_format,
                    tools=tools,
                    tool_choice=tool_choice,
                    parallel_tool_calls=False,  # Disable parallel tool calls (not supported by DeepSeek)
                    timeout=self._timeout,
                )
            else:
                # 2. No tools: omit tools/tool_choice from the request
                logger.info(f"Calling LLM without tools via OpenAI client, model={self._model_name}")
                response = await self._client.chat.completions.create(
                    model=self._model_name,
                    temperature=self._temperature,
                    max_tokens=self._max_tokens,
                    messages=messages,
                    response_format=response_format,
                    timeout=self._timeout,
                )

            # 3. Normalize response and return assistant message payload
            logger.info(f"OpenAI client response: {response.model_dump()}")
            return response.choices[0].message.model_dump()
        except Exception as e:
            logger.error(f"OpenAI client error: {str(e)}")
            raise ServerRequestsError("Failed to call the LLM via the OpenAI client.")


if __name__ == "__main__":
    import asyncio


    async def main():
        llm = OpenAILLM(LLMConfig(
            base_url="https://api.deepseek.com",
            api_key="",
            model_name="deepseek-chat",
        ))
        response = await llm.invoke([{"role": "user", "content": "Hi"}])
        print(response)


    asyncio.run(main())
