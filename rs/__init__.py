__author__ = 'Christian'

from Run import Execution
from DbRequests import DbRequests
from Evaluation import Evaluation

execc = Execution()

# Paris - 2704655808
# Los Angeles - 1209176819

db = DbRequests()

#res = db.users_and_hotel_in_location("1209176819")
#res = db.run("MATCH (p:Place{hash: 2704655808})-[:VISITED_BY]->(u:User) RETURN u LIMIT 300")

users = {}

#res[0]

#for row in res:
    #users.append(row[0]["data"]["name"])
    #print row

#for user in users:

execc.run(user_id="John S", location="2704655808")



#425097329
#"John S"