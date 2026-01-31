import math
import shutil
from datetime import datetime, timedelta


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
    output.append(
        center_text(f"{Colors.BOLD}{Colors.WHITE}{title}{Colors.RESET}", width)
    )
    if subtitle:
        output.append(center_text(f"{Colors.DIM}{subtitle}{Colors.RESET}", width))
    output.append(f"{Colors.BOLD}{Colors.BRIGHT_BLUE}{'=' * width}{Colors.RESET}")
    return "\n".join(output)


def render_footer():
    # TODO: Implement footer rendering here
    print("")


def render_fiat_table(data: dict):

    lines = []
    lines.append(render_header("CURRENCY RATES", "Base: USD"))
    lines.append("")

    header = (
        f"{Colors.BOLD}{Colors.UNDERLINE}{'CURRENCY':<10} {'RATE':>15}{Colors.RESET}"
    )
    lines.append(center_text(header))

    sorted_data = sorted(data.items())

    for iso, rate in sorted_data:
        color = Colors.CYAN
        if iso == "USD":
            color = Colors.GREEN
        if iso == "EUR":
            color = Colors.YELLOW

        try:
            rate_str = f"{rate:,.4f}"
        except (ValueError, TypeError):
            rate_str = str(rate)

        row = (
            f"{color}{iso:<10}{Colors.RESET} {Colors.WHITE}{rate_str:>15}{Colors.RESET}"
        )
        lines.append(center_text(row))

    lines.append("")
    lines.append(f"{Colors.DIM}crrcy.sh{Colors.RESET}")
    return "\n".join(lines) + "\n"


def _format_x_axis(date_obj, duration_delta):

    print("Formatting X Axis")

    days = duration_delta.days

    if days < 1:
        return date_obj.strftime("%H:%M")
    elif days > 60:
        return date_obj.strftime("%b %y")
    else:
        return date_obj.strftime("%d %b")


def _render_graph_footer(last_updated, start_date, end_date, start_price, end_price):
    width = get_terminal_width()

    fmt = "%Y-%m-%d %H:%M UTC"
    start_str = (
        start_date.strftime(fmt)
        if isinstance(start_date, datetime)
        else str(start_date)
    )
    end_str = (
        end_date.strftime(fmt) if isinstance(end_date, datetime) else str(end_date)
    )

    if isinstance(last_updated, str):
        try:
            last_updated = last_updated.replace("T", " ").replace("Z", " ")
        except:
            pass

    footer_lines = []
    footer_lines.append(f"{Colors.DIM}{'-' * width}{Colors.RESET}")

    col_width = width // 3

    l_col = f"Start: {start_str}"
    m_col = f"Updated: {last_updated}"
    r_col = f"End: {end_str}"

    line = f"{Colors.CYAN}{l_col:<{col_width}}{Colors.YELLOW}{m_col:^{col_width}}{Colors.CYAN}{r_col:>{col_width}}{Colors.RESET}"

    footer_lines.append(line)
    footer_lines.append("")
    footer_lines.append(center_text(f"{Colors.BOLD}crrcy.sh{Colors.RESET}"))

    return "\n".join(footer_lines)


def render_graph(data: dict, start_date, end_date):
    print("Imlement render graph here")

    metadata = data.get("meta", {})
    last_updated = metadata.get("last_updated_at", "Unknown")

    raw_data = data.get("data", {})

    points = []
