import unittest
import json
import os,io
from time import sleep

from pymongo import MongoClient
from app import  *
from db.models import *
from test.coderun import CodeRunTests
from datetime import datetime
import config
from db import redisClient

app_client=contestplatform.test_client()

#On first run, Run create.py first before this test file
#Note note note!!!! test functions are run in alphabetical order. So we are makking them by numbers
langs=['go', 'py', 'java', 'c', 'c++', 'python', 'python2', 'php', 'js']


class AppTests(unittest.TestCase):
    api_token_user=""
    api_token_admin=""
    problem_id=""
    contest_type=""
    contest_id = ""
    user_id=""
    user_id2=""
    admin_id=""
    admin_id2=""
    contest_prblmid = ""
    
    @classmethod
    def setTokenUser(cls,api_token):
        cls.api_token_user= api_token

    @classmethod
    def setTokenAdmin(cls,api_token):
        cls.api_token_admin= api_token

    @classmethod
    def setProblemID(cls,problem_id):
        cls.problem_id=problem_id

    @classmethod
    def setUserID(cls,id):
        cls.user_id=id 

    @classmethod
    def setAdminID(cls,id):
        cls.admin_id=id 

    @classmethod
    def setUserID2(cls,id2):
        cls.user_id2=id2

    @classmethod
    def setAdminID2(cls,id2):
        cls.admin_id2=id2

    @classmethod
    def setContestIdandType(cls,contest_type, contest_id):
        cls.contest_type = contest_type
        cls.contest_id = contest_id    

    @classmethod    
    def setContestProblemId(cls, uid): 
        cls.contest_prblmid = uid    

    def test_1_folder_avail(self): 
        for lgn in langs:
            directory = os.path.dirname("/tmp/{}".format(lgn))
            os.stat(directory)

    def getValidTime(self):
        return datetime.now().timestamp()*1000 + 13*60*60*1000.0        

    def reg_test(self,url,username,password,email,first=True):
        resp=app_client.post(url, data=dict(
            username=username,
            pswd=password
        )) 
        

        resp=app_client.post(url, data=dict(
            username=username,
            pswd=password,
            email=email
        ))
        self.assertTrue('email' in resp.data.decode())
        d=json.loads(resp.data.decode())
        if "registration" in url:
            if url=="/user/registration/":
                keyreg=list(redisClient.hgetall("unregisteredusersUSER").keys())[0]
            else:
                keyreg=list(redisClient.hgetall("unregisteredusersADMIN").keys())[0]
            resp=app_client.get(url+"?id="+keyreg.decode())
            resp=json.loads(resp.data.decode())


        self.assertTrue(len(resp["access_token"])>0)
        self.assertTrue(len(resp["data"]["uniqueid"])>0)

        if url=="/user/registration/":
            self.setTokenUser(resp["access_token"])
            checkid=resp["data"]["uniqueid"]
            if first:
                self.setUserID(resp["data"]["uniqueid"])
            else:
                self.setUserID2(resp["data"]["uniqueid"])  
        else:
            self.setTokenAdmin(resp["access_token"])
            if first:
                self.setAdminID(resp["data"]["uniqueid"])
            else:
                self.setAdminID2(resp["data"]["uniqueid"])    
        
        resp=app_client.post(url, data=dict(
            username=username,
            pswd=password,
            email=email
        ))

        self.assertTrue("taken" in resp.data.decode())

    def login_test(self,url,username,password):
        resp=app_client.post(url, data=dict(
            username=username,
            pswd=password
        ))

        self.assertTrue('login successfuly' in resp.data.decode())

        resp=app_client.post(url, data=dict(
            username=username,
            pswd="aburunakamakif"
        ))

        self.assertTrue('check the username and password' in resp.data.decode())


    def test_2_user_reg(self):
        # register two users
        self.reg_test("/user/registration/","abraham","akerele","abrahamakerele38@gmail.com")
        self.login_test("/user/login/","abraham","akerele")
        self.reg_test("/user/registration/","harjacober","harjoshuaer","harjacober@gmail.com",False)
        self.login_test("/user/login/","harjacober","harjoshuaer")

    def test_3_admin_reg(self):
        # register two admins
        self.reg_test("/admin/registration/","marlians","aburunakamaki","abrahamadeniyi38@gmail.com")
        self.login_test("/admin/login/","marlians","aburunakamaki")
        self.reg_test("/admin/registration/","admin","adminpassword","jacob.auduu@gmail.com",False)
        self.login_test("/admin/login/","admin","adminpassword")

    def test_4_contest_create(self):
       
        self.assertTrue(len(self.api_token_admin)>0)

        # Authorization: Bearer <token>
        header={"Authorization":"Bearer "+self.api_token_admin} 
        data=dict(
            title="Educational Contest",
            creator="marlians", 
            contesttype="TYPEA",
            desc=""
        )

        resp=app_client.post("/contest/initialize/", data=data, headers=header, content_type='multipart/form-data')

        self.assertTrue("Contest Created Successfully" in resp.data.decode())
        
        resp=json.loads(resp.data.decode())

        contest_id=resp["data"]["contestid"]
        contest_type = resp["data"]["contesttype"]

        self.setContestIdandType(contest_type, contest_id)

        data=dict(
            title = "Educational Contest", 
            desc = "Description goes here",
            duration = 120*60*60*1000.0,
            starttime = self.getValidTime(),
            author = "marlians",
            contestid = contest_id

        )
        resp=app_client.post("/contest/{}/update/".format(contest_type), data=data, headers=header)

        self.assertTrue("200" in resp.data.decode())
        self.assertTrue("Update Successful" in resp.data.decode()) 


        c1 = "1 2 3 4 5\n2 3 5 6 7,3 4 8 9 1\n4 2 3 5 1,5 2 4 3 1\n6 3 5 7 8"
        a1 = "[3, 5, 8, 10, 12],[7, 6, 11, 14, 2],[11, 5, 9, 10, 9]"
        s1 = "3 4 6 3\n2 4 6 2"
        as1= "[5, 8, 12, 5]"
        c2 = b"3\n1\n2\n3\n4\n5\n6,2\n7\n8\n9\n10,1\n9\n10"
        a2= b"3\n7\n11,\n15\n19,\n19"
        s2 = b"2\n3\n4\n2\n1"
        as2 = b"7\n3"
        data=dict(
            author = "marlians",
            name="problem test", 
            testcases=(io.BytesIO(c2), 'test.in'),
            sizeoftestcases="3",
            answercases=(io.BytesIO(a2), 'anstest.in'),
            samplecases=(io.BytesIO(s2), 'sampletest.in'),
            sizeofsamplecases="1",
            sampleanswercases = (io.BytesIO(as2), 'answersampletest.in'), 
            problemstatement="Read the input and print them",
            tags = "bfs,dfs",
            contestid = contest_id,
            timelimit=1,
            memorylimit=250,
            prblmscore=900 
        )
        resp=app_client.post("/contest/{}/problem/add/".format(contest_type), data=data,headers=header,content_type='multipart/form-data')
 
        self.assertTrue("200" in resp.data.decode())
        self.assertTrue("contestid" in resp.data.decode())
        self.assertTrue("prblmid" in resp.data.decode()) 

        resp=json.loads(resp.data.decode()) 
        contest_prblmid=resp["data"]["prblmid"]
        self.setContestProblemId(contest_prblmid)


        # Approve contest
        data=dict(
            creator = "marlians", 
            contestid = self.contest_id

        )
        resp=app_client.post("/contest/{}/approve/".format(contest_type), data=data, headers=header)

        self.assertTrue("200" in resp.data.decode())
        self.assertTrue("Success" in resp.data.decode())
        

    def test_5_problem_add(self):
       
        self.assertTrue(len(self.api_token_admin)>0)

        # Authorization: Bearer <token>
        header={"Authorization":"Bearer "+self.api_token_admin}
        c1 = "1 2 3 4 5\n2 3 5 6 7,3 4 8 9 1\n4 2 3 5 1,5 2 4 3 1\n6 3 5 7 8"
        a1 = "[3, 5, 8, 10, 12],[7, 6, 11, 14, 2],[11, 5, 9, 10, 9]"
        s1 = "3 4 6 3\n2 4 6 2"
        as1= "[5, 8, 12, 5]"
        c2 = b"3\n1\n2\n3\n4\n5\n6,2\n7\n8\n9\n10,1\n9\n10"
        a2= b"3\n7\n11,\n15\n19,\n19"
        s2 = b"2\n3\n4\n2\n1"
        as2 = b"7\n3"
        data=dict(
            name="problem test",
            author="marlians",
            testcases=(io.BytesIO(c2), 'test.in'),
            sizeoftestcases="3",
            answercases=(io.BytesIO(a2), 'anstest.in'),
            samplecases=(io.BytesIO(s2), 'sampletest.in'),
            sizeofsamplecases="1",
            sampleanswercases = (io.BytesIO(as2), 'answersampletest.in'), 
            problemstatement="Read the input and print them",
            category="test",
            timelimit=1,
            memorylimit=250,
            score=2500,
            tags = "bfs,dfs",
            contestid=self.contest_id
        )

        resp=app_client.post("/add/problem/",data=data,headers=header,content_type='multipart/form-data')
        
        self.assertTrue("New Problem Added" in resp.data.decode())

        resp=json.loads(resp.data.decode())

        problem_id=resp["data"]["prblmid"]

        self.setProblemID(problem_id)

        data=dict(
            prblmid=problem_id
        )

        resp=app_client.get("/get/problem/",data=data,headers=header)

        self.assertTrue("200" in resp.data.decode())
        self.assertTrue("author" in resp.data.decode())
        self.assertTrue("sizeoftestcases" in resp.data.decode())
        self.assertTrue("samplecases" in resp.data.decode())

        resp=app_client.get("/get/problem/?prblmid="+problem_id,headers=header)

        self.assertTrue("200" in resp.data.decode())
        self.assertTrue("author" in resp.data.decode())
        self.assertTrue("sizeoftestcases" in resp.data.decode())
        self.assertTrue("samplecases" in resp.data.decode())

    def test_6_run_code(self):
        self.assertTrue(len(self.problem_id)>0)
        self.assertTrue(len(self.user_id)>0)

        codeRun=CodeRunTests(self.problem_id,self.user_id)
        url = "/run/code/"
        url_status = "/run/code/status/"
        #testing python
        resp=codeRun.run(url,url_status,self.api_token_user,app_client,codeRun.pythonData())
        data=json.loads(resp.data.decode()) 
        print(data)
        for i in range(3):
            self.assertTrue(data["data"][0]["result"][i]["passed"])

        #tetsing php 
        resp=codeRun.run(url,url_status,self.api_token_user,app_client,codeRun.phpData())
        data=json.loads(resp.data.decode()) 
        for i in range(3):
            self.assertTrue(data["data"][0]["result"][i]["passed"])
        
        #testing js
        resp=codeRun.run(url,url_status,self.api_token_user,app_client,codeRun.jsData())
        data=json.loads(resp.data.decode())
        for i in range(3):
            self.assertTrue(data["data"][0]["result"][i]["passed"])
        
        #testing c++
        resp=codeRun.run(url,url_status,self.api_token_user,app_client,codeRun.cplusplusData())
        data=json.loads(resp.data.decode())
        for i in range(3):
            self.assertTrue(data["data"][0]["result"][i]["passed"])



        #testingtimeout py code
        resp=codeRun.run(url,url_status,self.api_token_user,app_client,codeRun.pythonData(testtimeout=True))
        data=json.loads(resp.data.decode())
        self.assertTrue(data["data"][0]["result"][0]["passed"]==False)
        
        """#testing golang
        resp=codeRun.run(url,url_status,self.api_token_user,app_client,codeRun.golangData())
        data=json.loads(resp.data.decode())
       
        if not data["data"][0]["result"][0]["passed"]:
            print(data["data"][0]["result"][0]["errput"]) 
        print(data)
        for i in range(3):
            self.assertTrue(data["data"][0]["result"][i]["passed"])"""

        #rtesting c
        resp=codeRun.run(url,url_status,self.api_token_user,app_client,codeRun.cData())
        data=json.loads(resp.data.decode())
        if not data["data"][0]["result"][0]["passed"]:
            print(data["data"][0]["result"][0]["errput"])
        for i in range(3):
            self.assertTrue(data["data"][0]["result"][i]["passed"])

         #rtesting timeout c
        resp=codeRun.run(url,url_status,self.api_token_user,app_client,codeRun.cData(testtimeout=True))
        data=json.loads(resp.data.decode())
        self.assertTrue(data["data"][0]["result"][0]["passed"]==False)

        #testing java
        resp=codeRun.run(url,url_status,self.api_token_user,app_client,codeRun.javaData())
        data=json.loads(resp.data.decode())
        if not data["data"][0]["result"][0]["passed"]:
            print(data["data"][0]["result"][0]["errput"])
        for i in range(3):
            self.assertTrue(data["data"][0]["result"][i]["passed"])

        #testing java timeout
        resp=codeRun.run(url,url_status,self.api_token_user,app_client,codeRun.javaData(testtimeout=True))
        data=json.loads(resp.data.decode())
        self.assertTrue(data["data"][0]["result"][0]["passed"]==False)

        #testing for memory
        resp=codeRun.run(url,url_status,self.api_token_user,app_client,codeRun.testMemory())
        data=json.loads(resp.data.decode())
        self.assertTrue(data["data"][0]["result"][0]["passed"]==False)

    def test_7_user_functions(self):
        self.assertTrue(len(self.contest_type)>0)
        self.assertTrue(len(self.contest_id)>0)

        # Authorization: Bearer <token>
        header={"Authorization":"Bearer "+self.api_token_user}

        #Register at least 1 users for contest
        data=dict( 
            contesttype = self.contest_type,
            contestid = self.contest_id

        )  
        resp=app_client.post("/register/contest/",data=data,headers=header)  
        self.assertTrue("Registration Success" in resp.data.decode())

        # Contest must have started before users can enter
        # force start contest
        resp=app_client.post("/contest/force/{}/{}/start/".format(self.contest_type, self.contest_id),headers=header) 
        self.assertTrue("Contest forcefully started" in resp.data.decode())  

        #/enter/contest/
        data=dict( 
            contesttype=self.contest_type,
            contestid=self.contest_id
        )

        resp=app_client.post("/enter/contest/",data=data,headers=header)  
        self.assertTrue("Contest participation history updated" in resp.data.decode())

        #/enter/contest/
        data=dict(   
            contesttype=self.contest_type,
            contestid=self.contest_id
        )

        resp=app_client.post("/enter/contest/",data=data,headers=header)  
        self.assertTrue("Contest participation history updated" in resp.data.decode())


        #/my/contest/history/"
        data=dict( )

        resp=app_client.get("/my/contest/history/",data=data,headers=header) 
        self.assertTrue("Success" in resp.data.decode())
        self.assertTrue(len(json.loads(resp.data.decode())["data"])>0)


        data=dict( 
            contestid=self.contest_id,
            contesttype=self.contest_type,
            prblmid=self.contest_prblmid
        )
        #submission for a specific contest problem
        resp=app_client.get("/my/submission/history/",data=data,headers=header)  
        self.assertTrue("Success" in resp.data.decode()) 

        data=dict( 
            contestid=self.contest_id,
            contesttype=self.contest_type
        )
        #submission for all contest problems
        resp=app_client.get("/my/submission/history/",data=data,headers=header)  
        self.assertTrue("Success" in resp.data.decode())   
    
    def test_8_run_contest_code(self):
        self.assertTrue(len(self.contest_prblmid)>0)
        self.assertTrue(len(self.user_id)>0)
        self.assertTrue(len(self.contest_id)>0)
        self.assertTrue(len(self.contest_type)>0)

        codeRun=CodeRunTests(self.contest_prblmid,self.user_id,self.contest_id,self.contest_type)

        url = "/contest/run/code/"
        url_status = "/contest/run/code/status/"
        #testing python
        resp=codeRun.run(url,url_status,self.api_token_user,app_client,codeRun.pythonData())
        data=json.loads(resp.data.decode())
        for i in range(3):
            self.assertTrue(data["data"][0]["result"][i]["passed"])

        #testingtimeout py code
        resp=codeRun.run(url,url_status,self.api_token_user,app_client,codeRun.pythonData(testtimeout=True))
        data=json.loads(resp.data.decode()) 
        self.assertTrue(data["data"][0]["result"][0]["passed"]==False)
        
        """#testing go
        resp=codeRun.run(url,url_status,self.api_token_user,app_client,codeRun.golangData())
        data=json.loads(resp.data.decode())  
        print(data)
        if not data["data"][0]["result"][0]["passed"]:
            print(data["data"][0]["result"][0]["errput"]) 
        for i in range(3):
            self.assertTrue(data["data"][0]["result"][i]["passed"])"""

        #rtesting c
        resp=codeRun.run(url,url_status,self.api_token_user,app_client,codeRun.cData())
        data=json.loads(resp.data.decode()) 
        if not data["data"][0]["result"][0]["passed"]:
            print(data["data"][0]["result"][0]["errput"])
        for i in range(3):
            self.assertTrue(data["data"][0]["result"][i]["passed"])

         #rtesting timeout c
        resp=codeRun.run(url,url_status,self.api_token_user,app_client,codeRun.cData(testtimeout=True))
        data=json.loads(resp.data.decode())
        self.assertTrue(data["data"][0]["result"][0]["passed"]==False)

        #testing java
        resp=codeRun.run(url,url_status,self.api_token_user,app_client,codeRun.javaData())
        data=json.loads(resp.data.decode())
        if not data["data"][0]["result"][0]["passed"]:
            print(data["data"][0]["result"][0]["errput"])
        for i in range(3):
            self.assertTrue(data["data"][0]["result"][i]["passed"])

        #testing java timeout
        resp=codeRun.run(url,url_status,self.api_token_user,app_client,codeRun.javaData(testtimeout=True))
        data=json.loads(resp.data.decode())
        self.assertTrue(data["data"][0]["result"][0]["passed"]==False)
        if config.CELERY_TEST:
            #see if it is updated
            with open("/home/celerytestfile.in") as f:
                self.assertTrue(f.read()=="a")
        
        

    def test_9_password_reset(self):
        data={"email":"abrahamadeniyi38@gmail.com"}
        resp=app_client.get("/forgot/password/",data=data) 
        self.assertTrue("Success" in resp.data.decode())

        key,url=json.loads(list(redisClient.hgetall("pendindmacs").values())[0])

        resp=app_client.get(url,data=data)
    
        data={"email":"abrahamadeniyi38@gmail.com","pswd":"mambamentality","changepswdid":key}
        resp=app_client.post("/change/password/",data=data)  
        self.assertTrue("Success" in resp.data.decode())

        header={"Authorization":"Bearer "+self.api_token_user}

        data={"email":"abrahamadeniyi38@gmail.com","pswd":"mambamentality"}
        resp=app_client.post("/change/password/authuser/",data=data,headers=header)  
        self.assertTrue("Success" in resp.data.decode())
        self.login_test("/admin/login/","marlians","mambamentality")

    def test_10_websocket(self):
        ws_client=contestplatform.socketio.test_client(contestplatform,namespace='/scoreboard/')
        received = ws_client.get_received()
        self.assertEqual(received[0]['args'],"Welcome to HackAlgo!!")

        

from test.test_task_queue import *

if __name__ == "__main__":
    unittest.main()