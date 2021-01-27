"""Configure logging."""

from __future__ import annotations
from typing import Any
import logging
import uvicorn


DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'


def configure_root_logging(log_path: str):
  """Set up root logger to send logs to file and console."""
  logger = logging.getLogger()
  logger.setLevel(logging.INFO)
  formatter = logging.Formatter(
      fmt=LOG_FORMAT,
      datefmt=DATE_FORMAT
  )
  file_handler = logging.FileHandler(log_path)
  file_handler.setFormatter(formatter)
  logger.addHandler(file_handler)
  console_handler = logging.StreamHandler()
  console_handler.setFormatter(formatter)
  logger.addHandler(console_handler)


def get_uvicorn_logger(log_path: str):
  """Configure uvicorn default logger to save to file."""

  lc: dict[str, Any] = uvicorn.config.LOGGING_CONFIG

  # changing default formatting
  lc['formatters']['access']['fmt'] = LOG_FORMAT
  lc['formatters']['access']['datefmt'] = DATE_FORMAT
  lc['formatters']['default']['fmt'] = LOG_FORMAT
  lc['formatters']['default']['datefmt'] = DATE_FORMAT

  # adding FileHandler to LOGGING_CONFIG
  lc['handlers']['default_file'] = {
      'formatter': 'default',
      'class': 'logging.FileHandler',
      'filename': log_path}
  lc['handlers']['access_file'] = {
      'formatter': 'access',
      'class': 'logging.FileHandler',
      'filename': log_path}

  # telling loggers to use the additional handler
  lc['loggers']['uvicorn']['handlers'].append('default_file')
  lc['loggers']['uvicorn.access']['handlers'].append('access_file')
  return lc
