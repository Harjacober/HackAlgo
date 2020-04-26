import os
from random import randint
from time import time
import subprocess
from datetime import datetime
from shutil import rmtree 
from db.models import UserRegisteredContest,Contest,ContestProblem,Problem,Submission
from bson.objectid import ObjectId
from platform import system
from flask import current_app


ORIGINAL_DIR=os.getcwd()


if system()=='Linux':
    py_dir="/usr/local/bin/python"
    go_dir="/usr/bin/go"
    cplus_dir="/usr/bin/g++"
    c_dir="/usr/bin/gcc" 
    import resource

compilers={
    "go":go_dir,
    "py":py_dir,
    "java":"/usr/bin/java",
    "c":c_dir,
    "c++":cplus_dir,
    "python":py_dir,
    "python2":"/usr/bin/python2",
    "php":"/usr/bin/php",
    "js":"/usr/bin/node"
}

def runCommand(*popenargs,input=None, capture_output=False, timeout=None, check=False,memorylimit=300,**kwargs):
    #mocking the standard implementation of subprocess.run
    #so we can set memory limit
    lang=kwargs.get("lang")
    if lang:kwargs.pop("lang")
    if input is not None:
        if kwargs.get('stdin') is not None:
            raise ValueError('stdin and input arguments may not both be used.')
        kwargs['stdin'] = subprocess.PIPE

    if capture_output:
        if kwargs.get('stdout') is not None or kwargs.get('stderr') is not None:
            raise ValueError('stdout and stderr arguments may not be used '
                             'with capture_output.')
        kwargs['stdout'] = subprocess.PIPE
        kwargs['stderr'] = subprocess.PIPE

    with subprocess.Popen(*popenargs, **kwargs) as process:
        if system()=='Linux':
            memorylimit=memorylimit+128 #extra 128 mb for startup
            memorylimithard=memorylimit*1024**2+10024
            
            if lang!="js":
                #js is single threaded that means we would be setting stack limit
                #for the entire js interpreter since js relies on callback functions
                #for it operations which essentially uses stack
                resource.prlimit(process.pid,resource.RLIMIT_DATA,(memorylimit*1024**2,memorylimithard))
            resource.prlimit(process.pid,resource.RLIMIT_STACK,(memorylimit*1024**2,memorylimithard))
            
        try:
            stdout, stderr = process.communicate(input, timeout=timeout)
        except subprocess.TimeoutExpired as exc:
            process.kill()
            if subprocess._mswindows:
                # Windows accumulates the output in a single blocking
                # read() call run on child threads, with the timeout
                # being done in a join() on those threads.  communicate()
                # _after_ kill() is required to collect that and add it
                # to the exception.
                exc.stdout, exc.stderr = process.communicate()
            else:
                # POSIX _communicate already populated the output so
                # far into the TimeoutExpired exception.
                process.wait()
            raise
        except:  # Including KeyboardInterrupt, communicate handled that.
            process.kill()
            # We don't call process.wait() as .__exit__ does that for us.
            raise
        retcode = process.poll()
        if check and retcode:
            raise subprocess.CalledProcessError(retcode, process.args,
                                     output=stdout, stderr=stderr)
    return subprocess.CompletedProcess(process.args, retcode, stdout, stderr)


