// function to print a device address
void printAddressToSerial(DeviceAddress deviceAddress)
{
  for (uint8_t i = 0; i < 8; i++)
  {
    if (deviceAddress[i] < 16) Serial.print("0");
    Serial.print(deviceAddress[i], HEX);
  }
}

void printAddressToClient(DeviceAddress deviceAddress, EthernetClient &client)
{
  for (uint8_t i = 0; i < 8; i++)
  {
    if (deviceAddress[i] < 16) client.print("0");
    client.print(deviceAddress[i], HEX);
  }
}
