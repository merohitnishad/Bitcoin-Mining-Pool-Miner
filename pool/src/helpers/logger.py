import logging
from typing import Optional


def setup_logger(
    name: Optional[str] = None, log_level: int = logging.INFO
) -> logging.Logger:
    """
    Set up a logger with consistent format and aligned output.

    Args:
        name: Logger name (optional). If None, returns root logger
        log_level: Logging level (default: logging.INFO)

    Returns:
        logging.Logger: Configured logger instance
    """
    # Get logger instance
    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    # Remove existing handlers to avoid duplicate logging
    if logger.handlers:
        logger.handlers.clear()

    # Create console handler
    handler = logging.StreamHandler()
    handler.setLevel(log_level)

    # Create formatter with fixed-width fields
    # %(filename)-20s: Left-aligned filename with 20 char width
    # %(lineno)4d: Right-aligned line number with 4 char width
    # %(levelname)-8s: Left-aligned level name with 8 char width
    formatter = logging.Formatter(
        "%(asctime)s - %(filename)-20s - %(lineno)4d - %(levelname)-8s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


# Create a logger instance
logger = setup_logger()
