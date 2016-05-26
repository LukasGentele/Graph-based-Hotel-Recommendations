import hashlib
import pickle
import datetime
from Run import Execution
import operator
import math

class Evaluation:
    cache = {}
    measures = {}
    measuresJoined = {}

    weights = [0.2, 0.2, 0.2, 0.2, 0.2]

    def __init__(self):
        self.runner = Execution()

    def run(self, user, location):
        a = datetime.datetime.now()
        result = self.runner.run(user_id=user, location=location)
        b = datetime.datetime.now()

        return {"data": result,
                "time": (b - a)}

    def getMeasures(self, user, location):
        hashQuery = hashlib.sha1(user.encode('utf-8')).hexdigest()

        if hashQuery not in self.cache and self.checkFileSystem(hashQuery) == False:
            self.cache[hashQuery] = self.run(user, location)
            self.saveFileSystem(hashQuery)

        return self.cache[hashQuery]

    def evaluateJoined(self, user, location, hotelId, overallRating):
        data = self.getMeasures(user, location)
        print("Start " + str(user))

        self.measuresJoined[hashlib.sha1(user.encode('utf-8')).hexdigest()] = {}

        weights = self.weights[:]
        i = 0

        for i,x in enumerate(data["data"]):
            if x == False or len(x) == 0 or hotelId not in x.keys():
                amZero = 1

                for j in weights:
                    if j == 0.0:
                        amZero += 1

                divisor = (len(weights) - amZero)

                if( divisor == 0 ):
                    self.measuresJoined[hashlib.sha1(user.encode('utf-8')).hexdigest()] = {
                        "notMeasured": True
                    }

                    return

                share = weights[i]/divisor
                weights[i] = 0

                for j, val in enumerate(weights):
                    if val != 0.0:
                        weights[j] += share

        hotelList = {}

        for i, x in enumerate(data["data"]):
            if weights[i] > 0.0:
                for j in x.keys():
                    if math.isnan(x[j]):
                        continue

                    if j not in hotelList:
                        hotelList[j] = x[j] * weights[i]
                    else:
                        hotelList[j] += x[j] * weights[i]

        sorted_x = sorted(hotelList.items(), key=operator.itemgetter(1), reverse=True)

        recommendations = [x[0] for x in sorted_x]
        index = recommendations.index(hotelId)

        _ndpm = self.ndpm(recommendations, hotelId)
        _rScore = self.rScore(index)
        _isInK = self.isInK(recommendations, hotelId)

        if (overallRating == 1 or overallRating == 2):
            self.measuresJoined[hashlib.sha1(user.encode('utf-8')).hexdigest()][i] = {
                "reverse": True,
                "ndpm": 1 - _ndpm,
                "rScore": 1 - _rScore,
                "isInK": not _isInK
            }
        else:
            self.measuresJoined[hashlib.sha1(user.encode('utf-8')).hexdigest()][i] = {
                "reverse": False,
                "ndpm": _ndpm,
                "rScore": _rScore,
                "isInK": _isInK
            }

    def evaluateDistinct(self, user, location, hotelId, overallRating):
        data = self.getMeasures(user, location)
        print("Start " + str(user))

        self.measures[hashlib.sha1(user.encode('utf-8')).hexdigest()] = {}
        i = 0

        for x in data["data"]:
            if x != False and len(x) > 0 and hotelId in x.keys():
                sorted_x = sorted(x.items(), key=operator.itemgetter(1), reverse=True)

                recommendations = [x[0] for x in sorted_x]
                index = recommendations.index(hotelId)

                _ndpm = self.ndpm(recommendations, hotelId)
                _rScore = self.rScore(index)
                _isInK = self.isInK(recommendations, hotelId)

                if ( overallRating == 1 or overallRating == 2 ):
                    self.measures[hashlib.sha1(user.encode('utf-8')).hexdigest()][i] = {
                        "reverse": True,
                        "ndpm": 1 - _ndpm,
                        "rScore": 1 - _rScore,
                        "isInK": not _isInK
                    }
                else:
                    self.measures[hashlib.sha1(user.encode('utf-8')).hexdigest()][i] = {
                        "reverse": False,
                        "ndpm": _ndpm,
                        "rScore": _rScore,
                        "isInK": _isInK
                    }
            else:
                self.measures[hashlib.sha1(user.encode('utf-8')).hexdigest()][i] = {
                    "notMeasured": True,
                    "ndpm": -1,
                    "rScore": -1,
                    "isInK": False
                }

            i += 1

        del self.cache[hashlib.sha1(user.encode('utf-8') + "-" + location.encode('utf-8')).hexdigest()]

    def checkFileSystem(self, hash):
        if hash in self.cache:
            return True

        try:
            self.cache[hash] = pickle.load(open("cache/" + hash, "rb"))
            return True
        except IOError:
            return False

    def saveFileSystem(self, hash):
        pickle.dump(self.cache[hash], open("cache/" + hash, "wb"))

    def sgn(self, val):
            if( val > 0 ):
                return 1.0
            elif( val < 0 ):
                return -1.0
            else:
                return 0.0

    def ndpm(self, recommendations, hotelId):
        countRecommendations = len(recommendations)
        index = recommendations.index(hotelId)

        c_plus = 0.0
        c_minus = 0.0
        c_u = 0.0

        stop = 0.5 * countRecommendations * (countRecommendations-1)
        iter = 0
        i = 0

        while iter < stop:
            j = i + 1

            while j < countRecommendations:
                r_ui = i
                r_uj = j

                if i>index:
                    if index == 0:
                        rt_ui = i
                    else:
                        rt_ui = i+1.0
                elif i<index:
                    rt_ui = i+1.0
                else:
                    rt_ui = 0.0

                if j>index:
                    if index == 0:
                        rt_uj = j
                    else:
                        rt_uj = j+1.0
                elif j<index:
                    rt_uj = j+1
                else:
                    rt_uj = 0.0

                c_plus += self.sgn(r_ui -r_uj) * self.sgn(rt_ui-rt_uj)
                c_minus += self.sgn(r_ui - r_uj) * self.sgn(rt_uj - rt_ui)
                c_u += abs(self.sgn(r_ui -r_uj) * self.sgn(rt_ui-rt_uj))

                iter += 1
                j += 1
            i += 1

        c_plus = max(0.0, c_plus)
        c_minus = max(0.0, c_minus)
        c_u0 = c_u - (c_plus + c_minus)

        return abs((c_minus+0.5*c_u0)/float(c_u)) * ((index+1.0)/2.0)

    def rScore(self, val):
        return 1.0/pow(2, (val/5))

    def isInK(self, recommendations, val):
        index = recommendations.index(val) + 1

        if index <= 10:
            return True
        else:
            return False