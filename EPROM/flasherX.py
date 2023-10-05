import time
import serial
import os

# Configura el puerto COM y la velocidad de comunicación según tu configuración
COM_PORT = 'COM3'
BAUD_RATE = 115200  # Esta velocidad puede variar según tu configuración

# Dirección del dispositivo AT24C256 para escritura
EEPROM_WRITE_ADDRESS = 0xA0

# Número total de bloques a escribir (creo que deben ser bloques de 21) *48= 1024 * 32 = 32768
NUM_BLOCKS = 1560 # 32 bytes x 1024 = 32768

# Nombre del archivo de imagen
IMG_FILE = 'eeprom.img'

def configure_bus_pirate(ser):
    # Configura el Bus Pirate para el modo I2C y la velocidad deseada (~100kHz)
    ser.write(b'm\n')  # Selecciona el modo I2C
    time.sleep(0.1)
    ser.write(b'4\n')  # Modo I2C
    time.sleep(0.1)
    ser.write(b'1\n')  # Selección de modo software
    time.sleep(0.1)
    ser.write(b'2\n')  # Establecer velocidad ~50kHz
    time.sleep(0.1)
    ser.write(b'W\n')  # Encender las fuentes de alimentación
    time.sleep(0.1)

def generate_write_commands(img_filename):
    commands = []
    with open(img_filename, 'rb') as img_file:
        img_data = img_file.read()

    # Divide los datos de la imagen en bloques de 21 bytes
    blocks = [img_data[i:i + 21] for i in range(0, len(img_data), 21)]

    # Genera los comandos de escritura para cada bloque
    for i, block in enumerate(blocks, start=0):
        # Dirección de memoria para escribir
        address_high = (i * 21) >> 8  # Segundo byte de la dirección
        address_low = (i * 21) & 0xFF  # Tercer byte de la dirección
        command = f'[0xA0 0x{address_high:02X} 0x{address_low:02X} ' + ' '.join([f'0x{byte:02X}' for byte in block]) + ']\n'
        commands.append(command)

    return commands

def send_commands(ser, commands):
    for i, command in enumerate(commands, start=0):
        print(f"Escribiendo bloque {i}: {command.strip()}")
        ser.write(command.encode())
        time.sleep(0.1)  # Espera para que el comando se ejecute correctamente

if __name__ == "__main__":
    try:
        # Abre la conexión con el puerto COM
        ser = serial.Serial(port=COM_PORT, baudrate=BAUD_RATE, timeout=1)

        # Espera a que se inicialice la comunicación
        time.sleep(2)

        # Configura el Bus Pirate para I2C
        configure_bus_pirate(ser)

        # Genera los comandos de escritura
        commands = generate_write_commands(IMG_FILE)

        # Envía los comandos de escritura
        send_commands(ser, commands)

    except Exception as e:
        print('Error:', str(e))
    finally:
        # Cierra la conexión
        ser.close()
