# Building an App Monitoring Environment using Telegraf, InfluxDB and Kubernetes

The containirization technology is applied nearly in all projects due to many reasons such as the easy management, isolation of the apps, rapid deployment, etc. To enable this technology, the docker is probably one of the most used container technology so far. Even it is well known and highly used software, it is management capabilities are limited in case the management complexity increases. At this point, a container managemenet and orchestration systems come in the play. Kuberenetes, known also as K8s, is by far the most well-known orchestration tool for the time being. The structure of the nodes, the distribution of the pods on the nods, different container deployment and scheduling strategies and an open API to the developer enabling the interaction with the internal component of the kubernetes converts it to highly scalable platform, on which a developer can apply her own strategies considering the environment conditions.

In the following Medium article, it is shown how a telegraf and influxdb softwares can be deployed in a kubernetes cluster without diving in the kubernetes details.

https://akpolatcem.medium.com/building-an-app-monitoring-environment-using-telegraf-influxdb-and-kubernetes-770b9861b3ce
