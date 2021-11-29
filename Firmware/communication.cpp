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

#include "communication.h"
void HandleMsg(char msg[], int len)
{
  char error = 0x00;
  char answer[32] = {0};
  char command = msg[0];
  
  if (TecolabData.temperatureStatus == TSTATUS_OVERHEATED)
    error |= ERROROVERHEATED;
  
  switch (command)
  {
    case 'R': // Read operation
    {
      char addr = msg[1], qty = min(msg[2], MAXQTYBYTES), checksum = msg[3];

      if (isChecksumCorrect(msg, 3, checksum)) // Correct checksum
      {
        unsigned int i;
        
        answer[0] = error;
        for (i = 0; i < qty; i++)
        {
          answer[1+i] = getValue(addr+i);
        }
        answer[1+i] = ComputeChecksum(answer, 1+i);
        TecolabData.lastCommunicationTime = millis();
        TecolabData.connectionStatus = CSTATUS_CONNECTED;
        Serial.write(answer, qty+2);
      }
      break;
    }
    case 'W': // Write operation
    {
      char addr = msg[1], qty = min(msg[2], MAXQTYBYTES), checksum = msg[3+qty];
      if (isChecksumCorrect(msg, 3+qty, checksum)) // Correct checksum
      {
        unsigned int i;

        answer[0] = error;
        answer[1] = error;
        for (i = 0; i < qty; i++)
        {
          setValue(addr+i, msg[3+i]);
        }
        TecolabData.lastCommunicationTime = millis();
        TecolabData.connectionStatus = CSTATUS_CONNECTED;
        Serial.write(answer, 2);
      }
      break;
    }
    case 'C': // Control operation (write PWMs and read temperatures)
    {
      char PWMH1 = msg[1], PWMH2 = msg[2], PWMC = msg[3], checksum = msg[4];

      if (isChecksumCorrect(msg, 4, checksum)) // Correct checksum
      {
        setValue(HEATER1PWM_ADDR, PWMH1);
        setValue(HEATER2PWM_ADDR, PWMH2);
        setValue(COOLERPWM_ADDR, PWMC);
        answer[0] = error;
        answer[1] = getValue(ROOMTEMP_LB_ADDR);
        answer[2] = getValue(ROOMTEMP_HB_ADDR);
        answer[3] = getValue(HEATER1TEMP_LB_ADDR);
        answer[4] = getValue(HEATER1TEMP_HB_ADDR);
        answer[5] = getValue(HEATER2TEMP_LB_ADDR);
        answer[6] = getValue(HEATER2TEMP_HB_ADDR);
        answer[7] = ComputeChecksum(answer, 7);
        TecolabData.lastCommunicationTime = millis();
        TecolabData.connectionStatus = CSTATUS_CONNECTED;
        Serial.write(answer, 8);
      }
      break;
    }
    case 'A': // Aknowledge (i.e. echo)
    {
      char checksum = msg[1];
      if (isChecksumCorrect(msg, 1, checksum)) // Correct checksum
      {
        answer[0] = 'A';
        answer[1] = 'A';
        TecolabData.lastCommunicationTime = millis();
        TecolabData.connectionStatus = CSTATUS_CONNECTED;
        Serial.write(answer, 2);
      }
      break;
    }
    default: // Unknown command
      error |= UNKNOWNCOMMAND;
      answer[0] = error;
      answer[1] = error; // It is its own checksum
      Serial.write(answer, 2);
      break;
  }
}

char ComputeChecksum(char msg[], int len)
{
  byte checksum = 0x00;
  
  for (int i = 0; i < len; i++)
    checksum += msg[i];
  return checksum;
}

bool isChecksumCorrect(char msg[], int len, char checksum)
{
  if (ComputeChecksum(msg, len) == checksum) // Correct checksum
    return true;
  return false;
}
