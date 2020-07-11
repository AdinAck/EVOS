import board
import digitalio
import analogio
import busio
import pulseio
import time
from adafruit_mcp230xx.mcp23008 import MCP23008
from ADS1248 import ADS1248
from BMS import BMS

# GPIO
buz = digitalio.DigitalInOut(board.D13)
buz.direction = digitalio.Direction.OUTPUT

relay = digitalio.DigitalInOut(board.A4)
relay.direction = digitalio.Direction.OUTPUT

# SERCOM
spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
i2c = busio.I2C(board.SCL, board.SDA)

# ADS1248
ADS1248.setup(spi, board.D3, board.D4)
adc0 = ADS1248(board.D2, board.D12, 2.5)
adc1 = ADS1248(board.D11, board.D10, 2.5)
adc2 = ADS1248(board.D9, board.D7, 2.5)

# ADS1248.verbose = True
ADS1248.wakeupAll()
ADS1248.wregAll(2,[0x40,0x00])
ADS1248.selfOffsetAll()

# MCP23008
mcp0 = MCP23008(i2c, address=0x20)
mcp1 = MCP23008(i2c, address=0x21)
mcp2 = MCP23008(i2c, address=0x22)

# Temp sensors
tmp0 = analogio.AnalogIn(board.A0)
tmp1 = analogio.AnalogIn(board.A1)
tmp2 = analogio.AnalogIn(board.A2)
tmp3 = analogio.AnalogIn(board.A3)

# Fan
# fan = pulseio.PWMOut(board.A5, frequency=5000, duty_cycle=0)
fan = digitalio.DigitalInOut(board.A5)
fan.direction = digitalio.Direction.OUTPUT

# BMS
bms = BMS(ADS1248, [mcp0, mcp1, mcp2], [tmp0, tmp1, tmp2, tmp3], buz, relay, fan)
bms.verbose = True

while True:
    bms.update()
    time.sleep(3)
