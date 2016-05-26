__author__ = 'Christian'

from DbRequests import DbRequests
from Run import Execution
from Evaluation import Evaluation


#execc = Execution()

# Paris - 2704655808
# Los Angeles - 1209176819

db = DbRequests()
evaluate = Evaluation()

res = db.users_and_hotel_in_location("1209176819")
#res = db.run("MATCH (p:Place{hash: 2704655808})-[:VISITED_BY]->(u:User) RETURN u LIMIT 300")

users = {}

#res[0]
i = 0
j = 0

for row in res:
    if row[2] == 1 or row[2] == 2:
        j += 1
        #evaluate.evaluateDistinct(row[0], "1209176819", row[1], row[2])

    if row[2] == 5:
        i += 1
        evaluate.evaluateDistinct(row[0], "1209176819", row[1], row[2])

    #users.append(row[0]["data"]["name"])
    #print row
    if i >= 30:
        break


#print evaluate.measuresJoined

evaluate.printAggregatedDistinct()
#for user in users:
#execc.run(user_id="John S", location="2704655808")

