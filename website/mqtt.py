import paho.mqtt.client as mqtt
from decouple import config

def on_connect(mqtt_client, userdata, flags, rc):
   if rc == 0:
       print('Connected successfully')
       mqtt_client.subscribe('website/mqtt')
   else:
       print('Bad connection. Code:', rc)

def on_message(mqtt_client, userdata, msg):
   print(f'Received message on topic: {msg.topic} with payload: {msg.payload}')

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.username_pw_set(config("MQTT_USER"), config("MQTT_PASSWORD"))
client.connect(
    host=config("MQTT_SERVER"),
    port=config("MQTT_PORT"),
    keepalive=config("MQTT_KEEPALIVE")
)