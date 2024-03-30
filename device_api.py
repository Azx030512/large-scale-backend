from flask import Flask, jsonify
from flask import make_response
from flask import request
from flask import abort
from database_connect import *
import psutil
from datetime import datetime
import math

import logging
logger = logging.getLogger("console_logger")
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

api = Flask('device_api')


@api.route('/api/device_api/binddevice', methods=['POST', 'get'])
def bind_device():
    # request.json里面包含请求数据，如果不是JSON或者里面没有包含title字段
    try:

        # class Device(Base):
        # __tablename__ = 'device'
        # device_id = Column(String(50), nullable=False, primary_key=True)
        # device_name = Column(String(50), nullable=False)
        # device_type = Column(String(20), nullable=False)
        # creation_date = Column(DateTime, nullable=False)
        # description = Column(String(100), nullable=True)
        session = Session()
        new_device_json = request.json
        new_device_info = {}
        for key in Device.info_keys:
            if key in new_device_json:
                new_device_info[key] = new_device_json[key]
        new_device = Device(**new_device_info)
        session.add(new_device)
        session.commit()

        return jsonify({'message': "新设备添加绑定成功！",
                        'signal': "success"
                        }), 200

    except Exception as e:
        logging.exception(e)
        session.rollback()
        return jsonify({'message': "新设备绑定失败！",
                        'signal': "fail"}), 200


@api.route('/api/device_api/modifydevice', methods=['POST', 'get'])
def modify_device():
    # request.json里面包含请求数据，如果不是JSON或者里面没有包含title字段

    try:
        session = Session()
        previous_device_info = request.json['previous_device_info']
        modified_device_info = request.json['modified_device_info']
        results = session.query(Device).filter_by(
            device_id=previous_device_info['device_id']).all()  # 查找表的所有数据
        logging.debug("query result: " + str(results))

        if len(results) == 0:
            return jsonify({'message': "未发现设备: "+previous_device_info['device_id'],
                            'signal': "fail"
                            }), 200
        elif len(results) > 1:
            return jsonify({'message': "设备信息错误, 查询到多个设备",
                            'signal': "fail"
                            }), 200
        target_device = results[0]
        if previous_device_info['device_id'] != modified_device_info['device_id']:
            results = session.query(Device).filter_by(
                device_id=modified_device_info['device_id']).all()  # 查找表的所有数据
            if len(results) != 0:
                return jsonify({'message': "新设备id已被占用: "+previous_device_info['device_id'],
                                'signal': "fail"
                                }), 200
            else:
                target_device.device_id = modified_device_info['device_id']
        target_device.device_name = modified_device_info['device_name']
        target_device.device_type = modified_device_info['device_type']
        target_device.description = modified_device_info['description']
        session.commit()
        return jsonify({'message': "修改设备信息成功!",
                        'signal': "success",
                        }), 200

    except Exception as e:
        logging.exception(e)
        session.rollback()
        return jsonify({'message': "设备修改失败",
                        'signal': "fail"}), 200


@api.route('/api/device_api/querydevice', methods=['POST', 'get'])
def query_device():
    # request.json里面包含请求数据，如果不是JSON或者里面没有包含title字段

    try:
        session = Session()
        query_device_info = request.json
        if query_device_info['query_mode'] == 1:
            results = session.query(Device).filter_by(
                device_id=query_device_info['old_device_id']).all()  # 查找表的所有数据
        elif query_device_info['query_mode'] == 2:
            results = session.query(Device).filter_by(
                device_name=query_device_info['old_device_name']).all()  # 查找表的所有数据
        logging.debug("query result: " + str(results))

        if len(results) == 0:
            return jsonify({'message': "未发现设备: "+query_device_info['old_device_id'],
                            'signal': "fail"
                            }), 200

        target_device = results[0]
        session.commit()
        return jsonify({'message': "查询设备到设备"+target_device.device_name,
                        'signal': "success",
                        'device_info': target_device.show_info()
                        }), 200

    except Exception as e:
        logging.exception(e)
        session.rollback()
        return jsonify({'message': "设备修改失败",
                        'signal': "fail"}), 200


@api.route('/api/device_api/listdevice', methods=['POST', 'get'])
def list_device():
    # request.json里面包含请求数据，如果不是JSON或者里面没有包含title字段
    try:
        session = Session()
        top_k = 100
        if 'top_k' in request.json:
            top_k = request.json['top_k']
        results = session.query(Device).all()  # 查找表的所有数据
        logging.debug("all the devices are: " + str(results))

        if len(results) == 0:
            return jsonify({'message': "尚未添加设备",
                            'signal': "success"
                            }), 200
        device_list = []
        for device in results:
            device_list.append(device.show_info())
        session.close()
        return jsonify({'message': "查询设备列表信息成功!",
                        'signal': "success",
                        'device_list': device_list[:top_k]
                        }), 200

    except Exception as e:
        logging.exception(e)
        session.rollback()
        return jsonify({'message': "设备查询失败",
                        'signal': "fail"}), 500


def get_cpu_load():
    cpu_load = psutil.cpu_percent(interval=1)
    return min(cpu_load*4, 80)


def get_memory_usage():
    memory_usage = psutil.virtual_memory().percent
    return min(memory_usage, 80)


def get_active_index():
    session = Session()
    active_threshold = 50
    messages = session.query(IotMessage).all()
    messages.sort(key=lambda x: x.timestamp, reverse=True)
    message_number = len(messages)
    devices = session.query(Device).all()
    device_number = len(devices)
    recenct_messages = messages[:active_threshold]
    active_devices = set([item.device_id for item in recenct_messages])
    active_device_number = len(active_devices)
    active_device_index = int((active_device_number/device_number)*80)
    current_time = datetime.fromtimestamp(time.time())
    past_time = messages[:active_threshold][-1].timestamp
    duration = current_time - past_time
    if duration.seconds < 10:
        active_message_index = 75
    elif duration.seconds < 60:
        active_message_index = 60
    elif duration.seconds < 300:
        active_message_index = 50
    elif duration.seconds < 1000:
        active_message_index = 40
    else:
        active_message_index = min(int(math.log2(duration.seconds)), 30)
    alert_number = sum([item.alert for item in recenct_messages])
    alert_index = int((alert_number/active_threshold)*80)
    session.close()
    return {
        'active_device_index': active_device_index,
        'active_message_index': active_message_index,
        'alert_index': alert_index,
        'cpu_load': get_cpu_load(),
        'memory_usage': get_memory_usage()
    }

@api.route('/api/device_api/radardata', methods=['POST', 'get'])
def radar_data():
    # request.json里面包含请求数据，如果不是JSON或者里面没有包含title字段
    try:
        item_tag_list=["服务器负载", "内存占用", "消息活跃度", "警报频繁度", "设备活跃度"]
        tag_key_map = {
            "服务器负载": 'cpu_load',
            "内存占用": 'memory_usage', 
            "消息活跃度": 'active_message_index', 
            "警报频繁度": 'alert_index', 
            "设备活跃度": 'active_device_index'
        }
        user_tag = "设备"
        radarData=[]
        active_index = get_active_index()
        for tag in item_tag_list:
            radarData.append({
                'item': tag,
                'score':active_index[tag_key_map[tag]],
                'user':user_tag
            })

        return jsonify({'message': "雷达信息加载成功!",
                        'signal': "success",
                        'radarData': radarData
                        }), 200

    except Exception as e:
        logging.exception(e)
        session.rollback()
        return jsonify({'message': "设备查询失败",
                        'signal': "fail"}), 200

if __name__ == '__main__':

    api.run(debug=False, port=5001, host='127.0.0.1')
