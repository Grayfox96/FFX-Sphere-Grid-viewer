import logging
import sys
from functools import wraps
from traceback import format_tb
from types import TracebackType

from .tkstatuslabel import TkStatusLabel


class UIHandler(logging.Handler):
    def __init__(self, output_widget: TkStatusLabel) -> None:
        super().__init__()
        self.output_widget = output_widget

    def emit(self, record: logging.LogRecord) -> None:
        self.output_widget.update(self.format(record))


def log_exceptions(logger: logging.Logger | None = None):
    if logger is None:
        logger = logging.getLogger(__name__)

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception:
                issue = 'exception in ' + func.__name__ + '\n'
                logger.exception(issue)
                raise
        return wrapper
    return decorator


def setup_main_logger() -> None:
    logger = logging.getLogger(__name__.split('.')[0])

    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        fmt='{asctime} - {name} - {levelname} - {message}',
        datefmt='%Y-%m-%d %H:%M:%S',
        style='{',
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    file_handler = logging.FileHandler('ffx_sphere_grid_viewer.log')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.WARNING)
    logger.addHandler(file_handler)


def log_tkinter_error(error: Exception,
                      message: tuple[str],
                      tb: TracebackType,
                      ) -> None:
    error_message = (f'Exception in Tkinter callback\n'
                     f'Traceback (most recent call last):\n'
                     f'{''.join(format_tb(tb))}'
                     f'{error.__name__}: {message}')
    logger = logging.getLogger(__name__)
    logger.error(error_message)
