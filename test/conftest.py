#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026-05-08 15:24
@Author  : fred.feng0326@gmail.com
@File    : conftest.py
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="session")
def client() -> TestClient:
    """
    Create a TestClient instance that can be shared by all test cases.
    scope="session" means this fixture is instantiated only once for the entire test run, which improves efficiency.
    :return: TestClient
    """
    with TestClient(app) as c:
        yield c
