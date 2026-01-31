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

    col_width = width // 5

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
    print("Imlement render graph here")

    metadata = data.get("meta", {})
    last_updated = metadata.get("last_updated_at", "Unknown")

    raw_data = data.get("data", {})

    points = []

    for date_str, info in raw_data.items():
        try:
            val = info["value"] if isinstance(info, dict) and "value" in info else info

            dt = datetime.strptime(date_str, "%Y-%m-%d")
            val = cast(Union[str, float, int], val)
            points.append((dt, float(val)))

        except (ValueError, TypeError):
            continue

    points.sort(key=lambda x: x[0])

    if not points:
        return f"\n{Colors.RED}Insufficient data to render graph.{Colors.RESET}\n"

    term_width = get_terminal_width()
    graph_height = 12
    y_axis_width = 12
    graph_width = term_width - y_axis_width - 2

    values = [p[1] for p in points]
    min_val = min(values)
    max_val = max(values)

    val_range = max_val - min_val if max_val != min_val else 1

    lines = []
    lines.append(render_header("PRICE HISTORY", f"{start_date} - {end_date}"))
    lines.append("")

    for row in range(graph_height):

        row_val = max_val - (row * (val_range / (graph_height - 1)))

        label = f"{Colors.WHITE}{row_val:10,.2f}{Colors.RESET} |"
        line_chars = []

        for col in range(graph_width):
            idx = int((col / graph_width) * (len(points) - 1))
            point_val = points[idx][1]

            normalized_h = (max_val - point_val) / val_range
            point_row = int(normalized_h * (graph_height - 1))

            if point_row == row:
                line_chars.append(f"{Colors.BRIGHT_GREEN}*{Colors.RESET}")
            elif point_row > row:
                line_chars.append(" ")
            else:
                line_chars.append(" ")

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
        dt = points[1][0]
        label_str = _format_x_axis(dt, duration)

        target_pos = padding_len + int((i / len(points)) * graph_width)

        spaces_needed = target_pos - current_line_len

        if spaces_needed > 0:
            x_labels.append(" " * spaces_needed)
            x_labels.append(f"{Colors.DIM}{label_str}{Colors.RESET}")
            current_line_len += spaces_needed + len(label_str)

    lines.append("".join(x_labels))
    lines.append("")

    lines.append(
        _render_graph_footer(last_updated, start_date, end_date, min_val, max_val)
    )

    return "\n".join(lines) + "\n"
