#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026-05-06 14:44
@Author  : fred.feng0326@gmail.com
@File    : status_routes.py
"""
import logging

from fastapi import APIRouter

from app.interfaces.schemas import Response

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/status", tags=["status"])


@router.get(
    path="",
    response_model=Response,
    summary="app health check",
    description="Check app postgres, redis, fastapi and other modules status",
)
async def get_status() -> Response:
    """Check app postgres, redis, fastapi and other modules status"""
    # TODO: waiting postgres/redis
    return Response.success()
