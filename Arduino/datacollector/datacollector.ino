#include <OneWire.h>
#include <DallasTemperature.h>
#include <SPI.h>
#include <EmonLib.h> 
#include <Ethernet.h>

// Data wire is plugged into port 2 on the Arduino
#define NB_TERMO 5

#define TEMPERATURE_PRECISION 12

class Thermometers {
    int precision, pin;
    float lastTemp;
    String name;
    OneWire *oneWire;
    DallasTemperature *manager;
  public:
    Thermometers ();
    Thermometers (String,int,int);
    Thermometers (String,int);
    void requestTemp ();
    void retrieveTemp ();
    String getDescription ();
    String getName ();
    float getTemperature ();
    int getPin ();
    void start();
    void init(String,int,int);
};

Thermometers::Thermometers () {

}

Thermometers::Thermometers (String name_, int pin_) {
  init(name_, pin_, 12);
}

Thermometers::Thermometers (String name_, int pin_, int precision_) {
  init(name_, pin_, precision_);
}

float Thermometers::getTemperature () {
  return lastTemp;
}

int Thermometers::getPin () {
  return pin;
}

String Thermometers::getName () {
  return name;
}

void Thermometers::init (String name_, int pin_, int precision_) {
  name = name_;
  pin = pin_;
  precision = precision_;
  oneWire = new OneWire(pin);
  manager = new DallasTemperature(oneWire);
  manager->begin();
  manager->setResolution(precision);
}


void Thermometers::requestTemp() {
  manager->requestTemperatures();
}

void Thermometers::retrieveTemp () {
  DeviceAddress tempDeviceAddress; 
  if(manager->getAddress(tempDeviceAddress, 0)){
    lastTemp = manager->getTempC(tempDeviceAddress);
  } 
  
}

String Thermometers::getDescription() {
  return "Thermometer " + name + "\n" 
    + "  pin: "+pin+"\n"
    + "  resolution: "+manager->getResolution()+"\n"
    + "  parasite mode: "+manager->isParasitePowerMode()+"\n";
}

// Ethernet server init
byte mac[] = { 0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED };
IPAddress ip(192,168,2,77);
EthernetServer server(88);

Thermometers *t0;
Thermometers *t1;
Thermometers *t2;
Thermometers *t3;
Thermometers *t4;
EnergyMonitor emon1;

void setup(void)
{
  Serial.println("BEGIN");
  Serial.begin(9600); 
//  for(uint16_t i = 0; i < NB_TERMO; i++) {
//    thermometers[i] = (Thermometers *) malloc(sizeof(Thermometers));
//  } 
  
  t0 = new Thermometers("t0", 2, 12);
  t1 = new Thermometers("t1", 4, 12);
  t2 = new Thermometers("t1", 5, 12);
  t3 = new Thermometers("t1", 6, 12);
  t4 = new Thermometers("t1", 7, 12);
  //thermometers[2]->init("t2", 5, 12);
  //thermometers[3]->init("t3", 6, 12);
  //thermometers[4]->init("t4", 7, 12);

  
//  for(int i=0;i<NB_TERMO; i++){
//    Serial.println(thermometers[i]->getDescription());
//  }

  t0->getDescription();
  t1->getDescription();
  t2->getDescription();
  t3->getDescription();
  t4->getDescription();
  
  emon1.current(1, 66.6);             // Current: input pin, calibration.
  
  // start the Ethernet connection and the server:
  Ethernet.begin(mac, ip);
  server.begin();
}

void loop(void)
{ 
  Thermometers thermometers[NB_TERMO] = {*t0, *t1, *t2, *t3, *t4};
  Serial.println("Requesting temperatures...");
//  for(int i=0;i<NB_TERMO; i++){
//    thermometers[i]->requestTemp(); 
//  }
  for(int i=0;i<NB_TERMO; i++){
    thermometers[i].requestTemp(); 
  }
  delay(1000);
  Serial.println("DONE");
  
  Serial.print("Requesting current...");
  double Irms = emon1.calcIrms(1480);  // Calculate Irms only
  Serial.println("DONE");
  
  for(int i=0;i<NB_TERMO; i++){
    thermometers[i].retrieveTemp();
  }
  
  for(int i=0;i<NB_TERMO; i++){
    Serial.print("Temperature for device ");
    Serial.print(thermometers[i].getPin());
    Serial.print(": ");
    Serial.println(thermometers[i].getTemperature());
  }
  


  // listen for incoming clients
  EthernetClient client = server.available();
  if (client) {

    // an http request ends with a blank line
    boolean currentLineIsBlank = true;
    while (client.connected()) {
      if (client.available()) {
        char c = client.read();
        Serial.write(c);
        
        // if you've gotten to the end of the line (received a newline
        // character) and the line is blank, the http request has ended,
        // so you can send a reply
        if (c == '\n' && currentLineIsBlank) {
          
          printHeader(client);
          client.print("{");
          client.print("\"date\":0,"); 
          client.print("\"c\":"); 
          client.print(Irms);
          client.print(",");  
   
          for(int i=0;i<NB_TERMO; i++){
            client.print("\"");
            client.print(i,DEC);
            client.print("\":");
            float tempC = thermometers[i].getTemperature();
            client.print(tempC);
            if(i<NB_TERMO-1){
              client.print(",");
            }
          }       

          client.print("}");
          break;
        }
        if (c == '\n') {
          // you're starting a new line
          currentLineIsBlank = true;
        } 
        else if (c != '\r') {
          // you've gotten a character on the current line
          currentLineIsBlank = false;
        }
      }
    }
    // give the web browser time to receive the data
    delay(1);
    // close the connection:
    client.stop();
    //Serial.println("client disonnected");
//    if(nbConnexions > 240){
//      software_Reset();
//    }
  }
}

void printHeader(EthernetClient client){
// send a standard http response header
          client.println("HTTP/1.1 200 OK");
          client.println("Content-Type: text/json");
          client.println("Connection: close");  // the connection will be closed after completion of the response
          client.println();  
}




