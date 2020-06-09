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
  > sed -i "s/origin/dst/g"  file  ；-i inplace edit 
  
  > sed 's/^[ ]*//g' filename
  
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
