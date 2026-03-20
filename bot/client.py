"""
client.py — Binance Futures API client wrapper.

Wraps python-binance's Client with futures-specific helpers:
  - get_market_price(symbol)
  - get_usdt_balance()
  - place_order(...)  delegates to orders.place_order()

All public methods log every request and response and re-raise exceptions
so the CLI layer can handle user-facing error messages.
"""
import logging
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException

from .orders import place_order as _place_order

logger = logging.getLogger(__name__)


class BinanceTradingBot:
    """Binance Futures API client wrapper."""

    def __init__(self, api_key: str, api_secret: str, testnet: bool = True):
        self.api_key    = api_key
        self.api_secret = api_secret
        self.testnet    = testnet
        self.client     = Client(api_key, api_secret, testnet=testnet)
        # Note: testnet=True in the Client constructor already routes all calls
        # to the Futures Testnet. No manual URL override needed.
        logger.info(f"Initialized BinanceTradingBot (Testnet: {testnet})")

    # ------------------------------------------------------------------
    # Market data
    # ------------------------------------------------------------------

    def get_market_price(self, symbol: str) -> float:
        """Fetch the current mark price for a futures symbol."""
        try:
            ticker = self.client.futures_symbol_ticker(symbol=symbol.upper())
            price  = ticker["price"]
            logger.info(f"Fetched price for {symbol}: {price}")
            return float(price)
        except (BinanceAPIException, BinanceRequestException) as e:
            logger.error(f"API Error fetching price for {symbol}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error fetching price: {e}")
            raise

    def get_usdt_balance(self) -> float:
        """Fetch the available USDT balance from the Futures wallet."""
        try:
            balances = self.client.futures_account_balance()
            for b in balances:
                if b["asset"] == "USDT":
                    logger.info(f"Fetched USDT Balance: {b['balance']}")
                    return float(b["balance"])
            return 0.0
        except (BinanceAPIException, BinanceRequestException) as e:
            logger.error(f"API Error fetching balance: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error fetching balance: {e}")
            raise

    # ------------------------------------------------------------------
    # Order placement — delegates to orders.py
    # ------------------------------------------------------------------

    def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        price: float = None,
        stop_price: float = None,
    ) -> dict:
        """
        Place a MARKET, LIMIT, or STOP_MARKET futures order.
        Delegates all business logic to bot.orders.place_order().
        """
        return _place_order(
            client     = self.client,
            symbol     = symbol,
            side       = side,
            order_type = order_type,
            quantity   = quantity,
            price      = price,
            stop_price = stop_price,
        )
