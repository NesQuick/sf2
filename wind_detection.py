import smbus
import time

i2cbus = smbus.SMBus(1)
i2caddress = 0x11
	
PROSHIVKA = 0x04 #version
IDENT = 0x05 #identifier
STATUS = 0x06 #status
ATEMPCOLD = 0x09 #temps of cold ACP
ATEMPHOT = 0x0B #temps of hot ACP
SPEED = 0x07 #wind speed
VOLTIN = 0x0D #input voltage
PHEAT = 0x0E #heating power
TEMPCOLD = 0x10 #temps of cold
TEMPHOT = 0x12 #temps of hot
TEMPDIFDEV = 0x14 #difference of temps on device
TEMPDIF = 0x10 #out temps, seems like the same as TEMPCOLD

TEMP_COLD_H = 0x10
TEMP_COLD_L = 0x11
WIND_H = 0x07
WIND_L = 0x08
	
while True:
	#print(i2cbus.read_byte_data(i2caddress, VOLTIN))
	#h = i2cbus.read_byte_data(i2caddress, TEMP_COLD_H)
	#l = i2cbus.read_byte_data(i2caddress, TEMP_COLD_L)
	h = i2cbus.read_byte_data(i2caddress, WIND_H)
	l = i2cbus.read_byte_data(i2caddress, WIND_L)
	tmp = (h << 8) | l
	tmp_out = tmp/10
	print(tmp_out)
	time.sleep(1)