class Task:
    """
    Handles running of submitted code and updates the submission details in the database
    """

    @classmethod
    def taskObj(cls,d):
        if isinstance(d,dict):
            obj=object()
            for classvar in d:
                setattr(obj,classvar,d[classvar])
            setattr(obj,"run",)
            return obj
            
    PossibelTasksState=["initialize","running","finished"]
    def __init__(self,lang,content,userid,problem,id,stype,codefile,contestid="",ctype=""):
        """
        :param stype: the type of submission. differentiates actual 
                      test cases from sample cases.
        :param content: code content
        :param problem: an Instance of :class: `ProblemInstance`.
        """
        self.state=Task.PossibelTasksState[0]
        self.lang=lang
        self.stype = stype 
        self.codefile = codefile
        if self.codefile:
            self.content = self.codefile.read().decode("utf-8") 
        else:
            self.content = content # get submitted code content    
        self.userid=userid  
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

        self.cases=[i.strip() for i in self.cases]
        self.answercase=[i.strip() for i in self.answercase]

        self.timelimit=problem.getTimeLimit()
        self.memlimit=problem.getMemLimit()
        self.enter()

    def toJson(self):
        return {"state":self.state,"lang":self.lang,"userid":self.userid,"_id":self.id,"result":self.result}

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return str(self.__dict__)
    
    def free(self):
        del self.contestid,self.ctype,self.problem,self.stype
        del self.cases,self.answercase,self.timelimit,self.memlimit

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


    def enter(self): 
        self.filename=self.randomFilename()
        if self.lang.lower()=="java":
            filename=os.path.join(*self.filename.split(".")[:-1])
            self.folder="/tmp/{}/{}/".format(self.lang,filename)
            os.makedirs(self.folder,exist_ok=True)
        else:
            self.folder="/tmp/{}/".format(self.lang)
        self.filepath=self.folder+self.filename
        with open(self.filepath,"w+") as f:
            f.write(self.content) 
        self.timeofsubmission=str(datetime.now())
    
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
    
    def formatRunOutput(self,string):
        if not string:return string
        #starting by replacing all file name with a generic name
        return string.replace(self.filepath,"submited."+self.lang)

    def runPerCase(self,n_cases,binargs,**kwargs):
        for cc in range(n_cases):
            errput = None
            ans = None
            try:
                ans=runCommand(binargs,input=self.cases[cc],**kwargs)
            except subprocess.TimeoutExpired:
                self.result[cc] ={"passed":False,"output":"Timeout","errput":"Timeout"}
                self.verdict = "Failed"
                errput = "TimeOut"
                break
            except MemoryError:
                self.result[cc] ={"passed":False,"output":"Memory Error","errput":"Memory Error"}
                self.verdict = "Failed"
                errput = "OutOFMemory"
                break
            except Exception as e:
                errput="RuntimeError"
                if str(type(e))=="<class 'subprocess.TimeoutExpired'>":
                    errput="TimeOut"
                    
            if ans:
                output=ans.stdout.strip()
                errput=errput or ans.stderr.strip()
                if not output and not errput:
                    errput="No result from Interpreter"
                if ans.returncode > 0:
                    errput="RuntimeError"

                self.result[cc] = {
                                    "passed":output==self.answercase[cc] and ans.returncode==0,
                                    "output":self.formatRunOutput(output),
                                    "errput":self.formatRunOutput(errput)
                                    }             
                if not self.answercase[cc] or ans.returncode>0 or output!=self.answercase[cc]: 
                    self.verdict = "Failed"
            else:
                self.result[cc] = {
                                    "passed":False,
                                    "output":"",
                                    "errput":self.formatRunOutput(errput)
                                    }   
                self.verdict = "Failed"

    def runCompile(self,compiler_name,compile_options,run_options,n_cases,binary):

        compileans=runCommand([compiler_name]+compile_options+[self.filepath],
                                            capture_output=True,encoding="utf-8",memorylimit=self.memlimit)

        #if while trying to compile and there was an error 
        l=len(self.result)
        if compileans.returncode >0 :
            for cc in range(l):
                self.result[cc] ={"passed":False,"output":self.formatRunOutput(compileans.stderr.strip()),"errput":"CompileError"}
            return

    
        self.runPerCase(l,[binary]+run_options,capture_output=True,timeout= self.timelimit,\
                                encoding="utf-8",memorylimit=self.memlimit)

    def run(self,ClientConnection):
        setattr(self,"runtime",time())
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
            self.memlimit= self.memlimit+100 # extra 100mb for interpreted languanges
            args=self.resolveFolder(self.lang)+[self.filepath]
            self.runPerCase(l,args,capture_output=True,timeout= self.timelimit,\
                            encoding="utf-8",memorylimit=self.memlimit,lang=self.lang)
            


        self.state=self.PossibelTasksState[2]
        #create a submission in the database    
        submission_data = {'prblmid':self.problem.getprblmid(),'name':self.problem.getName(),'userid':self.userid,'contestid':self.contestid,'ctype':self.ctype,'codecontent':self.content,
        'lang':self.lang,'stype':self.stype,'result': self.result,'verdict': self.verdict,'timesubmitted':self.timeofsubmission}
        if self.stype == "test":   
            if not bool(self.contestid):
                submission_data.pop('userid', None)
                submission_data.pop('contestid', None)
                submission_data.pop('ctype', None)
                Submission(self.userid).addDoc(submission_data) 
                if self.verdict == "Passed":
                    # problem solved, update this particular problem document
                    update = {"$addToSet": {"solvedby": self.userid}}
                    Problem().flexibleUpdate(update, _id=ObjectId(self.problem.getprblmid()))
            else:
                Submission(self.userid).addDoc(submission_data) #add this submission to the submission document
                self.gradeSubmission(submission_data)    
       
        os.remove(self.filepath)
        if self.lang.lower()=="java":
            rmtree(self.folder,ignore_errors=True)
        self.free()
        ClientConnection.send(["DONE",self.id])

    def gradeSubmission(self, data):
        """
        This method is called in :class: `Task' in task.py to make necessary 
        updates to the database when submission code to a problem in the contest has be run
        """
        userid = data.get('userid')
        contestid = data.get('contestid')
        ctype = data.get('ctype')
        prblmid = data.get('prblmid')
        verdict = data.get('verdict')
        contest_problem = ContestProblem(ctype, contestid).getBy(_id=ObjectId(prblmid))
        contest = Contest(ctype).getBy(_id=ObjectId(contestid))
        contest_start_time = contest.get('starttime')
        submission_time = datetime.now().timestamp() - contest_start_time

        prblmscorefield = 'problemscore.{}'.format(prblmid)
        if verdict != "Passed": 
            score = 0  
            penalty = -10
            # update the penalty field
            update = {'$inc': {'penalty': penalty}} 
            pScore = contest_problem.get('prblmscore')
            argDict={"contestid":contestid, prblmscorefield:{'$ne': pScore}}
            UserRegisteredContest(userid).flexibleUpdate(update, **argDict)  
        else:
            score = contest_problem.get('prblmscore')
            penalty = 0

        # update the user score for that problem and time penalty, if the new score is greater than the prev one
        update = {'$set': {'problemscore.{}'.format(prblmid): score}, '$inc': {'timepenalty': submission_time}}  
        argDict={"contestid":contestid,prblmscorefield:{'$lte': score}}
        if UserRegisteredContest(userid).flexibleUpdate(update, **argDict): 
            # calculate the total score
            reg_contest = UserRegisteredContest(userid).getBy(contestid=contestid)
            problemscore = reg_contest.get('problemscore')
            totalscore = reg_contest.get('penalty')
            timepenalty = reg_contest.get('timepenalty')
            for each in problemscore: 
                totalscore += problemscore[each]
            # update the total score
            update = {"$set": {'totalscore': totalscore}}
            UserRegisteredContest(userid).flexibleUpdate(update, contestid=contestid)   

            # update the contest document to reflect this participants current score. 
            update = {"$set": {'participants.{}.currscore'.format(userid): totalscore,
            'participants.{}.timepenalty'.format(userid): timepenalty}}
            Contest(ctype).flexibleUpdate(update, _id=ObjectId(contestid)) 
            data['score'] = totalscore
            current_app.socketio.emit('newscore', {'data':totalscore},namespace='/scoreboard/')
