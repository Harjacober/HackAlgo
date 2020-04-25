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

 if you want to deploy the app in a production environment run this  ```export BUILD=prod``` on the shell 

  To redploy the app in a production env run this ```./scripts/gracefuldeploy ```  

- it is expected that the current directory where the project is , is mounted on the container so changes are in sync from your ide  
- if you are using sudo always pass -E params to preserve env variables  

#  code formatting  
install yapf with ```pip install yapf``` then run ```yapf -i -r *.py```
#  Software Requirement  
Redis  
Mongo  
celery  
#  running celery  
check scripts/build  
#  Deploy using ansible   
use ```ansible-playbook -i host deployApi.yml -k```  
change the playbook name to the appropiate app you want to deploy

