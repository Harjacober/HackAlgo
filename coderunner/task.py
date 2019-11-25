import os
from random import randint
from time import time
import subprocess
from threading import Thread


ORIGINAL_DIR=os.getcwd()

#So this would be different for each machine not sure how to about this efficiently yet
#for unix we might use which to find binary but mehn i dont know brah
compilers={
    "go":"/usr/local/go/bin/go",
    "py":"/usr/bin/python3",
    "java":"",
    "c":"",
    "c++":"/usr/bin/g++",
    "python":"/usr/bin/python3",
    "python2":"/usr/bin/python3",
    "php":"php",
    "js":"node"
}

class Task(Thread):
    PossibelTasksState=["initialize","running","finished"]
    def __init__(self,lang,content,person_email,problem,id):
        Thread.__init__(self)
        self.state=Task.PossibelTasksState[0]
        self.lang=lang
        self.content=content
        self.person_email=person_email
        self.cases=problem.getCases().split("\n")
        self.answercase=problem.getAnswerForCases().split("\n")
        self.result=[None]*int(problem.getNCases())
        self.id=id
        self.enter()

    def toJson(self):
        return {"state":self.state,"lang":self.lang,"email":self.person_email,"_id":self.id,"result":self.result}

    def __del___(self):
        os.remove(self.filepath)

    def __lt__(self,other):
        return ~self.PossibelTasksState.index(self.state)< ~other.PossibelTasksState.index(other.state)

    def enter(self):
        self.filename=self.randomFilename()
        self.folder="/tmp/{}/".format(self.lang)
        self.filepath=self.folder+self.filename
        self.file=open(self.filepath,"w+")
        self.file.write(self.content)
        self.file.close()
    
    def resolveFolder(self,lang):
        #python is py,java is java e.t.c.This function exist if need be resolve the name later
        if lang not in compilers:
            raise NotImplementedError("Not yet suported")
        return compilers[lang]

    def randomFilename(self):
        return self.person_email+"{}{}".format(time(),hash(self))

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
                ans=subprocess.\
                        run([self.resolveFolder(self.lang),self.filepath],capture_output=True,\
                        input=self.cases[cc],encoding="utf-8")

                output=ans.stdout.strip()
                errput=ans.stderr.strip()
                
                res={"passed":output==self.answercase[cc],"output":output,"errput":errput}
                
                self.result[cc]= res
                
        self.state=self.PossibelTasksState[2]
        os.remove(self.filepath)


