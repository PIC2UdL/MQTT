//Libraries:
//Import the libraries of...
//Wifi-->
#include <ESP8266WiFi.h>
#include <ESP8266WiFiMulti.h>

//MQTT-->
#include <PubSubClient.h>
//defines of id mqtt and topics for publish and subscribe
#define FLOW_PUBLISH   "/sensor/FlowSensor"
#define Relay_SUBSCRIBE   "/sensor/Relay"   //topic MQTT to receive information from the Broker(Raspberry Pi)
#define ID_MQTT  "Anderson"

#define MAX_DELAY 5

//Variables and Global objects:
//Wifi-->
const char* SSID2 = "fameno-iot";   //Put here the SSID / name of the WI-FI that you want to connect
const char* PASSWORD2 = "provaprova"; //Put here the password of the WI-FI that you want to connect

const char* SSID1 = "HUAWEI-eA260-E42A";
const char* PASSWORD1 = "GdmYn8A0GHYB4Ad";

const char* SSID = "WLAN_91";
const char* PASSWORD = "Z001349ECBA90";

ESP8266WiFiMulti WiFiMulti;

//Flow-->
float count = 0.0; // variable to store the “rise ups” from the flowmeter pulses
int seconds = 0;
float lastvalue = 0;
const int Flow = 4; // variable for D2 pin

//Relay-->
const int Relay = D1;


//MQTT-->
WiFiClient espClient; // Create the object espClient
PubSubClient MQTT(espClient); // Instance the Cliente MQTT passing the object espClient

const char* BROKER_MQTT = "192.168.1.14"; //URL do broker MQTT that you want to user
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

//Flow-->
void getAmountOfBeer();
void SendFlowmeter(void);

//MQTT-->
void initMQTT();
void reconnectMQTT();
void mqtt_callback(char* topic, byte* payload, unsigned int length);

void setup() {
  InitOutputs();
  initSerial();
  initWiFi();
  initMQTT();
}

void loop() {
  //keep-alive the comunication with the Broker MQTT
  if (!MQTT.loop()) { //false - the client is no longer connected
    VerificaConexoesWiFIEMQTT();
  }
  checkTemps();
  if (digitalRead(Flow) == HIGH) {         // check if the input is HIGH (button released)
    getAmountOfBeer();
  }
  delay(10);
}

//Functions:
//Function: Inicialize the outputs and inputs
//Parameters: nothing
//Retorn: nothing
void InitOutputs(void)
{
  //Relay-->
  pinMode(Relay, OUTPUT);
  digitalWrite(Relay, 0);

  //Flow-->
  pinMode(Flow, INPUT);
}

//Function: Inicialize the Serial
//Parameters: nothing
//Retorn: nothing
void initSerial()
{
  Serial.begin(115200);
}

//Function: Inicialize and connect on the WI-FI
//Parameters: nothing
//Retorn: nothing
void initWiFi()
{
  Serial.println("------Conection WI-FI with NodeMCU -----");
  Serial.print("Connecting on WI-FI: ");
  Serial.println(SSID);
  Serial.println(SSID1);
  Serial.println(SSID2);
  // We start by connecting to a WiFi network
  WiFi.mode(WIFI_STA);
  WiFiMulti.addAP(SSID, PASSWORD);
  WiFiMulti.addAP(SSID1, PASSWORD1);
  WiFiMulti.addAP(SSID2, PASSWORD2);

  checkWiFi();
}

//Function: reconnect to broker MQTT and WI-FI
//Parameters: nothing
//Retorn: nothing
void VerificaConexoesWiFIEMQTT(void)
{
  checkMQTT();
  checkWiFi(); //reconnect on WI-Fi
}

//Function: check WiFi
//Parameters: nothing
//Retorn: nothing
void checkWiFi()
{
  if (WiFiMulti.run() != WL_CONNECTED)
    reconectWiFi();
}

//Function: reconnect to WiFi
//Parameters: nothing
//Retorn: nothing
void reconectWiFi()
{
  Serial.print("Wait for WiFi...");

  while (WiFiMulti.run() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("WiFi connected");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
}
//Function: check MQTT
//Parameters: nothing
//Retorn: nothing
void checkMQTT()
{
  if (!MQTT.connected())
    reconnectMQTT(); //reconnect with the broker
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

//Function: Inicialize parameters of connetion MQTT
//Parameters: nothing
//Retorn: nothing
void initMQTT()
{
  MQTT.setServer(BROKER_MQTT, BROKER_PORT);
  MQTT.setCallback(mqtt_callback);
}

//Function: function callback
//        this funtion will be called everytime that one information come from the broker
//Parameters: nothing
//Retorn: nothing
void mqtt_callback(char* topic, byte* payload, unsigned int length)
{
  String msg;

  //Get the string of payload received
  for (int i = 0; i < length; i++)
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

//Function: Get the amount of beer
//Parameters: nothing
//Retorn: nothing
void getAmountOfBeer()
{
  count += 1;
  seconds = 0;
  Serial.print("Click ");
  Serial.println(count);

}
void checkTemps() {
  if (seconds > MAX_DELAY && count > 0) {
    SendFlowmeter();
  }

  seconds += 1;
}

//Function: Send to Raspberry Pi the Flow value
//Parameters: nothing
//Retorn: nothing
void SendFlowmeter(void)
{
  static char value[7];
  //double to string format, 6 cifras, 2 decimales
  dtostrf(count, 6, 2, value);
  MQTT.publish("/sensor/FlowSensor", value);
  Serial.print("- Flow value ");
  Serial.print(value);
  Serial.println(" sent to Raspberry(Broker)");
  count = 0;
}

