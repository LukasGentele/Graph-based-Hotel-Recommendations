import hashlib
import pickle
import datetime
from Run import Execution
from RecommenderSystem import RecommenderSystem
from DbRequests import DbRequests
import operator
import math

class Evaluation:
    cache = {}
    measures = {}
    measuresJoined = []

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
        self.rs = RecommenderSystem()

    def preprocessForEvaluation(self, result, user, location, hotelId, time):
        i = 0

        hotelAmount = len(result[0])
        retArr = []

        for x in result:
            if x != False and len(x) > 0:
                sorted_x = sorted(x.items(), key=operator.itemgetter(1), reverse=True)

                recommendations = [x[0] for x in sorted_x]
                addedRecommendations = []

                if i != 0:
                    for k in retArr[0]["ranking"]:
                        if k not in recommendations:
                            recommendations.append(k)
                            addedRecommendations.append(k)

                    tempList = []

                    for k in recommendations:
                        if k in retArr[0]["ranking"]:
                            tempList.append(k)

                    recommendations = tempList

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
                    "time": time[i]
                })
            else:
                retArr.append({
                    "user": user,
                    "location": location,
                    "hotelId": hotelId,
                    "notMeasured": True,
                    "time": time[i]
                })

            i += 1

        return retArr

    def run(self, user, location, hotelId):
        result = []
        time = []

        # MEASURE 1
        a = datetime.datetime.now()
        result.append(self.rs.sim_measure1(location=location))
        b = datetime.datetime.now()

        time.append((b-a).total_seconds())

        # MEASURE 2
        a = datetime.datetime.now()
        result.append(self.rs.sim_measure2(user_id=user, location=location))
        b = datetime.datetime.now()

        time.append((b - a).total_seconds())

        # MEASURE 3
        a = datetime.datetime.now()
        result.append(self.rs.sim_measure3(user_id=user, location=location))
        b = datetime.datetime.now()

        time.append((b - a).total_seconds())

        # MEASURE 4
        a = datetime.datetime.now()
        result.append(self.rs.sim_measure4(user_id=user, location=location))
        b = datetime.datetime.now()

        time.append((b - a).total_seconds())

        # MEASURE 5
        a = datetime.datetime.now()
        result.append(self.rs.sim_measure5(user_id=user, location=location))
        b = datetime.datetime.now()

        time.append((b - a).total_seconds())

        # MEASURE 6
        a = datetime.datetime.now()
        result.append(self.rs.sim_measure6(user_id=user, location=location))
        b = datetime.datetime.now()

        time.append((b - a).total_seconds())

        result = self.preprocessForEvaluation(result, user, location, hotelId, time)

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
        avgIn = []
        avgPosition = 0.0
        avgHotelAmount = 0.0

        amountMeasures = [0,0,0,0,0,0]
        totalTimeMeasures = [0,0,0,0,0,0]
        totalTime = 0.0

        amount = 0

        positionDict = {}

        for x in self.measuresJoined:
            while len(avgIn) < len(x["isInK"]):
                avgIn.append(0)

            amount += 1
            avgNDPM += x["ndpm"]
            avgHotelAmount += x["hotelAmount"]
            avgRScore += x["rScore"]
            avgPosition += x["position"]

            if x["position"] in positionDict:
                positionDict[x["position"]] += 1
            else:
                positionDict[x["position"]] = 1

            for y in range(len(x["notAvailable"])):
                if x["notAvailable"][y] == False:
                    amountMeasures[y] += 1

            for y in range(len(x["totalTime"])):
                totalTimeMeasures[y] += float(x["totalTime"][y])
                totalTime += float(x["totalTime"][y])

            for y in range(len(x["isInK"])):
                if x["isInK"][y] == True:
                    avgIn[y] += 1


        avgNDPM = avgNDPM / amount
        avgRScore = avgRScore / amount
        avgPosition = avgPosition / amount
        avgHotelAmount = avgHotelAmount / amount

        print("\n\n### General Info ###\n")

        print("User Amount: " + str(amount))
        print("HotelAmount: " + str(avgHotelAmount))

        print("\n\n### Evaluation Metrics ###\n")

        print("Avg Position: " + str(avgPosition))
        print("Avg NDPM: " + str(avgNDPM))
        print("Avg RScore (5): " + str(avgRScore))

        if (len(avgIn) >= 30):
            print("Precision at 10: " + str(avgIn[9]/float(amount)*100) + "%")
            print("Precision at 30: " + str(avgIn[29]/float(amount)*100) + "%")

        print("\n\n### Times ###\n")

        for y in range(len(totalTimeMeasures)):
            print("Measure " + str(y+1) + " took: " + str(totalTimeMeasures[y]) + "s (avg. " + str(totalTimeMeasures[y]/max(1,amountMeasures[y])) + ", ex. " + str(amountMeasures[y]) + " times)")

        print("\nTotal Time: " + str(totalTime) + "s")

        print("\n\n### In K ###\n")

        for y in range(len(avgIn)):
            print("In k(" + str(y+1) + "): " + str(avgIn[y]) + " (" + str(avgIn[y]/float(amount)*100) + "%)")

        print("\n\n### Position Distribution ###\n")

        sorted_x = sorted(positionDict.items(), key=operator.itemgetter(0))

        for x,y in sorted_x:
            print(str(x+1) + ";" + str(y))



    def evaluateJoined(self, user, location, hotelId, weights, measure5 = 0.0, skipAtUserAmount = 4000):
        if user in self.blacklist:
            return

        self.rs.setSkipAtUserAmount(skipAtUserAmount)

        data = self.getMeasures(user, location, hotelId)

        i = 0
        newList = {}
        totalTime = []
        notAvailable = [False, False, False, False, False, False]

        # Calculate without 5
        for x in data:
            totalTime.append(0)

            if i == 4 or weights[i] <= 0:
                notAvailable[i] = True
                i += 1
                continue

            totalTime[i] += float(x["time"])

            if "notMeasured" in x:
                notAvailable[i] = True
                i += 1
                continue

            for h in x["ranking"]:
                if h in x["appended"]:
                    break

                if h not in newList:
                    newList[h] = x["values"][x["ranking"].index(h)] * weights[i]
                else:
                    newList[h] += x["values"][x["ranking"].index(h)] * weights[i]

            i += 1

        if measure5 <= 1.0 and "notMeasured" not in data[4]:
            notAvailable[4] = False

            tempList = {}
            y = 0

            totalTime[4] += float(data[4]["time"])

            for x in data[4]["ranking"]:
                if x in data[4]["appended"] or data[4]["values"][y] < measure5:
                    break

                tempList[x] = 10000 + data[4]["values"][y]
                y += 1

            for key, value in newList.iteritems():
                if key not in tempList:
                    tempList[key] = value

            newList = tempList

        sorted_x = sorted(newList.items(), key=operator.itemgetter(1), reverse=True)
        recommendations = [x[0] for x in sorted_x]

        if len(recommendations) == 0 or hotelId not in recommendations:
            return

        index = recommendations.index(hotelId)

        _ndpm = self.ndpm(recommendations, hotelId)
        _rScore = self.rScore(index)

        _isInK = []

        for i in range(1, min(101, len(recommendations))):
            _isInK.append(self.isInK(recommendations, hotelId, i))

        self.measuresJoined.append({
            "user": user,
            "location": location,
            "hotelId": hotelId,
            "ranking": recommendations,
            "ndpm": _ndpm,
            "rScore": _rScore,
            "isInK": _isInK,
            "position": index,
            "notAvailable": notAvailable,
            "hotelAmount": len(recommendations),
            "totalTime": totalTime
        })

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

    def isInK(self, recommendations, val, k = 10):
        index = recommendations.index(val) + 1

        if index <= k:
            return True
        else:
            return False