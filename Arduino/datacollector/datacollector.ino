#include <OneWire.h>
#include <DallasTemperature.h>
#include "EmonLib.h"                   // Include Emon Library
#include <SPI.h>
#include <Ethernet.h>
#include <string.h>

EnergyMonitor emon1;                   // Create an instance

/*******************************************************************
*                 Server Configuration
********************************************************************/
byte mac[] = { 0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED };
IPAddress ip(192,168,2,68);
EthernetServer server(80);


#define bufferMax 128
int bufferSize;
char buffer[bufferMax];

//-- Commands and parameters (sent by browser) --
char cmd[15];    
char param1[15];

/*******************************************************************
*                 Thermometers Configuration
********************************************************************/
#define ONE_WIRE_BUS_1 6
#define ONE_WIRE_BUS_2 7
#define TEMPERATURE_PRECISION 12

OneWire oneWire1(ONE_WIRE_BUS_1);
OneWire oneWire2(ONE_WIRE_BUS_2);

DallasTemperature sensors1(&oneWire1);
DallasTemperature sensors2(&oneWire2);

int numberOfDevices1; // Number of temperature devices found
int numberOfDevices2;

DeviceAddress tempDeviceAddress; // We'll use this variable to store a found device address

/*******************************************************************
*                 Current sensor Configuration
********************************************************************/
#define CURRENT_SENSOR_PIN 1


/*******************************************************************
*                    Setup
********************************************************************/
void setup(void){
    Serial.begin(9600);

    // Current: input pin, calibration.
    emon1.current(CURRENT_SENSOR_PIN, 66.6);             

    // start the Ethernet connection and the server:
    Ethernet.begin(mac, ip);
    server.begin();
    Serial.print("server is at ");
    Serial.println(Ethernet.localIP());

    // start serial port
    Serial.println("Hostel Automation Datacollector");
}

/*******************************************************************
*                    Main Loop
********************************************************************/

void loop(void){ 

/*******************************************************************
*                 Recording temperatures
********************************************************************/

      
     Serial.println("Loop 1");
    // Start up the Thermometers library
    sensors1.begin();
    sensors2.begin();
    Serial.println("Loop 2");  

    // Grab a count of devices on the wire
    numberOfDevices1 = sensors1.getDeviceCount();
    numberOfDevices2 = sensors2.getDeviceCount();
    Serial.println("Loop 3");

    // // locate devices on the bus
    Serial.print("Locating devices...");
    Serial.print("Found ");
    Serial.print(numberOfDevices1, DEC);
    Serial.print(" devices on pin ");
    Serial.println(ONE_WIRE_BUS_1, DEC);
    Serial.print("Found ");
    Serial.print(numberOfDevices2, DEC);
    Serial.print(" devices on pin ");
    Serial.println(ONE_WIRE_BUS_2, DEC);

    // // report parasite power requirements
    Serial.println("Parasite power is: "); 
    Serial.print("Bus 1: "); 
    if (sensors1.isParasitePowerMode()) Serial.println("ON");
    else Serial.println("OFF");
    Serial.print("Bus 2: "); 
    if (sensors2.isParasitePowerMode()) Serial.println("ON");
    else Serial.println("OFF");
    
    Serial.println("-- BUS 1 --");

    // // Loop through each device, print out address
    for(int i=0;i<numberOfDevices1; i++){
        // Search the wire for address
        if(sensors1.getAddress(tempDeviceAddress, i)){
            Serial.print("Found device ");
            Serial.print(i, DEC);
            Serial.print(" with address: ");
            printAddressToSerial(tempDeviceAddress);
            Serial.println();

            Serial.print("Setting resolution to ");
            Serial.println(TEMPERATURE_PRECISION,DEC);

            // set the resolution to 9 bit (Each Dallas/Maxim device is capable of several different resolutions)
            sensors1.setResolution(tempDeviceAddress, TEMPERATURE_PRECISION);

            Serial.print("Resolution actually set to: ");
            Serial.println(sensors1.getResolution(tempDeviceAddress), DEC); 
            
        }else{
            Serial.print("Found ghost device at ");
            Serial.print(i, DEC);
            Serial.print(" but could not detect address. Check power and cabling");
        }
    }
    
    Serial.println("-- BUS 2 --");

    // // Loop through each device, print out address
    for(int i=0;i<numberOfDevices2; i++){
        // Search the wire for address
        if(sensors2.getAddress(tempDeviceAddress, i)){
            Serial.print("Found device ");
            Serial.print(i, DEC);
            Serial.print(" with address: ");
            printAddressToSerial(tempDeviceAddress);
            Serial.println();

            Serial.print("Setting resolution to ");
            Serial.println(TEMPERATURE_PRECISION,DEC);

            // set the resolution to 9 bit (Each Dallas/Maxim device is capable of several different resolutions)
            sensors2.setResolution(tempDeviceAddress, TEMPERATURE_PRECISION);

            Serial.print("Resolution actually set to: ");
            Serial.println(sensors2.getResolution(tempDeviceAddress), DEC); 
        }else{
            Serial.print("Found ghost device at ");
            Serial.print(i, DEC);
            Serial.print(" but could not detect address. Check power and cabling");
        }
    }

    // call sensors.requestTemperatures() to issue a global temperature 
    // request to all devices on the bus
    Serial.print("Requesting temperatures...");
    sensors1.requestTemperatures(); // Send the command to get temperatures
    sensors2.requestTemperatures(); // Send the command to get temperatures
    Serial.println("DONE");
    Serial.print("Requesting current...");
    double Irms = emon1.calcIrms(1480);  // Calculate Irms only
    Serial.println("DONE");
    Serial.println(Irms);
  
    // Loop through each device, print out temperature data
    for(int i=0;i<numberOfDevices1; i++){
        // Search the wire for address
        if(sensors1.getAddress(tempDeviceAddress, i)){
            // Output the device ID
            Serial.print("Temperature for device ");
            printAddressToSerial(tempDeviceAddress);
            Serial.print(": ");
            // It responds almost immediately. Let's print out the data
            float tempC = sensors1.getTempC(tempDeviceAddress);
            Serial.println(tempC);
        } 
    }
    for(int i=0;i<numberOfDevices2; i++){
        // Search the wire for address
        if(sensors2.getAddress(tempDeviceAddress, i)){
            // Output the device ID
            Serial.print("Temperature for device ");
            printAddressToSerial(tempDeviceAddress);
            Serial.print(": ");
            // It responds almost immediately. Let's print out the data
            float tempC = sensors2.getTempC(tempDeviceAddress);
            Serial.println(tempC);
        } 
    }
    Serial.println("Loop 4");
delay(100);
// Serial.println(":");
// Serial.println(":");
// Serial.println(":");


/*******************************************************************
*                 Publishing temperatures
********************************************************************/

    EthernetClient client = server.available();
    if (client){
        Serial.println("Client connexion");
        WaitForRequest(client);
        server.println("HTTP/1.1 200 OK");
        server.println("Content-Type: text/json");
        server.println("Connection: close");  // the connection will be closed after completion of the response
        server.println();
        server.print("{");
        server.print("\"c"); 
        server.print(CURRENT_SENSOR_PIN); 
        server.print("\":"); 
        server.print(emon1.calcIrms(1480));
        server.print(",");

        for(int i=0;i<numberOfDevices1; i++){
            // Search the wire for address
            if(sensors1.getAddress(tempDeviceAddress, i)){
                server.print("\"");
                printAddressToClient(tempDeviceAddress);
                server.print("\":");
                float tempC = sensors1.getTempC(tempDeviceAddress);
                server.print(tempC);

                server.print(",");
                
            } 
        }

        for(int i=0;i<numberOfDevices2; i++){
            // Search the wire for address
            if(sensors2.getAddress(tempDeviceAddress, i)){
                server.print("\"");
                printAddressToClient(tempDeviceAddress);
                server.print("\":");
                float tempC = sensors2.getTempC(tempDeviceAddress);
                server.print(tempC);

                if(i<numberOfDevices2-1){
                    server.print(",");
                }
            } 
        }

    server.print("}");
    delay(1);
    client.stop();
    }
}

