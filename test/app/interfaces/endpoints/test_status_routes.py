#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026-05-08 15:32
@Author  : fred.feng0326@gmail.com
@File    : test_status_routes.py
"""
from fastapi.testclient import TestClient


def test_get_status(client: TestClient) -> None:
    """Test the API endpoint for retrieving application status."""
    # 1. Request data using the test client
    response = client.get("/api/status")
    data = response.json()

    # 2. Assert the HTTP status code and business status code
    assert response.status_code == 200
    assert data.get("code") == 200
