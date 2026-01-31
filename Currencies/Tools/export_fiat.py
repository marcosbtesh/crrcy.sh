import re


def extract_iso_codes(input_file, output_file):
    iso_codes = []

    with open(input_file, "r", encoding="utf-8") as f:
        for line in f:
            match = re.match(r"^([A-Z]{3})", line.strip())
            if match:
                iso_codes.append(match.group(1))


    unique_codes = sorted(list(set(iso_codes)))

    with open(output_file, "w", encoding="utf-8") as f:
        for code in unique_codes:
            f.write(f"{code}\n")

    print(
        f"Extraction complete. {len(unique_codes)} unique codes saved to {output_file}."
    )


if __name__ == "__main__":
    extract_iso_codes("currencies.txt", "fiat.txt")
