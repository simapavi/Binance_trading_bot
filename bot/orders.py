"""
orders.py — Order placement logic for Binance Futures.

Supports three order types:
  - MARKET     : executes immediately at the best available price
  - LIMIT      : executes at `price` or better (GTC time-in-force)
  - STOP_MARKET: triggers a market order when price crosses `stop_price`
                 (Bonus: third order type added beyond assignment minimum)

This module is intentionally stateless — it receives a plain Binance
`client` object so it can be tested independently of the wrapper class.
"""
import logging
from binance.exceptions import BinanceAPIException, BinanceRequestException

logger = logging.getLogger(__name__)


def place_order(
    client,
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: float = None,
    stop_price: float = None,
) -> dict:
    """
    Build params and send a futures order to the Binance API.

    Args:
        client     : A python-binance Client instance.
        symbol     : Trading pair, e.g. "BTCUSDT".
        side       : "BUY" or "SELL".
        order_type : "MARKET", "LIMIT", or "STOP_MARKET".
        quantity   : Contract quantity to trade.
        price      : Required for LIMIT orders.
        stop_price : Required for STOP_MARKET orders.

    Returns:
        dict: Raw Binance API response for the created order.

    Raises:
        BinanceAPIException, BinanceRequestException, ValueError
    """
    try:
        # Build a human-readable display label for the log
        if price:
            display = f"@ {price}"
        elif stop_price:
            display = f"STOP @ {stop_price}"
        else:
            display = "MARKET"

        logger.info(f"REQUEST: {order_type} {side} {quantity} {symbol} {display}")

        params = {
            "symbol"  : symbol.upper(),
            "side"    : side.upper(),
            "type"    : order_type.upper(),
            "quantity": quantity,
        }

        if order_type.upper() == "LIMIT":
            if not price:
                raise ValueError("price is required for LIMIT orders")
            params["price"]       = price
            params["timeInForce"] = "GTC"

        elif order_type.upper() == "STOP_MARKET":
            # Bonus: third order type — triggers market execution at stopPrice
            if not stop_price:
                raise ValueError("stop_price is required for STOP_MARKET orders")
            params["stopPrice"] = stop_price

        response = client.futures_create_order(**params)
        logger.info(f"RESPONSE: {response}")
        return response

    except (BinanceAPIException, BinanceRequestException) as e:
        logger.error(f"API Error placing order: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error placing order: {e}")
        raise
