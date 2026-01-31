def hex_to_ansi(hex_code):
    hex_code = hex_code.lstrip("#")
    r, g, b = tuple(int(hex_code[i : i + 2], 16) for i in (0, 2, 4))
    return f"\\033[38;2;{r};{g};{b}m"


print(f"ORANGE = \"{hex_to_ansi('#FFA500')}\"")
