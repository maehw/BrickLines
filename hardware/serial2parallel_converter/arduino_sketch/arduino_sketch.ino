// Original author: Toastie from eurobricks
// Modified by: maehw
//
// Serial Interface for TCLogo to 9750 parallel input/output
// Uses direct port manipulation: https://playground.arduino.cc/Learning/PortManipulation/                         
//  
// Port commands: DDRX  : port direction of port X; 0=in, 1=out
//                PORTX : write to port X
//                PINX  : read port X (also to read back output status)
// Works on Arduino Uno R3 and 
// Arduino Nano using the "Processor: ATmega328P/old bootloader" option in menu Tools  


void setup() {
  // Init IO pins ----------------------------------------------------------------------------------------------
  pinMode(8, INPUT_PULLUP);                   // Pull-ups need to be defined >before< port direction settings
  pinMode(9, INPUT_PULLUP);                   // This mimics the behavior of the 9750 sensor ports: Open = true

  // Port configuration for Arduino; see above Arduino reference link
  DDRD |= B11111100;                          // Port D direction setting 1 = output; 0 input.
                                              // This is safe: It sets pins 2 to 7 as outputs
                                              // without changing the mode of pins 0 & 1 (RX/TX) 

  DDRB |= B00001100;                          // Ports B2/B3 = outputs, all other unchanged (B5-7 not usable).
  DDRB &= B11111100;                          // Ports B0/B1 = inputs, all other unchanged.
    
  // Init serial port -----------------------------------------------------------------------------------------
  Serial.begin(19200);                        // Init hardware serial port (pins 0+1)
                                              // Notes: 9600 baud is the native QBasic maximum as well as the 
                                              // maximum on the IBM XT. 
                                              // 19200 baud work when reprogamming the UART using DEBUG within
                                              // DOSBox-X (although not fully) and on the Toshiba 4090.
                                              // 38400 baud work (only) on the 4090 as well 
                                              // using DOSBox-x
  while (!Serial) {}                          // Wait for serial port to connect     
}

void loop() {
    
  uint8_t inputs;                             // For temporal storage of port B status.
  uint8_t outputs;                            // For temporal storage of outputs.
  
  inputs = PINB & B00000011;                  // Read port B, lower 2 bits (=> sensors 6+7 on 9750).
                                              // Use a variable for temporal storage of port B status

  PORTB = inputs << 2;                        // LEDs on port B 2+3 showing the sensor status (optional)

  if(Serial.available()) {                    // Something arrived at the serial port = TCLogo_s write 
                                              // -> no error checking!

    outputs = Serial.read();
    PORTD = outputs << 2;                     // Arduino output port (0-5 on 9750 = PORTD 2-7)                                                                                         
    Serial.write((inputs << 6) | outputs);
                                              // Reply to TCLogo_s: 
                                              // Read the output status, shift right by 2 = bits 0-5.
                                              // Add bits 6+7 by shifting the port B input bits left by 6 
  }
}
