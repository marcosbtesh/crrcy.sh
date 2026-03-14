#include "config.h"
#include "LCDIC2.h"
#include <WiFi.h>
#include <esp_http_client.h>


LCDIC2 lcd(0x27, 16, 2);

// My Global Variables
char* SYMBOLS[] = {
    "USD", "EUR", "BTC", "ETH", "JPY", 
    "GBP", "USDT", "SOL", "AUD", "CAD", 
    "BNB", "CHF", "XRP"
};

char* SELECTED_SYMBOL = SYMBOLS[0]; 

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

 if (lcd.begin()) lcd.print("Hello, World!");

 pinMode(LED_GREEN_PIN, OUTPUT);
 pinMode(LED_YELLOW_PIN, OUTPUT);
 pinMode(LED_RED_PIN, OUTPUT);

 pinMode(BUTTON_PIN, INPUT_PULLDOWN);

}

void loop() {
   for (uint8_t i = 0; i < 15; i++) {
    lcd.setCursor(i, 1);
    delay(250);
  }
  for (uint8_t i = 15; i > 0; i--) {
    lcd.setCursor(i, 1);
    delay(250);
  }

}

void refresh_prices() {



}


void getSymbolPrice() {


}

void handleRequest(char endpoint, esp_http_client_method_t method) {

  if(WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi is not connected!")
    return;
  }


  HTTPClient http;

  char route = API_ENDPOINT + endpoint;

  http.begin(route);
  

  int response = http.method();

  if(response > 0) {
    Serial.print("HTTP Response Code: ");
    Serial.println(response);
    
  }





}




