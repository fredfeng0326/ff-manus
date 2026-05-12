#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026-05-08 10:19
@Author  : fred.feng0326@gmail.com
@File    : event.py
"""
import uuid
from datetime import datetime
from enum import Enum
from typing import Literal, List, Union, Optional, Any, Dict, Annotated

from pydantic import BaseModel, Field

from .file import File
from .plan import Plan, Step
from .search import SearchResultItem
from .tool_result import ToolResult


class PlanEventStatus(str, Enum):
    """Status of a plan-related event."""
    CREATED = "created"  # Created
    UPDATED = "updated"  # Updated
    COMPLETED = "completed"  # Completed


class StepEventStatus(str, Enum):
    """Status of a step-related event."""
    STARTED = "started"  # Started
    COMPLETED = "completed"  # Completed
    FAILED = "failed"  # Failed


class ToolEventStatus(str, Enum):
    """Status of a tool-related event."""
    CALLING = "calling"  # In progress
    CALLED = "called"  # Finished


class BaseEvent(BaseModel):
    """Base fields shared by all event types."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))  # Event id
    type: Literal[""] = ""  # Event discriminator type
    created_at: datetime = Field(default_factory=datetime.now)  # Creation timestamp


class PlanEvent(BaseEvent):
    """Event carrying an updated plan."""
    type: Literal["plan"] = "plan"
    plan: Plan  # Plan payload
    status: PlanEventStatus = PlanEventStatus.CREATED  # Plan event status


class TitleEvent(BaseEvent):
    """Event carrying a session or task title."""
    type: Literal["title"] = "title"
    title: str = ""  # Title text


class StepEvent(BaseEvent):
    """Event for a single plan step / subtask."""
    type: Literal["step"] = "step"
    step: Step  # Step payload
    status: StepEventStatus = StepEventStatus.STARTED


class MessageEvent(BaseEvent):
    """Event for a user or assistant chat message."""
    type: Literal["message"] = "message"
    role: Literal["user", "assistant"] = "assistant"  # Message role
    message: str = ""  # Message body
    attachments: List[File] = Field(default_factory=list)  # Attachments


class BrowserToolContent(BaseModel):
    """Extra payload for browser-related tools."""
    screenshot: str  # Screenshot (e.g. base64 or URL)


class SearchToolContent(BaseModel):
    """Extra payload for search tools."""
    results: List[SearchResultItem]  # Search hits


class ShellToolContent(BaseModel):
    """Extra payload for shell tools."""
    console: Any  # Console output


class FileToolContent(BaseModel):
    """Extra payload for file tools."""
    content: str  # File content


class MCPToolContent(BaseModel):
    """Extra payload for MCP tools."""
    result: Any  # MCP tool result


class A2AToolContent(BaseModel):
    """Extra payload for A2A agent tools."""
    a2a_result: Any  # A2A invocation result


ToolContent = Union[
    BrowserToolContent,
    SearchToolContent,
    ShellToolContent,
    FileToolContent,
    MCPToolContent,
    A2AToolContent,
]


class ToolEvent(BaseEvent):
    """Event for an LLM tool / function call and its result."""
    type: Literal["tool"] = "tool"
    tool_call_id: str  # Tool call correlation id
    tool_name: str  # Tool group or provider name
    tool_content: Optional[ToolContent] = None  # Structured tool output
    function_name: str  # Function / tool name from the LLM
    function_args: Dict[str, Any]  # Arguments from the LLM
    function_result: Optional[ToolResult] = None  # Execution result wrapper
    status: ToolEventStatus = ToolEventStatus.CALLING  # Tool event status


class WaitEvent(BaseEvent):
    """Event indicating the flow is waiting for user input or confirmation."""
    type: Literal["wait"] = "wait"


class ErrorEvent(BaseEvent):
    """Event carrying an error message."""
    type: Literal["error"] = "error"
    error: str = ""  # Error description


class DoneEvent(BaseEvent):
    """Event marking normal completion of the session or turn."""
    type: Literal["done"] = "done"


# Application event union with discriminator on `type`
Event = Annotated[
    Union[
        PlanEvent,
        TitleEvent,
        StepEvent,
        MessageEvent,
        ToolEvent,
        WaitEvent,
        ErrorEvent,
        DoneEvent,
    ],
    Field(discriminator="type"),
]
