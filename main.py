from datetime import datetime, timedelta

import dotenv
from flask import Flask, Response, jsonify, request

import renderer
from cache import check_rate_limit
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
    return [
        x.strip().upper() for x in arg_str.replace(",", "+").split("+") if x.strip()
    ]


def get_client_ip():
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.remote_addr


def check_request_rate_limit():
    client_ip = get_client_ip() or "unknown"

    rate_limit = check_rate_limit(
        ip_address=client_ip,
        max_requests=35,
        window_minutes=1,
        block_duration_minutes=60,
    )

    if not rate_limit["allowed"]:
        if is_curl_client():
            return Response(
                f"{renderer.Colors.RED}{rate_limit['message']}{renderer.Colors.RESET}\n",
                status=429,
            )
        return jsonify({"error": rate_limit["message"]}), 429

    return None


@app.route("/", defaults={"query": None})
@app.route("/<path:query>")
async def get_rates(query):

    rate_limit_response = check_request_rate_limit()
    if rate_limit_response:
        return rate_limit_response

    if query is None or query.lower() in ["usage", "help", "info"]:
        if is_curl_client():
            output = renderer.render_usage()
            return Response(output, mimetype="text/plain")
        return jsonify(
            {
                "message": "Use /usage endpoint to view help",
                "endpoints": {
                    "current_rates": "GET /",
                    "current_rates_with_base": "GET /{base}",
                    "current_rates_with_targets": "GET /{base}/{targets}",
                    "historical": "GET /last/{base}/{target}/{time}",
                    "historical_with_step": "GET /last/{base}/{target}/{time}/{step}",
                },
            }
        )

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


@app.route("/hist/<path:query>")
@app.route("/historical/<path:query>")
@app.route("/last/<path:query>")
async def get_historical_rates(query):

    rate_limit_response = check_request_rate_limit()
    if rate_limit_response:
        return rate_limit_response

    parts = query.split("/")
    if len(parts) < 3:
        return (
            jsonify(
                {
                    "error": "Invalid format. Use /last/base/target/time or /last/base/target/time/step"
                }
            ),
            400,
        )

    base = parts[0].upper()
    targets = parts[1].replace(",", "+").upper().split("+")
    time_str = parts[2].lower()

    days = 0
    if time_str.endswith("d"):
        days = int(time_str[:-1])
    elif time_str.endswith("m"):
        days = int(time_str[:-1]) * 30
    elif time_str.endswith("y"):
        days = int(time_str[:-1]) * 365
    else:
        try:
            days = int(time_str)
        except ValueError:
            return jsonify({"error": "Invalid time format"}), 400

    step = 1
    if days > 365:
        step = 30
    elif days > 90:
        step = 10
    elif days > 30:
        step = 1

    if len(parts) > 3:
        try:
            step = int(parts[3])
            if step <= 0:
                return jsonify({"error": "Step must be greater than 0"}), 400
        except (ValueError, IndexError):
            pass

    max_data_points = 365
    estimated_points = days // step if step > 0 else days
    if estimated_points > max_data_points:
        return (
            jsonify(
                {
                    "error": f"Requested data points ({estimated_points}) exceeds maximum ({max_data_points}). Increase step value or reduce time range"
                }
            ),
            400,
        )

    end_dt = datetime.now()
    start_dt = end_dt - timedelta(days=days)

    try:
        data = await currency_service.get_timeseries_data(
            base=base,
            targets=targets,
            start_date=start_dt,
            end_date=end_dt,
            step=step,
        )

        if is_curl_client():
            output = renderer.render_graph(
                data, start_dt.strftime("%Y-%m-%d"), end_dt.strftime("%Y-%m-%d")
            )
            return Response(output, mimetype="text/plain")

        return jsonify(data)

    except Exception as e:
        if is_curl_client():
            return Response(f"Error: {str(e)}\n", status=500)
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=False)
