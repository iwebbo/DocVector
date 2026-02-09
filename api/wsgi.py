# api/wsgi.py
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent))

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from app import app, init_clients

# Initialize
if not init_clients():
    logger.error("Failed to initialize clients")
    sys.exit(1)

logger.info("Application initialized successfully")

# WSGI application
application = app

if __name__ == "__main__":
    app.run()