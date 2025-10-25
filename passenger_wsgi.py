#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Passenger WSGI Entry Point for Namecheap Shared Hosting
FastAPI Application Deployment
"""

import sys
import os

# Virtual environment path
INTERP = os.path.join(os.environ['HOME'], 'public_html', 'venv', 'bin', 'python3')
if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

# Set environment to production
os.environ.setdefault('ENVIRONMENT', 'production')

# Import FastAPI app from simple_fastapi.py
try:
    from simple_fastapi import app as application
    
    # Log startup
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/passenger_startup.log'),
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger(__name__)
    logger.info("🚀 FastAPI application started successfully via Passenger")
    logger.info(f"📁 Working directory: {os.getcwd()}")
    logger.info(f"🐍 Python executable: {sys.executable}")
    logger.info(f"📦 Python path: {sys.path[:3]}")
    
except ImportError as e:
    # Fallback error handling
    import logging
    logging.basicConfig(level=logging.ERROR)
    logger = logging.getLogger(__name__)
    logger.error(f"❌ Failed to import FastAPI application: {e}")
    logger.error(f"📁 Current directory: {os.getcwd()}")
    logger.error(f"📦 Python path: {sys.path}")
    raise

except Exception as e:
    # General error handling
    import logging
    logging.basicConfig(level=logging.ERROR)
    logger = logging.getLogger(__name__)
    logger.error(f"❌ Failed to start application: {e}")
    raise

# Passenger expects 'application' variable (WSGI-compatible)
# FastAPI's app object is already ASGI-compatible, but Passenger uses WSGI
# We need an ASGI-to-WSGI adapter

try:
    from asgiref.wsgi import WsgiToAsgi
    application = WsgiToAsgi(application)
    logger.info("✅ ASGI-to-WSGI adapter applied successfully")
except ImportError:
    logger.warning("⚠️ asgiref not found - using direct ASGI (may not work with Passenger)")
    pass
