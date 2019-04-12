# This file is executed on every boot (including wake-boot from deepsleep)
import machine
import gc
import webrepl
import network
import config

webrepl.start()
gc.collect()

def do_connect_wlan():
    import network
    sta_if = network.WLAN(network.STA_IF)
    sta_if.disconnect()
    if not sta_if.isconnected():
        print('connecting to WLAN...' + config.WLAN_SSID)
        sta_if.active(True)
        sta_if.connect(config.WLAN_SSID, config.WLAN_PASSWORD)
        while not sta_if.isconnected():
            pass
    print('network config:', sta_if.ifconfig())


# Deactivate Access Point (to not annoy network guys)
def activate_ap():
    ap_if = network.WLAN(network.AP_IF)
    ap_if.active(True)

def deactivate_ap():
    ap_if = network.WLAN(network.AP_IF)
    ap_if.active(False)

deactivate_ap()
do_connect_wlan()

print("Load DHT22 module and Run")
import dht22




