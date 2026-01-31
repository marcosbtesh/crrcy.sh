import dotenv
from flask import Flask, jsonify, request, Response
import renderer
from currency import Currency

dotenv.load_dotenv()

app = Flask(__name__)
currency_service = Currency()


def is_curl_client():
    user_agent = request.headers.get("User-Agent", "").lower()
    return "curl" in user_agent


def parse_path_args(arg_str):
    if not arg_str:
        return []
    return [x.strip() for x in arg_str.replace(",", "+").split("+") if x.strip()]


@app.route("/", defaults={"query": "latest"})
@app.route("/<path:query>")
async def get_rates(query):
    parts = query.split("/")

    if len(parts) > 1:
        base_currency = parts[0].upper()
        requested_symbols = parse_path_args(parts[1])
    else:
        base_currency = "USD"
        requested_symbols = parse_path_args(parts[0])

    try:
        if not requested_symbols or "LATEST" in [s.upper() for s in requested_symbols]:
            data = await currency_service.get_rates(base=base_currency)
        else:
            data = await currency_service.get_rates(
                symbols=requested_symbols, base=base_currency
            )

        if is_curl_client():
            output = renderer.render_fiat_table(data)
            return Response(output, mimetype="text/plain")

        return jsonify({"data": data})

    except Exception as e:
        if is_curl_client():
            return Response(
                f"{renderer.Colors.RED}Error: {str(e)}{renderer.Colors.RESET}\n",
                status=500,
            )
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
