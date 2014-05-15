#include <OneWire.h>
#include <DallasTemperature.h>
#include "EmonLib.h"                   // Include Emon Library
#include <SPI.h>
#include <Ethernet.h>

EnergyMonitor emon1;                   // Create an instance

// Enter a MAC address and IP address for your controller below.
// The IP address will be dependent on your local network:
byte mac[] = { 0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED };
IPAddress ip(192,168,2,79);

// Initialize the Ethernet server library
// with the IP address and port you want to use 
// (port 80 is default for HTTP):
EthernetServer server(80);
//------------------------------------

// Data wire is plugged into port 2 on the Arduino
#define ONE_WIRE_BUS 7
#define TEMPERATURE_PRECISION 12

// Setup a oneWire instance to communicate with any OneWire devices (not just Maxim/Dallas temperature ICs)
OneWire oneWire(ONE_WIRE_BUS);

// Pass our oneWire reference to Dallas Temperature. 
DallasTemperature sensors(&oneWire);

int numberOfDevices; // Number of temperature devices found

int resetPin = 12;

DeviceAddress tempDeviceAddress; // We'll use this variable to store a found device address

void setup(void){
    digitalWrite(resetPin, HIGH);
    // Open serial communications and wait for port to open:
    Serial.begin(9600);

    // Current: input pin, calibration.
    emon1.current(1, 66.6);             

    // start the Ethernet connection and the server:
    Ethernet.begin(mac, ip);
    server.begin();
    Serial.print("server is at ");
    Serial.println(Ethernet.localIP());

    // start serial port
    Serial.println("Dallas Temperature IC Control Library Demo");
}


void loop(void){ 

/*******************************************************************
*                 Recording temperatures
********************************************************************/

    // Start up the Thermometers library
    sensors.begin();

    // Grab a count of devices on the wire
    numberOfDevices = sensors.getDeviceCount();

    // locate devices on the bus
    Serial.print("Locating devices...");
    Serial.print("Found ");
    Serial.print(numberOfDevices, DEC);
    Serial.println(" devices.");

    // report parasite power requirements
    Serial.print("Parasite power is: "); 
    if (sensors.isParasitePowerMode()) Serial.println("ON");
    else Serial.println("OFF");

    // Loop through each device, print out address
    for(int i=0;i<numberOfDevices; i++){
        // Search the wire for address
        if(sensors.getAddress(tempDeviceAddress, i)){
            Serial.print("Found device ");
            Serial.print(i, DEC);
            Serial.print(" with address: ");
            printAddressToSerial(tempDeviceAddress);
            Serial.println();

            Serial.print("Setting resolution to ");
            Serial.println(TEMPERATURE_PRECISION,DEC);

            // set the resolution to 9 bit (Each Dallas/Maxim device is capable of several different resolutions)
            sensors.setResolution(tempDeviceAddress, TEMPERATURE_PRECISION);

            Serial.print("Resolution actually set to: ");
            Serial.print(sensors.getResolution(tempDeviceAddress), DEC); 
            Serial.println();
        }else{
            Serial.print("Found ghost device at ");
            Serial.print(i, DEC);
            Serial.print(" but could not detect address. Check power and cabling");
        }
    }

    // call sensors.requestTemperatures() to issue a global temperature 
    // request to all devices on the bus
    Serial.print("Requesting temperatures...");
    sensors.requestTemperatures(); // Send the command to get temperatures
    Serial.println("DONE");
    Serial.print("Requesting current...");
    double Irms = emon1.calcIrms(1480);  // Calculate Irms only
    Serial.println("DONE");
    //String IrmsString = String(Irms);
    Serial.println(Irms);
  
    // Loop through each device, print out temperature data
    for(int i=0;i<numberOfDevices; i++){
        // Search the wire for address
        if(sensors.getAddress(tempDeviceAddress, i)){
            // Output the device ID
            Serial.print("Temperature for device ");
            printAddressToSerial(tempDeviceAddress);
            Serial.print(": ");
            // It responds almost immediately. Let's print out the data
            float tempC = sensors.getTempC(tempDeviceAddress);
            Serial.println(tempC);
        } 
    }
delay(100);
Serial.println(":");
Serial.println(":");
Serial.println(":");


/*******************************************************************
*                 Publishing temperatures
********************************************************************/

    // listen for incoming clients
    EthernetClient client = server.available();
    if (client) {
        Serial.println("new client");
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
                    // send a standard http response header
                    client.println("HTTP/1.1 200 OK");
                    client.println("Content-Type: text/json");
                    client.println("Connection: close");  // the connection will be closed after completion of the response
                    client.println();
                    client.print("{");
                    client.print("\"date\":0,"); 
                    client.print("\"c\":"); 
                    client.print(Irms);
                    client.print(",");

                    for(int i=0;i<numberOfDevices; i++){
                        // Search the wire for address
                        if(sensors.getAddress(tempDeviceAddress, i)){
                            client.print("\"");
                            printAddressToClient(tempDeviceAddress, client);
                            client.print("\":");
                            float tempC = sensors.getTempC(tempDeviceAddress);
                            client.print(tempC);

                            if(i<numberOfDevices-1){
                                client.print(",");
                            }
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
        Serial.println("client disonnected");
    }
}

