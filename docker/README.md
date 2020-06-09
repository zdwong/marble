## Build and Run Docker Image
sudo apt-get update && apt-get install docker-engine && service docker start

docker build -t **tag_name**

docker run -d -it -p 80:8080 -v /ssd:/ssd -v /home:/home **tag_name**

docker exec -it **container_id** bash
