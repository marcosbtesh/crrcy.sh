import math
import shutil
from datetime import datetime, timedelta
from typing import Any, Union, cast


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
    BRIGHT_RED = "\033[91m"


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


def render_usage():
    width = get_terminal_width()
    lines = []

    lines.append(f"{Colors.BOLD}{Colors.BRIGHT_BLUE}{'=' * width}{Colors.RESET}")
    lines.append(center_text(f"{Colors.BOLD}{Colors.WHITE}crrcy.sh{Colors.RESET}"))
    lines.append(
        center_text(
            f"{Colors.DIM}Real-time Currency Exchange Rates & Historical Charts{Colors.RESET}"
        )
    )
    lines.append(f"{Colors.BOLD}{Colors.BRIGHT_BLUE}{'=' * width}{Colors.RESET}")
    lines.append("")

    lines.append(f"{Colors.BOLD}{Colors.BRIGHT_CYAN}PROJECT DESCRIPTION{Colors.RESET}")
    lines.append(f"{Colors.DIM}{'─' * width}{Colors.RESET}")
    lines.append(
        "crrcy.sh is a lightweight, terminal-friendly currency exchange service that provides"
    )
    lines.append(
        "real-time rates for fiat and cryptocurrencies, along with beautiful historical price"
    )
    lines.append("charts rendered directly in your terminal via curl.")
    lines.append("")

    lines.append(f"{Colors.BOLD}{Colors.BRIGHT_CYAN}ENDPOINTS{Colors.RESET}")
    lines.append(f"{Colors.DIM}{'─' * width}{Colors.RESET}")
    lines.append("")

    lines.append(f"{Colors.BRIGHT_GREEN}1. Get Latest Rates{Colors.RESET}")
    lines.append(f"   {Colors.CYAN}GET /LATEST{Colors.RESET}")
    lines.append("   Get latest exchange rates")
    lines.append("")

    lines.append(f"{Colors.BRIGHT_GREEN}2. Get Current Rates{Colors.RESET}")
    lines.append(f"   {Colors.CYAN}GET /USD{Colors.RESET}")
    lines.append(f"   {Colors.CYAN}GET /EUR/USD,EUR,GBP{Colors.RESET}")
    lines.append("   Get current exchange rates for one or multiple currencies")
    lines.append("")

    lines.append(f"{Colors.BRIGHT_GREEN}3. Get Historical Charts{Colors.RESET}")
    lines.append(f"   {Colors.CYAN}GET /last/USD/BTC/30d{Colors.RESET}")
    lines.append(f"   {Colors.CYAN}GET /last/USD/BTC/30d/5{Colors.RESET}")
    lines.append("   Display historical price data as an ASCII chart in your terminal")
    lines.append("")

    lines.append(f"{Colors.BOLD}{Colors.BRIGHT_CYAN}PARAMETERS{Colors.RESET}")
    lines.append(f"{Colors.DIM}{'─' * width}{Colors.RESET}")
    lines.append("")

    lines.append(f"{Colors.BRIGHT_YELLOW}base{Colors.RESET}")
    lines.append("  Base currency for rate conversion (e.g., USD, EUR, BTC)")
    lines.append("")

    lines.append(f"{Colors.BRIGHT_YELLOW}target{Colors.RESET}")
    lines.append(
        "  Target currencies (comma-separated for multiple, e.g., USD,EUR,GBP)"
    )
    lines.append("")

    lines.append(f"{Colors.BRIGHT_YELLOW}time{Colors.RESET}")
    lines.append("  Time range for historical data:")
    lines.append(f"    {Colors.CYAN}30d   → 30 days{Colors.RESET}")
    lines.append(f"    {Colors.CYAN}6m    → 6 months (180 days){Colors.RESET}")
    lines.append(f"    {Colors.CYAN}1y    → 1 year (365 days){Colors.RESET}")
    lines.append(f"    {Colors.CYAN}90    → 90 days (numeric){Colors.RESET}")
    lines.append("")

    lines.append(f"{Colors.BRIGHT_YELLOW}step{Colors.RESET}")
    lines.append("  Data point interval (optional, default: auto-calculated)")
    lines.append("  Must be >= 1. Max 365 data points per request")
    lines.append("")

    lines.append(f"{Colors.BOLD}{Colors.BRIGHT_CYAN}EXAMPLES{Colors.RESET}")
    lines.append(f"{Colors.DIM}{'─' * width}{Colors.RESET}")
    lines.append("")

    lines.append(f"{Colors.BRIGHT_GREEN}Latest Rates:{Colors.RESET}")
    lines.append(f"  $ curl crrcy.sh/latest")
    lines.append("")

    lines.append(f"{Colors.BRIGHT_GREEN}Current Rates:{Colors.RESET}")
    lines.append(f"  $ curl crrcy.sh/EUR/USD,GBP,JPY")
    lines.append("")

    lines.append(f"{Colors.BRIGHT_GREEN}Historical Charts:{Colors.RESET}")
    lines.append(f"  $ curl crrcy.sh/last/USD/BTC/30d")
    lines.append(f"  $ curl crrcy.sh/last/USD/ETH,BTC/90d")
    lines.append(f"  $ curl crrcy.sh/last/USD/EUR/1y/10")
    lines.append("")

    lines.append(f"{Colors.BOLD}{Colors.BRIGHT_CYAN}FEATURES{Colors.RESET}")
    lines.append(f"{Colors.DIM}{'─' * width}{Colors.RESET}")
    lines.append(
        f"  {Colors.BRIGHT_GREEN}✓{Colors.RESET} Real-time currency exchange rates"
    )
    lines.append(
        f"  {Colors.BRIGHT_GREEN}✓{Colors.RESET} Support for 150+ fiat currencies & major cryptocurrencies"
    )
    lines.append("")

    lines.append(f"{Colors.BOLD}{Colors.BRIGHT_BLUE}{'=' * width}{Colors.RESET}")
    lines.append(
        center_text(
            f"{Colors.DIM}For more info: https://github.com/marcosbtesh/crrcy.sh{Colors.RESET}"
        )
    )
    lines.append(f"{Colors.BOLD}{Colors.BRIGHT_BLUE}{'=' * width}{Colors.RESET}")

    return "\n".join(lines) + "\n"


