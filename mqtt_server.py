import paho.mqtt.client as mqtt_client
import json
from database_connect import *

import logging
logger = logging.getLogger("console_logger")
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)
# 当连接成功时的回调函数


def on_connect(client, userdata, flags, rc):
    logger.debug("Connected with result code "+str(rc))
    logger.debug('userdata: '+str(userdata))
    logger.debug('flags: '+str(flags))
    # 订阅您感兴趣的主题
    for topic in userdata['subcriber_topic']:
        client.subscribe(topic)
        logger.info(f'subscribe to {topic}')


# 当收到消息时的回调函数
def on_message(client, userdata, msg):
    session = Session()
    logger.debug(msg.topic+":"+str(msg.payload.decode()))
    iot_massage_json = json.loads(msg.payload.decode())
    iot_massage = IotMessage(**iot_massage_json)
    session.add(iot_massage)
    session.commit()


if __name__ == '__main__':

    client = mqtt_client.Client()
    mqtt_configs = {
        'subcriber_topic': ["testapp"]
    }
    client.user_data_set(mqtt_configs)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect("127.0.0.1", 1883, 6000)
    client.loop_forever()
