import time
import serial

# Configura el puerto COM y la velocidad de comunicación según tu configuración
COM_PORT = 'COM3'
BAUD_RATE = 115200  # Esta velocidad puede variar según tu configuración

# Nombre del archivo
IMG_FILE = 'binario.txt'

def configure_bus_pirate(ser):
    # Configura el Bus Pirate para el modo I2C y la velocidad deseada (~100kHz)
    ser.write(b'm\n')  # Selecciona el modo I2C
    time.sleep(0.1)
    ser.write(b'5\n')  # Modo SPI
    time.sleep(0.1)
    ser.write(b'1\n')  # Speed
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
    ser.write(b']r:10[0x40 0x00 0x00 0x00 0x00 0x95 r:8]\n')  # modo SPI
    time.sleep(0.1)
    ser.write(b'[0x41 0x00 0x00 0x00 0x00 0xFF r:8]\n')  # sacar del modo IDLE
    time.sleep(0.1)
    ser.write(b'[0x41 0x00 0x00 0x00 0x00 0xFF r:8]\n')  # comprobar si ya no está en modo IDLE
    time.sleep(0.1)
    ser.write(b'[0x50 0x00 0x00 0x02 0x00 0xFF r:8]\n')  # establecer tamaño de bloque a 512 (0x200)
    time.sleep(0.1)

def generate_addresses():
    start_address = 0x000000
    end_address = 0xfffe00
    step = 0x200

    current_address = start_address
    while current_address <= end_address:
        # Calcular los bytes de dirección
        addr_byte1 = (current_address & 0xFF)
        addr_byte2 = ((current_address >> 8) & 0xFF)
        addr_byte3 = ((current_address >> 16) & 0xFF)

        # Devolver la dirección en el formato deseado usando yield
        yield f"[0x51 0x00 0x{addr_byte3:02X} 0x{addr_byte2:02X} 0x{addr_byte1:02X} 0xFF r:516]\n"

        # Mover a la siguiente dirección
        current_address += step

if __name__ == "__main__":
    ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=1)
    configure_bus_pirate(ser)

    try:
        # Abre un archivo para escribir las respuestas (modo 'ab' para agregar)
        with open(IMG_FILE, "ab") as f:
            # Itera sobre los comandos generados
            for command in generate_addresses():
                # Escribe el comando en el puerto serie
                ser.write(command.encode())

                # Imprime el comando enviado
                print("Comando enviado:", command)

                # Espera después de enviar el comando de lectura
                if "r:516" in command:
                    time.sleep(0.1)  # Ajusta este valor según sea necesario

                # Espera la respuesta
                response = ser.read(516)

                # Escribe la respuesta en el archivo
                f.write(response)

    except Exception as e:
        print("An exception occurred:", str(e))
    finally:
        # Cerrar el puerto serie
        ser.close()