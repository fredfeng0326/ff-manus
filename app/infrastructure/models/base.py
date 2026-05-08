#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026-05-08 10:30
@Author  : fred.feng0326@gmail.com
@File    : base.py
"""
from sqlalchemy.orm import declarative_base

# define base ORM，all models from this
Base = declarative_base()