def _format_x_axis(date_obj, duration_delta):
    days = duration_delta.days

    if days < 1:
        return date_obj.strftime("%H:%M")
    elif days > 60:
        return date_obj.strftime("%b %y")
    else:
        return date_obj.strftime("%d %b")


def _render_graph_footer(last_updated, start_date, end_date, min_val, max_val):
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
    min_val_col = f"Min: {min_val}"
    max_val_col = f"Max: {max_val}"

    line = f"{Colors.CYAN}{l_col:<{col_width}}{Colors.YELLOW}{m_col:^{col_width}}{Colors.CYAN}{r_col:>{col_width}}{Colors.RESET}"

    footer_lines.append(line)
    footer_lines.append("")
    footer_lines.append(center_text(f"{Colors.BOLD}crrcy.sh{Colors.RESET}"))

    return "\n".join(footer_lines)


def render_graph(data: dict, start_date, end_date):
    metadata = data.get("meta", {})
    last_updated = metadata.get("last_updated_at", "Unknown")

    series_data = data.get("data", {})

    if not series_data:
        return f"\n{Colors.RED}No data available to render graph.{Colors.RESET}\n"

    lines = []
    lines.append(render_header("PRICE HISTORY", f"{start_date} - {end_date}"))
    lines.append("")

    for target, target_data in series_data.items():
        points = []

        for date_str, info in target_data.items():
            try:
                val = (
                    info["value"]
                    if isinstance(info, dict) and "value" in info
                    else info
                )

                dt = datetime.strptime(date_str, "%Y-%m-%d")
                val = cast(Union[str, float, int], val)
                points.append((dt, float(val)))

            except (ValueError, TypeError):
                continue

        points.sort(key=lambda x: x[0])

        if not points or len(points) < 2:
            lines.append(f"{Colors.RED}Insufficient data for {target}.{Colors.RESET}")
            lines.append("")
            continue

        term_width = get_terminal_width()
        graph_height = 12
        y_axis_width = 12
        graph_width = term_width - y_axis_width - 2

        values = [p[1] for p in points]
        min_val = min(values)
        max_val = max(values)

        val_range = max_val - min_val if max_val != min_val else 1

        lines.append(f"{Colors.BOLD}{target} Rate Chart{Colors.RESET}")
        lines.append("")

        graph_rows = [[" " for _ in range(graph_width)] for _ in range(graph_height)]

        y_positions = []
        for col in range(graph_width):
            idx = (col / graph_width) * (len(points) - 1)
            idx_low = int(idx)
            idx_high = min(idx_low + 1, len(points) - 1)

            if idx_low == idx_high:
                val = points[idx_low][1]
            else:
                frac = idx - idx_low
                val = points[idx_low][1] * (1 - frac) + points[idx_high][1] * frac

            normalized_h = (max_val - val) / val_range if val_range > 0 else 0
            row_exact = normalized_h * (graph_height - 1)
            y_positions.append(row_exact)

        for col in range(graph_width - 1):
            x1 = col
            y1 = y_positions[col]
            x2 = col + 1
            y2 = y_positions[col + 1]

            row1 = int(round(y1))
            row2 = int(round(y2))
            row1 = max(0, min(graph_height - 1, row1))
            row2 = max(0, min(graph_height - 1, row2))

            price_change = y2 - y1
            if price_change < -0.1:
                color = Colors.BRIGHT_GREEN
            elif price_change > 0.1:
                color = Colors.BRIGHT_RED
            else:
                color = Colors.BRIGHT_YELLOW

            if row1 == row2:
                graph_rows[row1][col] = f"{color}─{Colors.RESET}"
            elif row1 > row2:
                start_row = row2
                end_row = row1
                for r in range(start_row, end_row + 1):
                    if graph_rows[r][col] == " ":
                        graph_rows[r][col] = f"{color}│{Colors.RESET}"
            else:
                start_row = row1
                end_row = row2
                for r in range(start_row, end_row + 1):
                    if graph_rows[r][col] == " ":
                        graph_rows[r][col] = f"{color}│{Colors.RESET}"

        for row in range(graph_height):
            row_val = max_val - (row * (val_range / (graph_height - 1)))
            label = f"{Colors.WHITE}{row_val:10,.2f}{Colors.RESET} |"

            graph_line = ""
            for col in range(graph_width):
                graph_line += graph_rows[row][col]

            lines.append(label + graph_line)

        lines.append(" " * y_axis_width + "+" + "-" * graph_width)

        x_labels = []
        padding_len = y_axis_width + 1
        current_line_len = padding_len
        x_labels.append(" " * padding_len)

        num_labels = 5
        step = len(points) // num_labels if len(points) >= num_labels else 1
        duration = (
            end_date - start_date
            if isinstance(end_date, datetime) and isinstance(start_date, datetime)
            else timedelta(days=3)
        )

        for i in range(0, len(points), step):
            dt = points[i][0]
            label_str = _format_x_axis(dt, duration)

            target_pos = padding_len + int((i / len(points)) * graph_width)

            spaces_needed = target_pos - current_line_len

            if spaces_needed > 0:
                x_labels.append(" " * spaces_needed)
                x_labels.append(f"{Colors.DIM}{label_str}{Colors.RESET}")
                current_line_len += spaces_needed + len(label_str)

        lines.append("".join(x_labels))
        lines.append("")

    all_values = []
    for target, target_data in series_data.items():
        for date_str, info in target_data.items():
            try:
                if isinstance(info, dict) and "value" in info:
                    val = info["value"]
                else:
                    val = info
                if isinstance(val, (int, float)):
                    all_values.append(float(val))
            except (ValueError, TypeError):
                continue

    min_all = min(all_values) if all_values else 0
    max_all = max(all_values) if all_values else 0

    footer_lines = _render_graph_footer(
        last_updated, start_date, end_date, min_all, max_all
    )
    lines.append(footer_lines)

    return "\n".join(lines) + "\n"
