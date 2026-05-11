#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026-05-10 13:57
@Author  : fred.feng0326@gmail.com
@File    : app_config.py
"""
import uuid
from enum import Enum
from typing import Dict, Optional, List, Any

from pydantic import BaseModel, HttpUrl, Field, ConfigDict, model_validator


class LLMConfig(BaseModel):
    """LLM provider configuration."""
    base_url: HttpUrl = "https://api.deepseek.com"  # Base URL for the model API
    api_key: str = ""  # Model API key
    model_name: str = "deepseek-reasoner"  # Model name; default deepseek-reasoner (reasoning); passing tools switches to deepseek-chat
    temperature: float = Field(0.7)  # Sampling temperature; default 0.7
    max_tokens: int = Field(8192, ge=0)  # Max output tokens; default matches deepseek-chat limit


class AgentConfig(BaseModel):
    """General agent configuration."""
    max_iterations: int = Field(default=100, gt=0, lt=1000)  # Maximum agent iterations
    max_retries: int = Field(default=3, gt=1, lt=10)  # Maximum retry attempts
    max_search_results: int = Field(default=10, gt=1, lt=30)  # Maximum number of search results


class MCPTransport(str, Enum):
    """MCP transport type enumeration."""
    STDIO = "stdio"  # Standard local I/O
    SSE = "sse"  # Server-sent events
    STREAMABLE_HTTP = "streamable_http"  # Streamable HTTP


class MCPServerConfig(BaseModel):
    """MCP server configuration."""
    # Common fields
    transport: MCPTransport = MCPTransport.STREAMABLE_HTTP  # Transport protocol
    enabled: bool = True  # Whether the server is enabled; default True
    description: Optional[str] = None  # Server description
    env: Optional[Dict[str, Any]] = None  # Environment variables

    # STDIO configuration
    command: Optional[str] = None  # Executable command
    args: Optional[List[str]] = None  # Command arguments

    # streamable_http and SSE configuration
    url: Optional[str] = None  # MCP service URL
    headers: Optional[Dict[str, Any]] = None  # HTTP headers for MCP requests

    model_config = ConfigDict(extra="allow")

    @model_validator(mode="after")
    def validate_mcp_server_config(self):
        """Validate MCPServerConfig fields (url for SSE/streamable_http, command for stdio)."""
        # 1. Check whether transport is SSE or streamable_http
        if self.transport in [MCPTransport.SSE, MCPTransport.STREAMABLE_HTTP]:
            # 2. These modes require a URL
            if not self.url:
                raise ValueError("url is required when transport is sse or streamable_http")

        # 3. Check whether transport is STDIO
        if self.transport == MCPTransport.STDIO:
            # 4. STDIO mode requires command
            if not self.command:
                raise ValueError("command is required when transport is stdio")

        return self


class MCPConfig(BaseModel):
    """Application MCP configuration."""
    mcpServers: Dict[str, MCPServerConfig] = Field(default_factory=dict)

    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)


class A2AServerConfig(BaseModel):
    """A2A server configuration."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))  # Unique identifier
    base_url: str  # Service base URL
    enabled: bool = True  # Whether the server is enabled


class A2AConfig(BaseModel):
    """A2A configuration."""
    a2a_servers: List[A2AServerConfig] = Field(default_factory=list)


class AppConfig(BaseModel):
    """Application settings: agent, LLM provider, MCP, and A2A configuration."""
    llm_config: LLMConfig  # Language model configuration
    agent_config: AgentConfig  # General agent configuration
    mcp_config: MCPConfig  # MCP server configuration
    a2a_config: A2AConfig  # A2A server configuration

    # Pydantic: allow extra fields during initialization
    model_config = ConfigDict(extra="allow")
