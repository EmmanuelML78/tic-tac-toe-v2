"""
Logging system for the application
"""
import logging
import os
from datetime import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ServerLog


def setup_logging(log_file: str = "logs/server.log", log_level: str = "INFO"):
    """
    Setup logging configuration

    Args:
        log_file: Path to log file
        log_level: Logging level
    """
    # Create logs directory if it doesn't exist
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

    logger = logging.getLogger(__name__)
    logger.info(f"Logging initialized - Level: {log_level}, File: {log_file}")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance

    Args:
        name: Logger name

    Returns:
        Logger instance
    """
    return logging.getLogger(name)


async def log_event(
    level: str,
    event_type: str,
    message: str,
    db: AsyncSession,
    user_id: Optional[int] = None,
    game_id: Optional[int] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None
):
    """
    Log an event to database

    Args:
        level: Log level ('INFO', 'WARNING', 'ERROR', 'CRITICAL')
        event_type: Type of event
        message: Log message
        db: Database session
        user_id: Optional user ID
        game_id: Optional game ID
        ip_address: Optional IP address
        user_agent: Optional user agent
    """
    try:
        log = ServerLog(
            level=level.upper(),
            event_type=event_type,
            user_id=user_id,
            game_id=game_id,
            message=message,
            ip_address=ip_address,
            user_agent=user_agent
        )

        db.add(log)
        await db.commit()

        # Also log to file
        logger = get_logger("server_events")
        log_method = getattr(logger, level.lower(), logger.info)
        log_method(f"[{event_type}] {message}")

    except Exception as e:
        logger = get_logger("logger")
        logger.error(f"Failed to log event: {str(e)}")
