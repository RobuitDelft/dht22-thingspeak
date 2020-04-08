def connect_and_subscribe_mqtt():
    global client_id
    time.sleep(1)
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

def restart_and_reconnect():
    print('Failed to connect to MQTT broker. Reconnecting...')
    time.sleep(10)
    machine.reset()
  
def send_tweet(txt):
    print('It is getting hot in here')
    data={'api_key':config.THINGTWEET_KEY, 'status':config.THINGTWEET_TXT % txt}
    response=requests.post(config.THINGTWEET_URL,json=data)
    print(response.status_code)
    
def measure_dht22():
    print('Perform Measurement')
    dhtpin = Pin(12, Pin.IN, Pin.PULL_UP)
    d = DHT22(dhtpin)
    time.sleep(5)
    d.measure()
    return d

# Led
led = Pin(2, Pin.OUT)

# MQTT variables
randomNum = int.from_bytes(urandom(3), 'little')
myMqttClient = bytes("client_"+str(randomNum), 'utf-8')
myMqttCredentials = bytes("channels/{:s}/publish/{:s}".format(config.THINGSPEAK_CHANNEL_ID, config.THINGSPEAK_WRITE_KEY), 'utf-8')

# Initialize MQTT objects
try:
  client = connect_and_subscribe_mqtt()
except OSError as e:
  print('could not connect to MQTT server {}{}'.format(type(e).__name__, e))
  restart_and_reconnect()
  
print('Start Main Loop')
# Main Loop
last_message = 0
while True:
    try:
        if (time.time() - last_message) % config.DELAY == 0:
            led.value(not led.value())
        if (time.time() - last_message) > config.MEASUREMENT_INTERVAL:
            vals = measure_dht22()
            t=vals.temperature()
            h=vals.humidity()
            print('temperature = %.2f' % t)
            print('humidity    = %.2f' % h)
            payload = bytes("field1={:.1f}&field2={:.1f}\n".format(t,h), 'utf-8')
            print('Publish')
            client.publish(myMqttCredentials, payload)
            last_message = time.time()
    except OSError as e:
        print('OSError Exception{}{}'.format(type(e).__name__, e))
        restart_and_reconnect()
    except MQTTException as e:
        print('MQTTException {}{}'.format(type(e).__name__, e))
        restart_and_reconnect()
#    except Exception as e:
#        print('Exception {}{}'.format(type(e).__name__, e))
#        restart_and_reconnect()

     
