#!/usr/bin/env python3

import serial
import time

s = serial.Serial(port="/dev/ttyUSB0", baudrate=115200, timeout=5)

# Cambiar modo
s.write(b"m\n") 
time.sleep(0.1)

# SPI
s.write(b"5\n")
time.sleep(0.1)

# 125kHz
s.write(b"2\n")
time.sleep(0.1)

# Clock: Idle low
s.write(b"1\n")
time.sleep(0.1)

# Clock: Active to idle
s.write(b"2\n")
time.sleep(0.1)

# Input sample phase: Middle
s.write(b"1\n")
time.sleep(0.1)

# CS: /CS
s.write(b"2\n")
time.sleep(0.1)

# Select output type: Normal
s.write(b"1\n")
time.sleep(0.1)

# Power supplies on
s.write(b"W\n")
time.sleep(0.1)

# Initialization of SD into SPI mode
s.write(b"]r:10[0x40 0x00 0x00 0x00 0x00 0x95 r:8]\n")
time.sleep(0.1)
s.write(b"[0x41 0x00 0x00 0x00 0x00 0xFF r:8]\n")
time.sleep(0.1)
s.write(b"[0x41 0x00 0x00 0x00 0x00 0xFF r:8]\n")
time.sleep(0.1)
s.write(b"[0x50 0x00 0x00 0x02 0x00 0xFF r:8]\n")
time.sleep(0.1)
s.reset_input_buffer()
s.reset_output_buffer()
f1 = open("even.bin", "wb")
f2 = open("odd.bin", "wb")
n = 0
for i in range(0, 16 * 1024 * 1024, 512):
    a4 = i >> 24 & 0xff
    a3 = i >> 16 & 0xff
    a2 = i >> 8 & 0xff
    a1 = i & 0xff
    print(f"Reading {hex(a4)} {hex(a3)} {hex(a2)} {hex(a1)}...")
    s.write(f"[0x51 {a4} {a3} {a2} {a1} 0xFF r:520]\n".encode())
    response = s.read_until(b"SPI>")
    sector_bytes_str = response.decode().split("\n")[8].lstrip("READ: ").split()
    header_bytes = bytes([ int(x, 16) for x in sector_bytes_str[:sector_bytes_str.index("0xFE")+1] ])
    sector_bytes = bytes([ int(x, 16) for x in sector_bytes_str[sector_bytes_str.index("0xFE")+1:sector_bytes_str.index("0xFE")+512+1] ])
    if n % 2 == 0:
        f1.write(sector_bytes)
    else:
        f2.write(sector_bytes)
    n += 1
