"""
logging_config.py — Central logging configuration for the trading bot.

Call setup_logging() once at application startup (in cli.py) before any
other module creates a logger, so all loggers inherit the same handlers
and format.
"""
import logging


def setup_logging(log_file: str = "trading_bot.log") -> None:
    """
    Configure the root logger with two handlers:
      - FileHandler    → captures INFO and above (full detail for debugging)
      - StreamHandler  → captures WARNING and above only, so the terminal
                         stays clean and doesn't duplicate the colored
                         print() output from cli.py
    """
    # File handler — full verbosity
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    )

    # Console handler — warnings and errors only (not noisy)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    )

    logging.basicConfig(
        level=logging.INFO,
        handlers=[file_handler, console_handler],
    )
