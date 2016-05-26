__author__ = 'Christian'

from Run import Execution
from DbRequests import DbRequests
import pickle

execc = Execution()
#db = DbRequests()
#res = db.run("MATCH (p:Place{hash: 2704655808})-[:VISITED_BY]->(u:User) RETURN u LIMIT 300")

#users = set()
#for row in res:
#    users.add(row[0]["data"]["name"])

#for user in users:

results = execc.run(user_id="John S", location="2704655808")

#425097329
#"John S"