"""File contains logging configuration"""

# NOTE: Moss of this file was made by AI, i cant bother with it.

import logging
import logging.handlers
import os
import sys
import asyncio
import contextvars
from pythonjsonlogger import jsonlogger  # Import python-json-logger

# --- Configuration Constants ---
LOG_LEVEL_STR = os.environ.get("LOG_LEVEL", "INFO").upper()
LOG_LEVEL_MAP = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}
LOG_LEVEL = LOG_LEVEL_MAP.get(LOG_LEVEL_STR, logging.INFO)

LOG_FILE_BACKUP_COUNT = 5
LOG_FILE_MAX_BYTES = 1024 * 1024 * 10  # 10 MB
LOG_FILE_PATH = ".log"
LOG_FORMAT_BASE = (
    "[%(requestId)s] - %(name)s:%(lineno)d - %(message)s"  # For local text
)
LOG_FORMAT_DATE = "%Y-%m-%d %H:%M:%S"  # For local text
LOG_LEVEL_WIDTH = 9

# --- ANSI Color Codes (for local only) ---
RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[1;%dm"
COLORS = {
    "DEBUG": COLOR_SEQ % 34,
    "INFO": COLOR_SEQ % 32,
    "WARNING": COLOR_SEQ % 33,
    "ERROR": COLOR_SEQ % 31,
    "CRITICAL": COLOR_SEQ % 31,
}

# --- Context Variable for Request ID ---
request_id_var = contextvars.ContextVar("request_id", default="NotSet")


# --- Logging Filters ---
class RequestIdFilter(logging.Filter):
    def filter(self, record):
        record.requestId = request_id_var.get()
        return True


class TaskContextFilter(logging.Filter):
    def filter(self, record):
        try:
            task = asyncio.current_task()
            record.taskName = task.get_name() if task else "NoTask"
        except RuntimeError:
            record.taskName = "NoTaskContext"
        # Add default for fields that python-json-logger might expect if not present
        if not hasattr(record, "requestId"):
            record.requestId = "NotSet"
        return True


# --- Custom Formatters ---
class AlignedColoredFormatter(logging.Formatter):  # Same as before
    def __init__(
        self,
        fmt=LOG_FORMAT_BASE,
        datefmt=LOG_FORMAT_DATE,
        use_color=True,
        level_width=LOG_LEVEL_WIDTH,
    ):
        super().__init__(fmt=fmt, datefmt=datefmt)
        self.use_color = use_color
        self.level_width = level_width
        self._base_formatter = logging.Formatter(fmt, datefmt)

    def format(self, record):
        message = self._base_formatter.format(record)
        timestamp = self.formatTime(record, self.datefmt)
        levelname = record.levelname
        level_prefix = f"{levelname}:"
        padded_prefix = f"{level_prefix:<{self.level_width}}"
        is_tty = hasattr(sys.stdout, "isatty") and sys.stdout.isatty()
        if self.use_color and levelname in COLORS and is_tty:
            colored_padded_prefix = f"{COLORS[levelname]}{padded_prefix}{RESET_SEQ}"
            return f"{timestamp} {colored_padded_prefix} {message}"
        else:
            return f"{timestamp} {padded_prefix} {message}"


class CustomJsonFormatter(jsonlogger.JsonFormatter): # type: ignore
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        # Rename fields for GCP compatibility
        if "levelname" in log_record:
            log_record["severity"] = log_record.pop("levelname")
        else:
            log_record["severity"] = record.levelname  # Default if not in log_record

        if (
            "asctime" in log_record
        ):  # python-json-logger can add asctime if in fmt string
            log_record["timestamp"] = log_record.pop("asctime")
        else:  # Or format it ourselves
            log_record["timestamp"] = self.formatTime(
                record, self.datefmt or logging.Formatter.default_time_format
            )

        # Add GCP source location
        log_record["logging.googleapis.com/source_location"] = {
            "file": record.pathname,
            "line": record.lineno,
            "function": record.funcName,
        }
        # Add custom fields if they exist on the record
        if hasattr(record, "requestId"):
            log_record["requestId"] = record.requestId # type: ignore
        if hasattr(record, "taskName"):
            log_record["taskName"] = record.taskName


# --- Logger Configuration Function ---
def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(LOG_LEVEL)

    if logger.hasHandlers():
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
            handler.close()

    request_filter = RequestIdFilter()
    task_filter = (
        TaskContextFilter()
    )  # Ensure this adds default requestId if not present

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(LOG_LEVEL)
    console_handler.addFilter(request_filter)
    console_handler.addFilter(task_filter)

    file_handler = None
    RUNNING_IN_CLOUD = os.environ.get("K_SERVICE") is not None

    if RUNNING_IN_CLOUD:
        print(
            "INFO: Running in Cloud Run: Configuring JSON logging (python-json-logger) to console.",
            file=sys.stderr,
        )
        # Define the format string for fields you want from the LogRecord
        # These will be keys in `log_record` dict passed to `add_fields`
        # The `message` field is handled specially by python-json-logger
        log_format = "%(asctime)s %(levelname)s %(name)s %(module)s %(funcName)s %(lineno)d %(message)s %(requestId)s %(taskName)s"
        formatter_console = CustomJsonFormatter(
            log_format, datefmt=LOG_FORMAT_DATE
        )  # Pass datefmt here too
        console_handler.setFormatter(formatter_console)
    else:  # Local environment
        print(
            f"{COLORS.get('INFO', '')}INFO:{RESET_SEQ}     Running Locally: Configured colored standard logging to console.",
            file=sys.stderr,
        )
        formatter_console = AlignedColoredFormatter(
            fmt=LOG_FORMAT_BASE, datefmt=LOG_FORMAT_DATE, use_color=True
        )
        console_handler.setFormatter(formatter_console)

        log_dir = os.path.dirname(LOG_FILE_PATH)
        if log_dir and not os.path.exists(log_dir):
            try:
                os.makedirs(log_dir)
            except OSError as e:
                print(
                    f"Warning: Could not create log directory {log_dir}: {e}",
                    file=sys.stderr,
                )
        try:
            file_handler = logging.handlers.RotatingFileHandler(
                LOG_FILE_PATH,
                maxBytes=LOG_FILE_MAX_BYTES,
                backupCount=LOG_FILE_BACKUP_COUNT,
                encoding="utf-8",
            )
            file_handler.setLevel(LOG_LEVEL)
            formatter_file = AlignedColoredFormatter(
                fmt=LOG_FORMAT_BASE, datefmt=LOG_FORMAT_DATE, use_color=False
            )
            file_handler.setFormatter(formatter_file)
            file_handler.addFilter(request_filter)
            file_handler.addFilter(task_filter)
            logger.addHandler(file_handler)
            print(
                f"{COLORS.get('INFO', '')}INFO:{RESET_SEQ}     Running Locally: Configured rotating file logging to {LOG_FILE_PATH}",
                file=sys.stderr,
            )
        except Exception as e:
            print(f"Error: Failed to configure file logging: {e}", file=sys.stderr)
            file_handler = None

    logger.addHandler(console_handler)

    # --- Configure Uvicorn Loggers ---
    for log_name in ["uvicorn", "uvicorn.error", "uvicorn.access"]:
        uvicorn_logger = logging.getLogger(log_name)
        if uvicorn_logger.hasHandlers():
            for handler in uvicorn_logger.handlers[:]:
                uvicorn_logger.removeHandler(handler)
                handler.close()
        uvicorn_logger.propagate = False
        if log_name == "uvicorn.access":
            uvicorn_logger.setLevel(logging.INFO)
        else:
            uvicorn_logger.setLevel(LOG_LEVEL)
        uvicorn_logger.addHandler(console_handler)
        if file_handler:
            uvicorn_logger.addHandler(file_handler)

    final_log = logging.getLogger(__name__)
    final_log.info("Logging setup complete.")
