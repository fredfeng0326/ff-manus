#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026-05-12 10:28
@Author  : fred.feng0326@gmail.com
@File    : repair_json_parser.py
"""
import logging
from typing import Optional, Any, Union, Dict, List

import json_repair

from app.domain.external.json_parser import JSONParser

logger = logging.getLogger(__name__)


class RepairJSONParser(JSONParser):
    """JSON parser that repairs malformed JSON before parsing."""

    async def invoke(self, text: str, default_value: Optional[Any] = None) -> Union[Dict, List, Any]:
        """Parse text as JSON, using json-repair to fix common syntax issues."""
        # 1. Log and validate input text
        logger.info(f"Parsing JSON text: {text}")
        if not text or not text.strip():
            if default_value is not None:
                return default_value
            raise ValueError("JSON text is empty and no default_value was provided.")

        # 2. Repair and parse with json_repair
        return json_repair.repair_json(text, ensure_ascii=False, return_objects=True)
