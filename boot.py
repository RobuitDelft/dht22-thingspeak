# Complete project details at https://RandomNerdTutorials.com

import time
import machine
#import micropython
import network
import esp
import gc
import config

from machine import Pin
from dht import DHT22
from umqtt.robust import MQTTClient
from os import urandom
import config
import urequests as requests
from os import urandom

# Debug None, Activate the Garbage Collector
esp.osdebug(None)
gc.collect()

# Disable Access Point (to not annoy network guys)
accesspoint = network.WLAN(network.AP_IF)
accesspoint.active(False)

# Connect to Wifi
station = network.WLAN(network.STA_IF)
station.active(True)
station.connect(config.WLANSSID, config.WLANPASS)

# Wait while connection comes up
while station.isconnected() == False:
  time.sleep(1)
  pass

print('Connection successful')
print(station.ifconfig())