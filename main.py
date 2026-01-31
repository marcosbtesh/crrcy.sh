import dotenv
from flask import Flask, jsonify, request, Response
from utils import is_curl_client, parse_list
import renderer
from crypto import Crypto
from fiat import Fiat

dotenv.load_dotenv()

app = Flask(__name__)

crypto = Crypto()
fiat = Fiat()


@app.route("/")
def _home_():
    if is_curl_client():
        return Response(
            renderer.render_header("CURRENCY API", "Welcome")
            + f"\n{renderer.Colors.GREEN}Available Endpoints:{renderer.Colors.RESET}\n"
            f"  /fiat    - Get Fiat Rates\n"
            f"  /crypto  - Get Crypto Prices\n\n"
            f"{renderer.Colors.DIM}Try: curl localhost:5000/fiat{renderer.Colors.RESET}\n",
            mimetype="text/plain",
        )

    return jsonify(
        {
            "status": "online",
            "endpoints": ["/fiat", "/crypto"],
            "usage": "Use query parameters to filter data.",
        }
    )


# --- FIAT ROUTE ---
@app.route("/fiat", methods=["GET"])
async def get_fiat():
    isos_param = request.args.get("isos")

    try:
        if isos_param:
            iso_list = parse_list(isos_param)
            data = await fiat.get_iso_rate(iso_list)
        else:
            data = await fiat.get_latest()

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


# --- CRYPTO ROUTE ---
@app.route("/crypto", methods=["GET"])
def get_crypto():
    coins_param = request.args.get("coins")
    vs_currency = request.args.get("vs", "usd")

    if not coins_param:
        error_msg = (
            "Missing required parameter: 'coins'. Example: ?coins=bitcoin,ethereum"
        )
        if is_curl_client():
            return Response(
                f"{renderer.Colors.RED}{error_msg}{renderer.Colors.RESET}\n", status=400
            )
        return jsonify({"error": error_msg}), 400

    try:
        coin_list = parse_list(coins_param)
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
