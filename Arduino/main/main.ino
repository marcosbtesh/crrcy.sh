#include "config.h"

#include "LCDIC2.h"

#include <WiFi.h>

#include <float.h>

#include <HTTPClient.h>

#include <ArduinoJson.h>

#include <Keypad.h>

LCDIC2 lcd(0x27, 16, 2);

// My Global Variables
const char * SYMBOLS[] = {
  "ARS",
  "EUR",
  "BTC",
  "ETH",
  "JPY",
  "GBP",
  "USDT",
  "SOL",
  "AUD",
  "CAD",
  "BNB",
  "CHF",
  "XRP"
};
const char * SELECTED_SYMBOL = SYMBOLS[0];

const char * BASE_CURRENCY = "USD";

float current_min = 0.0;
float current_max = 0.0;
float current_price = 0.0;

// LED's 
const int LED_GREEN_PIN = 21;
const int LED_YELLOW_PIN = 22;
const int LED_RED_PIN = 23;

const float VARIATION_CHANGE_PERCENT = 0.2;

// BUTTON
const int BUTTON_PIN = 0; // change this 

// KEYPAD
const byte ROWS = 4; //four rows
const byte COLS = 4; //three columns

char keys[ROWS][COLS] = {
  {
    '1',
    '2',
    '3',
    '4'
  },
  {
    '5',
    '6',
    '7',
    '8'
  },
  {
    '9',
    'A',
    'B',
    'C'
  }, // A=10, B=11, C=12
  {
    'D',
    '<',
    '#',
    '>'
  } // D=13
};

byte rowPins[ROWS] = {
  5,
  4,
  3,
  2
}; //connect to the row pinouts of the keypad
byte colPins[COLS] = {
  8,
  7,
  6
}; //connect to the column pinouts of the keypad

Keypad keypad = Keypad(makeKeymap(keys), rowPins, colPins, ROWS, COLS);

// TIMEFRAME
const char * TIMEFRAME_PERIOD = "d"; // "d", "m" or "y"
int TIMEFRAME_VALUE = 7;

bool HISTORY_MODE = false;

void setup() {

  Serial.begin(115200);

  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  //  if (lcd.begin()) lcd.print("Hello, World!");

  pinMode(LED_GREEN_PIN, OUTPUT);
  pinMode(LED_YELLOW_PIN, OUTPUT);
  pinMode(LED_RED_PIN, OUTPUT);

  pinMode(BUTTON_PIN, INPUT_PULLDOWN);

}

void loop() {

  unsigned long current_millis = millis();

  char key = keypad.getKey();

  if (key) {
    handle_keypad_press(key);
  }

  if ((current_millis / 1000) % 2 == 0) {
    digitalWrite(LED_BUILTIN, HIGH);
  } else {
    digitalWrite(LED_BUILTIN, LOW);
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("WiFi connected!");
    // getSymbolPrice();
    getHistoricPrice();
    delay(5000);
  }

}

// Single Symbol Prices
void refresh_prices() {
  getSymbolPrice();
}

void getSymbolPrice() {
  handleRequest(SELECTED_SYMBOL);
}

JsonDocument handleRequest(const char * endpoint) {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi not connected");
    return {};
  }

  HTTPClient http;

  String url = String(API_ENDPOINT) + "/" + String(endpoint);

  http.begin(url);

  int httpResponseCode = http.GET();

  if (httpResponseCode > 0) {
    Serial.print("HTTP Response code: ");
    Serial.println(httpResponseCode);

    JsonDocument doc;
    DeserializationError error = deserializeJson(doc, http.getStream());

    if (!error) {
      current_price = doc["data"][endpoint];
      Serial.print("Symbol: ");
      Serial.print(endpoint);
      Serial.print(" | Price: ");
      Serial.println(current_price);

      return doc;

    } else {
      Serial.print("deserializeJson() failed: ");
      Serial.println(error.f_str());
    }
  } else {
    Serial.print("Error code: ");
    Serial.println(httpResponseCode);
  }

  http.end();

  return JsonDocument {};
}

