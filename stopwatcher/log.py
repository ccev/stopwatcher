import logging
import sys

from loguru import logger

log_level = logging.INFO


class InterceptHandler(logging.Handler):
    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


console_format = (
    "<cyan>{time:HH:mm:ss.SS}</cyan>",
    "<level>{level: >1.1}</level>",
    "<cyan>{name: <22.22}</cyan>",
    "<level>{message}</level>",
)
console_format = " | ".join(console_format)

logger.remove()

logger.add(
    sink=sys.stdout,
    format=console_format,
    colorize=True,
    level=log_level,
    filter=lambda record: record["level"].no < logging.ERROR,
    enqueue=True,
)
logger.add(sink=sys.stderr, format=console_format, colorize=True, level=logging.ERROR, backtrace=True, enqueue=True)

logging.basicConfig(handlers=[InterceptHandler()], level=0)

log = logger
