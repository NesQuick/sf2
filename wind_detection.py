import smbus2 as smbus
import time

DEVICE_BUS = 1
DEVICE_ADDR = 0x11
while True:
	bus = smbus.SMBus(DEVICE_BUS)
	print(bus.write_byte_data(DEVICE_ADDR, 0x00, 0x01))
	time.sleep(0.5)

