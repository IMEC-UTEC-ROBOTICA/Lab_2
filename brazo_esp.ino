#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <Servo.h>

// Update these with values suitable for your network.
const char *ssid = "raul";
const char *password = "123456789";
const char *mqtt_server = "192.168.43.70";
WiFiClient espClient;
PubSubClient client(espClient);
unsigned long lastMsg = 0;
#define MSG_BUFFER_SIZE (50)
char msg[MSG_BUFFER_SIZE];
char orden[15];



Servo servo1;
Servo servo2;


int max_servo_1=2500;
int min_servo_1=500;
int max_servo_2=2500;
int min_servo_2=500;
int value = 0;
int ang_1_actual=0;
int ang_2_actual=0;
char mov_1_ok=0;
char mov_2_ok=0;

void setup_wifi()
{
    delay(10); // We start by connecting to a WiFi network
    Serial.println();
    Serial.print("Connecting to ");
    Serial.println(ssid);
    WiFi.mode(WIFI_STA);
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED)
    {
        delay(500);
        Serial.print(".");
    }
    randomSeed(micros());
    Serial.println("");
    Serial.println("WiFi connected");
    Serial.println("IP address: ");
    Serial.println(WiFi.localIP());
}
void responder();
void mover_servo_1(int angulo);
void mover_servo_2(int angulo);
int angulo_relativo_1(int angulo);
int angulo_relativo_2(int angulo);

void callback(char *topic, byte *payload, unsigned int length){
    Serial.print("Message arrived [");
    Serial.print(topic);
    Serial.print("] ");

    String valor_ang = String((char *)payload).substring(0, length);
    Serial.println(valor_ang);

    if (strcmp(topic, "q1") == 0)
    {
        // Lógica para manejar los comandos MQTT para controlar el brazo
        ang_1_actual = valor_ang.toInt();
        mover_servo_1(ang_1_actual);
        Serial.println(ang_1_actual);
    }

    if (strcmp(topic, "q2") == 0)
    {
        // Lógica para manejar los comandos MQTT para controlar el brazo
        ang_2_actual = valor_ang.toInt();
        mover_servo_2(ang_2_actual);
        Serial.println(ang_2_actual);
    }}

    void reconnect()
    { // Loop until we're reconnected
        while (!client.connected())
        {
            Serial.print("Attempting MQTT connection...");
            // Create a random client ID
            String clientId = "ESP8266Client-";
            clientId += String(random(0xffff), HEX);
            // Attempt to connect
            if (client.connect(clientId.c_str()))
            {
                Serial.println("connected");
                client.publish("prueba", "hello world"); // Once connected, publish an announcement...
                client.subscribe("q1");      
                client.subscribe("q2");        // ... and resubscribe
            }
            else
            {
                Serial.print("failed, rc=");
                Serial.print(client.state());
                Serial.println(" try again in 5 seconds");
                delay(5000); // Wait 5 seconds before retrying
            }
        }
    }
    void setup()
    {
        servo1.attach(0,min_servo_1,max_servo_1);//d3
        servo2.attach(2,min_servo_2,max_servo_2); //d4
        Serial.begin(115200);
        setup_wifi();
        client.setServer(mqtt_server, 1883);
        client.setCallback(callback);
    }
    void loop()
    {
        if (!client.connected())
        {
            reconnect();
        }
        client.loop();
        unsigned long now = millis();
        if (now - lastMsg > 2000)
        {
            lastMsg = now;
            ++value;
            snprintf(msg, MSG_BUFFER_SIZE, "hello world #%ld", value);
            // Serial.print("Publish message: "); Serial.println(msg);
            client.publish("outTopic", msg);
        }
    }
int angulo_relativo_1(int angulo){
    return angulo+90;
}

int angulo_relativo_2(int angulo){
    return 180-angulo;
}
void responder(){
    if(mov_1_ok==1 and mov_2_ok==1){
        client.publish("respuesta", "ok");
        mov_1_ok=0;
        mov_2_ok=0;
    }
    
}
void mover_servo_1(int angulo){
    angulo=angulo_relativo_1(angulo);

    Serial.println("en mover servo 1");
    servo1.write(angulo);
    Serial.println(angulo);
    ang_1_actual=angulo;
    mov_1_ok=1;
    responder();

}
void mover_servo_2(int angulo){
  angulo = angulo_relativo_2(angulo);
  Serial.println("en mover servo 2");
  servo2.write(angulo);
      Serial.println(angulo);
  
    ang_2_actual=angulo;
    mov_2_ok=1;
    responder();
}