// Historic Prices
void getHistoricPrice() {
  char endpoint[64];
  snprintf(endpoint, sizeof(endpoint), "hist/%s/%s/%s%d", BASE_CURRENCY, SELECTED_SYMBOL, TIMEFRAME_PERIOD, TIMEFRAME_VALUE);

  JsonDocument response = handleRequest(endpoint);

  if (response.isNull()) {
    Serial.println("Invalid JSON response");
    return;
  }

  float price_min = FLT_MAX;
  float price_max = -FLT_MAX;

  JsonObject prices = response["data"][SELECTED_SYMBOL];

  for (JsonPair kv: prices) {
    float value = kv.value()["value"];
    if (value < price_min) price_min = value;
    if (value > price_max) price_max = value;
  }

  Serial.print("Min: ");
  Serial.println(price_min);
  Serial.print("Max: ");
  Serial.println(price_max);

  current_min = price_min;
  current_max = price_max;
  handleLedsHistoricPrices(price_min, price_max);
}

void handleLedsHistoricPrices(float min, float max) {

  int change = _calculateChangeMinMax(min, max);

  if (change < -VARIATION_CHANGE_PERCENT) {
    digitalWrite(LED_GREEN_PIN, HIGH);
  } else if (change > VARIATION_CHANGE_PERCENT) {
    digitalWrite(LED_RED_PIN, HIGH);
  } else {
    digitalWrite(LED_YELLOW_PIN, HIGH);
  }

}

// Utility Methods
float _calculateChangeMinMax(float min, float max) {
  return ((max - min) / min) * 100.0;
}

// LCD
void render_lcd() {
  render_lcd_top();
  render_lcd_bottom();
}

void render_lcd_top() {
  lcd.clear();
  lcd.setCursor(0, 0);

  if (HISTORY_MODE == true) {
    // Historic mode: show symbol + timeframe range
    // e.g. "BTC 7d" or "ETH 3m"
    char top[17];
    snprintf(top, sizeof(top), "%-4s LAST %2d%s", SELECTED_SYMBOL, TIMEFRAME_VALUE, TIMEFRAME_PERIOD);
    lcd.print(top);
  } else {
    // Normal mode: just show symbol + base currency
    char top[17];
    snprintf(top, sizeof(top), "%-4s / %s", SELECTED_SYMBOL, BASE_CURRENCY);
    lcd.print(top);
  }
}

void render_lcd_bottom() {
  lcd.setCursor(0, 1);

  if (HISTORY_MODE == true) {
    // Historic mode: show min and max
    // e.g. "L:1200.5 H:1350.2"
    char bottom[17];
    snprintf(bottom, sizeof(bottom), "L:%-7.1f H:%.1f", current_min, current_max);
    lcd.print(bottom);
  } else {
    // Normal mode: show current price
    // e.g. "Price: 1285.30"
    char bottom[17];
    snprintf(bottom, sizeof(bottom), "Price:%-10.2f", current_price);
    lcd.print(bottom);
  }
}

// Keypad

void handle_keypad_press(char key) {
  if (key == '<') {
    handle_less_timeframe();
  } else if (key == '>') {
    handle_more_timeframe();
  } else if (key == '#') {
    handle_change_timeframe_interval();
  } else {
    int num;
    if (key >= '1' && key <= '9') num = key - '1';
    else if (key == 'A') num = 9;
    else if (key == 'B') num = 10;
    else if (key == 'C') num = 11;
    else if (key == 'D') num = 12;
    else return;
    SELECTED_SYMBOL = SYMBOLS[num];
  }
}

// Timeframes

void handle_less_timeframe() {
  TIMEFRAME_VALUE = TIMEFRAME_VALUE - 1;
}

void handle_more_timeframe() {
  TIMEFRAME_VALUE = TIMEFRAME_VALUE + 1;
}

void handle_change_timeframe_interval() {
  if (strcmp(TIMEFRAME_PERIOD, "d") == 0) {
    TIMEFRAME_PERIOD = "m";
  } else if (strcmp(TIMEFRAME_PERIOD, "m") == 0) {
    TIMEFRAME_PERIOD = "y";
  } else if (strcmp(TIMEFRAME_PERIOD, "y") == 0) {
    TIMEFRAME_PERIOD = "d";
  }
}
