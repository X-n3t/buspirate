import time
import serial

# Configura el puerto COM y la velocidad de comunicación según tu configuración
COM_PORT = 'COM3'
BAUD_RATE = 115200  # Esta velocidad puede variar según tu configuración

def configure_bus_pirate(ser):
    # Configura el Bus Pirate para el modo I2C y la velocidad deseada (~100kHz)
    ser.write(b'm\n')  # Selecciona el modo I2C
    time.sleep(0.1)
    ser.write(b'5\n')  # Modo SPI
    time.sleep(0.1)
    ser.write(b'5\n')  # Speed
    time.sleep(0.1)
    ser.write(b'1\n')  # Clock Polarity
    time.sleep(0.1)
    ser.write(b'2\n')  # Clock Edge
    time.sleep(0.1)
    ser.write(b'1\n')  # Sample Phase
    time.sleep(0.1)
    ser.write(b'2\n')  # CS
    time.sleep(0.1)
    ser.write(b'2\n')  # Output
    time.sleep(0.1)   
    ser.write(b'W\n')  # Encender las fuentes de alimentación
    time.sleep(0.1)
    # Initialization of SD into SPI mode
    ser.write(b']r:10[0x40 0x00 0x00 0x00 0x00 0x95 r:8]\n')  # modo SPI
    time.sleep(0.1)
    ser.write(b'[0x41 0x00 0x00 0x00 0x00 0xFF r:8]\n')  # sacar del modo IDLE
    time.sleep(0.1)
    ser.write(b'[0x41 0x00 0x00 0x00 0x00 0xFF r:8]\n')  # comprobar si ya no está en modo IDLE
    time.sleep(0.1)
    ser.write(b'[0x50 0x00 0x00 0x02 0x00 0xFF r:8]\n')  # establecer tamaño de bloque a 512 (0x200)
    time.sleep(0.1)
    ser.reset_input_buffer()
    ser.reset_output_buffer()

if __name__ == "__main__":
    ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=1)
    configure_bus_pirate(ser)

    f1 = open("even.bin", "wb")
    f2 = open("odd.bin", "wb")
    n = 0
    for i in range(0, 16 * 1024 * 1024, 512):
        a4 = i >> 24 & 0xff
        a3 = i >> 16 & 0xff
        a2 = i >> 8 & 0xff
        a1 = i & 0xff
        print(f"Reading {hex(a4)} {hex(a3)} {hex(a2)} {hex(a1)}...")
        ser.write(f"[0x51 {a4} {a3} {a2} {a1} 0xFF r:520]\n".encode())
        response = ser.read_until(b"SPI>")
        sector_bytes_str = response.decode().split("\n")[8].lstrip("READ: ").split()
        header_bytes = bytes([ int(x, 16) for x in sector_bytes_str[:sector_bytes_str.index("0xFE")+1] ])
        sector_bytes = bytes([ int(x, 16) for x in sector_bytes_str[sector_bytes_str.index("0xFE")+1:sector_bytes_str.index("0xFE")+512+1] ])
        if n % 2 == 0:
            f1.write(sector_bytes)
        else:
            f2.write(sector_bytes)
        n += 1