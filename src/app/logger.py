"""File contains logging configuration"""

import logging
import logging.handlers
import os
import sys
import asyncio
import contextvars
import json_log_formatter  # For Cloud Run JSON logs

# TODO: Fix this whole file, i asked for the ai to do it, and it is full of unecessary stuff...
# For now this is not important, but probably it will carry performance issues


# --- Configuration Constants ---
LOG_LEVEL = logging.INFO
LOG_FILE_BACKUP_COUNT = 5
LOG_FILE_MAX_BYTES = 1024 * 1024 * 10  # 10 MB
LOG_FILE_PATH = ".log"
# Base format string (everything AFTER the 'LEVELNAME: ' part)
LOG_FORMAT_BASE = "[%(requestId)s] [%(taskName)s] - %(name)s:%(lineno)d - %(message)s"
# Date format
LOG_FORMAT_DATE = "%Y-%m-%d %H:%M:%S"
# Width for the 'LEVELNAME:' prefix including padding
LOG_LEVEL_WIDTH = 9  # (e.g., len("CRITICAL:") + 1 space)

# --- ANSI Color Codes ---
RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[1;%dm"
BOLD_SEQ = "\033[1m"

COLORS = {
    "DEBUG": COLOR_SEQ % 34,  # Blue
    "INFO": COLOR_SEQ % 32,  # Green
    "WARNING": COLOR_SEQ % 33,  # Yellow
    "ERROR": COLOR_SEQ % 31,  # Red
    "CRITICAL": COLOR_SEQ % 31,  # Red
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
        return True


# --- Custom Formatter for Level Alignment and Color ---
class AlignedColoredFormatter(logging.Formatter):
    """
    Formats logs with LEVELNAME: prefix aligned to a fixed width,
    optionally adding ANSI color codes.
    """

    def __init__(
        self,
        fmt=LOG_FORMAT_BASE,
        datefmt=LOG_FORMAT_DATE,
        use_color=True,
        level_width=LOG_LEVEL_WIDTH,
    ):
        # Initialize with the BASE format (message part)
        super().__init__(fmt=fmt, datefmt=datefmt)
        self.use_color = use_color
        self.level_width = level_width

    def format(self, record):
        # 1. Format the main message part first using the base format string
        message = super().format(record)

        # 2. Create the level prefix and pad it
        levelname = record.levelname
        level_prefix = f"{levelname}:"
        # Use left-alignment '<' and the specified width
        padded_prefix = f"{level_prefix:<{self.level_width}}"

        # 3. Add color if applicable
        is_tty = (
            hasattr(sys.stdout, "isatty")
            and sys.stdout.isatty()
            or hasattr(sys.stderr, "isatty")
            and sys.stderr.isatty()
        )

        if self.use_color and levelname in COLORS and is_tty:
            colored_padded_prefix = f"{COLORS[levelname]}{padded_prefix}{RESET_SEQ}"
            # Add timestamp at the beginning (optional, could be part of base fmt)
            # timestamp = self.formatTime(record, self.datefmt)
            # return f"{timestamp} {colored_padded_prefix} {message}"
            return f"{colored_padded_prefix} {message}"  # Timestamp handled by base if needed
        else:
            # No color, just the padded prefix
            # timestamp = self.formatTime(record, self.datefmt)
            # return f"{timestamp} {padded_prefix} {message}"
            return f"{padded_prefix} {message}"  # Timestamp handled by base if needed


# --- Logger Configuration Function ---
def setup_logging():
    """Configures logging based on execution environment (Cloud Run vs Local)."""
    logger = logging.getLogger()  # Get root logger
    logger.setLevel(LOG_LEVEL)  # Set level on ROOT logger

    # Clear existing handlers to avoid duplicates during reloads
    if logger.hasHandlers():
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
            handler.close()

    # Create filters
    request_filter = RequestIdFilter()
    task_filter = TaskContextFilter()

    # Check if running in Google Cloud Run
    RUNNING_IN_CLOUD = os.environ.get("K_SERVICE") is not None

    # --- CONSOLE Handler ---
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(LOG_LEVEL)  # <<< SET LEVEL ON HANDLER
    console_handler.addFilter(request_filter)
    console_handler.addFilter(task_filter)

    # --- FILE Handler (initialized only if needed) ---
    file_handler = None  # Initialize as None

    if RUNNING_IN_CLOUD:
        # Configure JSON formatter for Console Handler
        # ... (CloudLoggingJSONFormatter class definition) ...
        class CloudLoggingJSONFormatter(json_log_formatter.JSONFormatter):
            def format(self, record):
                json_record = super().format(record)
                severity_map = {
                    "DEBUG": "DEBUG",
                    "INFO": "INFO",
                    "WARNING": "WARNING",
                    "ERROR": "ERROR",
                    "CRITICAL": "CRITICAL",
                }
                # TODO: Fix horrible code, honestly i hate this function. 
                json_record["severity"] = severity_map.get(record.levelname, "DEFAULT") # type: ignore Atrocious codding for my part
                json_record["logging.googleapis.com/source_location"] = { # type: ignore
                    "file": record.pathname,
                    "line": record.lineno,
                    "function": record.funcName,
                }
                # Ensure message field exists and handle potential formatting issues
                try:
                    json_record["message"] = record.getMessage() # type: ignore
                except Exception as e:
                    json_record["message"] = f"Error formatting log message: {e}" # type: ignore
                    json_record["original_log_args"] = ( # type: ignore
                        record.args
                    )  # Add original args for debugging
                return json_record

        formatter_console = CloudLoggingJSONFormatter(
            {  # Fields for JSON output
                "timestamp": "asctime",
                "name": "name",
                "taskName": "taskName",
                "requestId": "requestId",
            }, # type: ignore
            datefmt=LOG_FORMAT_DATE,  # Or ISO format
        )
        console_handler.setFormatter(formatter_console)
        print(
            "INFO: Running in Cloud Run: Configured JSON logging to console.",
            file=sys.stderr,
        )

    else:  # Local environment
        # Configure Aligned/Colored formatter for Console Handler
        formatter_console = AlignedColoredFormatter(
            fmt=LOG_FORMAT_BASE, datefmt=LOG_FORMAT_DATE, use_color=True
        )
        console_handler.setFormatter(formatter_console)
        print(
            f"{COLORS.get('INFO', '')}INFO:{RESET_SEQ}     Running Locally: Configured colored standard logging to console.",
            file=sys.stderr,
        )

        # --- FILE Handler (Only for Local) ---
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
            file_handler.setLevel(LOG_LEVEL)  # <<< SET LEVEL ON HANDLER
            # Configure Aligned formatter (no color) for File Handler
            formatter_file = AlignedColoredFormatter(
                fmt=LOG_FORMAT_BASE, datefmt=LOG_FORMAT_DATE, use_color=False
            )
            file_handler.setFormatter(formatter_file)
            file_handler.addFilter(request_filter)
            file_handler.addFilter(task_filter)
            # Add file handler to ROOT logger (for app logs)
            logger.addHandler(file_handler)
            print(
                f"{COLORS.get('INFO', '')}INFO:{RESET_SEQ}     Running Locally: Configured rotating file logging to {LOG_FILE_PATH}",
                file=sys.stderr,
            )
        except Exception as e:
            print(f"Error: Failed to configure file logging: {e}", file=sys.stderr)
            file_handler = None  # Ensure it's None if setup fails

    # Add console handler to ROOT logger (for app logs)
    logger.addHandler(console_handler)

    # --- Configure Uvicorn Loggers ---
    # Apply the *same handlers* (with levels already set) to Uvicorn's loggers
    for log_name in ["uvicorn", "uvicorn.error", "uvicorn.access"]:
        uvicorn_logger = logging.getLogger(log_name)
        # Clear existing handlers Uvicorn might have added forcefully
        if uvicorn_logger.hasHandlers():
            for handler in uvicorn_logger.handlers[:]:
                uvicorn_logger.removeHandler(handler)
                handler.close()
        # Crucial: Prevent Uvicorn logs from bubbling up to root logger's handlers
        # (which would cause duplicates since we add handlers directly below)
        uvicorn_logger.propagate = False

        # Set the logger level itself (controls if messages *reach* the handlers)
        # You might want uvicorn.access at INFO, but uvicorn/uvicorn.error matching LOG_LEVEL
        if log_name == "uvicorn.access":
            uvicorn_logger.setLevel(logging.INFO)  # Capture all access logs
        else:
            uvicorn_logger.setLevel(
                LOG_LEVEL
            )  # Match app's level for general/error logs

        # Add the configured handler(s) directly to this Uvicorn logger
        uvicorn_logger.addHandler(console_handler)
        if file_handler:  # Add file handler if it exists (local only)
            uvicorn_logger.addHandler(file_handler)

    final_log = logging.getLogger(__name__)
    final_log.info("Logging setup complete.")
