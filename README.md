# Telegraf InfluxDB Kubernetes Example

The containirization technology is applied nearly in all projects due to many reasons such as the easy management, isolation of the apps, rapid deployment, etc. To enable this technology, the docker is probably one of the most used container technology so far. Even it is well known and highly used software, it is management capabilities are limited in case the management complexity increases. At this point, a container managemenet and orchestration systems come in the play. Kuberenetes, known also as K8s, is by far the most well-known orchestration tool for the time being. The structure of the nodes, the distribution of the pods on the nods, different container deployment and scheduling strategies and an open API to the developer enabling the interaction with the internal component of the kubernetes converts it to highly scalable platform, on which a developer can apply her own strategies considering the environment conditions.

In this article, it will be shown how a telegraf and influxdb softwares can be deployed in a kubernetes cluster without diving in the kubernetes details. In the previous article[add here the link], how a similar system can be deployed via docker containers. In order to simplify the understanding steps, the scenario is kept much more simplier. 

The scenario is based on the measurement of the internal memory, CPU usage of telegraf container, a python application offers a REST interface and this data will be delivered into the influxdb cluster. To extend this example to cover more sensors connected to the telegraf, you may utilize the previous article, however, keep in mind that you need to also expand the existing kuberneter configuration.

The development of the system components are composed of the following steps:

1. Telegraf Configuration
2. Implement Python Application& Build its Docker Image
3. Kubernetes Configuration
4. Understanding Kubernetes Logic

## 1. Telegraf Configuration

The configuration of the telegraf.conf file isnt' complicated. It can start with an agent configuration that expains how the telegraf software behave such as the interval of the data collection period, collection jitter, etc. In case this is n't defined, a default configuration will be used. 

The rest is constructed on the input and output processes. In this example, there is no processors and aggregators. Three inputs are defined, cpu, mem and http. By default, cpu and mem delivers the CPU and memory of the container in which telegraf runs. There is no additional code requirement. For the `http` case, this is different, since the intention is to connect a python REST interface to the telegraf. All details for this input such as HTTP URL, the interval for the data aggregation frequency, the name of the metrics when they appear in influxdb, and JSON data format are provided. The final configuration belongs to the influxdb. The URL address of URL is default, hwoever, the `token`, `organization`, and `bucket` are first generated when the application is booted. Most probably, there is way to automate this process, however, this is not the focus of this example. In this example[link], how the required parmaters should be created are detailled.

```
    [[inputs.cpu]]
    [[inputs.mem]]

    [[inputs.http]]
      urls = ["http://app:5000/random-data"]
      interval = "10s"
      name_override = "app_metrics"
      method = "GET"
      timeout = "5s"
      data_format = "json"


    [[outputs.influxdb_v2]]
      urls = ["http://influxdb:8086"]
      token = "8ETqAttnAv1QQNS9UBX1MyE2Q_Q_nlCv5Hm-D_LlWjFqX_Kh5QBPZHJOH5l4wCow1Kiip0zt6E3qFuRmufpsiw=="
      organization = "org"
      bucket = "bucket"
```

The telegraf configuration is ready, only the token name will be changed in case you use the same organization and bucket name. 

## 2. Implement Python Application& Build its Docker Image

Developing a python serving a REST interface doesn't require too much effort, and below it is simply the python code, the required libraries and the needed Dockerfile are placed.

```
from flask import Flask, jsonify
import random

app = Flask(__name__)

@app.route('/random-data', methods=['GET'])
def get_random_data():
    # Generate random data (replace with your actual data generation logic)
    random_value = random.randint(1, 100)
    return jsonify({"random_metric": random_value})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

```

The required libraries are written in the `requirements.txt` file.
```
Flask==2.0.1
requests==2.26.0
```
The Dockerfile for building a Docker image from the python code can be realized via the following code, which selects a based image, creates an app folder as a working directory, copy the `requirements.txt` file into this folder, install these libraries via `pip` tool, copy the `app.py` in the `app/` folder and finally executes the `app.py` file.

```
FROM python:3.8-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

CMD ["python", "app.py"]

```
A successfull image generation can be performed with the commandline below:

`docker build -t random_data_app .`
Once the image is built, you may check whether its is available in the docker images via `docker images | grep random_data_app` command on the terminal.


## 3. Kubernetes Configuration

Assuming that you have in your environment at least one node,  kubectl is installed and a docker image is generated for the python app. Now, our single purpose is to create a kubernetes cluster in which all these softeware run in a harmony, the telegraf aggregates the data, forwards in the influxdb, and to observe the incoming data in the influxdb through a web interface. 

