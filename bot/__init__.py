"""
bot/ — Binance Futures Trading Bot package.

Exposes the main API client for convenience:
    from bot import BinanceTradingBot
"""
from .client import BinanceTradingBot

__all__ = ["BinanceTradingBot"]
