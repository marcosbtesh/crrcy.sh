#include "config.h"
#include "LCDIC2.h"
#include <WiFi.h>
#include <HTTPClient.h> 
#include <ArduinoJson.h>

LCDIC2 lcd(0x27, 16, 2);

// My Global Variables
const char* SYMBOLS[] = {
    "USD", "EUR", "BTC", "ETH", "JPY", 
    "GBP", "USDT", "SOL", "AUD", "CAD", 
    "BNB", "CHF", "XRP"
};

const char* SELECTED_SYMBOL = SYMBOLS[0]; 

// LED's 
const int LED_GREEN_PIN = 21;
const int LED_YELLOW_PIN = 22;
const int LED_RED_PIN = 23;

// BUTTON
const int BUTTON_PIN = 5;

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

  if ((current_millis / 1000) % 2 == 0) {
    digitalWrite(LED_BUILTIN, HIGH);
  } else {
    digitalWrite(LED_BUILTIN, LOW);
  }

   getSymbolPrice();
  delay(10000000);



}

void refresh_prices() {


}


void getSymbolPrice() {

  handleRequest(SELECTED_SYMBOL);

}



void handleRequest(const char* endpoint) {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi not connected");
    return;
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
      float price = doc["price"]; 
      Serial.print("Symbol: ");
      Serial.print(endpoint);
      Serial.print(" | Price: ");
      Serial.println(price);
      
      
    } else {
      Serial.print("deserializeJson() failed: ");
      Serial.println(error.f_str());
    }
  } else {
    Serial.print("Error code: ");
    Serial.println(httpResponseCode);
  }

  http.end(); 
}



