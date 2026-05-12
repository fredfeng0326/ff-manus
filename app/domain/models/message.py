#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026-05-12 11:33
@Author  : fred.feng0326@gmail.com
@File    : message.py
"""
from typing import List

from pydantic import BaseModel, Field


class Message(BaseModel):
    """the message from user"""
    message: str = ""  # message from user
    attachments: List[str] = Field(default_factory=list)  # attachments from user
