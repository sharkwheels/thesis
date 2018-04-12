#include "config.h"
#include <ESP8266WiFi.h>
#include <Arduino.h>
#include <SoftwareSerial.h>
#include <Wire.h>
#include <Esp.h>

#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <ArduinoJson.h>

#include <Adafruit_Thermal.h>
#include <elapsedMillis.h>


#define TX_PIN 14   // printer rx = blue / yellow
#define RX_PIN 12   // printer tx = green


SoftwareSerial pSerial(RX_PIN, TX_PIN); 
Adafruit_Thermal printer(&pSerial,13);

String timeStamp = "";
String newMsg = "";
String newMsg2 = "";
String newMsg3 = "";
String newMsg4 = "";
String greeting = "";

String oldTs = "";
String oldMsg = "";


bool isActive = false;
bool isConnected = false;
bool oneOffWarning = false;
bool systemSleep = false;

const long oneSecond = 1000; 					// a second is a thousand milliseconds
const long oneMinute = oneSecond * 60;			
const long oneHour   = oneMinute * 60;

// Time to sleep (in seconds):
const long sleepTimeS = oneMinute * 30; // sleep for 30 minutes

elapsedMillis timerRest;      
const long dataInterval = oneSecond * 5;   	// 5 second intervals for active polling
											// yes i know this brute force AF but for now its fine


void setup() {
	Serial.begin(115200);
	Serial.setDebugOutput(true);
	delay(100);
	pinMode(LED_BUILTIN, OUTPUT);

	// WIFI SETUP

	WiFi.mode(WIFI_STA);
	WiFi.begin(ssid, password);

	if (WiFi.waitForConnectResult() != WL_CONNECTED) {
	Serial.println("Failed");
	} else {
	Serial.println("WiFi connected");
	}

	Serial.print("\n\nIP Address: ");
	Serial.println(WiFi.localIP());
	Serial.print("Mask: ");
	Serial.println(WiFi.subnetMask());
	Serial.print("Gateway: ");
	Serial.println(WiFi.gatewayIP());
	Serial.print("DNS0: ");
	Serial.println(WiFi.dnsIP(0));
	Serial.print("DNS1: ");
	Serial.println(WiFi.dnsIP(1)); 
	Serial.print("DHCP Hostname: ");
	Serial.println(WiFi.hostname());
	Serial.print("AutoConnect: ");
	Serial.println(WiFi.getAutoConnect());
	Serial.print("SSID: ");
	Serial.println(WiFi.SSID());
	long rssi = WiFi.RSSI();
	Serial.print("Signal Strength (RSSI):");
	Serial.println(rssi);

	getData();
	oldTs = timeStamp;
	oldMsg = newMsg;

	pSerial.begin(9600); 
	printer.begin();  
	Serial.println("setup done");
	//printer.println("testing the printer");
  	printer.feed(2);

	timerRest = 0;
	isActive = false;
}

void loop() {

	/*
	if the timestamp is between 6pm and 9am
		set the systemSleepflag to true
			start a sleep cycle.
			sleep for 30 minutes.
				wake up
				connect to wifi
				grab the timestamp
					check timestamp.
					set newtimestamp as old timestamp
	else
		wake the sysetm, begin your 5 second poll
	*/

	if(!systemSleep){

		if (timerRest > dataInterval) {
	        timerRest -= dataInterval; 
	        getData();
	        int ledPin = digitalRead(LED_BUILTIN);
	        digitalWrite(LED_BUILTIN, !ledPin);
	    }
	    

		if(isConnected){

			if((newMsg != oldMsg) && newMsg !=""){
	    		isActive = true;
	    	}

			// if the message is new, print it.
	        if(isActive){
	        	Serial.println("live print");
				Serial.println(timeStamp);
				Serial.println(newMsg);
				
				printer.setSize('S');
				printer.justify('C');
				printer.println("*****************");
				printer.setDefault();
				printer.setSize('S');
				printer.boldOn();
				printer.println(timeStamp);
				printer.boldOff();
				printer.feed(1);
				printer.println(greeting);
				printer.feed(1);
				printer.println(newMsg);
				printer.feed(1);
				printer.println(newMsg2);
				printer.feed(1);
				printer.println(newMsg3);
				printer.feed(1);
				printer.println(newMsg4);
				printer.feed(1);
				printer.justify('C');
				printer.println("*****************");
				printer.feed(15);

	        	oldTs = timeStamp;
	        	oldMsg = newMsg;
	        	isActive = false;
	        }
	        
		}else{
			if(!oneOffWarning){
				Serial.println("Could not reach server. Restart Pi.");
			}
			oneOffWarning = true;
			digitalWrite(LED_BUILTIN, HIGH);
		}
	}else{
		//ESP.deepSleep(sleepTimeS,WAKE_RF_DEFAULT);
		// you can only sleep for 71 minutes.
	}
}

