import os
from random import randint
from time import time
import subprocess
from threading import Thread

from db.models import Submission

ORIGINAL_DIR=os.getcwd()

#So this would be different for each machine not sure how 
#to go about this efficiently yet for unix. 
py_dir = "C:/Users/Harjacober/AppData/Local/Programs/Python/Python37/python.exe"
#py_dir="/usr/local/bin/python"
compilers={
    "go":"/usr/bin/go",
    "py":py_dir,
    "java":"/usr/bin/java",
    "c":"/usr/bin/gcc",
    "c++":"/usr/bin/g++",
    "python":py_dir,
    "python2":"/usr/bin/python2",
    "php":"/usr/bin/php",
    "js":"/usr/bin/node"
}

class Task(Thread):
    """
    Handles running of submitted code and updates the submission details in the database
    """
    PossibelTasksState=["initialize","running","finished"]
    def __init__(self,lang,content,userid,problem,id,stype):
        """
        :param stype: the type of submission. differentiates actual 
                      test cases from sample cases.
        :param content: code content
        :param problem: an Instance of :class: `ProblemInstance`.
        """
        Thread.__init__(self)
        self.state=Task.PossibelTasksState[0]
        self.lang=lang
        self.content=content
        self.userid=userid
        self.stype = stype
        if self.stype == "test":
            self.cases=problem.getTestCases().split(",")
            self.answercase=problem.getAnswerForTestCases().split(",")
            self.result=[None]*int(problem.getSizeOfTestCases())
        elif self.stype == "sample":
            self.cases=problem.getSampleCases().split(",")
            self.answercase=problem.getAnswerForSampleCases().split(",")
            self.result=[None]*int(problem.getSizeOfSampleCases()) 
        self.id=id
        self.enter()

    def toJson(self):
        return {"state":self.state,"lang":self.lang,"userid":self.userid,"_id":self.id,"result":self.result}

    def __del___(self):
        #cleaning up
        os.remove(self.filepath)
        if self.lang.lower()=="java":
            os.rmdir(self.folder)

    def __lt__(self,other):
        return ~self.PossibelTasksState.index(self.state)< ~other.PossibelTasksState.index(other.state)

    def enter(self):
        self.filename=self.randomFilename()
        if self.lang.lower()=="java":
            filename=os.path.join(*self.filename.split(".")[:-1])
            self.folder="/tmp/{}/{}/".format(self.lang,filename)
            os.makedirs(self.folder,exist_ok=True)
        else:
            self.folder="/tmp/{}/".format(self.lang)
        self.filepath=self.folder+self.filename
        self.file = open(self.filepath,"w+")
        self.file.write(self.content)
        self.file.close()
    
    def resolveFolder(self,lang):
        #python is py,java is java e.t.c.This function exist if need be resolve the name later
    
        if lang not in compilers:
            raise NotImplementedError("Not yet suported")
        if lang.lower()=="go":
            return [compilers[lang],"run"]
        return [compilers[lang]]

    def randomFilename(self):
        return self.userid+"{}{}.{}".format(hash(time()),hash(self),self.lang)

    def status(self):
        return self.state

    def runCompile(self,compiler_name,compile_options,run_options,n_cases,binary):

        subprocess.run([compiler_name]+compile_options+[self.filepath])
    
        for cc in range(n_cases):
            ans=subprocess.\
                run([binary]+run_options, capture_output=True,\
                            input=self.cases[cc],encoding="utf-8")

            output=ans.stdout.strip()
            errput=ans.stderr.strip()

            self.result[cc] ={
                            "passed":output==self.answercase[cc],
                            "output":output,
                            "errput":errput
                            }

    def run(self):
        l=len(self.result)
        self.state=self.PossibelTasksState[1]
        #some languagues have to compile then run 
        if self.lang == "java":
            options_compile=["-d",self.folder,"-s",self.folder,"-h",self.folder]
            options_run=["-classpath",self.folder,"Solution"]
            self.runCompile("javac",options_compile,options_run,l,"java")
        elif self.lang == "c":
            options_compile=["-o",self.filepath+".out"]
            options_run=[]
            self.runCompile("gcc",options_compile,options_run,l,self.filepath+".out")
        elif self.lang=="c++":
            options_compile=["-o",self.filepath+".out"]
            options_run=[]
            self.runCompile("g++",options_compile,options_run,l,self.filepath+".out")
        else:
            # languages like python, js, php should be fine.
            for cc in range(l):
                args=[]
                args.extend(self.resolveFolder(self.lang))
                args.append(self.filepath)
                ans=subprocess.run(args,capture_output=True,
                input=self.cases[cc],encoding="utf-8")

                output=ans.stdout.strip()
                errput=ans.stderr.strip()

                self.result[cc] = {
                                "passed":output==self.answercase[cc],
                                "output":output,
                                "errput":errput
                                }

        #update submission in the database    
        if self.stype == "test":     
            category = Submission(self.userid)
            category.update(params={'verdict': self.result}, userid=userid)  
        self.state=self.PossibelTasksState[2]
        os.remove(self.filepath)


