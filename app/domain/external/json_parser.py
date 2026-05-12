#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026-05-12 10:25
@Author  : fred.feng0326@gmail.com
@File    : json_parser.py
"""
from typing import Protocol, Optional, Any, Union, Dict, List


class JSONParser(Protocol):
    """JSON Parser，used to parse and repair json file."""

    async def invoke(self, text: str, default_value: Optional[Any] = None) -> Union[Dict, List, Any]:
        """Call the function to parse the passed-in text and return it."""
        ...
