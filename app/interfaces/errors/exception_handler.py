#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026-05-06 15:12
@Author  : fred.feng0326@gmail.com
@File    : exception_handler.py.py
"""
import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

from app.application.errors.exceptions import AppException
from app.interfaces.schemas import Response

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    """Handle all exceptions in the ff Manus project with unified handling, covering: custom business exceptions,
    HTTP exceptions, and generic exceptions."""

    @app.exception_handler(AppException)
    async def app_exception_handler(req: Request, e: AppException) -> JSONResponse:
        """Handle ff Manus business exceptions and return them in a unified response structure."""
        logger.error(f"AppException: {e.msg}")
        return JSONResponse(
            status_code=e.status_code,
            content=Response(
                code=e.status_code,
                msg=e.msg,
                data={}
            ).model_dump(),
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(req: Request, e: HTTPException) -> JSONResponse:
        """Handle HTTP exceptions raised by FastAPI and return them in a unified response structure."""
        logger.error(f"HTTPException: {e.detail}")
        return JSONResponse(
            status_code=e.status_code,
            content=Response(
                code=e.status_code,
                msg=e.detail,
                data={}
            ).model_dump(),
        )

    @app.exception_handler(Exception)
    async def exception_handler(req: Request, e: Exception) -> JSONResponse:
        """Handle any undefined exception in MoocManus by returning HTTP 500 with a unified response structure."""
        logger.error(f"Exception: {str(e)}")
        return JSONResponse(
            status_code=500,
            content=Response(
                code=500,
                msg="Server encountered an error. Please try again later.",
                data={},
            ).model_dump()
        )
