/*
Copyright 2021 Leonardo Cabral

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
*/

#include "tecolab.h"
#include "communication.h"

void GetTemperatures()
{
  unsigned long currenttime = millis();
  unsigned long diftime = currenttime - TecolabData.lastConversionTime;
  double roomTemp, heater1Temp, heater2Temp;
  
  if (diftime >= TEMPERATURECONVTIME)
  {
    // Update conversion time
    TecolabData.lastConversionTime = currenttime;
    // Get sensor temperatures (float point variables)
    roomTemp = roomTempSensor.getTempCByIndex(0);
    heater1Temp = heater1TempSensor.getTempCByIndex(0);
    heater2Temp = heater2TempSensor.getTempCByIndex(0);
    // Convert the temperatures to byte variables
    TecolabData.roomTemp = (short)(100*roomTemp);
    TecolabData.heater1Temp = (short)(100*heater1Temp);
    TecolabData.heater2Temp = (short)(100*heater2Temp);
    // Request new temperatures
    roomTempSensor.requestTemperatures();
    heater1TempSensor.requestTemperatures();
    heater2TempSensor.requestTemperatures();
    // Check for overheating and high temperature
    if ((heater1Temp >= OVERHEATTEMPERATURE) || (heater2Temp >= OVERHEATTEMPERATURE))
      TecolabData.temperatureStatus = TSTATUS_OVERHEATED;
    if (((heater1Temp >= HIGHTEMPERATURE) || (heater2Temp >= HIGHTEMPERATURE)) && (TecolabData.temperatureStatus != TSTATUS_OVERHEATED))
      TecolabData.temperatureStatus = TSTATUS_HIGHTEMP;
    if (((heater1Temp < HIGHTEMPERATURE) || (heater2Temp < HIGHTEMPERATURE)) && (TecolabData.temperatureStatus != TSTATUS_OVERHEATED))
      TecolabData.temperatureStatus = TSTATUS_LOWTEMP;
  }
}

void HardwareControl()
{
  static unsigned long lastblink = 0;
  static bool blinkstatus = HIGH;
  unsigned long currenttime = millis();

  if (TecolabData.temperatureStatus == TSTATUS_OVERHEATED)
  {
    analogWrite(HEATER1_PIN, 0);
    analogWrite(HEATER2_PIN, 0);
    analogWrite(COOLER_PIN, 255);
  }
  else
  {
    analogWrite(HEATER1_PIN, TecolabData.heater1PWM);
    analogWrite(HEATER2_PIN, TecolabData.heater2PWM);
    analogWrite(COOLER_PIN, TecolabData.coolerPWM);
  }
  
  if (currenttime - lastblink >= BLINK_TIME)
  {
    lastblink = currenttime;
    blinkstatus = !blinkstatus;
  }
  switch (TecolabData.temperatureStatus)
  {
    case TSTATUS_OVERHEATED:
      if (digitalRead(LEDRED_PIN) != HIGH)
        digitalWrite(LEDRED_PIN, HIGH);
      break;
    case TSTATUS_HIGHTEMP:
      if (digitalRead(LEDRED_PIN) != blinkstatus)
        digitalWrite(LEDRED_PIN, blinkstatus);
      break;
    case TSTATUS_LOWTEMP:
      if (digitalRead(LEDRED_PIN) != LOW)
        digitalWrite(LEDRED_PIN, LOW);
      break;
  }
  switch (TecolabData.connectionStatus)
  {
    case CSTATUS_CONNECTED:
      if (digitalRead(LEDGREEN_PIN) != HIGH)
        digitalWrite(LEDGREEN_PIN, HIGH);
      break;
    case CSTATUS_WAITING:
      if (digitalRead(LEDGREEN_PIN) != blinkstatus)
        digitalWrite(LEDGREEN_PIN, blinkstatus);
      break;
  }
}

void CheckSerial()
{
  unsigned long currenttime = millis();
  char serialbytes[32] = {0};
  
  if (Serial.available() > 0)
  {
    Serial.readBytes(serialbytes, 32);
    HandleMsg(serialbytes, 32);
  }
  if (currenttime - TecolabData.lastCommunicationTime > CONNECTION_TIME)
  {
    TecolabData.connectionStatus = CSTATUS_WAITING;
  }
}

byte getValue(byte address)
{
  void *ptr = &TecolabData;
  byte *byteptr;
  if (address >= sizeof(TecolabData)) // Invalid address
    return 0;
  byteptr = (byte*)ptr + address;
  return (*byteptr);
}

void setValue(byte address, byte value)
{
  void *ptr = &TecolabData;
  byte *byteptr;
  if (address > sizeof(TecolabData)) // Invalid address
    return;
  byteptr = (byte*)ptr + address;
  *byteptr = value;
}
