# This file is executed on every boot (including wake-boot from deepsleep)
import machine
import gc
import webrepl
import network
import config
import time

webrepl.start()
gc.collect()

# Connect to WIFI
def connect_to_wifi():
    nic = network.WLAN(network.STA_IF)
    nic.active(True)
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
        
    print('connection failed')
    return False


# Deactivate Access Point (to not annoy network guys)
def activate_ap():
    ap_if = network.WLAN(network.AP_IF)
    ap_if.active(True)

def deactivate_ap():
    ap_if = network.WLAN(network.AP_IF)
    ap_if.active(False)

deactivate_ap()
connect_to_wifi()

print("Load DHT22 module and Run")
import dht22




