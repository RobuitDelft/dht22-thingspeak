from machine import I2C, Pin
from esp8266_i2c_lcd import I2cLcd
import time
import sys
from os import urandom
from umqtt.robust import MQTTClient
from dht import DHT22
import config
import network

try:
    import usocket as socket
except:
    import socket

import ussl as ssl

# Connect to WIFI
def connect_to_wifi():
    # Try all wlans in config.wlandict
    for x in range(len(config.wlandict)):
        print('connecting to network: %s' % config.wlandict[x][0])
        nic.connect(config.wlandict[x][0],config.wlandict[x][1])
        # Wait some time
        time.sleep(2.0)
        attempt =  1
        while attempt < 5 and not nic.isconnected():
            print('connecting ... %s' % str(attempt*2))
            time.sleep(2.0)
            attempt = attempt + 1

        if nic.isconnected():
            print('connected')
            print(nic.ifconfig()[0])
            return True
            lcd.putstr("WLAN:% \n IP:%s" % config.wlandict[x][0], nic.ifconfig()[0])
            time.sleep(2.0)
        
    print('connection failed')
    return False


# measures temperature and humidity with DHT22 sensor, and sends the data to ThingSpeak, Terminal, LED and LCD
def measure_temperature_and_humidity():
    # DHT Sensor
    d = DHT22(Pin(config.DHT22_PIN,Pin.IN,Pin.PULL_UP))
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
        credentials = bytes("channels/{:s}/publish/{:s}".format(config.THINGSPEAK_CHANNEL_ID, config.THINGSPEAK_WRITE_KEY), 'utf-8')  
        payload = bytes("field1={:.1f}&field2={:.1f}\n".format(t,h), 'utf-8')
        client.publish(credentials, payload)
    except Exception as e:
        print('could not connect to MQTT server {}{}'.format(type(e).__name__, e))
        pass



    # LED Output
    # LED light
    led = Pin(config.LED_PIN,Pin.OUT)
    led(1)
    time.sleep_ms(200)
    if h < 70:
       led(0)


## INIT SECTION

# Network interface
nic = network.WLAN(network.STA_IF)
nic.active(True)

# create a random MQTT clientID & MQTTClient object
randomNum = int.from_bytes(urandom(3), 'little')
myMqttClient = bytes("client_"+str(randomNum), 'utf-8')
client = MQTTClient(client_id=myMqttClient, 
                    server=config.THINGSPEAK_URL, 
                    user=config.THINGSPEAK_USER_ID, 
                    password=config.THINGSPEAK_MQTT_KEY, 
                    ssl=False)

# Init LCD screen and set backlight off
i2c = I2C(scl=Pin(config.LCD_PIN_SCL), sda=Pin(config.LCD_PIN_SDA), freq=400000)
lcd = I2cLcd(i2c, 0x27, 2, 16)
lcd.backlight_off()

## RUN SECTION

# (Re)Connect to TU Visitor WLAN
if not nic.isconnected():
    connect_to_wifi()
lcd.clear()
lcd.putstr(nic.ifconfig()[0])
time.sleep(2.0)
# Doing things
measure_temperature_and_humidity()
last_measurement_time = time.time()

# Start Looping
while True:
    try:
        current_time = time.time()
        if current_time - last_measurement_time > config.MEASUREMENT_INTERVAL: 
            # (Re)Connect to TU Visitor WLAN
            if not nic.isconnected():
                connect_to_wifi()
            lcd.clear()
            lcd.putstr(nic.ifconfig()[0])
            time.sleep(2.0)
            # Doing things
            measure_temperature_and_humidity()
            last_measurement_time = current_time
        time.sleep(config.DELAY)
    except KeyboardInterrupt:
        print('Ctrl-C pressed...exiting')
        client.disconnect()
        sys.exit()
    except:
        continue   
