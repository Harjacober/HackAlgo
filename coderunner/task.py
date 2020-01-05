import os
from random import randint
from time import time
import subprocess
from threading import Thread
from datetime import datetime
from shutil import rmtree
from api.access.user import gradeSubmission
from db.models import Submission

ORIGINAL_DIR=os.getcwd()

#So this would be different for each machine not sure how 
#to go about this efficiently yet for unix. 

py_dir = "C:/Users/Harjacober/AppData/Local/Programs/Python/Python37/python.exe"
py_dir="/usr/local/bin/python"
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
    def __init__(self,lang,content,userid,problem,id,stype,codefile,contestid,ctype):
        """
        :param stype: the type of submission. differentiates actual 
                      test cases from sample cases.
        :param content: code content
        :param problem: an Instance of :class: `ProblemInstance`.
        """
        Thread.__init__(self)
        self.state=Task.PossibelTasksState[0]
        self.lang=lang
        self.stype = stype 
        if codefile is not None:
            self.content = self.input_data['codefile'].read().decode("utf-8") 
        else:
            self.content = content # get submitted code content   
        self.userid=userid
        self.cases=problem.getCases().split("\n")
        self.answercase=problem.getAnswerForCases().split("\n")
        self.result=[None]*int(problem.getNCases())
        self.id=id 
        self.state=Task.PossibelTasksState[0]  
        self.verdict = "Passed"
        self.contestid = contestid
        self.ctype = ctype
        self.problem = problem

        if self.stype == "test":
            self.cases=self.problem.getTestCases().split(",")
            self.answercase=self.problem.getAnswerForTestCases().split(",") 
            self.result=[None]*int(self.problem.getSizeOfTestCases())
        elif self.stype == "sample":
            self.cases=self.problem.getSampleCases().split(",")
            self.answercase=self.problem.getAnswerForSampleCases().split(",")
            self.result=[None]*int(self.problem.getSizeOfSampleCases()) 

        self.timelimit=problem.getTimeLimit()
        self.memlimit=problem.getMemLimit()
        self.formatcase() # This method is temporal    
        self.enter()

    def toJson(self):
        return {"state":self.state,"lang":self.lang,"userid":self.userid,"_id":self.id,"result":self.result}

    def __del___(self):
        #cleaning up
        try:
            os.remove(self.filepath)
            if self.lang.lower()=="java":
                rmtree(self.folder,ignore_errors=True)
        except FileNotFoundError:
            pass

    def __lt__(self,other):
        return ~self.PossibelTasksState.index(self.state)< ~other.PossibelTasksState.index(other.state)

    def formatcase(self):
        # The two for loops should be removed else an efficient way to the
        # processing should be found.
        # In the future, there should be no need to remove \r as the reading
        # of the file in `ProblemAdd` method will be fixed to not read in \r
        for i in range(len(self.cases)):
            string = self.cases[i].lstrip("\r\n")   
            arr = []
            for e in string:
                if e != "\r":
                    arr.append(e)
            self.cases[i] = "".join(arr)   
        for i in range(len(self.answercase)):
            string = self.answercase[i].lstrip("\r\n")   
            arr = []
            for e in string:
                if e != "\r":
                    arr.append(e)
            self.answercase[i] = "".join(arr) 

    def enter(self):
        #add the submission to database as the task has started. 
        #And modify verdict in the `Task` Class once the task is done. 
        if self.stype == "test":
            self.input_data['verdict'] = 'running'
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
        self.input_data["timesubmitted"]=str(datetime.now())
    
    def resolveFolder(self,lang):
        #python is py,java is java e.t.c.This function exist if need be resolve the name later
    
        if lang not in compilers:
            raise NotImplementedError("Not yet supported")
        if lang.lower()=="go":
            return [compilers[lang],"run"]
        return [compilers[lang]]

    def randomFilename(self):
        return self.userid+"{}{}.{}".format(hash(time()),hash(self),self.lang)

    def status(self):
        return self.state

    def runCompile(self,compiler_name,compile_options,run_options,n_cases,binary):

        compileans=subprocess.run([compiler_name]+compile_options+[self.filepath],
                                            capture_output=True,encoding="utf-8")

        #if while trying to compile there was an error 
        if compileans.returncode >0 :
            for cc in range(n_cases):
                self.result[cc] ={"passed":False,"output":"","errput":compileans.stderr.strip()}
            return

    
        for cc in range(n_cases):
            try:
                ans=subprocess.\
                    run([binary]+run_options, capture_output=True,timeout= self.timelimit,\
                                input=self.cases[cc],encoding="utf-8")
            except subprocess.TimeoutExpired:
                self.result[cc] ={"passed":False,"output":"Timeout","errput":"Timeout"}
                return

            output=ans.stdout.strip()
            errput=ans.stderr.strip()

            self.result[cc] ={
                            "passed":output==self.answercase[cc] and ans.returncode==0,
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
                try:
                    ans=subprocess.run(args,capture_output=True,timeout= self.timelimit,
                            input=self.cases[cc],encoding="utf-8")
                except subprocess.TimeoutExpired:
                    self.result[cc] ={"passed":False,"output":"Timeout","errput":"Timeout"}
                    self.verdict = "Failed"  
                    continue

                output=ans.stdout.strip()
                errput=ans.stderr.strip()

                if output!=self.answercase[cc]:
                    self.verdict = "Failed"     
                self.result[cc] = {
                                "passed":output==self.answercase[cc] and ans.returncode==0,
                                "output":output,
                                "errput":errput
                                }             

        self.state=self.PossibelTasksState[2]
        #create a submission in the database    
        submission_data = {'prblmid':self.getprblmid(),'userid':self.userid,'contestid':self.contestid,'ctype':self.ctype,'codecontent':self.codecontent,
                                            'codefile':self.codefile,'lang':self.lang,'stype':self.stype,'result': self.result,'verdict': self.verdict}
        if self.stype == "test":   
            if not contestid:
                submission_data.pop('userid', None)
                submission_data.pop('contestid', None)
                submission_data.pop('ctype', None)
                Submission(self.userid).addDoc(submission_data) 
            else:
                gradeSubmission(submission_data)    
       
        os.remove(self.filepath)
        if self.lang.lower()=="java":
            rmtree(self.folder,ignore_errors=True)


