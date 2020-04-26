import math
class Rating:
    def __init__(self, participants, owner=None):
        self.owner = owner
        self.participants = participants
        self.N = len(self.participants)

    def performaceProbability(self, Ra, Rb, Va, Vb): 
        return (1/(1+(math.pow(4, (Ra-Rb)/math.sqrt(Va**2 + Vb**2))))) + 1

    def expectedRank(self):
        ERank = 0
        for key in self.participants:
            other = self.participants[key]
            if other['uid'] != self.owner['uid']:
                ERank += self.performaceProbability(self.owner['rating'], other['rating'], self.owner['volatility'], other['volatility'])
        return ERank

    def expectedPerformace(self, erank):
        return math.log(self.N/(erank-1))/math.log(4)

    def actualPerformace(self):
        currrank = self.owner['currrank']
        return math.log(self.N/(currrank-1))/math.log(4)

    def ratingAverage(self):
        return sum(self.participants[key]['rating'] for key in self.participants) / self.N

    def competitionFactor(self):
        sVa = sum(self.participants[key]['volatility']**2 for key in self.participants) / self.N
        Ravg = self.ratingAverage()
        sRa = sum((self.participants[key]['rating'] - Ravg)**2 for key in self.participants) / self.N
        return math.sqrt(sVa + sRa)

    def ratingWeight(self):
        return (0.4*self.owner['timesplayed'] + 0.2)/(0.7*self.owner['timesplayed'] + 0.6)

    def volatilityWeight(self):
        return (0.5*self.owner['timesplayed'] + 0.8)/(self.owner['timesplayed'] + 0.6)
    

    def newRating(self):
        Erank = self.expectedRank()
        Aperf = self.actualPerformace()
        Eperf = self.expectedPerformace(Erank)
        CFactor = self.competitionFactor()
        Rweight = self.ratingWeight()
        new_rating =  self.owner['rating'] + (Aperf - Eperf)*CFactor*Rweight
        # set new volatility
        new_volatility = self.newVolatility(new_rating, self.owner['rating'], self.owner['volatility'])
        self.owner['new_volatility'] = new_volatility
        # set new rating
        self.owner['new_rating'] = new_rating
        return self.owner['rating']

    def newVolatility(self, nRa, oldRa, oldVa):
        vWa = self.volatilityWeight()
        return math.sqrt((vWa*(nRa - oldRa)**2 + oldVa**2) / (vWa + 1.1))

    def calculateRatings(self): 
        for key in self.participants:
            Rating(self.participants, self.participants[key]).newRating()
        return self.participants 
        




