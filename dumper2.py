import time
import serial
import os

# Configura el puerto COM y la velocidad de comunicación según tu configuración
COM_PORT = 'COM3'
BAUD_RATE = 115200  # Esta velocidad puede variar según tu configuración

# Dirección del dispositivo AT24C256 para lectura
EEPROM_READ_ADDRESS = 0xA1

# Número total de bloques a leer
NUM_BLOCKS = 32  # 32 bytes x 1024 = 32768

# Nombre del archivo para guardar el dump con todo el output
DUMP_FILE = 'eeprom_dump.log'

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
    ser.write(b'[0xA0 0x00 0x00]\n')  # Direccion de inicio para leer


def read_eeprom_dump():
    try:
        # Abre la conexión con el puerto COM
        ser = serial.Serial(port=COM_PORT, baudrate=BAUD_RATE, timeout=1)

        # Espera a que se inicialice la comunicación
        time.sleep(2)

        # Configura el Bus Pirate para I2C
        configure_bus_pirate(ser)

        # Realiza la lectura de la EEPROM y guarda los datos en el archivo
        with open(DUMP_FILE, 'wb') as dump_file:
            # Realiza la lectura de los datos en bloques de 64 bytes

            data = ser.read(1200)
            dump_file.write(data)
            for _ in range(NUM_BLOCKS):
                ser.write(b'[0xA1 r:1024]\n')  # Envía el comando para leer 64 bytes
                time.sleep(0.1)
                data = ser.read(12800)
                dump_file.write(data)
                

        print('Dump guardado en:', DUMP_FILE)
    except Exception as e:
        print('Error:', str(e))
    finally:
        # Cierra la conexión
        ser.close()


def parse_log_and_extract_ascii(filename, output_filename):
    ascii_values = []
    with open(filename, 'r') as file:
        lines = file.readlines()
        read_block = False  # Flag para indicar que estamos dentro de un bloque de lectura
        for line in lines:
            if "READ:" in line:
                # Si encontramos un bloque de lectura, marcamos el flag y lo procesamos
                read_block = True
                hex_values = line.split(" ")[1:]  # Extraer los valores hexadecimales

                # Filtrar los valores hexadecimales válidos y convertir a ASCII
                ascii_values.append(''.join([chr(int(value, 16)) for value in hex_values if is_hex(value)]))

    # Filtramos las líneas no deseadas y escribimos los valores ASCII en el archivo de salida
    formatted_values = ''.join(ascii_values)  # Unimos los valores sin saltos de línea
    with open(output_filename, 'w') as output_file:
        output_file.write(formatted_values)

    print('Valores ASCII guardados en:', output_filename)

# Función para verificar si una cadena es un valor hexadecima
def is_hex(value):
    try:
        int(value, 16)
        return True
    except ValueError:
        return False


if __name__ == "__main__":
    read_eeprom_dump()
    parse_log_and_extract_ascii(DUMP_FILE, 'ascii_values.img')
