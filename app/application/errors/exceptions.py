#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026-05-06 15:15
@Author  : fred.feng0326@gmail.com
@File    : exceptions.py
"""

from typing import Any


class AppException(RuntimeError):
    """Base application exception class, inheriting from RuntimeError."""

    def __init__(
            self,
            code: int = 400,  # Custom business error code
            status_code: int = 400,
            msg: str = "An application error occurred. Please try again later.",
            data: Any = None,
    ):
        """Constructor that initializes error data."""
        self.code = code
        self.status_code = status_code
        self.msg = msg
        self.data = data
        super().__init__()


class BadRequestError(AppException):
    """Client request error."""

    def __init__(self, msg: str = "Bad client request. Please check and try again."):
        super().__init__(status_code=400, code=400, msg=msg)


class NotFoundError(AppException):
    """Resource not found error."""

    def __init__(self, msg: str = "Resource not found. Please verify and try again."):
        super().__init__(status_code=404, code=404, msg=msg)


class ValidationError(AppException):
    """Data validation error."""

    def __init__(self, msg: str = "Request parameter validation failed. Please verify and try again."):
        super().__init__(status_code=422, code=422, msg=msg)


class TooManusRequestsError(AppException):
    """Too many requests error (rate limit triggered)."""

    def __init__(self, msg: str = "Too many requests. Rate limit triggered. Please try again later."):
        super().__init__(status_code=429, code=429, msg=msg)


class ServerRequestsError(AppException):
    """Server error."""

    def __init__(self, msg: str = "The server encountered an error. Please try again later."):
        super().__init__(status_code=500, code=500, msg=msg)
