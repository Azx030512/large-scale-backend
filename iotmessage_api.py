import copy
from flask import Flask, jsonify
from flask import make_response
from flask import request
from flask import abort
from database_connect import *

import logging
logger = logging.getLogger("console_logger")
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

api = Flask('iotmessage_api')


@api.route('/api/iotmessage_api/querymessage', methods=['POST', 'get'])
def query_message():
    # request.json里面包含请求数据，如果不是JSON或者里面没有包含title字段
    try:
        session = Session()
        requirement_json = request.json
        newest_k = 10
        if 'newest_k' in requirement_json:
            newest_k = requirement_json['newest_k']
        elif 'pageNo' in requirement_json:
            parameter = {
                'pageNo': requirement_json['pageNo'], 'pageSize': requirement_json['pageSize']}

        if 'device_id' in requirement_json and requirement_json['device_id'] != 'all':
            specify_device_id = requirement_json['device_id']
            results = session.query(IotMessage).filter_by(
                device_id=specify_device_id).all()
            results.sort(key=lambda x: x.timestamp, reverse=True)
        else:
            results = session.query(IotMessage).all()
            results.sort(key=lambda x: x.timestamp, reverse=True)
        if 'threshold' in requirement_json:
            filtered_results = []
            for message in results:
                if message.value > float(requirement_json['threshold']):
                    filtered_results.append(message)
            results = filtered_results
        '''{pageSize: 10, pageNo: 1, totalCount: 5701, totalPage: 571, data:[...]'''

        if 'pageNo' in requirement_json:
            result = {}
            data = []
            for message in results[(parameter['pageNo']-1)*parameter['pageSize']: parameter['pageNo']*parameter['pageSize']]:
                data.append(message.show_info(accuracy=1))
            session.close()
            result.update(parameter)
            result['totalCount'] = len(results)
            result['totalPage'] = result['totalCount']//parameter['pageSize']
            result['data'] = data
            return jsonify({'message': "消息列表查询成功！",
                            'signal': "success",
                            'result': result
                            }), 200
        else:
            message_list = []
            for message in results[:newest_k]:
                message_list.append(message.show_info())
            session.close()
            return jsonify({'message': "消息列表查询成功！",
                            'signal': "success",
                            'message_list': message_list
                            }), 200

    except Exception as e:
        logging.exception(e)
        session.rollback()
        return jsonify({'message': "消息列表查询失败！",
                        'signal': "fail"}), 500


@api.route('/api/iotmessage_api/statisticquery', methods=['POST', 'get'])
def statistic_query():
    try:
        session = Session()
        requirement_json = request.json
        active_threshold = 50
        messages = session.query(IotMessage).all()
        messages.sort(key=lambda x: x.timestamp, reverse=True)
        message_number = len(messages)
        devices = session.query(Device).all()
        device_number = len(devices)
        recenct_messages = messages[:active_threshold]
        active_devices = set([item.device_id for item in recenct_messages])
        active_device_number = len(active_devices)
        alert_number = sum([item.alert for item in messages])
        statistic = {
            'message_number': message_number,
            'device_number': device_number,
            'active_device_number': active_device_number,
            'alert_number': alert_number
        }
        session.close()
        return jsonify({'message': "消息列表查询成功！",
                        'signal': "success",
                        'statistic': statistic,
                        }), 200

    except Exception as e:
        logging.exception(e)
        session.rollback()
        return jsonify({'message': "新设备绑定失败！",
                        'signal': "fail"}), 500


@api.route('/api/iotmessage_api/positionquery', methods=['POST', 'get'])
def position_query():
    try:
        session = Session()
        requirement_json = request.json
        specify_device_id = 'all'
        if 'device_id' in requirement_json:
            specify_device_id = requirement_json['device_id']
        '''{ lng: 116.404, lat: 39.915 }'''
        devices = session.query(Device).all()
        positions = []
        track = []
        if specify_device_id == 'all':
            for device in devices:
                messages = session.query(IotMessage).filter_by(
                    device_id=device.device_id).all()
                messages.sort(key=lambda x: x.timestamp, reverse=True)
                if len(messages)==0:
                    continue
                positions.append( {'lng': messages[0].longitude, 'lat':messages[0].latitude,'tag':messages[0].device_id, 'color':"blue" } )
        else:
            messages = session.query(IotMessage).filter_by(
                device_id=specify_device_id).all()
            messages.sort(key=lambda x: x.timestamp, reverse=True)
            for i in range(0, min(len(messages), 50), 10):
                positions.append({'lng': messages[i].longitude, 'lat':messages[i].latitude, 'tag':((str(i)+'min前' if i!=0 else "现在")+(" "+"报警" if messages[i].alert else "正常")), 'color':("red" if messages[i].alert else "blue") } )
                track.append({'lng': messages[i].longitude, 'lat':messages[i].latitude})

        session.close()
        return jsonify({'message': "设备位置查询成功！",
                        'signal': "success",
                        'positions': positions,
                        'track':track
                        }), 200

    except Exception as e:
        logging.exception(e)
        session.rollback()
        return jsonify({'message': "设备位置查询成功失败！",
                        'signal': "fail"}), 200


