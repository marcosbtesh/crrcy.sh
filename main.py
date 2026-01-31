import dotenv
from flask import Flask, jsonify, request

from crypto import Crypto
from fiat import Fiat

dotenv.load_dotenv()

app = Flask(__name__)

crypto = Crypto()
fiat = Fiat()


def parse_list(param_str):
    if not param_str:
        return []
    return [x.strip() for x in param_str.split(",")]


@app.route("/")
def _home_():
    return jsonify(
        {
            "status": "online",
            "endpoints": ["/fiat", "/crypto"],
            "usage": "Use query parameters to filter data.",
        }
    )


@app.route("/fiat", methods=["GET"])
async def get_fiat():
    """
    Retrieves Fiat currency rates.

    Curl Examples:
      1. Get all latest rates:
         curl "http://localhost:5000/fiat"

      2. Get specific ISOs:
         curl "http://localhost:5000/fiat?isos=USD,EUR,GBP"

      3. (Future) Get Time Range:
         curl "http://localhost:5000/fiat?start_date=2023-01-01&end_date=2023-01-31"
    """
    isos_param = request.args.get("isos")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    if start_date or end_date:
        # TODO: Implement get_historical_rates(start_date, end_date) in fiat.py
        return (
            jsonify(
                {
                    "message": "Time range filtering is coming soon.",
                    "params_received": {"start": start_date, "end": end_date},
                }
            ),
            501,
        )

    try:
        if isos_param:
            iso_list = parse_list(isos_param)
            data = await fiat.get_iso_rate(iso_list)
        else:
            data = await fiat.get_latest()

        return jsonify({"data": data})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/crypto", methods=["GET"])
def get_crypto():
    """
    Retrieves Crypto currency prices.

    Curl Examples:
      1. Get prices for Bitcoin and Ethereum in USD:
         curl "http://localhost:5000/crypto?coins=bitcoin,ethereum"

      2. Change target currency (e.g., EUR):
         curl "http://localhost:5000/crypto?coins=solana&vs=eur"
    """
    coins_param = request.args.get("coins")
    vs_currency = request.args.get("vs", "usd")  # Default to USD
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    if not coins_param:
        return (
            jsonify(
                {
                    "error": "Missing required parameter: 'coins'. Example: ?coins=bitcoin,ethereum"
                }
            ),
            400,
        )

    if start_date or end_date:
        return (
            jsonify(
                {
                    "message": "Historical crypto data coming soon.",
                    "params_received": {"start": start_date, "end": end_date},
                }
            ),
            501,
        )

    try:
        coin_list = parse_list(coins_param)

        data = crypto.get_prices(coins=coin_list, vs_currency=vs_currency)

        return jsonify({"data": data})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
