"""
trading_bot.py — Backward-compatibility shim.

The project has been refactored into a proper package structure:

    bot/
        __init__.py
        client.py         <- Binance client wrapper
        orders.py         <- order placement logic
        validators.py     <- input validation
        logging_config.py <- logging setup
    cli.py                <- CLI entry point  (run this file)

This file exists only so that anyone who previously ran:
    python trading_bot.py ...
continues to get the same behaviour without changing their command.
"""
from cli import main

if __name__ == "__main__":
    main()
