#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026-05-06 14:52
@Author  : fred.feng0326@gmail.com
@File    : routes.py
"""
from fastapi import APIRouter

from . import status_routes


def create_api_routes() -> APIRouter:
    """create API router, manage all api endpoint"""
    # create API router object
    api_router = APIRouter()

    # add all modules router to api_router
    api_router.include_router(status_routes.router)

    # return api router object
    return api_router


router = create_api_routes()
