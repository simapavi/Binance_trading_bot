"""
validators.py — Input validation for CLI arguments and wizard prompts.

All validation functions print a descriptive error message and call
sys.exit(1) on failure so the caller never needs to handle bad input.
"""
import sys


# ---------------------------------------------------------------------------
# ANSI colour helpers (shared across validators and cli)
# ---------------------------------------------------------------------------

class Colors:
    CYAN    = "\033[96m"
    GREEN   = "\033[92m"
    YELLOW  = "\033[93m"
    RED     = "\033[91m"
    BLUE    = "\033[94m"
    MAGENTA = "\033[95m"
    BOLD    = "\033[1m"
    RESET   = "\033[0m"


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------

def validate_order_args(args) -> None:
    """
    Validate all order arguments after CLI parsing or interactive wizard.

    Checks performed:
      - quantity must be > 0
      - LIMIT orders require --price
      - STOP_MARKET orders require --stop-price

    Exits with code 1 and prints a descriptive message on failure.
    """
    order_type = args.type.upper()

    if args.quantity <= 0:
        _fail("--quantity must be greater than zero.")

    if order_type == "LIMIT" and not args.price:
        _fail("--price is required for LIMIT orders.")

    if order_type == "STOP_MARKET" and not getattr(args, "stop_price", None):
        _fail("--stop-price is required for STOP_MARKET orders.")


def prompt_positive_float(label: str, optional: bool = False):
    """
    Interactive prompt that loops until the user enters a valid positive float.
    Returns None only when optional=True and the user enters an empty string.
    """
    while True:
        raw = input(f"  {Colors.BOLD}{label}:{Colors.RESET}  ").strip()
        if optional and raw == "":
            return None
        try:
            value = float(raw)
            if value <= 0:
                raise ValueError
            return value
        except ValueError:
            print(f"  {Colors.RED}✘  Please enter a valid positive number.{Colors.RESET}")


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _fail(message: str) -> None:
    """Print a formatted error and exit."""
    print(f"\n  {Colors.RED}✘  Error: {message}{Colors.RESET}")
    sys.exit(1)
