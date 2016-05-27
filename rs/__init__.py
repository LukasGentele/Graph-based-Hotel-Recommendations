from DbRequests import DbRequests
from Run import Execution
from Evaluation import Evaluation

# Paris - 2704655808
# Los Angeles - 1209176819

db = DbRequests()
evaluate = Evaluation()

res = db.users_and_hotel_in_location("1209176819")

users = {}
i = 0

for row in res:
    if row[2] == 5:
        i += 1
        print("User(" + str(i) + "): " + row[0])
        evaluate.evaluateDistinct(row[0], "1209176819", row[1])

    if i >= 500:
        break

evaluate.printAggregatedDistinct()
#evaluate.printCSV()