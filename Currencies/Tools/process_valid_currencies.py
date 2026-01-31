import json


def process_currencies(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    crypto_list = []
    fiat_list = []

    for code, info in data.items():
        currency_type = info.get("type", "").lower()

        if currency_type == "crypto":
            crypto_list.append(code)
        elif currency_type == "fiat":
            fiat_list.append(code)

    crypto_list.sort()
    fiat_list.sort()

    with open("crypto.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(crypto_list))

    with open("fiat.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(fiat_list))

    print(
        f"Done! Created crypto_new.txt ({len(crypto_list)} items) and fiat_new.txt ({len(fiat_list)} items)."
    )


if __name__ == "__main__":
    process_currencies("currencies.json")
