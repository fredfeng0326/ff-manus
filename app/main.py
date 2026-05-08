#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026-05-06 14:24
@Author  : fred.feng0326@gmail.com
@File    : main.py
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.infrastructure.logging import setup_logging
from app.infrastructure.storage.cos import get_cos
from app.infrastructure.storage.postgres import get_postgres
from app.infrastructure.storage.redis import get_redis
from app.interfaces.endpoints.routes import router
from app.interfaces.errors.exception_handler import register_exception_handlers
from core.config import get_settings

# 1. load config
settings = get_settings()

# 2. initialize the logging system
setup_logging()
logger = logging.getLogger(__name__)

# 3. define FastAPI router tags
openapi_tags = [
    {
        "name": "状态模块",
        "description": "包含 **状态监测** 等API 接口，用于监测系统的运行状态。"
    }
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """create FastAPI lifespan"""
    # 1. print logging start app
    logger.info("ff Manus starting")

    # 2. initialize redis,postgres,Cos client
    await get_redis().init()
    await get_postgres().init()
    await get_cos().init()

    # TODO

    try:
        yield
    finally:
        await get_redis().shutdown()
        await get_postgres().shutdown()
        await get_cos().shutdown()
        logger.info("ff Manus stopping")


app = FastAPI(
    title="ff Manus agent",
    description="ff Manus agent is a AI agent, can deploy local.",
    lifespan=lifespan,
    openapi_tags=openapi_tags,
    version="1.0.0",
)

# CORS middleware to solve CORS Issue
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# register exception handlers
register_exception_handlers(app)

app.include_router(router, prefix="/api")
