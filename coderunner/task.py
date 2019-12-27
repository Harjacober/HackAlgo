import os
from random import randint
from time import time
import subprocess
from threading import Thread


ORIGINAL_DIR=os.getcwd()

#So this would be different for each machine not sure how 
#to go about this efficiently yet for unix. 
py_dir = "C:/Users/Harjacober/AppData/Local/Programs/Python/Python37/python.exe"
#py_dir="/usr/local/bin/python"
compilers={
    "go":"/usr/local/go/bin/go",
    "py":py_dir,
    "java":"",
    "c":"",
    "c++":"/usr/bin/g++",
    "python":py_dir,
    "python2":"/usr/bin/python",
    "php":"php",
    "js":"node"
}

class Task(Thread):
    PossibelTasksState=["initialize","running","finished"]
    def __init__(self,lang,content,userid,problem,id,stype):
        """
        :param stype: the type of submission. differentiate testing against sample
                     cases and actual submission against test cases.
        :param content: code content
        :param problem: an Instance of :class: `ProblemInstance`.
        """
        Thread.__init__(self)
        self.state=Task.PossibelTasksState[0]
        self.lang=lang
        self.content=content
        self.userid=userid
        if stype == "test":
            self.cases=problem.getTestCases().split(",")
            self.answercase=problem.getAnswerForTestCases().split(",")
            self.result=[None]*int(problem.getSizeOfTestCases())
        elif stype == "sample":
            self.cases=problem.getSampleCases().split(",")
            self.answercase=problem.getAnswerForSampleCases().split(",")
            self.result=[None]*int(problem.getSizeOfSampleCases()) 
        self.id=id
        self.enter()

    def toJson(self):
        return {"state":self.state,"lang":self.lang,"userid":self.userid,"_id":self.id,"result":self.result}

    def __del___(self):
        os.remove(self.filepath)

    def __lt__(self,other):
        return ~self.PossibelTasksState.index(self.state)< ~other.PossibelTasksState.index(other.state)

    def enter(self):
        self.filename=self.randomFilename()
        self.folder="/tmp/{}/".format(self.lang)
        self.filepath=self.folder+self.filename
        self.file = open(self.filepath,"w+")
        self.file.write(self.content)
        self.file.close()
    
    def resolveFolder(self,lang):
        #python is py,java is java e.t.c.This function exist if need be resolve the name later
        if lang not in compilers:
            raise NotImplementedError("Not yet suported")
        return compilers[lang]

    def randomFilename(self): 
        return self.userid+"{}{}".format(hash(time()),hash(self))

    def status(self):
        return self.state

    def runCompile(self,compiler_name,compile_options,run_options,n_cases,compile_file_ext,binary):

        subprocess.run([compiler_name]+compile_options+[self.filepath])
    
        for cc in range(n_cases):
            ans=subprocess.\
                run([binary]+run_options+[self.filepath+compile_file_ext], capture_output=True,\
                            input=self.cases[cc],encoding="utf-8").stdout.decode()

            self.result[l]=ans==self.answercase[cc] #would scrutinize this line soon cos answer formatting might be disimilar to stored answrer

    def run(self):
        l=len(self.result)
        self.state=self.PossibelTasksState[1]
        #some languagues have to compile then run 
        if self.lang == "java":
            options_compile=["-d",self.folder,"-s",self.folder,"-h",self.folder]
            options_run=[]
            self.runCompile("javac",options_compile,options_run,l,".class","java")
        elif self.lang == "c":
            options_compile=["-o",self.filepath+"CP"]
            options_run=[]
            self.runCompile("g++",options_compile,options_run,l,"",self.filepath+"CP")
        elif self.lang=="c++":
            options_compile=["-o",self.filepath+"CP"]
            options_run=[]
            self.runCompile("g++",options_compile,options_run,l,"",self.filepath+"CP")
        else:
            # languages like python, js, php should be fine.
            
            for cc in range(l):
                ans=subprocess.run([self.resolveFolder(self.lang),self.filepath],capture_output=True,
                input=self.cases[cc],encoding="utf-8")

                output=ans.stdout.strip()
                errput=ans.stderr.strip()
                
                res={"passed":output==self.answercase[cc],"output":output,"errput":errput}
                
                self.result[cc]= res
                
        self.state=self.PossibelTasksState[2]
        os.remove(self.filepath)


