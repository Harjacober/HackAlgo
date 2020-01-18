# Development procedure  
- To get started for development install mongodb and make sure its  running on port 27017  
- Then do *pip install -r requirement.txt* in the project root  

# Genaral project docs  
- Runs on python3.7  

# DOCKER setup
- you need docker and docker-compose install  
```docker-compose up --force-recreate --remove-orphans --build```

  ```docker-compose up --force-recreate --remove-orphans --build -d (Rebuild the containers in the backgroud)```

  ```docker-compose up```  
  
  ```docker-compose up -d (This restart the container in the backgroud)```  
- it is expected that the current directory where the project is , is mounted on the container so changes are in sync from your ide  
- This an only developement setup 
#  code formatting  
install yapf with ```pip install yapf``` then run ```yapf -i -r *.py```
#  Software Requirement  
Redis  
Mongo  
celery  
#  running celery  
use ```celery multi start w1 -A coderunner.celerytasks -l info --pidfile=/var/run/celery/%n.pid \
                                        --logfile=/var/log/celery/%n%I.log```  
or whatever works for you  
check test 9 for sample usage
