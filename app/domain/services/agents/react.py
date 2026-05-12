#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026-05-12 14:24
@Author  : fred.feng0326@gmail.com
@File    : react.py
"""
import logging
from typing import AsyncGenerator

from app.domain.models.event import (
    StepEventStatus,
    StepEvent,
    ToolEvent,
    MessageEvent,
    ErrorEvent,
    ToolEventStatus,
    WaitEvent,
    BaseEvent
)
from app.domain.models.file import File
from app.domain.models.message import Message
from app.domain.models.plan import Plan, Step, ExecutionStatus
from app.domain.services.prompts.react import REACT_SYSTEM_PROMPT, EXECUTION_PROMPT, SUMMARIZE_PROMPT
from app.domain.services.prompts.system import SYSTEM_PROMPT
from .base import BaseAgent

logger = logging.getLogger(__name__)


class ReActAgent(BaseAgent):
    """Execution agent following a ReAct-style loop (reason + act)."""
    name: str = "react"
    _system_prompt: str = SYSTEM_PROMPT + REACT_SYSTEM_PROMPT
    # response_format controls structured content; tool_calls are independent
    _format: str = "json_object"

    async def execute_step(self, plan: Plan, step: Step, message: Message) -> AsyncGenerator[BaseEvent, None]:
        """Run a single plan step using the user message and plan context."""
        # 1. Build the execution prompt from message, attachments, language, and step description
        query = EXECUTION_PROMPT.format(
            message=message.message,
            attachments="\n".join(message.attachments),
            language=plan.language,
            step=step.description,
        )

        # 2. Mark step as running and emit started event
        step.status = ExecutionStatus.RUNNING
        yield StepEvent(step=step, status=StepEventStatus.STARTED)

        # 3. Stream events from BaseAgent.invoke
        async for event in self.invoke(query):
            # 4. Branch by event type
            if isinstance(event, ToolEvent):
                # 5. Handle user-facing ask tool specially
                if event.function_name == "message_ask_user":
                    # 6. CALLING: surface prompt text to the user as assistant message
                    if event.status == ToolEventStatus.CALLING:
                        yield MessageEvent(
                            role="assistant",
                            message=event.function_args.get("text", "")
                        )
                    elif event.status == ToolEventStatus.CALLED:
                        # 7. CALLED: pause flow and wait for user input
                        yield WaitEvent()
                        return
                    continue
            elif isinstance(event, MessageEvent):
                # 8. Final assistant message means this step produced structured output
                step.status = ExecutionStatus.COMPLETED

                # 9. Parse JSON payload into Step fields
                parsed_obj = await self._json_parser.invoke(event.message)
                new_step = Step.model_validate(parsed_obj)

                # 10. Merge parsed fields back onto the live step
                step.success = new_step.success
                step.result = new_step.result
                step.attachments = new_step.attachments

                # 11. Emit step completed
                yield StepEvent(step=step, status=StepEventStatus.COMPLETED)

                # 12. Optionally surface step.result as an assistant message to the user
                if step.result:
                    yield MessageEvent(role="assistant", message=step.result)
                continue
            elif isinstance(event, ErrorEvent):
                # 13. Map agent error to failed step
                step.status = ExecutionStatus.FAILED
                step.error = event.error

                # 14. Emit step failed
                yield StepEvent(step=step, status=StepEventStatus.FAILED)

            # 15. Forward any other event types unchanged
            yield event

        # 16. Invoke loop finished without early exit—ensure step marked completed
        step.status = ExecutionStatus.COMPLETED

    async def summarize(self) -> AsyncGenerator[BaseEvent, None]:
        """Produce a final summary message and attachments from conversation history."""
        # 1. Build summarize prompt
        query = SUMMARIZE_PROMPT

        # 2. Stream invoke events
        async for event in self.invoke(query):
            # 3. Structured summary arrives as MessageEvent with JSON body
            if isinstance(event, MessageEvent):
                # 4. Log and parse into Message
                logger.info(f"ReActAgent summary output: {event.message}")
                parsed_obj = await self._json_parser.invoke(event.message)

                # 5. Validate as Message
                message = Message.model_validate(parsed_obj)

                # 6. Wrap attachment paths as File models
                attachments = [File(filepath=filepath) for filepath in message.attachments]

                # 7. Emit assistant message with attachments
                yield MessageEvent(
                    role="assistant",
                    message=message.message,
                    attachments=attachments,
                )
            else:
                # 8. Pass through other events
                yield event