void WaitForRequest(EthernetClient client) // Sets buffer[] and bufferSize
{
  bufferSize = 0;
 
  while (client.connected()) {
    if (client.available()) {
      char c = client.read();
      if (c == '\n')
        break;
      else
        if (bufferSize < bufferMax)
          buffer[bufferSize++] = c;
        else
          break;
    }
  }
  
  PrintNumber("bufferSize", bufferSize);
}

void ParseReceivedRequest()
{
  Serial.println("in ParseReceivedRequest");
  Serial.println(buffer);
  
  //Received buffer contains "GET /cmd/param1/param2 HTTP/1.1".  Break it up.
  char* slash1;
  char* slash2;
  char* space2;
  
  slash1 = strstr(buffer, "/") + 1; // Look for first slash
  slash2 = strstr(slash1, "/") + 1; // second slash
  space2 = strstr(slash1, " ") + 1; // space after second slash (in case there is no third slash)
  if (slash2 > space2) slash2=slash1;

  PrintString("slash1",slash1);
  PrintString("slash2",slash2);
  PrintString("space2",space2);
  
  // strncpy does not automatically add terminating zero, but strncat does! So start with blank string and concatenate.
  cmd[0] = 0;
  param1[0] = 0;
  strncat(cmd, slash1, slash2-slash1-1);
  strncat(param1, slash2, space2-slash2-1);
  
  PrintString("cmd",cmd);
  PrintString("param1",param1);
}

void PerformRequestedCommands()
{
     if ( strcmp(cmd,"read") != 0 ) return;
     Serial.println("perform");
     int bus = param1[0] - '0';
     PrintNumber("bus", bus);
     int numberOfDevices;
     DallasTemperature *sensors;
     if(bus == 1){
         Serial.println("bus 1");
         numberOfDevices = numberOfDevices1;
         sensors = &sensors1;
     }else if(bus == 2){
         Serial.println("bus 2");
         numberOfDevices = numberOfDevices2;
         sensors = &sensors2;
     }else{
       return;
     }
  // send a standard http response header
    
}


void printAddressToSerial(DeviceAddress deviceAddress)
{
  for (uint8_t i = 0; i < 8; i++)
  {
    if (deviceAddress[i] < 16) Serial.print("0");
    Serial.print(deviceAddress[i], HEX);
  }
}

void printAddressToClient(DeviceAddress deviceAddress)
{
  for (uint8_t i = 0; i < 8; i++)
  {
    if (deviceAddress[i] < 16) server.print("0");
    server.print(deviceAddress[i], HEX);
  }
}

void PrintString(char* label, char* str)
{
  Serial.print(label);
  Serial.print("=");
  Serial.println(str);
}

void PrintNumber(char* label, int number)
{
  Serial.print(label);
  Serial.print("=");
  Serial.println(number, DEC);
}
