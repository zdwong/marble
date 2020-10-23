## Build and Run Docker Image
apt-get update && apt-get install docker-engine && service docker start

docker build -t **tag_name**

docker run -d -it -p 80:8080 -v /ssd:/ssd -v /home:/home **tag_name**

docker exec -it **container_id** bash

## Push docker 
docker login addr

docker commit -a wong -m "Seq-FIQ" -p **container_id** addr/name/seq-fiq:v0

docker push addr/name/seq-fiq:v0


### Difference of docker and nvidia-docker command
In old version, nvidia-docker for GPU while docker for CPU

In new version, docker can for GPU and CPU

### Note
1. pip install -i  https://pypi.tuna.tsinghua.edu.cn/simple numpy   **change install source address** 
2. Change apt-get install source address
3. conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free/
4. conda config --set show_channel_urls yes

### Add ~/.condarc
channels:
  
  - defaults
  
show_channel_urls: true

channel_alias: https://mirrors.tuna.tsinghua.edu.cn/anaconda
default_channels:
  - https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main
  - https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free
  - https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/r
  - https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/pro
  - https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/msys2
custom_channels:
  conda-forge: https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud
  msys2: https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud
  bioconda: https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud
  menpo: https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud
  pytorch: https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud
  simpleitk: https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud
