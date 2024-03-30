import os
from threading import Thread
from time import sleep, ctime


def account_server():
    os.system("python ./account_api.py")
def device_server():
    os.system("python ./device_api.py")
def iotmessage_server():
    os.system("python ./iotmessage_api.py")
def mqtt_server():
    os.system("python ./mqtt_server.py")
def mqtt_clients():
    os.system("python ./mqtt_clients.py")


if __name__=="__main__":
    try:
        print("设备模拟器开始发送消息")
        print("设备模拟器BS后端开始运行")
        print("关闭请按Ctrl+C")
        thread_list=[
            Thread(target=mqtt_clients),
            Thread(target=account_server),
            Thread(target=device_server),
            Thread(target=iotmessage_server),
            Thread(target=mqtt_server)
        ]
        for thread in thread_list:
            thread.start()
        for thread in thread_list:
            thread.join()
    except:
        print("BS后端关闭成功")