@api.route('/api/iotmessage_api/chartdataquery', methods=['POST', 'get'])
def chart_data_query():
    try:
        session = Session()
        # requirement_json = request.json
        devices = session.query(Device).all()
        result = {}

        x = []
        date_list = []
        current_time = time.localtime()
        current_time_dict = {
            'year': current_time.tm_year,
            'month': current_time.tm_mon,
            'day': current_time.tm_mday,
        }
        current_date = datetime(**current_time_dict)
        for i in range(-1, 7):
            temp_date = time.strftime("%Y-%m-%d",time.localtime(time.time()-i*24*60*60))
            date_list.append(datetime.fromisoformat(temp_date))
            
        date_list.reverse()
        for temp_date in date_list[:-1]:
            x.append(temp_date.isoformat().split('T')[0])

        messages = session.query(IotMessage).all()
        messages.sort(key=lambda x: x.timestamp, reverse=True)
        session.close()

        date_cluster = {}
        for item in x:
            date_cluster[item] = []

        for message in messages:
            for i in range(len(x)):
                if date_list[i] < message.timestamp < date_list[i+1]:
                    date_cluster[date_list[i].isoformat().split('T')[
                        0]].append(message)
                else:
                    continue

        chart1_dataflow = {'x': x}
        data_flow = []
        for key in x:
            data_flow.append(compute_dataflow(date_cluster[key]))
        chart1_dataflow['data_flow'] = [
            {'x': x[i], 'y': data_flow[i]} for i in range(len(data_flow))]
        chart1_dataflow['average'] = round(sum(data_flow)/(len(data_flow)+1), 2)
        result['chart1_dataflow'] = chart1_dataflow

        chart2_activedevice = {'x': x}
        activedevice = []
        for key in x:
            activedevice.append(compute_activedevice(date_cluster[key]))
        chart2_activedevice['activedevice'] = [
            {'x': x[i], 'y': activedevice[i]} for i in range(len(activedevice))]
        chart2_activedevice['average'] = round(
            sum(activedevice)/(len(activedevice)+1), 2)
        result['chart2_activedevice'] = chart2_activedevice

        chart3_alerts = {'x': x}
        alerts = []
        for key in x:
            alerts.append(compute_alerts(date_cluster[key]))
        chart3_alerts['alerts'] = [
            {'x': x[i], 'y': alerts[i]} for i in range(len(alerts))]
        chart3_alerts['average'] = round(sum(alerts)/(len(alerts)+1), 2)
        result['chart3_alerts'] = chart3_alerts

        chart4_values = {'x': x}
        values = []
        for key in x:
            values.append(compute_values(date_cluster[key]))
        chart4_values['values'] = [
            {'x': x[i][5:], 'y': values[i]} for i in range(len(values))]
        chart4_values['average'] = round(sum(values)/(len(values)+1), 2)
        result['chart4_values'] = chart4_values

        chart5_times = {'x': x}
        times = []
        for key in x:
            times.append(compute_dataflow(
                date_cluster[key], per_data_volume=2))
        chart5_times['times'] = [{'x': x[i][5:], 'y': times[i]}
                                 for i in range(len(times))]
        chart5_times['average'] = round(sum(times)/(len(times)+1), 2)
        result['chart5_times'] = chart5_times

        device_cluster = {}
        device_id_set = set([item.device_id for item in messages])
        for item in device_id_set:
            device_cluster[item] = []

        for message in messages:
            device_cluster[message.device_id].append(message)

        rank1_values = []
        '''rankList.push({
            name: '设备编号: ' + (i + 1),
            total: 224 - i * 10
        })'''

        for key in device_cluster:
            rank1_values.append({
                'name': "设备ID: "+key,
                'total': compute_values(device_cluster[key])
            })

        result['rank1_values'] = sorted(
            rank1_values, key=lambda x: x['total'], reverse=True)

        rank2_times = []

        for key in device_cluster:
            rank2_times.append({
                'name': "设备ID: "+key,
                'total': compute_dataflow(device_cluster[key], per_data_volume=2)
            })

        result['rank2_times'] = sorted(
            rank2_times, key=lambda x: x['total'], reverse=True)

        '''const sourceData = [
        { item: '家用电器', count: 32.2 },
        { item: '食用酒水', count: 21 },
        { item: '个护健康', count: 17 },
        { item: '服饰箱包', count: 13 },
        { item: '母婴产品', count: 9 },
        { item: '其他', count: 7.8 }
        ]'''

        id_type_map = {}
        for device in devices:
            id_type_map[device.device_id] = device.device_type

        pie1_dataflow = []
        total_dataflow = compute_dataflow(messages, per_data_volume=2)

        device_type_cluster = {}
        device_type_set = set(
            [id_type_map.get(item.device_id, '手机') for item in messages])
        for key in device_type_set:
            device_type_cluster[key] = []

        for message in messages:
            device_type_cluster[id_type_map.get(
                message.device_id, '手机')].append(message)

        for device_type in device_type_set:
            pie1_dataflow.append({
                'item': device_type,
                'count': round(compute_dataflow(device_type_cluster[device_type], per_data_volume=2)/total_dataflow * 100, 2)
            })

        result['pie1_dataflow'] = pie1_dataflow

        return jsonify({'message': "数据查询成功！",
                        'signal': "success",
                        'result': result
                        }), 200

    except Exception as e:
        logging.exception(e)
        session.rollback()
        return jsonify({'message': "设备信息查询失败！",
                        'signal': "fail"}), 200


