#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026-05-12 14:20
@Author  : fred.feng0326@gmail.com
@File    : planer.py
"""
import logging
from typing import Optional, AsyncGenerator

from app.domain.models.event import BaseEvent, MessageEvent, PlanEvent, PlanEventStatus
from app.domain.models.message import Message
from app.domain.models.plan import Plan, Step
from app.domain.services.prompts.planner import (
    PLANNER_SYSTEM_PROMPT,
    CREATE_PLAN_PROMPT,
    UPDATE_PLAN_PROMPT,
)
from app.domain.services.prompts.system import SYSTEM_PROMPT
from .base import BaseAgent

"""
Multi-agent flow (conceptual): PlannerAgent + ReActAgent

Typical order:
1. PlannerAgent produces an initial plan from the user request.
2. Loop: take the next plan step and let ReActAgent execute it.
3. After each step, pass step results + Plan back to PlannerAgent to refresh the plan.
4. Repeat until all steps are done.
5. Optionally aggregate step outputs for a final summary (often ReActAgent).

PlannerAgent:
- Role: decompose the user goal into subtasks; revise the plan as steps complete.
- Prompts: create-plan and update-plan templates.

ReActAgent:
- Role: execute each subtask and optionally summarize when everything is finished.
- Prompts: execution and summary templates (defined elsewhere).
"""

logger = logging.getLogger(__name__)


class PlannerAgent(BaseAgent):
    """Agent that turns a user request into a structured Plan with steps."""
    name: str = "planner"
    _system_prompt: str = SYSTEM_PROMPT + PLANNER_SYSTEM_PROMPT
    _format: Optional[str] = "json_object"
    _tool_choice: Optional[str] = "none"

    async def create_plan(self, message: Message) -> AsyncGenerator[BaseEvent, None]:
        """Build a plan from the user message and stream events (PlanEvent on success)."""
        # 1. Build the create-plan prompt from the user message and attachments
        query = CREATE_PLAN_PROMPT.format(
            message=message.message,
            attachments="\n".join(message.attachments),
        )

        # 2. Delegate to BaseAgent.invoke and forward/transform events
        async for event in self.invoke(query):
            # 3. With json_object format we expect a MessageEvent carrying JSON
            if isinstance(event, MessageEvent):
                # 4. Log and parse JSON into a Plan object
                logger.info(f"PlannerAgent produced message: {event.message}")
                parsed_obj = await self._json_parser.invoke(event.message)

                # 5. Validate as Plan
                plan = Plan.model_validate(parsed_obj)

                # 6. Emit plan-created event
                yield PlanEvent(plan=plan, status=PlanEventStatus.CREATED)
            else:
                # Forward any non-message event unchanged
                yield event

    async def update_plan(self, plan: Plan, step: Step) -> AsyncGenerator[BaseEvent, None]:
        """Refresh the plan after a step completes, merging model output with existing steps."""
        # 1. Build update prompt from current plan and completed step
        query = UPDATE_PLAN_PROMPT.format(
            plan=plan.model_dump_json(),
            step=step.model_dump_json(),
        )

        # 2. Run invoke and handle events
        async for event in self.invoke(query):
            # 3. Same pattern: MessageEvent holds JSON plan payload
            if isinstance(event, MessageEvent):
                # 4. Log and parse
                logger.info(f"PlannerAgent produced message: {event.message}")
                parsed_obj = await self._json_parser.invoke(event.message)

                # 5. Validate updated plan from the model
                updated_plan = Plan.model_validate(parsed_obj)

                # 6. Rebuild steps list from parsed output to avoid accidental shared mutation
                new_steps = [Step.model_validate(step) for step in updated_plan.steps]

                # 7. Find first step that is still pending in the original plan
                first_pending_index = None
                for idx, step in enumerate(plan.steps):
                    if not step.done:
                        first_pending_index = idx
                        break

                # 8. If there is a pending tail, splice completed prefix with new steps from the model
                if first_pending_index is not None:
                    # 9. Keep completed steps, append updated step
                    updated_steps = plan.steps[:first_pending_index]
                    updated_steps.extend(new_steps)

                    # 10. Mutate plan in place for downstream consumers
                    plan.steps = updated_steps

                # 11. Emit plan-updated event
                yield PlanEvent(plan=plan, status=PlanEventStatus.UPDATED)
            else:
                # Pass through other event types
                yield event
