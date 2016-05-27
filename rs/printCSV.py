from DbRequests import DbRequests
from Evaluation import Evaluation
import sys

def main(argv):
    if len(argv) < 2 or len(argv) > 3:
        print "Usage: python printCSV.py [locationId] [userLimit] [userOffset]"
        sys.exit(2)

    db = DbRequests()
    evaluate = Evaluation()

    limit = int(argv[1])
    locationId = str(argv[0])
    offset = 0

    if len(argv) == 3:
        offset = int(argv[2])

    res = db.users_and_hotel_in_location(locationId)
    i = 0

    for row in res:
        if row[2] == 5:
            if i >= offset:
                evaluate.evaluateDistinct(row[0], locationId, row[1])

            i += 1

        if i >= (limit+offset):
            break

    evaluate.printCSV()
    sys.exit(2)

if __name__ == "__main__":
    main(sys.argv[1:])