import logging
import time

# Configure Logging (matching the real script)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("mock_trading_bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MockBinanceTradingBot:
    """A simulated version of the trading bot for demonstration purposes."""
    def __init__(self, api_key="MOCK_KEY", api_secret="MOCK_SECRET", testnet=True):
        logger.info(f"Initialized MockBinanceTradingBot (Simulating Testnet: {testnet})")
        self.api_key = api_key

    def get_market_price(self, symbol="BTCUSDT"):
        """Simulate fetching market price."""
        logger.info(f"Fetching market price for {symbol}...")
        time.sleep(0.5)
        price = 65432.10
        logger.info(f"Current price for {symbol}: {price}")
        return price

    def get_usdt_balance(self):
        """Simulate fetching USDT balance."""
        logger.info("Fetching USDT Balance...")
        time.sleep(0.5)
        balance = 1000.00
        logger.info(f"USDT Balance: {balance}")
        return balance

    def place_order(self, symbol, side, order_type, quantity, price=None):
        """Simulate placing an order."""
        logger.info(f"Attempting to place {order_type} {side} order for {quantity} {symbol}...")
        time.sleep(1)
        
        if order_type == 'LIMIT' and not price:
            logger.error("Failed to place order: Price is required for LIMIT orders.")
            return None
        
        # Simulate a successful response
        order_id = 987654321
        logger.info(f"Order successful! Simulated ID: {order_id}")
        return {"orderId": order_id, "status": "FILLED", "symbol": symbol, "side": side}

if __name__ == "__main__":
    print("-" * 30)
    print("MOCK TRADING BOT DEMONSTRATION")
    print("-" * 30)
    
    bot = MockBinanceTradingBot()
    
    # 1. Fetch Price
    bot.get_market_price("BTCUSDT")
    
    # 2. Check Balance
    bot.get_usdt_balance()
    
    # 3. Place Market Buy
    bot.place_order(symbol="BTCUSDT", side="BUY", order_type="MARKET", quantity=0.001)
    
    # 4. Place Limit Sell (with failure simulation if price missing)
    bot.place_order(symbol="BTCUSDT", side="SELL", order_type="LIMIT", quantity=0.001, price=66000.0)
    
    print("-" * 30)
    print("Demonstration completed. See 'mock_trading_bot.log' for details.")
    print("-" * 30)
