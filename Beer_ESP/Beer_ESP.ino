//Map_pins:
/*
 * #Relay D1
 * Flow D2
 * 
 * NFC:
 * 3.3V --> 3.3V
 * GND --> GND
 * MISO --> D6
 * MOSI --> D7
 * SCK --> D5
 * SDA -->D4
 */

//Libraries:
//Import the libraries of...
//Wifi-->
#include <ESP8266WiFi.h>
#include <ESP8266WiFiMulti.h>


//NFC-->
#include <Wire.h>
#include <MFRC522.h>
#include <SPI.h>

//MQTT-->
#include <PubSubClient.h> 


//defines:
//NFC-->
#define RST_PIN 20 // RST-PIN for RC522 - RFID - SPI - Module GPIO15 
#define SS_PIN  2  // SDA-PIN for RC522 - RFID - SPI - Module GPIO2
MFRC522 mfrc522(SS_PIN, RST_PIN);   // Create MFRC522 instance


//MQTT-->
//defines of id mqtt and topics for publish and subscribe
#define NFC_PUBLISH   "/sensor/NFCSensor"    //topic MQTT to send information to the Broker(Raspberry Pi)
#define FLOW_PUBLISH   "/sensor/FlowSensor"  
#define Relay_SUBSCRIBE   "/sensor/Relay"   //topic MQTT to receive information from the Broker(Raspberry Pi)
#define ID_MQTT  "Anderson"  

//Variables and Global objects:
//Wifi-->
const char* SSID = "fameno-iot";   //Put here the SSID / name of the WI-FI that you want to connect
const char* PASSWORD = "provaprova"; //Put here the password of the WI-FI that you want to connect

const char* SSID1 = "HUAWEI-eA260-E42A";
const char* PASSWORD1 = "GdmYn8A0GHYB4Ad";

ESP8266WiFiMulti WiFiMulti;


//NFC-->
String content= "";

//Flow-->
float count = 0.0; // variable to store the “rise ups” from the flowmeter pulses
float lastvalue = 0;
const int  Flow = D2; // variable for D2 pin

//Relay-->
const int Relay = D1;


//MQTT-->
WiFiClient espClient; // Create the object espClient
PubSubClient MQTT(espClient); // Instance the Cliente MQTT passing the object espClient

const char* BROKER_MQTT = "172.16.0.133"; //URL do broker MQTT that you want to user
int BROKER_PORT = 1883; // Port of Broker MQTT

//Relay-->
char* Relay_status = "OFF";


//Prototypes(Methods):
//Serial-->
void initSerial();
void InitOutputs(void);

//Wifi-->
void initWiFi();
void reconectWiFi();
void VerificaConexoesWiFIEMQTT(void); 

//NFC-->
void initNFC();
void getNFCard();
void SendNFCard(void);

//Flow-->
void getAmountOfBeer();
void initFlow();
void SendFlowmeter(void);

//MQTT-->
void initMQTT();
void reconnectMQTT();
void mqtt_callback(char* topic, byte* payload, unsigned int length);

void setup() {
  InitOutputs();
  initSerial();
  initWiFi();
  initNFC();
  initFlow();
  initMQTT();
}

//Function: Inicialize the Serial
//Parameters: nothing
//Retorn: nothing
void initSerial() 
{
    Serial.begin(115200); 
}

//Functions:
//Function: Inicialize the outputs and inputs
//Parameters: nothing
//Retorn: nothing
void InitOutputs(void)
{
  //Relay-->
  pinMode(Relay, OUTPUT);
  digitalWrite(Relay,0);

  //Flow-->
  pinMode(Flow, INPUT);
}

//Function: Inicialize and connect on the WI-FI
//Parameters: nothing
//Retorn: nothing
void initWiFi() 
{
    delay(10);
    Serial.println("------Conection WI-FI with NodeMCU -----");
    Serial.print("Connecting on WI-FI: ");
    Serial.println(SSID);
    Serial.println("Wait");
    
    reconectWiFi();
}

//Function: Inicialize parameters of NFC
//Parameters: nothing
//Retorn: nothing
void initNFC() 
{
  SPI.begin();           // Init SPI bus
  mfrc522.PCD_Init();    // Init MFRC522 
}

//Function: Inicialize parameters of Flowmeter
//Parameters: nothing
//Retorn: nothing
void initFlow()
{
  // Attach an interrupt to the ISR vector
  attachInterrupt(digitalPinToInterrupt(Flow), getAmountOfBeer, RISING);
}

//Function: Inicialize parameters of connetion MQTT
//Parameters: nothing
//Retorn: nothing
void initMQTT() 
{
    MQTT.setServer(BROKER_MQTT, BROKER_PORT);   
    MQTT.setCallback(mqtt_callback);            
}

