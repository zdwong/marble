## Linux Command

### File Operation

#### sort & wc
  > sort -t "," -k 2,2 **file**
  
  > cat small_face.csv | awk -F, '{print $2}' | sort -u | wc -l

#### find

  > find . -name "*.py" | xargs grep -l "mx\.symbol\.Scale"
  
  > find . -type d -name "img*" -exec rm -rf {} \;
  
  > find sourcePath/ -name "*.txt" -exec mv {} targetPath/ \;
  
#### du & df
  > du -sh .
  
  > df -hl 

### Process Management

#### kill
  > ps -aux  |  grep python  | grep -v grep | cut -c 9-15  |  xargs kill -s 9

####  top & free

### Text Processing

#### sed
  > sed -i "s/origin/dst/g"  filename  ；-i inplace edit 
  
  > sed 's/^[ ]*//g' filename
  
  > sed -i '/*pattern*/d' filename
  
#### vim 
  > :%s/origin/dst/g
  
#### awk 
  > awk -F ':' '{print $1}' /etc/passwd
  
  > netstat -ntpl | awk ' $3>0 {print $0}'
  
  > awk -F: '$1 ~ /root|admin/{print}' /etc/passwd
  
### Git
#### git 
  > git status | grep typechange | awk '{print $2}' | xargs git checkout
  
  > git log && git reset --hard **commit_id**

  > git merge branch
  
#### Docker
  > docker image prune -a
  
  > docker stop container_id
  
  > docker rm container_id
  
  > docker image ls
  
  > docker image rm image_id
  
  > docker build -t tag_name

  > docker run -d -it -p 80:8080 -v /ssd:/ssd -v /home:/home tag_name

  > docker exec -it container_id bash
  
 #### SSH
  > sshpass -p password scp -r -P 22 /var/data root@172.20.10.4:/home/
