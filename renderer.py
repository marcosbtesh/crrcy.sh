import shutil

class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    UNDERLINE = "\033[4m"
    
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_CYAN = "\033[96m"

def get_terminal_width():
    return shutil.get_terminal_size((80, 20)).columns

def center_text(text, width=None):
    if width is None:
        width = get_terminal_width()
    return text.center(width)

def render_header(title, subtitle=None):
    width = get_terminal_width()
    output = []
    output.append(f"{Colors.BOLD}{Colors.BRIGHT_BLUE}{'=' * width}{Colors.RESET}")
    output.append(center_text(f"{Colors.BOLD}{Colors.WHITE}{title}{Colors.RESET}", width))
    if subtitle:
        output.append(center_text(f"{Colors.DIM}{subtitle}{Colors.RESET}", width))
    output.append(f"{Colors.BOLD}{Colors.BRIGHT_BLUE}{'=' * width}{Colors.RESET}")
    return "\n".join(output)

def render_fiat_table(data: dict):
    """
    Renders a flat dictionary of {ISO: Rate} into a 2-column table.
    """
    lines = []
    lines.append(render_header("FIAT CURRENCY RATES", "Base: USD"))
    lines.append("")
    
    header = f"{Colors.BOLD}{Colors.UNDERLINE}{'CURRENCY':<10} {'RATE':>15}{Colors.RESET}"
    lines.append(center_text(header))
    
    sorted_data = sorted(data.items())
    
    for iso, rate in sorted_data:
        color = Colors.CYAN
        if iso == "USD": color = Colors.GREEN
        if iso == "EUR": color = Colors.YELLOW

        try:
            rate_str = f"{rate:,.4f}"
        except (ValueError, TypeError):
            rate_str = str(rate)

        row = f"{color}{iso:<10}{Colors.RESET} {Colors.WHITE}{rate_str:>15}{Colors.RESET}"
        lines.append(center_text(row))
        
    lines.append("")
    lines.append(f"{Colors.DIM}Usage: curl host/fiat?isos=USD,EUR{Colors.RESET}")
    return "\n".join(lines) + "\n"

def render_crypto_table(data: dict):
    """
    Renders a dictionary of {Coin: {vs: price}} into a table.
    """
    lines = []
    lines.append(render_header("CRYPTO MARKET", "Real-time Prices"))
    lines.append("")

    if not data:
        return f"{Colors.RED}No data available.{Colors.RESET}"

    first_coin = list(data.values())[0]
    vs_currencies = list(first_coin.keys())
    
    col_width = 15
    name_width = 15
    
    header_str = f"{'COIN':<{name_width}}"
    for vs in vs_currencies:
        header_str += f"{vs.upper():>{col_width}}"
        
    lines.append(center_text(f"{Colors.BOLD}{Colors.UNDERLINE}{header_str}{Colors.RESET}"))

    for coin, prices in data.items():
        row_str = f"{Colors.BRIGHT_YELLOW}{coin.capitalize():<{name_width}}{Colors.RESET}"
        
        for vs in vs_currencies:
            price = prices.get(vs, 0)
            if price < 1:
                p_str = f"{price:.6f}"
            else:
                p_str = f"{price:,.2f}"
            
            row_str += f"{Colors.WHITE}{p_str:>{col_width}}{Colors.RESET}"
            
        lines.append(center_text(row_str))

    lines.append("")
    lines.append(f"{Colors.DIM}Usage: curl host/crypto?coins=btc,eth&vs=usd,eur{Colors.RESET}")
    return "\n".join(lines) + "\n"