@api.route('/api/iotmessage_api/singledevicequery', methods=['POST', 'get'])
def single_device_query():
    try:
        session = Session()
        requirement_json = request.json
        devices = session.query(Device).all()
        if 'device_id' in requirement_json:
            specify_device_id = requirement_json['device_id']
        messages = session.query(IotMessage).all()
        messages.sort(key=lambda x: x.timestamp, reverse=True)
        session.close()
        result = {}
        device_cluster = {}
        device_id_set = set([item.device_id for item in messages])
        for item in device_id_set:
            device_cluster[item] = []

        for message in messages:
            device_cluster[message.device_id].append(message)

        latest_messages = []
        for i in range(0, min(len(device_cluster[specify_device_id]), 50), 10):
            latest_messages.append(device_cluster[specify_device_id][i])

        chart6_values = []
        for i, key in enumerate(['40min前', '30min前', '20min前', '10min前', '现在']):
            chart6_values.append({
                'x': key,
                'y': latest_messages[4-i].value
            }
            )

        chart7_dataflow = []
        for i, key in enumerate(['40min前', '30min前', '20min前', '10min前', '现在']):
            chart7_dataflow.append({
                'x': key,
                'y': round(8*latest_messages[4-i].value**0.5,1)
            }
            )
        

        return jsonify({'message': "单个设备信息查询成功！",
                        'signal': "fail",
                        "chart6_values": chart6_values,
                        "chart6_now": latest_messages[0].value,
                        "chart7_dataflow": chart7_dataflow,
                        "chart7_now": round(8*latest_messages[0].value**0.5,1)
                        }), 200

    except Exception as e:
        logging.exception(e)
        session.rollback()
        return jsonify({'message': "单个设备信息查询失败！",
                        'signal': "fail"}), 200


def compute_dataflow(messages, per_data_volume=0.2):
    return len(messages) * per_data_volume


def compute_activedevice(messages):
    device_set = set([item.device_id for item in messages])
    return len(device_set)


def compute_alerts(messages):
    alerts = sum([item.alert for item in messages])
    return alerts


def compute_values(messages):
    if len(messages) == 0:
        return 0
    values = sum([item.value for item in messages])/len(messages)
    return round(values, 2)


if __name__ == '__main__':
    api.run(debug=False, port=5002, host='127.0.0.1')
    # chart_data_query()
