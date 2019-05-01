import spidev
import time
from libsoc import gpio
from gpio_96boards import GPIO
from dweet import Dweet

GPIO_CS = GPIO.gpio_id('GPIO_CS')
sensorGas = GPIO.gpio_id('GPIO_A')
alarmeGas = GPIO.gpio_id('GPIO_C')
ctrlLamp0 = GPIO.gpio_id('GPIO_E')

pins = ((GPIO_CS, 'out'), (alarmeGas, 'out'), (ctrlLamp0, 'out'),(sensorGas, 'in'),)

spi = spidev.SpiDev()
spi.open(0,0)
spi.max_speed_hz = 10000
spi.mode = 0b00
spi.bits_per_word = 8

system_status = 1

dweet = Dweet()


def readDigital(gpio):
	digital = [0,0,0]
	digital[0] = gpio.digital_read(ctrlLamp0)
	digital[1] = gpio.digital_read(alarmeGas)
        digital[2] = gpio.digital_read(sensorGas)
        #digital[2] = 1
	return digital

def writeDigital(gpio, digital):
	write = digital
	gpio.digital_write(ctrlLamp0, write[0])
	gpio.digital_write(alarmeGas, write[1])
	return digital


def readvolAgua(gpio):

	gpio.digital_write(GPIO_CS, GPIO.HIGH)
	time.sleep(0.0002)
	gpio.digital_write(GPIO_CS, GPIO.LOW)
	r = spi.xfer2([0x01, 0xA0, 0x00])
	gpio.digital_write(GPIO_CS, GPIO.HIGH)

	adcout = (r[1] << 8) & 0b1100000000
	adcout = adcout | (r[2] & 0xff)
	adc_volAgua = (adcout*20)/1023
	return adc_volAgua

def readLumi(gpio):

	gpio.digital_write(GPIO_CS, GPIO.HIGH)
	time.sleep(0.0002)
	gpio.digital_write(GPIO_CS, GPIO.LOW)
	r = spi.xfer2([0x01, 0x80, 0x00])
	gpio.digital_write(GPIO_CS, GPIO.HIGH)
	adcout = (r[1] << 8) & 0b1100000000
	adcout = adcout | (r[2] & 0xff)
        adcout = (adcout*100)/1023
	return adcout

#def readDweet():


if __name__=='__main__':
	with GPIO(pins) as gpio:
		while True:
			digital = [0,0,0]
			resposta = dweet.latest_dweet(name="inatel_ead1")
			writeDigital(gpio, digital)
			volumeAgua = readvolAgua(gpio)
			Lumi = readLumi(gpio)
			digital = readDigital(gpio)
                        if digital[2]==1:
		               gpio.digital_write(alarmeGas, GPIO.HIGH)
                               digital[1] = gpio.digital_read(alarmeGas)
                        else:
		               gpio.digital_write(alarmeGas, GPIO.LOW)
                               digital[1] = gpio.digital_read(alarmeGas)

                        if Lumi < 20:
		               gpio.digital_write(ctrlLamp0, GPIO.HIGH)
                               digital[0] = gpio.digital_read(ctrlLamp0)
                        else:
		            gpio.digital_write(ctrlLamp0, GPIO.LOW)
                            digital[0] = gpio.digital_read(ctrlLamp0)

			print "__volAgua: %3.1f\n__Luminos: %d\nctrlLamp0: %d\nalarmeGas: %d\nsensorGas: %d" %(volumeAgua, Lumi,
                        digital[0], digital[1],digital[2])
			dweet.dweet_by_name(name="inatel_ead", data={"ctrlLamp0":digital[0],"alarmeGas": digital[1], "sensorGas": digital[1],"volAgua":volumeAgua,"luminosidade": Lumi})

			time.sleep(2)
