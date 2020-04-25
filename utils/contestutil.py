
class ContestStatus: 

    @staticmethod
    def getStatusKey(code:int):
        contestStatus = {100:'inreview', 200:'active', 300:'started', 400:'completed'}
        return contestStatus[code]

    @staticmethod 
    def getStatusCode(key:str):
        contestCode = {'inreview':100, 'active':200, 'started':300, 'completed':400}
        return contestCode[key] 
    1