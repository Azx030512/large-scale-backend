# readme

## build docker image

**构建docker时需要分别在前端和后端的目录下构建，/code/flask_server下有backend.dockerfile，mysql.dockerfile，mosquitto.dockerfile 3个文件需要构建**

```
docker build --file backend.dockerfile -t backend .

docker build --file mysql.dockerfile -t mysql .

docker build --file mosquitto.dockerfile -t mosquitto .
```



## single docker start up in turn

**依次运行4个docker镜像，确保先运行起mqtt broker和数据库后，再运行前端和后端代码，不然后端连接数据库时可能会出错**

### start database 

**如果使用windows或Mac，最好使用端口映射，可能本机的3306端口已经被本机数据库软件占用了，请关闭占用程序**

```
docker run --network=host -p 3306:3306 mysql
```

**如果使用Linux，可以直接使用本机网络**

```
docker run --network=host mysql  
```

### start mosquitto(mqtt broker)

**如果使用windows或Mac，最好使用端口映射，可能本机的1883端口已经被本机数据库软件占用了，请关闭占用的程序**

```
docker run --network=host -p 1883:1883 mosquitto 
```

**如果使用Linux，可以直接使用本机网络**

```
docker run --network=host mosquitto 
```

### start backend(Flask)

**如果使用windows或Mac，最好使用端口映射**

```
docker run --network=host -p 5000:5000 -p 5001:5001 -p 5002:5002  backend
```

**如果使用Linux，可以直接使用本机网络**

```
docker run --network=host  backend
```

