#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026-05-11 17:03
@Author  : fred.feng0326@gmail.com
@File    : plan.py
"""
import uuid
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class ExecutionStatus(str, Enum):
    """Execution status for plans/tasks."""
    PENDING = "pending"  # Idle or waiting
    RUNNING = "running"  # In progress
    COMPLETED = "completed"  # Finished successfully
    FAILED = "failed"  # Failed


class Step(BaseModel):
    """A single step/subtask in a plan."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))  # Subtask ID
    description: str = ""  # Step description
    status: ExecutionStatus = ExecutionStatus.PENDING  # Execution status of this subtask
    result: Optional[str] = None  # Execution result
    error: Optional[str] = None  # Error message
    success: bool = False  # Whether execution succeeded
    attachments: List[str] = Field(default_factory=list)  # List of attachment references

    @property
    def done(self) -> bool:
        """Read-only property indicating whether the step is finished."""
        return self.status in [ExecutionStatus.COMPLETED, ExecutionStatus.FAILED]


class Plan(BaseModel):
    """Plan domain model storing subtasks/steps derived from a user request."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))  # Plan ID
    title: str = ""  # Task title
    goal: str = ""  # Task goal
    language: str = ""  # Working language
    steps: List[Step] = Field(default_factory=list)  # List of steps/subtasks
    message: str = ""  # AI-generated message
    status: ExecutionStatus = ExecutionStatus.PENDING  # Plan execution status
    error: Optional[str] = None  # Error message

    @property
    def done(self) -> bool:
        """Read-only property indicating whether the plan is finished."""
        return self.status in [ExecutionStatus.COMPLETED, ExecutionStatus.FAILED]

    def get_next_step(self) -> Optional[Step]:
        """Get the next step that still needs execution."""
        return next((step for step in self.steps if not step.done), None)
