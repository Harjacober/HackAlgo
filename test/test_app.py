import unittest
import json
import os
from time import sleep

from pymongo import MongoClient
from app import  *
from db.models import *
app_client=app.test_client()


langs=['go', 'py', 'java', 'c', 'c++', 'python', 'python2', 'php', 'js']

class AppTests(unittest.TestCase):
    api_token=""
    problem_id=""

    @classmethod
    def setToken(cls,api_token):
        cls.api_token= api_token

    @classmethod
    def setProblemID(cls,problem_id):
        cls.problem_id=problem_id

    def test_folder_avail(self):
        for lgn in langs:
            os.stat("/tmp/{}".format(lgn))

    def reg_test(self,url):
        resp=app_client.post(url, data=dict(
            username="marlians",
            pswd="aburunakamaki"
        ))

        self.assertTrue('blank' in resp.data.decode())

        resp=app_client.post(url, data=dict(
            username="marlians",
            pswd="aburunakamaki",
            email="nairamarley@yahoo.com"
        ))

        resp=json.loads(resp.data.decode())

        self.assertTrue(len(resp["access_token"])>0)

        self.api_token=resp["access_token"]
        AppTests.setToken(self.api_token)

        resp=app_client.post(url, data=dict(
            username="marlians",
            pswd="aburunakamaki",
            email="nairamarley@yahoo.com"
        ))

        self.assertTrue("taken" in resp.data.decode())

    def login_test(self,url):
        print(url)
        resp=app_client.post(url, data=dict(
            username="marlians",
            pswd="aburunakamaki"
        ))

        self.assertTrue('login successfuly' in resp.data.decode())

        resp=app_client.post(url, data=dict(
            username="marlians",
            pswd="aburunakamakif"
        ))

        self.assertTrue('check the username and password' in resp.data.decode())

        
       
    def test_admin_reg(self):
        self.reg_test("/nimdareg/")
        self.login_test("/nimdalogin/")

    def test_user_reg(self):
        self.reg_test("/userreg/")
        self.login_test("/userlogin/")


    def test_problem_add(self):
       
        self.assertTrue(len(self.api_token)>0)

        # Authorization: Bearer <token>
        header={"Authorization":"Bearer "+self.api_token}

        data=dict(
            name="problem test",
            author="abraham",
            cases="1\n2\n3",
            ncases="3",
            answercases="1\n2\n3",
            tcases="1",
            ntcases="1",
            answertcases="1",
            problemstatement="Read the input and print them",
            category="test"
        )

        resp=app_client.post("/add/problem/",data=data,headers=header)

        self.assertTrue("New Problem added" in resp.data.decode())

        resp=json.loads(resp.data.decode())

        problem_id=resp["data"][0]

        self.setProblemID(problem_id)

        data=dict(
            prblid=problem_id
        )

        resp=app_client.post("/get/problem/",data=data,headers=header)

        self.assertTrue("200" in resp.data.decode())
        self.assertTrue("author" in resp.data.decode())
        self.assertTrue("ncases" in resp.data.decode())
        self.assertTrue("tcases" in resp.data.decode())

        resp=app_client.get("/get/problem/?prblid="+problem_id,headers=header)


        self.assertTrue("200" in resp.data.decode())
        self.assertTrue("author" in resp.data.decode())
        self.assertTrue("ncases" in resp.data.decode())
        self.assertTrue("tcases" in resp.data.decode())



    def test_run_code(self):
        self.assertTrue(len(self.problem_id)>0)

        header={"Authorization":"Bearer "+self.api_token}

        data=dict(
            prblmid=self.problem_id,
            usermail="nairamarley@yahoo.com",
            codecontent="ot=input()\nprint(ot)",
            lang="py"
        )

        resp=app_client.post("/run/code/",data=data,headers=header)
       
        resp=json.loads(resp.data.decode())["data"][0]

        task_id=resp["_id"]
      
        data=dict(
            prblmid=self.problem_id,
            usermail="nairamarley@yahoo.com",
            taskid=task_id,
            lang="py"
        )

        sleep(1) # wait a second for result

        resp=app_client.post("/run/code/status/",data=data,headers=header)

        self.assertTrue("Task state is" in resp.data.decode())


if __name__ == "__main__":
    unittest.main()
