#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026-05-11 12:46
@Author  : fred.feng0326@gmail.com
@File    : health_status.py
"""
from pydantic import BaseModel, Field


class HealthStatus(BaseModel):
    """Health check status for a service."""
    service: str = Field(default="", description="Name of the service being checked")
    status: str = Field(
        default="",
        description="Health status: ok for healthy, error for failure",
    )
    details: str = Field(default="", description="Additional detail when status is error")
