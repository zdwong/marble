## Linux Command

- sort & wc

  > sort -t "," -k 2,2 **file**
  
  > cat small_face.csv | awk -F, '{print $2}' | sort -u | wc -l

- find

  > find . -name "*.py" | xargs grep -l "mx\.symbol\.Scale"
  
  > find . -type d -name "img*" -exec rm -rf {} \;
  
  > find sourcePath/ -name "*.txt" -exec mv {} targetPath/ \;


- kill
  > ps -aux  |  grep python  | grep -v grep | cut -c 9-15  |  xargs kill -s 9
  
- du & df
  > du -sh .
  
  > df -hl 
 
- git 
  > git status | grep typechange | awk '{print $2}' | xargs git checkout

- sed
  > sed -i "s/origin/dst/g"  file  ；-i inplace edit 
  
  > sed 's/^[ ]*//g' filename
  
- vim 
  > :%s/origin/dst/g
  
 