//Function: reconnect to WiFi
//Parameters: nothing
//Retorn: nothing
void reconectWiFi() 
{
    // We start by connecting to a WiFi network
    WiFi.mode(WIFI_STA);
    WiFiMulti.addAP(SSID, PASSWORD);
    WiFiMulti.addAP(SSID1, PASSWORD1);
    Serial.println();
    Serial.println();
    Serial.print("Wait for WiFi... ");

    while(WiFiMulti.run() != WL_CONNECTED) {
        Serial.print(".");
        delay(500);
    }

    Serial.println("");
    Serial.println("WiFi connected");
    Serial.println("IP address: ");
    Serial.println(WiFi.localIP());

    delay(500);
}

//Function: reconnect to broker MQTT 
//Parameters: nothing
//Retorn: nothing
void reconnectMQTT() 
{
    while (!MQTT.connected()) 
    {
        Serial.print("* Trying connect to Broker MQTT: ");
        Serial.println(BROKER_MQTT);
        if (MQTT.connect(ID_MQTT)) 
        {
            Serial.println("Connected to broker MQTT!");
            MQTT.subscribe(Relay_SUBSCRIBE); 
        } 
        else 
        {
            Serial.println("Fail to reconnect with broker.");
            Serial.println("There will be another connection in 2s");
            delay(2000);
        }
    }
}
 
//Function: reconnect to broker MQTT and WI-FI 
//Parameters: nothing
//Retorn: nothing 
void VerificaConexoesWiFIEMQTT(void)
{
    if (!MQTT.connected()) 
        reconnectMQTT(); //reconnect with the broker
    
     reconectWiFi(); //reconnect on WI-Fi
}
 

//Function: function callback 
//        this funtion will be called everytime that one information come from the broker
//Parameters: nothing
//Retorn: nothing
void mqtt_callback(char* topic, byte* payload, unsigned int length) 
{
    String msg;
 
    //Get the string of payload received
    for(int i = 0; i < length; i++) 
    {
       char c = (char)payload[i];
       msg += c;
    }
  
    if (msg.equals("ON"))
    {
        digitalWrite(Relay, 1);
   
        Relay_status = "ON";
        delay(6000);
        Serial.println(Relay_status);
    }
 
    if (msg.equals("OFF"))
    {
        digitalWrite(Relay, 0);

        Serial.println(Relay_status);
        Relay_status = "OFF";
    }
}

//Function: Get the value of NFC card
//Parameters: nothing
//Retorn: nothing
void getNFCard()
{
  // Look for new cards
  if ( ! mfrc522.PICC_IsNewCardPresent()) {   
    delay(50);
    return;
  }
  // Select one of the cards
  if ( ! mfrc522.PICC_ReadCardSerial()) {   
    delay(50);
    return;
  }
  

  // Shows the card ID on the serial console
  for (byte i = 0; i < mfrc522.uid.size; i++) 
  {
     content.concat(String(mfrc522.uid.uidByte[i] < 0x10 ? " 0" : " "));
     content.concat(String(mfrc522.uid.uidByte[i], HEX));
  }

  Serial.println();
  content.toUpperCase();
  Serial.println("Cart read:" + content);

  SendNFCard();

}

//Function: Send to Raspberry Pi the NFC Card 
//Parameters: nothing
//Retorn: nothing
void SendNFCard(void)
{
    char text[512];
    content.toCharArray(text,511);
    MQTT.publish( "/sensor/NFCSensor",  ( const char*) text);
    Serial.println(text);
    Serial.println("- NFC Card sent to Raspberry(Server)");
    delay(1000);
}

//Function: Get the amount of beer by NFC 
//Parameters: nothing
//Retorn: nothing
void getAmountOfBeer()
{
  count += 1; 
  /*
    delay(3000);
    if (lastvalue == count){
      break;
   }
   lastvalue = count;
  */
  
  SendFlowmeter();
}

//Function: Send to Raspberry Pi the Flow value 
//Parameters: nothing
//Retorn: nothing
void SendFlowmeter(void)
{
    static char Flow[7];
    //double to string format, 6 cifras, 2 decimales
    dtostrf(count,6,2,Flow);
  
    MQTT.publish("/sensor/FlowSensor", Flow);
    Serial.println(Flow);
    Serial.println("- Flow value sent to Raspberry(Server)");
  }

void loop() {    
  //If need reconnect with the WI-FI and MQTT Broker
  VerificaConexoesWiFIEMQTT();

  //Get the NFC card and Flow
  getNFCard();  

  //keep-alive the comunication with the Broker MQTT
  MQTT.loop();
    
  //"Turn off" 

}
