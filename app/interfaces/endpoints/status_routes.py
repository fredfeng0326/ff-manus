#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026-05-06 14:44
@Author  : fred.feng0326@gmail.com
@File    : status_routes.py
"""
import logging
from typing import List

from fastapi import APIRouter, Depends

from app.application.services.status_service import StatusService
from app.domain.models.health_status import HealthStatus
from app.interfaces.schemas import Response
from app.interfaces.service_dependencies import get_status_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/status", tags=["status"])


@router.get(
    path="",
    response_model=Response[List[HealthStatus]],
    summary="app health check",
    description="Check app postgres, redis, fastapi and other modules status",
)
async def get_status(status_service: StatusService = Depends(get_status_service)) -> Response:
    """Check app postgres, redis, fastapi and other modules status"""
    statues = await status_service.check_all()

    if any(item.status == "error" for item in statues):
        return Response.fail(503, "system have service error", statues)

    return Response.success(msg="system health check ok", data=statues)
