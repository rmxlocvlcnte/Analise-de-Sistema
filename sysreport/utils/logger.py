import logging
import sys
from pathlib import Path
from datetime import datetime

_logger: logging.Logger | None = None

def logger_setup(log_dir: Path, timestamp: str) -> logging.Logger:
    global _logger

    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f"report_{timestamp}.txt"

    formatter = logging.Formatter(
        fmt="[%(asctime)s] %(levelname)s — %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    logger = logging.getLogger("sysreport")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    _logger = logger
    return logger

def get_logger() -> logging.Logger:
    if _logger is None:
        raise RuntimeError("Logger não identificado. Chame logger_setup() primeiro")
    return _logger