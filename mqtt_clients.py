import paho.mqtt.client as mqtt_client
import json
from database_connect import *
import random
# 当连接成功时的回调函数
random.seed(int(time.time()))


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"{userdata['device_id']} connect to mqtt server!")


# 当收到消息时的回调函数
def on_message(client, userdata, msg):
    session = Session()
    iot_massage_json = json.loads(msg.payload.decode())
    iot_massage = IotMessage(**iot_massage_json)
    session.add(iot_massage)
    session.commit()


info_list = ['辛勤的蜜蜂永没有时间悲哀',
             '我这个人走得很慢，但是我从不后退',
             '一个人几乎可以在任何他怀有无限热忱的事情上成功',
             '深窥自己的心，而后发觉一切的奇迹在你自己',
             '失败也是我需要的，它和成功对我一样有价值',
             '人需要真理，就像瞎子需要明快的引路人一样',
             '任何问题都有解决的办法，无法可想的事是没有的',
             '每一种挫折或不利的突变，是带着同样或较大的有利的种子',
             '如果是玫瑰，它总会开花的',
             '失败是坚忍的最后考验',
             '善于利用零星时间的人，才会做出更大的成绩来',
             '少而好学，如日出之阳；壮而好学，如日中之光；老而好学，如炳烛之明',
             '生活的情况越艰难，我越感到自己更坚强，甚而也更聪明',
             '如果我比笛卡尔看得远些，那是因为我站在巨人们的肩上的缘故',
             '一次失败，只是证明我们成功的决心还够坚强',
             '对于不屈不挠的人来说，没有',
             '人生应该如蜡烛一样，从顶燃到底，一直都是光明的',
             '人生的价值，即以其人对于当代所做的工作为尺度',
             '我们关心的，不是你是否失败了，而是你对失败能否无怨',
             '人生不是一种享乐，而是一桩十分沉重的工作',
             '但愿每次回忆，对生活都不感到负疚',
             '人的一生可能燃烧也可能腐朽，我不能腐朽，我愿意燃烧起来!',
             '你若要喜爱你自己的价值，你就得给世界创造价值',
             '社会犹如一条船，每个人都要有掌舵的准备',
             '人生不是一种享乐，而是一桩十分沉重的工作',
             '人生的价值，并不是用时间，而是用深度去衡量的',
             '人只有献身于社会，才能找出那短暂而有风险的生命的意义',
             '芸芸众生，孰不爱生?爱生之极，进而爱群',
             '生活真象这杯浓酒，不经三番五次的提炼呵，就不会这样可口!',
             '充满着欢乐与斗争精神的人们，永远带着欢乐，欢迎雷霆与阳光',
             '生命的意义在于付出，在于给予，而不是在于接受，也不是在于争取',
             '时间是伟大的作者，她能写出未来的结局',
             '为了生活中努力发挥自己的作用，热爱人生吧',
             '希望是附丽于存在的，有存在，便有希望，有希望，便是光明',
             '沉沉的黑夜都是白天的前奏',
             '当一个人用工作去迎接光明，光明很快就会来照耀着他',
             '东天已经到来，春天还会远吗?',
             '过去属于死神，未来属于你自己',
             '世间的活动，缺点虽多，但仍是美好的',
             '辛勤的蜜蜂永没有时间悲哀',
             '希望是厄运的忠实的姐妹',
             '当你的希望一个个落空，你也要坚定，要沉着!',
             '先相信你自己，然后别人才会相信你',
             '宿命论是那些缺乏意志力的弱者的借口',
             '我们唯一不会改正的缺点是软弱',
             '人人好公，则天下太平；人人营私，则天下大乱',
             '自私自利之心，是立人达人之障',
             '如烟往事俱忘却，心底无私天地宽',
             '常求有利别人，不求有利自己',
             '一切利己的生活，都是非理性的，动物的生活',
             '人的理性粉碎了迷信，而人的感情也将摧毁利己主义',
             '无私是稀有的道德，因为从它身上是无利可图的',
             '生活只有在平淡无味的人看来才是空虚而平淡无味的',
             '一个人的价值，应该看他贡献什么，而不应当看他取得什么',
             '知识是珍宝，但实践是得到它的钥匙',
             '自然赐给了我们知识的种子，而不是知识的本身',
             '坚强的信念能赢得强者的心，并使他们变得更坚强',
             '清贫，洁白朴素的生活，正是我们革命者能够战胜许多困难的地方!',
             '不幸可能成为通向幸福的桥梁',
             '苦难磨炼一些人，也毁灭另一些人',
             '过去属于死神，未来属于你自己',
             '真正的人生，只有在经过艰难卓绝的斗争之后才能实现',
             '当一个人用工作去迎接光明，光明很快就会来照耀着他',
             '幸运并非没有恐惧和烦恼；厄运也决非没有安慰和希望',
             '勿问成功的秘诀为何，且尽全力做你应该做的事吧',
             '多数人都拥有自己不了解的能力和机会，都有可能做到未曾梦想的事情',
             '那脑袋里的智慧，就像打火石里的火花一样，不去打它是不肯出来的',
             '坚强的信念能赢得强者的心，并使他们变得更坚强',
             '生活的全部意义在于无穷地探索尚未知道的东西，在于不断地增加更多的知识',
             '壮心未与年俱老，死去犹能作鬼雄',
             '故立志者，为学之心也；为学者，立志之事也',
             '贫不足羞，可羞是贫而无志',
             '我们以人们的目的来判断人的活动',
             '目的伟大，活动才可以说是伟大的',
             '毫无理想而又优柔寡断是一种可悲的心理',
             '生活的理想，就是为了理想的生活',
             '人，只要有一种信念，有所追求，什么艰苦都能忍受，什么环境也都能适应',
             '理想的人物不仅要在物质需要的满足上，还要在精神旨趣的满足上得到表现',
             '生命多少用时间计算，生命的价值用贡献计算',
             '时间，就象海棉里的水，只要愿挤，总还是有的']


if __name__ == '__main__':
    session = Session()
    device_list = session.query(Device).all()
    random.shuffle(device_list)
    device_list = device_list[:int(len(device_list)*0.8)]
    device_client_list = []
    for device in device_list:
        client = mqtt_client.Client()
        client.user_data_set({"device_id": device.device_id})
        client.on_connect = on_connect
        client.connect("127.0.0.1", 1883, 6000)
        device_client_list.append(client)
    while (True):
        index = random.randint(0, len(device_list)-1)
        temperature = random.randint(0, 100)
        if temperature <= 80:
            alert = 0
        else:
            alert = 1
        info = random.choice(info_list)
        longitude = 119.9 + random.random() * 0.6
        latitude = 30.1 + random.random() * 0.4
        """
        {"alert":0,
        "device_id":"device0001",
        "device_name":"无人机",
        "info":"Device Data 2023/12/24 19:32:38",
        "latitude":30.39648098945618,
        "longitude":120.40087410211564,
        "timestamp":1703417558188,
        "value":43}"""
        message = {"device_id": device_list[index].device_id,
                   "device_name": device_list[index].device_name,
                   "timestamp": int(1000*time.time()),
                   "alert": alert,
                   "info": info,
                   "latitude": latitude,
                   "longitude": longitude,
                   "value": temperature}
        device_client_list[index].publish(
            topic="testapp", payload=json.dumps(message))
        time.sleep(random.randint(1, 3))