void getData(){
	if((WiFi.status() == WL_CONNECTED)) {
		HTTPClient http;
		//Serial.print("[HTTP] begin...\n");
    	http.begin(hostAddr); 
		//Serial.print("[HTTP] GET...\n");
		// start connection and send HTTP header
		int httpCode = http.GET();

		// httpCode will be negative on error
		if(httpCode > 0) {
			// HTTP header has been send and Server response header has been handled
			Serial.printf("[HTTP] GET... code: %d\n", httpCode);
			// file found at server
			if(httpCode == HTTP_CODE_OK) {
				isConnected = true;
				String payload = http.getString();
				parsePayload(payload);
			}else{
				isConnected = false;
			}
		} else {
			Serial.printf("[HTTP] GET... failed, error: %s\n", http.errorToString(httpCode).c_str());
			// do a default fortune. maybe have a few here it can choose from, like 3.
		}
		http.end();
	}
}

void parsePayload(String payload){
	
	if(payload){
		Serial.println("got payload");
		//Serial.println(payload);
	}
	
	DynamicJsonBuffer jsonBuffer;
	JsonObject& root = jsonBuffer.parseObject(payload);
	if (!root.success()) {
		Serial.println("parseObject() failed");
		return;
	}
	String ts = root["timestamp"];
  	String gs = root["greeting"];
	String messagePt1 = root["msg1"];
	String messagePt2 = root["msg2"];
	String messagePt3 = root["msg3"];
	String messagePt4 = root["msg4"];

	timeStamp = ts;
  	greeting = gs;
	newMsg = messagePt1;
	newMsg2 = messagePt2;
	newMsg3 = messagePt3;
	newMsg4 = messagePt4;	
}

/*
			printer.setSize('S');
			printer.justify('C');
			printer.println("*****************");
			printer.justify('L');
			printer.feed(1);
			printer.println(newMsg4);
			printer.feed(1);
			printer.println(newMsg3);
			printer.feed(1);
			printer.println(newMsg2);
			printer.println(1);
			printer.println(newMsg);
			printer.println(1);
			printer.println(greeting);
			printer.feed(1);
			printer.println(timeStamp);
			printer.justify('C');
			printer.println("*****************");
			printer.feed(12);
			printer.upsideDownOff();
			printer.setDefault(); // Restore printer to defaults*/

// original //////
			//printer.setSize('S');
			//printer.justify('C');
			//printer.println("*****************");
			//printer.setDefault();
			//printer.setSize('S');
			//printer.boldOn();
			//printer.println(timeStamp);
			//printer.boldOff();
			//printer.feed(1);
			//printer.println(greeting);
			//printer.println(1);
			//printer.println(newMsg);
			//printer.feed(1);
			//printer.println(newMsg2);
			//printer.feed(1);
			//printer.println(newMsg3);
			//printer.feed(1);
			//printer.println(newMsg4);
			//printer.feed(1);
			//printer.justify('C');
			//printer.println("*****************");
			//printer.feed(12);

			/*
			if((!printerTimerFired) && (printerTimer > printerPauseTime)){
				
            	Serial.println("stopping printer");
            	printerTimerFired = true;
            	Serial.println("setting to inactive");
            	
        	}*/
	/*

	if(isActive){
		// if the printer hasn't run
		
			if(!printerRan){
				Serial.println("live");
				Serial.println(timeStamp);
				Serial.println("printing");
				printer.setSize('S');
				printer.justify('C');
				printer.println("*****************");
				printer.setDefault();
				printer.setSize('S');
				printer.boldOn();
				printer.println(timeStamp);
				printer.boldOff();
				printer.feed(1);
				printer.println(greeting);
				printer.feed(1);
				printer.println(newMsg);
				printer.feed(1);
				printer.println(newMsg2);
				printer.feed(1);
				printer.println(newMsg3);
				printer.feed(1);
				printer.println(newMsg4);
				printer.feed(1);
				printer.justify('C');
				printer.println("*****************");
				printer.feed(12);
				printerRan = true;
				oldTs = timeStamp;
	            isActive = false; 
			}
		}
		
	}else{
		if (timerRest > dataInterval) {
            timerRest -= dataInterval; 
            getData();
            if((timeStamp != oldTs) && timeStamp != ""){
            	isActive = true;
            	printerRan = false;
            }        
        }
	}*/


  /*Serial.println("live");
				Serial.println(timeStamp);
				printer.setSize('S');
				printer.justify('C');
				printer.println("*****************");
				printer.setDefault();
				printer.setSize('S');
				printer.boldOn();
				printer.println(timeStamp);
				printer.boldOff();
				printer.feed(1);
				printer.println(greeting);
				printer.feed(1);
				printer.println(newMsg);
				printer.feed(1);
				printer.println(newMsg2);
				printer.feed(1);
				printer.println(newMsg3);
				printer.feed(1);
				printer.println(newMsg4);
				printer.feed(1);
				printer.justify('C');
				printer.println("*****************");
				printer.feed(12);*/	