To realize all these components, the following things should be takne into account.
1. Python app necessitates a deployment to place it as a pod, and a service so that other services can access it.
2. Telegraf requires a deployment to place it as a pod, a service to make it acessible to other pods, and a configMap for the telegraf.conf data.
3. InfluxDB requires a deployment to run it in a pod, and a service to make it open to the usage of other pods, as well as an additional service either nodeport or loadbalancer to enable its access on the web browser.

### Kubernetes Config for Python App


```
---
apiVersion: v1
kind: Service
metadata:
  name: app
  namespace: your-namespace
  labels:
    app: app
spec:
  selector:
    app: app
  ports:
    - protocol: TCP
      port: 5000 # The port your Python app listens on
      targetPort: 5000 # The port your Python app listens on within the container
---

apiVersion: apps/v1
kind: Deployment
metadata:
  name: app
  namespace: your-namespace
  labels:
    app: app
spec:
  replicas: 0
  selector:
    matchLabels:
      app: app
  template:
    metadata:
      labels:
        app: app
    spec:
      containers:
        - name: app
          image: app:latest
          imagePullPolicy: Never  # or IfNotPresent
          ports:
            - containerPort: 5000




---

```

### Kubernetes Config for Telegraf

```

---

apiVersion: v1
kind: ConfigMap
metadata:
  name: telegraf-config
  namespace: your-namespace
data:
  telegraf.conf: |
    [global_tags]
      # Add any global tags here

    [agent]
      interval = "10s" # Adjust the interval as per your requirements
      round_interval = true
      metric_batch_size = 1000
      metric_buffer_limit = 10000
      collection_jitter = "0s"
      flush_interval = "10s"
      flush_jitter = "0s"
      precision = ""
      hostname = "" # Set the hostname for identifying metrics source


    [[inputs.cpu]]
    [[inputs.mem]]

    [[inputs.http]]
      urls = ["http://app:5000/random-data"]
      interval = "10s"
      name_override = "app_metrics"
      method = "GET"
      timeout = "5s"
      data_format = "json"


    [[outputs.influxdb_v2]]
      urls = ["http://influxdb:8086"]
      token = "8ETqAttnAv1QQNS9UBX1MyE2Q_Q_nlCv5Hm-D_LlWjFqX_Kh5QBPZHJOH5l4wCow1Kiip0zt6E3qFuRmufpsiw=="
      organization = "org"
      bucket = "bucket"

---


apiVersion: apps/v1
kind: Deployment
metadata:
  name: telegraf
  namespace: your-namespace
spec:
  replicas: 0 # Adjust the number of replicas as needed
  selector:
    matchLabels:
      app: telegraf
  template:
    metadata:
      labels:
        app: telegraf
    spec:
      containers:
        - name: telegraf
          image: telegraf:latest # Replace with the Telegraf image name and version
          volumeMounts:
            - name: config-volume
              mountPath: /etc/telegraf
      volumes:
        - name: config-volume
          configMap:
            name: telegraf-config

---
apiVersion: v1
kind: Service
metadata:
  name: telegraf-service
  namespace: your-namespace
spec:
  selector:
    app: telegraf  # Replace with the appropriate label for your Telegraf Deployment
  ports:
    - protocol: TCP
      port: 8181  # The port Telegraf listens on
      targetPort: 8181  # The port Telegraf listens on within the container

---
```

### Kubernetes Config for InfluxDB


```
---

apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: influxdb-pvc
  namespace: your-namespace
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi # Adjust storage size as needed

---

apiVersion: apps/v1
kind: Deployment
metadata:
  name: influxdb
  namespace: your-namespace
spec:
  replicas: 0
  selector:
    matchLabels:
      app: influxdb
  template:
    metadata:
      labels:
        app: influxdb
    spec:
      containers:
        - name: influxdb
          image: influxdb:latest
          ports:
            - containerPort: 8086
          volumeMounts:
            - name: influxdb-storage
              mountPath: /var/lib/influxdb
      volumes:
        - name: influxdb-storage
          persistentVolumeClaim:
            claimName: influxdb-pvc

---

apiVersion: v1
kind: Service
metadata:
  name: influxdb
  namespace: your-namespace
spec:
  selector:
    app: influxdb
  ports:
    - protocol: TCP
      port: 8086
      targetPort: 8086

---

apiVersion: v1
kind: Service
metadata:
  name: influxdb-nodeport
  namespace: your-namespace
spec:
  selector:
    app: influxdb
  type: NodePort
  ports:
    - protocol: TCP
      port: 8086
      targetPort: 8086
      nodePort: 30001 # Choose any available port number in your range

```

Starting 

## 4. Understanding Kubernetes Logic


1. Telegraf Configuration
2. Implement Python Application& Build its Docker Image
3. Kubernetes Configuration
4. Understanding Kubernetes Logic

## Summary