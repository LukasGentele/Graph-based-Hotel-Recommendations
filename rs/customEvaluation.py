from DbRequests import DbRequests
from Evaluation import Evaluation
import sys

def main(argv):
    if len(argv) != 11:
        # python customEvaluation.py 1209176819 1 0 0.2 0.2 0.2 0.2 0.2 y 0 100
        print "Usage: python customEvaluation.py [location] [limit] [offset] [1] [2] [3] [4] [6] [Measure 5 y/n] [lowerBoundReviewCount] [upperBoundReviewCount]"
        sys.exit(2)

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

    db = DbRequests()
    evaluate = Evaluation()

    locationId = str(argv[0])
    limit = int(argv[1])
    offset = int(argv[2])

    weights = [float(argv[3]), float(argv[4]), float(argv[5]), float(argv[6]), 0, float(argv[7])]

    if ( str(argv[8]) == "n" ):
        measure5 = False
    else:
        measure5 = True

    lowerReviewBound = int(argv[9])
    upperReviewBound = int(argv[10])

    res = db.users_and_hotel_in_location_with_bound(locationId, lowerReviewBound, upperReviewBound)
    i = 0

    for row in res:
        if row[0] in blacklist:
            continue

        if row[2] == 5:
            if i >= offset:
                print("User(" + str(i) + "): " + row[0])
                evaluate.evaluateJoined(row[0], locationId, row[1], weights, measure5)

            i += 1

        if i >= (limit+offset):
            break

    print("\n\n### Input Params ###\n")
    print("Weights:")
    print("Measure 1: " + str(weights[0]))
    print("Measure 2: " + str(weights[1]))
    print("Measure 3: " + str(weights[2]))
    print("Measure 4: " + str(weights[3]))
    print("Measure 5: " + str(argv[8]))
    print("Measure 6: " + str(weights[5]))

    print("\nLocation: " + str(locationId))
    print("Limit/Offset: " + str(limit) + "/" + str(offset))
    print("Lower/Upper Reviewbound: " + str(lowerReviewBound) + "/" + str(upperReviewBound))
    evaluate.printAggregatedJoined()
    #print(evaluate.measuresJoined)
    sys.exit(2)

if __name__ == "__main__":
    main(sys.argv[1:])