"""
cli.py — CLI entry point for the Binance Futures Trading Bot.

This module is the top-level entry point that wires together all layers:
  - bot.logging_config  → configure logging before anything else
  - bot.client          → BinanceTradingBot (API wrapper)
  - bot.validators      → validate args & interactive prompts
  - bot.orders          → called indirectly via BinanceTradingBot.place_order()

Run:
    python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.002
    python cli.py   # launches interactive wizard
"""
import os
import sys
import argparse
from dotenv import load_dotenv
from binance.exceptions import BinanceAPIException, BinanceRequestException

# --- Internal package imports ---
from bot.logging_config import setup_logging
from bot.client import BinanceTradingBot
from bot.validators import Colors, validate_order_args, prompt_positive_float

# Initialise logging FIRST — before any logger.getLogger() calls in sub-modules
setup_logging()

import logging
logger = logging.getLogger(__name__)

# Load .env credentials
load_dotenv()


# =============================================================================
# CLI OUTPUT HELPERS
# =============================================================================

def print_banner(text: str, color: str = Colors.CYAN) -> None:
    """Print a styled section banner."""
    line = "═" * 54
    print(f"\n{color}{Colors.BOLD}{line}{Colors.RESET}")
    print(f"{color}{Colors.BOLD}  {text}{Colors.RESET}")
    print(f"{color}{Colors.BOLD}{line}{Colors.RESET}")


def print_order_summary(args) -> None:
    """Print a clear, colour-coded summary of the order request."""
    print_banner("ORDER REQUEST SUMMARY", Colors.BLUE)
    side_color = Colors.GREEN if args.side.upper() == "BUY" else Colors.RED
    print(f"  {Colors.BOLD}Symbol  :{Colors.RESET}  {Colors.CYAN}{args.symbol.upper()}{Colors.RESET}")
    print(f"  {Colors.BOLD}Side    :{Colors.RESET}  {side_color}{Colors.BOLD}{args.side.upper()}{Colors.RESET}")
    print(f"  {Colors.BOLD}Type    :{Colors.RESET}  {args.type.upper()}")
    print(f"  {Colors.BOLD}Quantity:{Colors.RESET}  {args.quantity}")
    if args.type.upper() == "LIMIT":
        print(f"  {Colors.BOLD}Price   :{Colors.RESET}  {Colors.YELLOW}{args.price}{Colors.RESET}")
    if args.type.upper() == "STOP_MARKET":
        print(f"  {Colors.BOLD}Stop Px :{Colors.RESET}  {Colors.YELLOW}{args.stop_price}{Colors.RESET}")
    network_label = (
        f"{Colors.YELLOW}Testnet (USDT-M){Colors.RESET}"
        if args.testnet
        else f"{Colors.RED}{Colors.BOLD}MAINNET — REAL FUNDS{Colors.RESET}"
    )
    print(f"  {Colors.BOLD}Network :{Colors.RESET}  {network_label}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'═' * 54}{Colors.RESET}")


def print_order_response(response: dict) -> None:
    """Print orderId, status, executedQty, and avgPrice from the API response."""
    print_banner("ORDER RESPONSE DETAILS", Colors.MAGENTA)
    print(f"  {Colors.BOLD}Order ID    :{Colors.RESET}  {response.get('orderId')}")

    status = response.get("status", "UNKNOWN")
    status_color = Colors.GREEN if status in ("FILLED", "NEW") else Colors.YELLOW
    print(f"  {Colors.BOLD}Status      :{Colors.RESET}  {status_color}{Colors.BOLD}{status}{Colors.RESET}")
    print(f"  {Colors.BOLD}Executed Qty:{Colors.RESET}  {response.get('executedQty')}")

    # For STOP_MARKET show stop price; for MARKET/LIMIT show avg price
    stop_price = response.get("stopPrice")
    if stop_price and float(stop_price) > 0:
        print(f"  {Colors.BOLD}Stop Price  :{Colors.RESET}  {Colors.YELLOW}{stop_price}{Colors.RESET}")
    else:
        avg_price = response.get("avgPrice")
        if not avg_price or float(avg_price) == 0:
            cum_quote = float(response.get("cumQuote", 0))
            exec_qty  = float(response.get("executedQty", 0))
            avg_price = cum_quote / exec_qty if exec_qty > 0 else response.get("price", "N/A")
        print(f"  {Colors.BOLD}Avg Price   :{Colors.RESET}  {avg_price}")

    print(f"{Colors.MAGENTA}{Colors.BOLD}{'═' * 54}{Colors.RESET}")
    print(f"\n  {Colors.GREEN}{Colors.BOLD}✔  Order processed successfully.{Colors.RESET}")
    print(f"{Colors.MAGENTA}{Colors.BOLD}{'═' * 54}{Colors.RESET}\n")


# =============================================================================
# BONUS: INTERACTIVE WIZARD
# =============================================================================

