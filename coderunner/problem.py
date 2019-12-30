class ProblemInstance:
    def __init__(self,problem_ds):
        assert isinstance(problem_ds,dict)
        self.problem=problem_ds

    def getName(self):
        return self.problem["name"]
    def getTimeLimit(self):
        return self.problem["timelimit"]
    def getMemLimit(self):
        return self.problem["memorylimit"]
    def getAuthor(self):
        return self.problem["author"]
    
    def getTestCases(self):
        return self.problem["testcases"]

    def getSizeOfTestCases(self):
        return self.problem["sizeoftestcases"]
    
    def getAnswerForTestCases(self):
        return self.problem["answercases"]
    
    def getSampleCases(self):
        return self.problem["samplecases"]

    def getSizeOfSampleCases(self):
        return self.problem["sizeofsamplecases"]
    
    def getAnswerForSampleCases(self):
        return self.problem["sampleanswercases"]

    def getProblemStatement(self):
        return self.problem["problemstatement"]

    def getProblemCategory(self):
        return self.problem["category"]
    