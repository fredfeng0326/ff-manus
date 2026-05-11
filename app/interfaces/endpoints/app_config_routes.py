#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026-05-10 13:51
@Author  : fred.feng0326@gmail.com
@File    : app_config_routes.py
"""
import logging

from fastapi import APIRouter, Depends

from app.application.services.app_config_service import AppConfigService
from app.domain.models.app_config import LLMConfig
from app.interfaces.schemas.base import Response
from app.interfaces.service_dependencies import get_app_config_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/app-config", tags=["App configuration"])


@router.get(
    path="/llm",
    response_model=Response[LLMConfig],
    summary="Get LLM configuration",
    description="Returns LLM provider settings: base_url, temperature, model_name, and max_tokens (api_key is omitted).",
)
async def get_llm_config(
        app_config_service: AppConfigService = Depends(get_app_config_service)
) -> Response[LLMConfig]:
    """Get LLM configuration."""
    llm_config = await app_config_service.get_llm_config()
    return Response.success(data=llm_config.model_dump(exclude={"api_key"}))


@router.post(
    path="/llm",
    response_model=Response[LLMConfig],
    summary="Update LLM configuration",
    description="Updates LLM settings; when api_key is empty or whitespace, the existing key is kept.",
)
async def update_llm_config(
        new_llm_config: LLMConfig,
        app_config_service: AppConfigService = Depends(get_app_config_service)
) -> Response[LLMConfig]:
    """Update LLM configuration."""
    updated_llm_config = await app_config_service.update_llm_config(new_llm_config)
    return Response.success(
        msg="LLM configuration updated successfully.",
        data=updated_llm_config.model_dump(exclude={"api_key"})
    )
