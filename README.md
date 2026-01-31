# crrcy.sh

> Real-time Currency Exchange Rates & Historical Charts via Terminal

![Project Status](https://img.shields.io/badge/status-active-brightgreen)
![License](https://img.shields.io/badge/license-MIT-blue)

## 📺 Demo Video

[Watch Demo](./images/demo.mp4)

## 📖 Description

**crrcy.sh** is a lightweight, terminal-friendly currency exchange service that provides real-time rates for fiat and cryptocurrencies, along with beautiful historical price charts rendered directly in your terminal via curl.

Whether you're tracking forex rates, monitoring crypto prices, or analyzing historical trends—all from the comfort of your command line—crrcy.sh delivers fast, accurate data with stunning ASCII visualizations.

## 🎯 Features

- ✅ **Real-time currency exchange rates** - Instant access to current rates
- ✅ **150+ fiat currencies** - Comprehensive coverage of world currencies
- ✅ **Major cryptocurrencies** - BTC, ETH, XRP, and more
- ✅ **Historical data** - Track price movements over days, months, or years
- ✅ **ASCII charts** - Beautiful terminal-rendered graphs with color-coded trends
- ✅ **curl-friendly** - Designed for terminal workflows and scripting
- ✅ **Zero friction** - No authentication or rate limits for moderate use
- ✅ **Smart caching** - Redis-backed caching for performance

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/marcosbtesh/crrcy.sh.git
cd crrcy.sh

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys

# Start the server
python main.py
```

### Basic Usage

```bash
# Get latest rates
curl http://localhost:5001/

# Get current rates for specific currencies
curl http://localhost:5001/EUR/USD,GBP,JPY

# Get historical price chart (30 days)
curl http://localhost:5001/last/USD/BTC/30d

# Help menu
curl http://localhost:5001/usage
```

## 📚 API Endpoints

### 1. Get Latest Rates

**Endpoint:** `GET /latest`  
**Description:** Get latest exchange rates

```bash
curl http://localhost:5001/latest
```

**Response:**
```
═════════════════════════════════════════════════════════════════════════════════
                              CURRENCY RATES
                                Base: USD
═════════════════════════════════════════════════════════════════════════════════

                     CURRENCY              RATE
                     AED              3.6725
                     AFN             69.8500
                     ALL             92.5000
                     ...
```

**Screenshot:** [See latest rates example](./images/01-latest-rates.png)

---

### 2. Get Current Rates with Specific Base

**Endpoint:** `GET /{base}`  
**Description:** Get exchange rates from a specific base currency

```bash
curl http://localhost:5001/EUR
curl http://localhost:5001/BTC
```

**Parameters:**
- `base` - Base currency code (e.g., USD, EUR, BTC)

**Screenshot:** [See EUR rates example](./images/02-eur-rates.png)

---

### 3. Get Current Rates for Multiple Targets

**Endpoint:** `GET /{base}/{targets}`  
**Description:** Get current rates for one or multiple target currencies

```bash
curl http://localhost:5001/EUR/USD,GBP,JPY
curl http://localhost:5001/USD/BTC,ETH,XRP
```

**Parameters:**
- `base` - Base currency code
- `targets` - Comma-separated list of target currencies

**Screenshot:** [See multi-currency example](./images/03-multi-currency-rates.png)

---

### 4. Get Historical Price Chart

**Endpoint:** `GET /last/{base}/{target}/{time}`  
**Description:** Display historical price data as an ASCII chart in your terminal

```bash
curl http://localhost:5001/last/USD/BTC/30d
curl http://localhost:5001/last/USD/ETH/90d
curl http://localhost:5001/last/EUR/USD/1y
```

**Parameters:**
- `base` - Base currency
- `target` - Target currency or currencies (comma-separated)
- `time` - Time range:
  - `30d` → 30 days
  - `90d` → 90 days
  - `6m` → 6 months (180 days)
  - `1y` → 1 year (365 days)
  - Numeric values (e.g., `90`) also work

**Screenshot:** [See 30-day chart example](./images/04-historical-30d.png)

---

### 5. Get Historical Chart with Custom Step

**Endpoint:** `GET /last/{base}/{target}/{time}/{step}`  
**Description:** Get historical data with custom data point intervals

```bash
curl http://localhost:5001/last/USD/EUR/1y/10
curl http://localhost:5001/last/USD/BTC/90d/5
```

**Parameters:**
- `base` - Base currency
- `target` - Target currency or currencies
- `time` - Time range
- `step` - Data point interval (must be ≥ 1, max 365 points per request)

**Screenshot:** [See 1-year chart with step example](./images/05-historical-1y-step.png)

---

## 📋 Parameter Reference

### Base/Target Currencies

#### Common Fiat Currencies
```
USD - US Dollar
EUR - Euro
GBP - British Pound
JPY - Japanese Yen
CHF - Swiss Franc
CAD - Canadian Dollar
AUD - Australian Dollar
... and 150+ more
```

#### Popular Cryptocurrencies
```
BTC  - Bitcoin
ETH  - Ethereum
XRP  - Ripple
LTC  - Litecoin
ADA  - Cardano
SOL  - Solana
... and many more
```

### Time Format

- `Xd` - X days (e.g., `30d`, `7d`)
- `Xm` - X months (e.g., `6m`, `3m`)
- `Xy` - X years (e.g., `1y`, `2y`)
- `X` - Numeric days (e.g., `90`, `180`)

### Step Parameter

- **Default:** Auto-calculated to fit terminal width
- **Minimum:** 1
- **Maximum:** 365 data points per request
- **Purpose:** Control data point density in historical charts

## 🎨 Chart Features

- **Color-coded trends:**
  - 🟢 Green: Price moving up
  - 🔴 Red: Price moving down
  - 🟡 Yellow: Price relatively flat

- **Smooth curves** - Linear interpolation between data points
- **Automatic scaling** - Y-axis adjusts to data range
- **Time labels** - X-axis shows dates/times appropriate to range
- **Summary stats** - Min/max prices and date range in footer

## 💻 Examples

### Track Bitcoin for 30 Days
```bash
$ curl http://localhost:5001/last/USD/BTC/30d
```

**Screenshot:** [See BTC chart](./images/06-btc-30d-chart.png)

### Compare Multiple Cryptos
```bash
$ curl http://localhost:5001/last/USD/BTC,ETH/90d
```

**Screenshot:** [See multi-crypto comparison](./images/07-btc-eth-comparison.png)

### Long-term Currency Tracking
```bash
$ curl http://localhost:5001/last/EUR/USD,GBP/1y/10
```

**Screenshot:** [See EUR/USD/GBP 1-year chart](./images/08-eur-longterm.png)

### Quick Currency Check
```bash
$ curl http://localhost:5001/USD/EUR,GBP,JPY,CHF
```

**Screenshot:** [See quick currency check](./images/09-quick-check.png)

---

## 🛠️ Technical Stack

- **Framework:** Flask with async route handlers
- **Currency Data:** currencyapicom API
- **Caching:** Redis for performance
- **Language:** Python 3.8+
- **Terminal Rendering:** ANSI color codes + Unicode line drawing


## ⚙️ Configuration

Create a `.env` file in the project root:

```env
# Currency API Key (get from currencyapicom)
FIAT_FREE_CURRENCY_API_KEY=your_api_key_here

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Server Configuration
FLASK_ENV=production
FLASK_PORT=5001
```

## 🔐 API Limits

- **Data points:** Maximum 365 per request (enforced via step parameter)
- **Rate limiting:** Implemented via caching
- **No authentication:** Required for public use

## 📝 Usage Notes

- Data is cached to reduce API calls
- Historical data is permanently cached (no expiration)
- Current rates are cached for 24 hours
- Crypto rates are automatically inverted (showing base/crypto instead of crypto/base)

## 🐛 Troubleshooting

### "No data available"
- Check that the currency pair exists
- Try a shorter time range
- Verify API key is configured

### Slow responses
- Check Redis is running
- Verify API key credentials
- Clear cache if stale data suspected

## 🤝 Contributing

Contributions are welcome! Please feel free to:
- Report bugs
- Suggest features
- Submit pull requests

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

Created by [marcosbtesh](https://github.com/marcosbtesh)

## 🔗 Links

- [GitHub Repository](https://github.com/marcosbtesh/crrcy.sh)
- [Currency API](https://currencyapi.com)
- [Redis Documentation](https://redis.io)

---

**Built with ❤️ for the terminal**
