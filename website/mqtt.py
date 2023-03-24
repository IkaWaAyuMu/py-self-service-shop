# import paho.mqtt.client as mqtt

# def on_connect(mqtt_client, userdata, flags, rc):
#    if rc == 0:
#        print('Connected successfully')
#        mqtt_client.subscribe('scanner/0')
#    else:
#        print('Bad connection. Code:', rc)

# def on_message(mqtt_client, userdata, msg):
#     print(f'Received message on topic: {msg.topic} with payload: {msg.payload}')


# client.on_connect = on_connect
# client.on_message = on_message
# client.username_pw_set(config("MQTT_USER"), config("MQTT_PASSWORD"))
# client.connect(
#     host=config("MQTT_SERVER"),
#     port=int(config("MQTT_PORT")),
#     keepalive=int(config("MQTT_KEEPALIVE"))
# )

# def send_message(mqtt_client, userdata, msg):
# #    print(f'Received message on topic: {msg.topic} with payload: {msg.payload}')
#    return msg.payload