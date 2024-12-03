# Serial to parallel converter

## Hardware

An Arduino Nano will work.

## Software

See the source code of the Arduino sketch in `./arduino_sketch/arduino_sketch.ino`.

## Pinout

| Arduino pin  | MCU port-pin | Interface A functionality | Interface A pin | Other                                      |
|--------------|--------------|---------------------------|-----------------|--------------------------------------------|
| 0 / D0 / RXD | PD0          | N/A                       | N/A             | Serial connection to PC                    |
| 1 / D1 / TXD | PD1          | N/A                       | N/A             | Serial connection to PC                    |
| 2 / D2       | PD2          | Output 0                  | 6               |                                            |
| 3 / D3       | PD3          | Output 1                  | 8               |                                            |
| 4 / D4       | PD4          | Output 2                  | 10              |                                            |
| 5 / D5       | PD5          | Output 3                  | 12              |                                            |
| 6 / D6       | PD6          | Output 4                  | 14              |                                            |
| 7 / D7       | PD7          | Output 5                  | 16              |                                            |
| 8 / D8       | PB0          | Input 6                   | 18              |                                            |
| 9 / D9       | PB1          | Input 7                   | 20              |                                            |
| 10 / D10     | PB2          | N/A                       | N/A             | LED indicator for input 6 (optional)       |
| 11 / D11     | PB3          | N/A                       | N/A             | LED indicator for input 7 (optional)       |
| +5V          | N/A          | Opto-coupler supply       | 1+3             | Interface A power supply for opto-couplers |
| GND          | N/A          | Reference voltage         | 5, 7, ...       | Interface A GND reference voltage          |
