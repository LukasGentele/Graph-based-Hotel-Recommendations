import hashlib
import pickle
import datetime
from Run import Execution
from DbRequests import DbRequests
import operator
import math

class Evaluation:
    cache = {}
    measures = {}
    measuresJoined = {}

    weights = [0.2, 0.2, 0.2, 0.2, 0.2, 0.2]

    blacklist = [
        "A TripAdvisor Member",
        "lass=",
        "Posted by a La Quinta traveler",
        "Bus_Travel_TX",
        "Posted by an Easytobook.com traveler",
        "Posted by an Accorhotels.com traveler",
        "Posted by a cheaprooms.com traveler",
        "Posted by a Worldhotels.com traveler",
        "Posted by a Virgin Holidays traveler",
        "Posted by an OctopusTravel traveler",
        "Posted by a Hotell.no traveler",
        "Posted by a Husa Hoteles traveler",
        "Posted by a Best Western traveler",
        "Posted by a Langham Hotels traveler",
        "Posted by a trip.ru traveler",
        "Posted by a BanyanTree.com traveler",
        "Posted by a Deutsche Bahn traveler",
        "Posted by a Partner traveler",
        "Posted by a Cleartrip traveler",
        "Posted by a Wyndham Hotel Group traveler"
    ]

    def __init__(self):
        self.runner = Execution()
        self.db = DbRequests()

    def preprocessForEvaluation(self, result, user, location, hotelId, time):
        i = 0

        hotelAmount = len(result[0])
        retArr = []

        for x in result:
            if x != False and len(x) > 0:
                sorted_x = sorted(x.items(), key=operator.itemgetter(1), reverse=True)

                recommendations = [x[0] for x in sorted_x]
                addedRecommendations = []

                if hotelAmount > len(recommendations):
                    if i == 0:
                        raise AssertionError('Measure 1 returned wrong results!')

                    for k in retArr[0]["ranking"]:
                        if k not in recommendations:
                            recommendations.append(k)
                            addedRecommendations.append(k)

                            if len(recommendations) == hotelAmount:
                                break
                elif hotelAmount < len(recommendations):
                    for k in recommendations:
                        if k not in retArr[0]["ranking"]:
                            del recommendations[recommendations.index(k)]

                index = recommendations.index(hotelId)

                _ndpm = self.ndpm(recommendations, hotelId)
                _rScore = self.rScore(index)
                _isInK = self.isInK(recommendations, hotelId)

                retArr.append({
                    "user": user,
                    "location": location,
                    "hotelId": hotelId,
                    "ranking": recommendations,
                    "values": [x[1] for x in sorted_x],
                    "appended": addedRecommendations,
                    "ndpm": _ndpm,
                    "rScore": _rScore,
                    "isInK": _isInK,
                    "position": index,
                    "hotelAmount": hotelAmount,
                    "time": time
                })
            else:
                retArr.append({
                    "user": user,
                    "location": location,
                    "hotelId": hotelId,
                    "notMeasured": True,
                    "time": time
                })

            i += 1

        return retArr

    def run(self, user, location, hotelId):
        a = datetime.datetime.now()
        result = self.runner.run(user_id=user, location=location)
        b = datetime.datetime.now()

        result = self.preprocessForEvaluation(result, user, location, hotelId, (b-a).total_seconds())

        return result

    def getMeasures(self, user, location, hotelId):
        hashQuery = hashlib.sha1(user.encode('utf-8') + location.encode('utf-8') + str(hotelId).encode('utf-8')).hexdigest()

        if hashQuery not in self.cache and self.checkFileSystem(hashQuery) == False:
            self.cache[hashQuery] = self.run(user, location, hotelId)
            self.saveFileSystem(hashQuery)

        return self.cache[hashQuery]

    def printCSV(self, delimiter=";"):
        print("UserName" + delimiter + "PlaceHash" + delimiter + "VisitedHotelId" + delimiter + "HotelId" + delimiter + "Measure1" + delimiter\
              + "Measure2" + delimiter + "Measure3" + delimiter + "Measure4" + delimiter + "Measure5" + delimiter + "Measure6")

        for x in self.measures:
            x = self.measures[x]

            hotelAmount = x[0]["hotelAmount"]

            for i in range(hotelAmount):
                curHotelId = x[0]["ranking"][i]

                _str = str(x[0]["user"]) + delimiter + str(x[0]["location"]) + delimiter + str(x[0]["hotelId"]) + delimiter + str(curHotelId) + delimiter + str(x[0]["values"][i])

                h = 0
                for y in x:
                    if h > 0:
                        if "notMeasured" in y or curHotelId in y["appended"]:
                            _str += delimiter + "-1"
                        else:
                            _str += delimiter + str(y["values"][y["ranking"].index(curHotelId)])

                    h += 1

                print(_str)
        return

    def printAggregatedDistinct(self):
        for i in range(len(self.weights)):
            avgNDPM = 0.0
            avgRScore = 0.0
            avgInK = 0.0
            avgPosition = 0.0
            avgHotelAmount = 0.0
            avgTime = 0.0

            amount = 0

            for x in self.measures:
                x = self.measures[x][i]

                if "notMeasured" not in x:
                    amount += 1

                    avgNDPM += x["ndpm"]
                    avgHotelAmount += x["hotelAmount"]
                    avgRScore += x["rScore"]
                    avgPosition += x["position"]
                    avgTime += x["time"]

                    if x["isInK"] == True:
                        avgInK += 1

            if amount == 0:
                continue

            avgNDPM = avgNDPM / amount
            avgRScore = avgRScore / amount
            avgInK = avgInK / amount
            avgPosition = avgPosition / amount
            avgHotelAmount = avgHotelAmount / amount
            avgTime = avgTime / amount

            print("######")
            print("Measure: " + str(i+1))
            print("Amount: " + str(amount))

            print("Avg NDPM: " + str(avgNDPM))
            print("Avg RScore: " + str(avgRScore))
            print("Avg InK: " + str(avgInK))
            print("Avg Position: " + str(avgPosition))
            print("Avg Time: " + str(avgTime))
            print("HotelAmount: " + str(avgHotelAmount))

    def printAggregatedJoined(self):
        avgNDPM = 0.0
        avgRScore = 0.0
        avgInK = 0.0
        avgPosition = 0.0

        amount = 0

        for x in self.measuresJoined:
            x = self.measuresJoined[x]

            if x["ndpm"] >= 0:
                amount += 1

                avgNDPM += x["ndpm"]
                avgRScore += x["rScore"]
                avgPosition += x["position"]

                if x["isInK"] == True:
                    avgInK += 1

        if amount == 0:
            return

        avgNDPM = avgNDPM / amount
        avgRScore = avgRScore / amount
        avgInK = avgInK / amount
        avgPosition = avgPosition / amount

        print("Amount: " + str(amount))
        print("Avg NDPM: " + str(avgNDPM))
        print("Avg RScore: " + str(avgRScore))
        print("Avg InK: " + str(avgInK))
        print("Avg Position: " + str(avgPosition))

    def evaluateJoined(self, user, location, hotelId, overallRating):
        if user in self.blacklist:
            return

        #print("Start " + str(user))
        data = self.getMeasures(user, location)

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

        if (overallRating == 1 or overallRating == 2):
            sorted_x = sorted(hotelList.items(), key=operator.itemgetter(1))
        else:
            sorted_x = sorted(hotelList.items(), key=operator.itemgetter(1), reverse=True)

        #print sorted_x

        recommendations = [x[0] for x in sorted_x]
        index = recommendations.index(hotelId)

        _ndpm = self.ndpm(recommendations, hotelId)
        _rScore = self.rScore(index)
        _isInK = self.isInK(recommendations, hotelId)

        #print len(recommendations)
        #print _ndpm
        #print index
        #print _isInK

        self.measuresJoined[hashlib.sha1(user.encode('utf-8')).hexdigest()] = {
            "reverse": False,
            "position": index,
            "ndpm": _ndpm,
            "rScore": _rScore,
            "isInK": _isInK,
            "time": data["time"]
        }

    def evaluateDistinct(self, user, location, hotelId):
        if user in self.blacklist:
            return

        #print("Start " + str(user))

        self.measures[hashlib.sha1(user.encode('utf-8')).hexdigest()] = self.getMeasures(user, location, hotelId)

        #del self.cache[hashlib.sha1(user.encode('utf-8') + location.encode('utf-8')).hexdigest()]

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

        if c_u == 0:
            return 0.0

        return abs((c_minus+0.5*c_u0)/float(c_u)) * ((index+1.0)/2.0)

    def rScore(self, val):
        return 1.0/pow(2, (val/5))

    def isInK(self, recommendations, val):
        index = recommendations.index(val) + 1

        if index <= 10:
            return True
        else:
            return False