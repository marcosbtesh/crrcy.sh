import dotenv
from flask import Flask, jsonify, request, Response
import renderer
from crypto import Crypto
from fiat import Fiat

dotenv.load_dotenv()

app = Flask(__name__)

crypto = Crypto()
fiat = Fiat()


def is_curl_client():
    user_agent = request.headers.get("User-Agent", "").lower()
    return "curl" in user_agent


def parse_path_args(arg_str):
    if not arg_str:
        return []
    return [x.strip() for x in arg_str.replace(",", "+").split("+") if x.strip()]


@app.route("/")
def _home_():
    if is_curl_client():
        return Response(
            renderer.render_header("CRRCY.SH", "Welcome")
            + f"\n{renderer.Colors.GREEN}Available Endpoints:{renderer.Colors.RESET}\n"
            f"  /fiat/latest       - Get All Fiat Rates\n"
            f"  /fiat/usd+eur      - Get Specific Fiat Rates\n"
            f"  /crypto/btc+eth    - Get Crypto Prices\n\n"
            f"{renderer.Colors.DIM}Try: curl localhost:5001/fiat/latest{renderer.Colors.RESET}\n",
            mimetype="text/plain",
        )

    return jsonify(
        {
            "status": "online",
            "endpoints": ["/fiat", "/crypto"],
            "usage": "Use path arguments: /fiat/usd+eur",
        }
    )


@app.route("/fiat", defaults={"query": "latest"})
@app.route("/fiat/<path:query>")
async def get_fiat(query):
    try:
        if not query or query.lower() == "latest":
            data = await fiat.get_latest()
        else:
            iso_list = parse_path_args(query.upper())
            data = await fiat.get_iso_rate(iso_list)

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


@app.route("/crypto/<path:query>")
def get_crypto(query):
    vs_currency = request.args.get("vs", "usd")

    try:
        coin_list = parse_path_args(query.lower())
        data = crypto.get_prices(coins=coin_list, vs_currency=vs_currency)

        if is_curl_client():
            output = renderer.render_crypto_table(data)
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
