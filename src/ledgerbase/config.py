#!/usr/bin/env python
"""---
# Front-Matter for Python Module

title: "Configuration Module"
name: "config.py"
description: "Defines application configuration classes and selection logic."
category: module
usage: "Imported by application to obtain environment-specific configs."
behavior: "Provides Config subclasses and helper functions for security settings."
inputs: "FLASK_ENV, DATABASE_URL, SECRET_KEY"
outputs: "Config class types and settings dict"
dependencies: none
author: "Byron Williams"
last_modified: "2025-04-26"
changelog: "Embedded front-matter, updated type annotations, improved docstrings"
tags: [config, settings]
---

Module: config

This module defines base and environment-specific configuration classes
for the LedgerBase application. It includes:
  - Config: Base settings loaded from environment variables.
  - DevelopmentConfig: Debug settings for local development.
  - ProductionConfig: Secure settings for production usage.

Functions:
    get_security_settings() -> dict[str, Any]
    get_config(env: str | None = None) -> type[Config]
"""

import os
from typing import Any


class Config:
    """Base configuration with environment-backed settings."""

    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY", "unsafe-development-key")


class DevelopmentConfig(Config):
    """Development configuration (e.g., local debugging)."""

    DEBUG = True


class ProductionConfig(Config):
    """Production configuration with hardened settings."""

    DEBUG = False
    SESSION_COOKIE_SECURE = True
    PREFERRED_URL_SCHEME = "https"


def get_security_settings() -> dict[str, Any]:
    """Return default security settings for the application.

    These settings can be extended to read from secure storage.

    Returns:
        Dictionary with SESSION_COOKIE_SECURE and PREFERRED_URL_SCHEME.

    """
    return {
        "SESSION_COOKIE_SECURE": getattr(
            ProductionConfig,
            "SESSION_COOKIE_SECURE",
            False,
        ),
        "PREFERRED_URL_SCHEME": getattr(
            ProductionConfig,
            "PREFERRED_URL_SCHEME",
            "http",
        ),
    }


def get_config(env: str | None = None) -> type[Config]:
    """Select a Config subclass based on the given environment.

    Args:
        env: One of 'development', 'production', or None. If None, reads
             the FLASK_ENV environment variable (defaults to 'development').

    Returns:
        The Config subclass corresponding to the environment.

    """
    mapping: dict[str, type[Config]] = {
        "development": DevelopmentConfig,
        "production": ProductionConfig,
    }
    if env is None:
        env = os.getenv("FLASK_ENV", "development")
    return mapping.get(env.lower(), DevelopmentConfig)
