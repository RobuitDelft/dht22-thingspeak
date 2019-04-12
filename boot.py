# This file is executed on every boot (including wake-boot from deepsleep)
import machine
import gc
import webrepl
import network

webrepl.start()
gc.collect()

def do_connect_wlan():
    import network
    sta_if = network.WLAN(network.STA_IF)
    sta_if.disconnect()
    if not sta_if.isconnected():
        print('connecting to WLAN...')
        sta_if.active(True)
        sta_if.connect('<SSID>', '<password>')
        while not sta_if.isconnected():
            pass
    print('network config:', sta_if.ifconfig())

def scan_wlan():
    import network
    import ubinascii
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    netw_found = 0
    print('-' * 51)
    print('| SSID                 | BSSID        | Ch | RSSI |')
    print('-' * 51)
    for item in sta_if.scan():
        if len(item[0]) > 20:
            ssid = item[0][0:18] + '>>'
        else:
            ssid = item[0]
        print("| {0:<20} | {1} | {2:>2} | {3:>4} |".format(ssid, ubinascii.hexlify(item[1]).decode(), item[2], item[3]))
        netw_found += 1
    print('-' * 51)
    print('Total networks found: {}\n'.format(netw_found))
    return

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




