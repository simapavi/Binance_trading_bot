# Binance Futures Trading Bot

A Python-based CLI trading bot for the Binance Futures Testnet (USDT-M). Developed as part of a Python Developer Intern assignment.

## Features
- **Order Types**: MARKET, LIMIT, and **STOP_MARKET** (bonus third type)
- **Interactive Wizard**: Auto-launches guided prompts when no CLI args are passed
- **Enhanced CLI Output**: Color-coded summaries, responses, and error messages
- **Balance Pre-Check**: Validates estimated order cost against account balance
- **Robust Logging**: All API requests, responses, and errors logged to `trading_bot.log` and console
- **Exception Handling**: Covers invalid input, API errors, and network failures

## Tech Stack
- Python 3.x
- `python-binance`
- `python-dotenv`

## Project Structure

```
trading_bot/
  bot/
    __init__.py           # package init
    client.py             # Binance client wrapper
    orders.py             # order placement logic (MARKET / LIMIT / STOP_MARKET)
    validators.py         # input validation + ANSI colors
    logging_config.py     # centralised logging setup
  cli.py                  # CLI entry point  ← run this
  trading_bot.py          # backward-compat shim (calls cli.main)
  README.md
  requirements.txt
  .env
```

## Setup Instructions

1. **Clone the project** and navigate to the directory.

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   venv\Scripts\activate       # Windows
   source venv/bin/activate    # Mac/Linux
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure API Keys**:
   - Rename `.env.example` to `.env`
   - Add your [Binance Futures Testnet](https://testnet.binancefuture.com) credentials:
     ```
     BINANCE_API_KEY=your_api_key_here
     BINANCE_API_SECRET=your_api_secret_here
     ```

## How to Run

### Option A — Interactive Wizard (no arguments needed)
```bash
python cli.py
```
The bot guides you step-by-step through symbol, side, type, quantity, and price.

---

### Option B — CLI Arguments

#### Place a MARKET Order
```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.002
```

#### Place a LIMIT Order
```bash
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.002 --price 75000
```

#### Place a STOP_MARKET Order *(Bonus)*
```bash
python cli.py --symbol BTCUSDT --side SELL --type STOP_MARKET --quantity 0.002 --stop-price 65000
```

#### Switch to Mainnet *(real funds — use with caution)*
```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.002 --no-testnet
```

---

### All CLI Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--symbol` | Yes | Trading pair (e.g. `BTCUSDT`) |
| `--side` | Yes | `BUY` or `SELL` |
| `--type` | Yes | `MARKET`, `LIMIT`, or `STOP_MARKET` |
| `--quantity` | Yes | Amount to trade (must be > 0) |
| `--price` | LIMIT only | Limit order price |
| `--stop-price` | STOP_MARKET only | Stop trigger price |
| `--testnet` / `--no-testnet` | No | Testnet mode (default: `--testnet`) |

---

## Assumptions
- All orders target USDT-M Binance Futures (not Coin-M or Spot)
- Default network is **Testnet**; mainnet requires explicit `--no-testnet`
- LIMIT orders use **GTC** (Good Till Cancelled) time-in-force
- STOP_MARKET triggers a market order when price crosses `stopPrice`
- Minimum notional value per order is **100 USDT** (Binance requirement)

## Architecture

```
cli.py  (entry point)
  │
  ├── bot/logging_config.py   ← sets up FileHandler + StreamHandler
  ├── bot/client.py           ← BinanceTradingBot (price, balance, place_order)
  ├── bot/orders.py           ← stateless place_order() function
  └── bot/validators.py       ← validate_order_args(), Colors, prompts
```

## Log Files
All operations recorded to `trading_bot.log`. Example entries after a successful order:
```
2026-03-20 10:02:45 - INFO - Initialized BinanceTradingBot (Testnet: True)
2026-03-20 10:02:45 - INFO - Fetched price for BTCUSDT: 70701.80
2026-03-20 10:02:45 - INFO - USDT Balance: 5000.00000000
2026-03-20 10:02:45 - INFO - REQUEST: MARKET BUY 0.002 BTCUSDT MARKET
2026-03-20 10:02:45 - INFO - RESPONSE: {'orderId': 12891786775, 'status': 'NEW', ...}
```
