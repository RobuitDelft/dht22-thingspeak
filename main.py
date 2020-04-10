def connect_and_subscribe_mqtt():
    global client_id
    time.sleep(1)
    randomNum = int.from_bytes(urandom(3), 'little')
    myMqttClient = bytes("client_"+str(randomNum), 'utf-8')
    client = MQTTClient(client_id=myMqttClient,
                        server=config.THINGSPEAK_URL, 
                        user=config.THINGSPEAK_USER_ID, 
                        password=config.THINGSPEAK_MQTT_KEY, 
                        ssl=False)
    time.sleep(1)
    client.connect()
    time.sleep(1)
    print('Connected to %s MQTT broker' % config.THINGSPEAK_URL.decode())
    return client

def reconnect_wifi():
    # Disable Access Point (to not annoy network guys)
    accesspoint = network.WLAN(network.AP_IF)
    accesspoint.active(False)

    # Wait while connection comes up
    station = network.WLAN(network.STA_IF)
    while station.isconnected() == False:
        time.sleep(1)
        station.active(True)
        station.connect(config.WLANSSID, config.WLANPASS)
    print('Connection successful')
    print(station.ifconfig())

def restart_and_reconnect():
    print('Failed to connect to MQTT broker. Reconnecting...')
    time.sleep(10)
    client.disconnect()
    machine.reset()
  
def send_tweet(txt):
    print('It is getting hot in here')
    data={'api_key':config.THINGTWEET_KEY, 'status':config.THINGTWEET_TXT % txt}
    response=requests.post(config.THINGTWEET_URL,json=data)
    print(response.status_code)
    
def measure_dht22():
    print('Perform Measurement')
    dhtpin = Pin(config.DHT22_PIN, Pin.IN, Pin.PULL_UP)
    d = DHT22(dhtpin)
    time.sleep(2)
    d.measure()
    time.sleep(2)
    print('temperature = %.2f' % d.temperature())
    print('humidity    = %.2f' % d.humidity())
    return d

def flash_led():
    led.value(0)
    time.sleep(0.2)
    led.value(1)

# Led
led = Pin(2, Pin.OUT)

# Initialize MQTT objects
print('Initialize MQTT objects')
try:
  myMqttCredentials = bytes("channels/{:s}/publish/{:s}".format(config.THINGSPEAK_CHANNEL_ID, config.THINGSPEAK_WRITE_KEY), 'utf-8')
  client = connect_and_subscribe_mqtt()
except OSError as e:
  print('could not connect to MQTT server {}{}'.format(type(e).__name__, e))
  restart_and_reconnect()

 
# Main Loop
print('Start Main Loop')
last_message = (-(config.MEASUREMENT_INTERVAL+100))
last_led=0
while True:
    try:

        # Flash led every config.DELAY seconds
        if (time.time() - last_led) >  config.LED_INTERVAL:
            flash_led()
            last_led = time.time()
        # Measure and process data every config.MEASUREMENT_INTERVAL seconds
        if (time.time() - last_message) > config.MEASUREMENT_INTERVAL:
            vals = measure_dht22()
            message = bytes("field1={:.1f}&field2={:.1f}\n".format(vals.temperature(),vals.humidity()), 'utf-8')
            # Check Wifi
            if station.isconnected() == False:
                print('Reconnect to wifi')
                reconnect_wifi()
            print('Publish MQTT Data')
            client.publish(myMqttCredentials, message)
            last_message = time.time()
    except KeyboardInterrupt:
        print('Ctrl-C pressed...exiting')
        client.disconnect()
        sys.exit()
    except:
        restart_and_reconnect()

     
