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

#ifndef TECOLAB_H
#define TECOLAB_H

/* Libraries */
#include <Arduino.h>
#include <OneWire.h> 
#include <DallasTemperature.h>

/* Pins Definitions */
#define LEDRED_PIN 							2
#define COOLER_PIN 							3
#define LEDGREEN_PIN 						4
#define HEATER1_PIN 						5
#define HEATER2_PIN 						6
#define ROOMTEMPSENSOR_PIN			7
#define HEATER1TEMPSENSOR_PIN		9
#define HEATER2TEMPSENSOR_PIN		8

/* Addresses Definitions */
#define ROOMTEMP_LB_ADDR        0x00
#define ROOMTEMP_HB_ADDR        0x01
#define HEATER1TEMP_LB_ADDR     0x02
#define HEATER1TEMP_HB_ADDR     0x03
#define HEATER2TEMP_LB_ADDR     0x04
#define HEATER2TEMP_HB_ADDR     0x05
#define HEATER1PWM_ADDR         0x06
#define HEATER2PWM_ADDR         0x07
#define COOLERPWM_ADDR          0x08

/* Configurations */
#define BLINK_TIME 							250   // milliseconds
#define CONNECTION_TIME 				2000  // milliseconds
#define SENSORRESOLUTION 				9     // number of bits  
#define TEMPERATURECONVTIME  		100   // milliseconds (it depends on the resolution)
#define OVERHEATTEMPERATURE     100   // degrees Celsius
#define HIGHTEMPERATURE         50    // degrees Celsius

/* Status Definitions */
#define TSTATUS_LOWTEMP         0
#define TSTATUS_HIGHTEMP        1
#define TSTATUS_OVERHEATED      2
#define CSTATUS_WAITING					0
#define CSTATUS_CONNECTED				1

/* TeCoLab data struct */
struct TecolabDataStruct
{
	short roomTemp;
	short heater1Temp;
	short heater2Temp;
	byte heater1PWM;
	byte heater2PWM;
	byte coolerPWM;
	byte connectionStatus;
  byte temperatureStatus;
	unsigned long lastConversionTime;
	unsigned long lastCommunicationTime;
};

/* TeCoLab functions */
void GetTemperatures(void);
void HardwareControl(void);
void CheckSerial(void);
byte getValue(byte);
void setValue(byte, byte);

/* External variables */
extern TecolabDataStruct TecolabData;
extern OneWire roomTemperatureSensorBus;
extern OneWire heater1TemperatureSensorBus;
extern OneWire heater2TemperatureSensorBus;
extern DallasTemperature roomTempSensor;
extern DallasTemperature heater1TempSensor;
extern DallasTemperature heater2TempSensor;

#endif
