#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026-05-11 18:19
@Author  : fred.feng0326@gmail.com
@File    : search.py
"""
from typing import Optional, List

from pydantic import BaseModel, Field


class SearchResultItem(BaseModel):
    """A single search result row."""
    url: str  # Result URL
    title: str  # Result title
    snippet: str = ""  # Short snippet or summary


class SearchResults(BaseModel):
    """Aggregated search response."""
    query: str  # User query
    date_range: Optional[str] = None  # Optional date filter string
    total_results: int = 0  # Total hit count
    results: List[SearchResultItem] = Field(default_factory=list)  # Result rows