def run_interactive_wizard():
    """
    Step-by-step interactive prompt — launches automatically when no
    CLI arguments are supplied.
    """
    print_banner("INTERACTIVE ORDER WIZARD", Colors.CYAN)
    print(f"  {Colors.YELLOW}No arguments detected — launching interactive mode.{Colors.RESET}\n")

    # Symbol
    symbol = input(f"  {Colors.BOLD}Symbol{Colors.RESET} (e.g. BTCUSDT) [BTCUSDT]: ").strip().upper()
    symbol = symbol or "BTCUSDT"

    # Side
    print(f"\n  {Colors.BOLD}Order Side:{Colors.RESET}")
    print(f"    {Colors.GREEN}[1] BUY{Colors.RESET}   — go long")
    print(f"    {Colors.RED}[2] SELL{Colors.RESET}  — go short")
    while True:
        choice = input("  Choose (1/2) [1]: ").strip()
        if choice in ("", "1", "2"):
            break
        print(f"  {Colors.RED}✘  Please enter 1 or 2.{Colors.RESET}")
    side = "SELL" if choice == "2" else "BUY"

    # Order type
    print(f"\n  {Colors.BOLD}Order Type:{Colors.RESET}")
    print(f"    [1] MARKET      — execute immediately at current price")
    print(f"    [2] LIMIT       — execute at your specified price or better")
    print(f"    [3] STOP_MARKET — trigger a market order at a stop price  {Colors.YELLOW}(Bonus){Colors.RESET}")
    while True:
        choice = input("  Choose (1/2/3) [1]: ").strip()
        if choice in ("", "1", "2", "3"):
            break
        print(f"  {Colors.RED}✘  Please enter 1, 2, or 3.{Colors.RESET}")
    order_type = {"": "MARKET", "1": "MARKET", "2": "LIMIT", "3": "STOP_MARKET"}[choice]

    # Quantity
    print()
    quantity   = prompt_positive_float("Quantity (e.g. 0.002)")
    price      = None
    stop_price = None

    if order_type == "LIMIT":
        price = prompt_positive_float("Limit Price")
    elif order_type == "STOP_MARKET":
        stop_price = prompt_positive_float("Stop Price")

    # Build a namespace to mimic argparse output
    class Args:
        pass

    args            = Args()
    args.symbol     = symbol
    args.side       = side
    args.type       = order_type
    args.quantity   = quantity
    args.price      = price
    args.stop_price = stop_price
    args.testnet    = True
    return args


# =============================================================================
# MAIN — CLI ENTRY POINT
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Binance Futures Trading Bot CLI",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument("--symbol",     type=str,   help="Trading symbol (e.g. BTCUSDT)")
    parser.add_argument("--side",       type=str,   choices=["BUY", "SELL"],
                        help="Order side: BUY or SELL")
    parser.add_argument("--type",       type=str,
                        choices=["MARKET", "LIMIT", "STOP_MARKET"],
                        help="Order type: MARKET | LIMIT | STOP_MARKET")
    parser.add_argument("--quantity",   type=float, help="Quantity to trade (must be > 0)")
    parser.add_argument("--price",      type=float, help="Limit price (LIMIT orders only)")
    parser.add_argument("--stop-price", type=float, dest="stop_price",
                        help="Stop trigger price (STOP_MARKET orders only)")
    # BooleanOptionalAction correctly handles --testnet / --no-testnet
    # (plain type=bool would make bool("False") == True, breaking the flag)
    parser.add_argument("--testnet", action=argparse.BooleanOptionalAction, default=True,
                        help="Use Binance Futures Testnet (default).\n"
                             "Pass --no-testnet to trade on mainnet with real funds.")

    args = parser.parse_args()

    # --- Launch interactive wizard if required fields are missing ---
    if not all([args.symbol, args.side, args.type, args.quantity]):
        args = run_interactive_wizard()

    # --- Input validation (bot/validators.py) ---
    validate_order_args(args)

    # --- Print request summary ---
    print_order_summary(args)

    # --- Load API credentials ---
    api_key    = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_API_SECRET")

    if not api_key or not api_secret:
        print(f"\n  {Colors.RED}✘  Error: API credentials missing in .env file.{Colors.RESET}")
        sys.exit(1)

    try:
        # Initialise API client (bot/client.py)
        bot = BinanceTradingBot(api_key, api_secret, testnet=args.testnet)

        # Pre-order checks
        print(f"\n  {Colors.CYAN}[*]{Colors.RESET} Fetching current price for "
              f"{Colors.BOLD}{args.symbol.upper()}{Colors.RESET}...")
        current_price = bot.get_market_price(args.symbol)

        print(f"  {Colors.CYAN}[*]{Colors.RESET} Checking account balance...")
        balance = bot.get_usdt_balance()

        estimated_cost = args.quantity * (args.price if args.price else current_price)
        if balance < estimated_cost:
            logger.warning(
                f"Low balance: {balance:.2f} USDT "
                f"(estimated cost: {estimated_cost:.2f} USDT)"
            )
            print(f"  {Colors.YELLOW}⚠  Warning: balance ({balance:.2f} USDT) may be insufficient "
                  f"for this order (~{estimated_cost:.2f} USDT).{Colors.RESET}")

        # Place order — delegates to bot/orders.py via bot/client.py
        print(f"  {Colors.CYAN}[*]{Colors.RESET} Placing "
              f"{Colors.BOLD}{args.type.upper()}{Colors.RESET} order on Binance...\n")
        response = bot.place_order(
            symbol     = args.symbol,
            side       = args.side,
            order_type = args.type,
            quantity   = args.quantity,
            price      = args.price,
            stop_price = getattr(args, "stop_price", None),
        )

        # Print response details
        if response:
            print_order_response(response)
        else:
            print(f"\n  {Colors.RED}✘  Order was not successful (empty response).{Colors.RESET}")

    except BinanceAPIException as e:
        print(f"\n  {Colors.RED}✘  Binance API Error: {e.message}{Colors.RESET}")
        logger.error(f"Execution Error: {e}")
    except BinanceRequestException as e:
        print(f"\n  {Colors.RED}✘  Network / Request Error: {e}{Colors.RESET}")
        logger.error(f"Request Error: {e}")
    except Exception as e:
        print(f"\n  {Colors.RED}✘  Unexpected error: {e}{Colors.RESET}")
        logger.error(f"Fatal Error: {e}")


if __name__ == "__main__":
    main()
