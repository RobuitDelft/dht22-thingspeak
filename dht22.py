from machine import I2C, Pin
from esp8266_i2c_lcd import I2cLcd
import time
import sys
from os import urandom
from umqtt.robust import MQTTClient
from dht import DHT22

try:
    import usocket as socket
except:
    import socket

import ussl as ssl

# Pins
DHT22_PIN = 12
LCD_PIN_SDA=4
LCD_PIN_SCL=5
LED_PIN=14

## Thingspeak vars
#API_THINGSPEAK_HOST = 'api.thingspeak.com'
#API_THINGSPEAK_PORT = 443
THINGSPEAK_CHANNEL_ID = '<channelid>' # put your key here
THINGSPEAK_WRITE_KEY = '<write api key>' # put your key here
THINGSPEAK_MQTT_KEY = '<mqtt api key>' # put your key here
THINGSPEAK_URL = b"mqtt.thingspeak.com" 
THINGSPEAK_USER_ID = b'<userid>'

# timings in seconds
#MEASUREMENT_INTERVAL = 300 # TODO: read this from a config file
MEASUREMENT_INTERVAL = 60 # TODO: read this from a config file
DELAY = 5

## INIT SECTION

# create a random MQTT clientID & MQTTClient object
randomNum = int.from_bytes(urandom(3), 'little')
myMqttClient = bytes("client_"+str(randomNum), 'utf-8')
client = MQTTClient(client_id=myMqttClient, 
                    server=THINGSPEAK_URL, 
                    user=THINGSPEAK_USER_ID, 
                    password=THINGSPEAK_MQTT_KEY, 
                    ssl=False)

# Init LCD screen and set backlight off
i2c = I2C(scl=Pin(LCD_PIN_SCL), sda=Pin(LCD_PIN_SDA), freq=400000)
lcd = I2cLcd(i2c, 0x27, 2, 16)
lcd.backlight_off()

# Connect to TU Visitor WLAN
def do_connect_WLAN():
    import network
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect('<SSID>','<password>')
        while not sta_if.isconnected():
            pass
        print('network config:', sta_if.ifconfig())

# measures temperature and humidity with DHT22 sensor, and sends the data to ThingSpeak, Terminal, LED and LCD
def measure_temperature_and_humidity():
    # DHT Sensor
    d = DHT22(Pin(DHT22_PIN,Pin.IN,Pin.PULL_UP))
    # Measure
    d.measure()
    t = d.temperature()
    h = d.humidity()

    # Terminal Output
    print('temperature = %.2f' % t)
    print('humidity    = %.2f' % h)

    # LCD Output
    lcd.clear()
    lcd.putstr("Temp : %s%sC\nHumi : %s%s" % (str(t),"",str(h),"%"))

    # MQTT

    try:
        print('send data to ThingSpeak')            
        client.connect()
        credentials = bytes("channels/{:s}/publish/{:s}".format(THINGSPEAK_CHANNEL_ID, THINGSPEAK_WRITE_KEY), 'utf-8')  
        payload = bytes("field1={:.1f}&field2={:.1f}\n".format(t,h), 'utf-8')
        client.publish(credentials, payload)
    except Exception as e:
        print('could not connect to MQTT server {}{}'.format(type(e).__name__, e))
        pass



    # LED Output
    # LED light
    led = Pin(LED_PIN,Pin.OUT)
    led(1)
    time.sleep_ms(200)
    if h < 70:
       led(0)

## RUN SECTION

# (Re)Connect to TU Visitor WLAN
do_connect_WLAN()
measure_temperature_and_humidity()
last_measurement_time = time.time()

while True:
    try:
        current_time = time.time()
        if current_time - last_measurement_time > MEASUREMENT_INTERVAL: 
            # (Re)Connect to TU Visitor WLAN
            do_connect_WLAN()
            # Doing things
            measure_temperature_and_humidity()
            last_measurement_time = current_time
        time.sleep(DELAY)
    except KeyboardInterrupt:
        print('Ctrl-C pressed...exiting')
        client.disconnect()
        sys.exit()
    except:
        pass   
