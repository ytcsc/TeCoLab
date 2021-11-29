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
//#include "communication.h"


TecolabDataStruct TecolabData;

OneWire roomTemperatureSensorBus(ROOMTEMPSENSOR_PIN);
OneWire heater1TemperatureSensorBus(HEATER1TEMPSENSOR_PIN);
OneWire heater2TemperatureSensorBus(HEATER2TEMPSENSOR_PIN);

DallasTemperature roomTempSensor(&roomTemperatureSensorBus);
DallasTemperature heater1TempSensor(&heater1TemperatureSensorBus);
DallasTemperature heater2TempSensor(&heater2TemperatureSensorBus);

void setup()
{
  Serial.begin(9600);
  Serial.setTimeout(3);
  while (Serial.available() > 0)
    Serial.read();
  
  roomTempSensor.begin();
  roomTempSensor.setResolution(SENSORRESOLUTION);
  roomTempSensor.setWaitForConversion(false);

  heater1TempSensor.begin();
  heater1TempSensor.setResolution(SENSORRESOLUTION);
  heater1TempSensor.setWaitForConversion(false);

  heater2TempSensor.begin();
  heater2TempSensor.setResolution(SENSORRESOLUTION);
  heater2TempSensor.setWaitForConversion(false);

  pinMode(LEDRED_PIN, OUTPUT);
  pinMode(COOLER_PIN, OUTPUT);
  pinMode(LEDGREEN_PIN, OUTPUT);
  pinMode(HEATER1_PIN, OUTPUT);
  pinMode(HEATER2_PIN, OUTPUT);

  digitalWrite(LEDRED_PIN, HIGH);
  digitalWrite(LEDGREEN_PIN, HIGH);
  delay(BLINK_TIME);
  digitalWrite(LEDRED_PIN, LOW);
  digitalWrite(LEDGREEN_PIN, LOW);
}

void loop()
{ 
  GetTemperatures();
  HardwareControl();
  CheckSerial();
}
