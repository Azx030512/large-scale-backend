from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, TIMESTAMP, Double
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from datetime import datetime
import time
import random

# python2: MySQLdb
# python3: pymysql
# 使用create_engine建立同数据库的连接，返回的是一个Engine实例
# 指向数据库的一些核心的接口
# echo=True， 可以在控制台看到操作涉及的SQL语言


# 声明基类
Base = declarative_base()


# 基于这个基类来创建我们的自定义类，一个类就是一个数据库表
class Account(Base):
    __tablename__ = 'account'
    user_name = Column(String(255), nullable=False, primary_key=True)
    password = Column(String(512), nullable=False)
    email = Column(String(30), nullable=False, unique=True)
    md5 = Column(String(512), nullable=False)
    phone = Column(String(20), nullable=False)
    # date = Column(Date, nullable=False)
    info_keys = ['user_name', 'password', 'email', 'phone']

    def __repr__(self):
        return self.user_name

    def __init__(self, user_name, password, email, md5, phone):
        self.user_name = user_name
        self.password = password
        self.email = email
        self.md5 = md5
        self.phone = phone

    def show_info(self):
        information = {}
        for key in self.info_keys:
            information[key] = self.__getattribute__(key)
        return information


class Device(Base):
    __tablename__ = 'device'
    device_id = Column(String(50), nullable=False, primary_key=True)
    device_name = Column(String(50), nullable=False)
    device_type = Column(String(20), nullable=False)
    creation_date = Column(DateTime, nullable=False)
    description = Column(String(100), nullable=True)
    avatar_flag = Column(Integer, nullable=True)
    info_keys = ['device_id', 'device_name',
                 'device_type', 'creation_date', 'description', 'avatar_flag']

    def __repr__(self):
        return self.device_id

    def __init__(self, device_id, device_name, device_type, description='还没有添加设备描述'):
        self.device_id = device_id
        self.device_name = device_name
        self.device_type = device_type
        current_time = time.localtime()
        current_time_dict = {
            'year': current_time.tm_year,
            'month': current_time.tm_mon,
            'day': current_time.tm_mday,
            'hour': current_time.tm_hour,
            'minute': current_time.tm_min,
            'second': current_time.tm_sec,
        }
        self.creation_date = datetime(**current_time_dict)
        self.description = description
        self.avatar_flag = random.randint(0, 10)

    def show_info(self):
        information = {}
        for key in self.info_keys:
            information[key] = self.__getattribute__(key)
        return information


class IotMessage(Base):
    __tablename__ = 'iotmessage'
    device_id = Column(String(50), nullable=False, primary_key=True)
    device_name = Column(String(50), nullable=False)
    message_id = Column(Integer, autoincrement=True, primary_key=True)
    timestamp = Column(DateTime, nullable=False)
    alert = Column(Integer, nullable=False)
    info = Column(String(200), nullable=False)
    latitude = Column(Double, nullable=False)
    longitude = Column(Double, nullable=False)
    # 以下内容暂定
    value = Column(Integer, nullable=False)
    info_keys = ['device_id', 'message_id', 'timestamp',
                 'alert', 'info', 'latitude', 'longitude', 'device_name','value']

    def __repr__(self):
        return self.device_id+'-'+str(self.timestamp)

    def __init__(self, device_id, device_name, timestamp, alert, info, latitude, longitude, value):
        self.device_id = device_id
        self.device_name = device_name
        if type(timestamp) == int:
            self.timestamp = datetime.fromtimestamp(timestamp/1000)
        else:
            self.timestamp = timestamp
        self.alert = alert
        self.info = info
        self.latitude = latitude
        self.longitude = longitude
        # 以下内容暂定
        self.value = value

    def show_info(self, accuracy=None):
        information = {}
        for key in self.info_keys:
            information[key] = self.__getattribute__(key)
        if accuracy is not None:
            information['latitude'] = round(information['latitude'], accuracy)
            information['longitude'] = round(information['longitude'], accuracy)
        return information

try:
    port = "3306"
    engine = create_engine(
        "mysql+pymysql://root:lyh031026@116.62.11.140:"+port+"/mqtt", echo=True)
        
    # 检查表的存在性，如果不存在的话会执行表的创建工作
    Base.metadata.create_all(bind=engine)
    # 创建缓存对象
    Session = sessionmaker(bind=engine)
    print("mysql use port 3306")
except:
    time.sleep(5)
    port = "3306"
    engine = create_engine(
        "mysql+pymysql://root:azx@127.0.0.1:"+port+"/mqtt", echo=True)
        
    # 检查表的存在性，如果不存在的话会执行表的创建工作
    Base.metadata.create_all(bind=engine)
    # 创建缓存对象
    Session = sessionmaker(bind=engine)
    print("mysql use port 3306")


if __name__ == '__main__':

    session = Session()
    devices = session.query(Device).all()
    for device in devices:
        print(device.show_info())
    session.close()
