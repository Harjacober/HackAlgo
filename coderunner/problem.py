class problem:
    def __init__(self,problem_ds):
        assert isinstance(problem_ds,dict)
        self.problem=problem_ds

    def getName(self):
        return self.problem["name"]

    def getAuthor(self):
        return self.problem["author"]
    
    def getCases(self):
        return self.problem["cases"]

    def getNCases(self):
        return self.problem["ncases"]
    
    def getAnswerForCases(self):
        return self.problem["answercases"]

    
    def getTestCases(self):
        return self.problem["tases"]

    def getNTestCases(self):
        return self.problem["ntcases"]
    
    def getAnswerForTestCases(self):
        return self.problem["answertcases"]
    