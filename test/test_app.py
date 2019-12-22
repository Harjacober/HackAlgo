import unittest
import json
import os,io
from time import sleep

from pymongo import MongoClient
from app import  *
from db.models import *
app_client=app.test_client()

#Run create.py first before this test file
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
            directory = os.path.dirname("/tmp/{}".format(lgn))
            os.stat(directory)

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
        self.reg_test("/adminreg/")
        self.login_test("/adminlogin/")

    def test_user_reg(self):
        self.reg_test("/userreg/")
        self.login_test("/userlogin/")


    def test_problem_add(self):
       
        self.assertTrue(len(self.api_token)>0)

        # Authorization: Bearer <token>
        header={"Authorization":"Bearer "+self.api_token}
        c1 = "1 2 3 4 5\n2 3 5 6 7,3 4 8 9 1\n4 2 3 5 1,5 2 4 3 1\n6 3 5 7 8"
        a1 = "[3, 5, 8, 10, 12],[7, 6, 11, 14, 2],[11, 5, 9, 10, 9]"
        s1 = "3 4 6 3\n2 4 6 2"
        as1= "[5, 8, 12, 5]"
        c2 = b"3\r\n1\r\n2\r\n3\r\n4\r\n5\r\n6,2\r\n7\r\n8\r\n9\r\n10,1\r\n9\r\n10'"
        a2= b"3\n7\n11,\n15\n19,\n19"
        s2 = b"2\n3\n4\n2\n1"
        as2 = b"7\n3"
        data=dict(
            name="problem test",
            author="abraham",
            testcases=(io.BytesIO(c2), 'test.in'),
            sizeoftestcases="3",
            answercases=(io.BytesIO(a2), 'anstest.in'),
            samplecases=(io.BytesIO(s2), 'sampletest.in'),
            sizeofsamplecases="1",
            sampleanswercases = (io.BytesIO(as2), 'answersampletest.in'), 
            problemstatement="Read the input and print them",
            category="test"
        )

        resp=app_client.post("/add/problem/",data=data,headers=header,content_type='multipart/form-data')

        self.assertTrue("New Problem Added" in resp.data.decode())

        resp=json.loads(resp.data.decode())

        problem_id=resp["data"]["prblid"]

        self.setProblemID(problem_id)

        data=dict(
            prblid=problem_id
        )

        resp=app_client.post("/get/problem/",data=data,headers=header)
        print(resp.data.decode())

        self.assertTrue("200" in resp.data.decode())
        self.assertTrue("author" in resp.data.decode())
        self.assertTrue("sizeoftestcases" in resp.data.decode())
        self.assertTrue("samplecases" in resp.data.decode())

        resp=app_client.get("/get/problem/?prblid="+problem_id,headers=header)


        self.assertTrue("200" in resp.data.decode())
        self.assertTrue("author" in resp.data.decode())
        self.assertTrue("sizeoftestcases" in resp.data.decode())
        self.assertTrue("samplecases" in resp.data.decode())



    def test_run_code(self):
        self.assertTrue(len(self.problem_id)>0)

        header={"Authorization":"Bearer "+self.api_token}
        code1="a=map(int,input().split())\nb=map(int,input().split())\nprint(list(map(lambda x:sum(x), zip(a,b))))"
        code2="n = int(input())\nfor i in range(n):\n\tprint(int(input()) + int(input()))"
        data=dict(
            prblmid=self.problem_id,
            userid="wkgs426haqie6yvnacswteelkjsndteaqp",
            codecontent=code2,
            lang="py",
            stype = "sample"
        )

        resp=app_client.post("/run/code/",data=data,headers=header)

        resp=json.loads(resp.data.decode())["data"][0]

        task_id=resp["_id"]
      
        data=dict(
            prblmid=self.problem_id,
            userid="wkgs426haqie6yvnacswteelkjsndteaqp",
            taskid=task_id,
            lang="py",
            stype = "test"
        )

        sleep(1) # wait a second for result

        resp=app_client.post("/run/code/status/",data=data,headers=header)

        self.assertTrue("Task state is" in resp.data.decode())


if __name__ == "__main__":
    unittest.main()