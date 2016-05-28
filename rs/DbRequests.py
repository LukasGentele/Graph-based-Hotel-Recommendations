from neo4jrestclient.client import GraphDatabase
import hashlib
import pickle

class DbRequests:
    cache = {}

    def __init__(self):
        with open("credentials") as f:
            content = f.readlines()

        self.gdb = GraphDatabase(content[0].replace('\r', '').replace('\n', ''),
                                 username=content[1].replace('\r', '').replace('\n', ''), password=content[2])

    def checkCache(self, query):
        hashQuery = hashlib.sha1(query.encode('utf-8')).hexdigest()

        if hashQuery not in self.cache and self.checkFileSystem(hashQuery) == False:
            self.cache[hashQuery] = self.run(query)
            self.saveFileSystem(hashQuery)

        return self.cache[hashQuery]

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

    def run(self, query):
        return self.gdb.query(query)

    def users_and_hotel_in_location_with_bound(self, location, lower, upper):
        q = "MATCH (p:Place {hash: " + str(location) + "})-[:OFFERS]-(h:Hotel)-[:RATED_BY]-(r:Review)-[:WRITTEN_BY]-(u:User)-[:WROTE]->(r2:Review) WHERE NOT(u.name IN ['A TripAdvisor Member', 'lass=', 'Posted by a La Quinta traveler', 'Posted by an Easytobook.com traveler', 'Posted by an Accorhotels.com traveler', 'Posted by a cheaprooms.com traveler', 'Posted by a Worldhotels.com traveler', 'Posted by a Virgin Holidays traveler', 'Posted by an OctopusTravel traveler', 'Posted by a Hotell.no traveler', 'Posted by a Husa Hoteles traveler', 'Posted by a Best Western traveler', 'Posted by a Langham Hotels traveler', 'Posted by a trip.ru traveler', 'Posted by a BanyanTree.com traveler', 'Posted by a Deutsche Bahn traveler', 'Posted by a Partner traveler', 'Posted by a Cleartrip traveler', 'Posted by a Wyndham Hotel Group traveler']) WITH u,h,r,count(r2) as numReviews WHERE numReviews >= " + str(lower) + " AND numReviews <= " + str(upper) + " RETURN u.name,h.id,r.ratingOverall"
        #print (q)
        return self.checkCache(q)

    def users_and_hotel_in_location(self, location):
        q = "MATCH (p:Place {hash: " + location + "})-[:OFFERS]-(h:Hotel)-[:RATED_BY]-(r:Review)-[:WRITTEN_BY]->(u:User) WHERE NOT(u.name IN ['A TripAdvisor Member', 'lass=', 'Posted by a La Quinta traveler', 'Posted by an Easytobook.com traveler', 'Posted by an Accorhotels.com traveler', 'Posted by a cheaprooms.com traveler', 'Posted by a Worldhotels.com traveler', 'Posted by a Virgin Holidays traveler', 'Posted by an OctopusTravel traveler', 'Posted by a Hotell.no traveler', 'Posted by a Husa Hoteles traveler', 'Posted by a Best Western traveler', 'Posted by a Langham Hotels traveler', 'Posted by a trip.ru traveler', 'Posted by a BanyanTree.com traveler', 'Posted by a Deutsche Bahn traveler', 'Posted by a Partner traveler', 'Posted by a Cleartrip traveler', 'Posted by a Wyndham Hotel Group traveler']) RETURN u.name,h.id,r.ratingOverall"
        return self.checkCache(q)

    def hotels_in_same_class_in_location(self, hotel, clas):
        q = "MATCH (h1:Hotel {id: \"" + hotel + "\"})-[:LOCATED_IN]-(p:Place)-[:OFFERS]->(h2: Hotel {class: " + str(clas) + "}) RETURN h2"
        #print(q)
        return self.run(q)

    def users_same_hotel_for_target_location(self, hotel, location, user):
        q = "MATCH (h:Hotel {id: \"" + hotel + "\"})-[:BOOKED_BY]->(u:User)-[:HAS_VISITED]->(p:Place {hash: " + location + "}) WHERE NOT(u.name IN ['A TripAdvisor Member', 'lass=', 'Posted by a La Quinta traveler', 'Posted by an Easytobook.com traveler', 'Posted by an Accorhotels.com traveler', 'Posted by a cheaprooms.com traveler', 'Posted by a Worldhotels.com traveler', 'Posted by a Virgin Holidays traveler', 'Posted by an OctopusTravel traveler', 'Posted by a Hotell.no traveler', 'Posted by a Husa Hoteles traveler', 'Posted by a Best Western traveler', 'Posted by a Langham Hotels traveler', 'Posted by a trip.ru traveler', 'Posted by a BanyanTree.com traveler', 'Posted by a Deutsche Bahn traveler', 'Posted by a Partner traveler', 'Posted by a Cleartrip traveler', 'Posted by a Wyndham Hotel Group traveler']) AND NOT u.name = \"" + user + "\" RETURN u"
        #print(q)
        return self.run(q)

    def reviews_for_user_set(self, hotel, users):
        q = "MATCH (h: Hotel {id: \"" + hotel + "\"})-[RATED_BY]-(r:Review)-[WRITTEN_BY]->(u:User) WHERE u.name IN ['" + "','".join(users) + "'] RETURN u,r"
        #print(q)
        return self.run(q)

    def all_users_for_hotel(self, user, hotel):
        q = "MATCH (h:Hotel {id: \"" + hotel + "\"})-[:BOOKED_BY]->(u:User) WHERE NOT(u.name IN ['A TripAdvisor Member', 'lass=', 'Posted by a La Quinta traveler', 'Posted by an Easytobook.com traveler', 'Posted by an Accorhotels.com traveler', 'Posted by a cheaprooms.com traveler', 'Posted by a Worldhotels.com traveler', 'Posted by a Virgin Holidays traveler', 'Posted by an OctopusTravel traveler', 'Posted by a Hotell.no traveler', 'Posted by a Husa Hoteles traveler', 'Posted by a Best Western traveler', 'Posted by a Langham Hotels traveler', 'Posted by a trip.ru traveler', 'Posted by a BanyanTree.com traveler', 'Posted by a Deutsche Bahn traveler', 'Posted by a Partner traveler', 'Posted by a Cleartrip traveler', 'Posted by a Wyndham Hotel Group traveler']) AND NOT u.name = \"" + user + "\" RETURN u"

        #print(q)
        return self.run(q)

    def user_reviews_per_hotel(self, user, location):
        q = "MATCH (u:User {name: \"" + user + "\"})-[:WROTE]-(r:Review)-[g:RATES]-(h:Hotel)-[:LOCATED_IN]->(p:Place) "\
           + "WHERE NOT p.hash = " + location + " RETURN h.id, r.ratingService, r.ratingLocation, r.ratingSleepQuality, r.ratingValue, r.ratingCleanliness, r.ratingRooms, u.name"
        #print(q)
        return self.run(q)

    def user_reviews_per_hotel_sim2(self, user, location):
        q = "MATCH (u:User {name: \"" + user + "\"})-[:WROTE]-(r:Review)-[g:RATES]-(h:Hotel)-[:LOCATED_IN]->(p:Place) \
            WHERE NOT p.hash = " + location + " RETURN h.class,h.priceLowerLimit,h.priceUpperLimit"
        #print(q)
        return self.run(q)

    def reviews_per_hotel_per_place(self, location):
        q = "MATCH (p:Place {hash: " + str(location) + "})-[:OFFERS]->(h:Hotel)-[:RATED_BY]->(r:Review) "\
                "RETURN h.id, r.ratingOverall, r.ratingService, r.ratingLocation, r.ratingSleepQuality, r.ratingValue, r.ratingCleanliness, r.ratingRooms"
        #print(q)
        return self.checkCache(q)

    def hotels_per_place(self, location):
        q = "MATCH (h:Hotel)-[:LOCATED_IN]->(p:Place {hash:" + location + "}) RETURN h.id,h.class,h.priceLowerLimit,h.priceUpperLimit"
        #print(q)
        return self.checkCache(q)

    def reviews_per_hotel(self, hotel):
        q = "MATCH (h:Hotel {name: \"" + hotel + "\"})-[:RATED_BY]->(r:Review) RETURN r"
        #print(q)
        return self.run(q)

    def hotel_review_for_user_and_location(self, user, location):
        q = "MATCH (u:User {name: \"" + user + "\"})-[:WROTE]-(r:Review)-[:RATES]-(h:Hotel)-[:LOCATED_IN]->(p:Place {hash: "+location+"}) RETURN r.ratingOverall,h.id"
        #print(q)
        return self.checkCache(q)

    def get_nationality_from_user(self, user):
        q = "MATCH (u:User {name:\"" + user + "\"})-[:IS_CITIZEN_OF]->(c:Country) RETURN c.code"

        # print(q)
        return self.run(q)

    def get_amount_hotels_in_place(self, location):
        q = "MATCH (h:Hotel)-[:LOCATED_IN]->(p:Place {hash: " + location + "}) RETURN COUNT(DISTINCT h)"

        return self.checkCache(q)

    def nationality_majoriy_voting(self, user, location):
        code = self.get_nationality_from_user(user)

        if len(code) == 0:
            return False

        q = "MATCH (u:User)-[:HAS_VISITED]->(p:Place {hash: " + location + "}) MATCH (u)-[:IS_CITIZEN_OF]->\
            (c:Country {code:\"" + code[0][0] + "\"}) MATCH (u)-[:WROTE]->(r:Review)-[:RATES]->(h:Hotel)-[:LOCATED_IN]->(p) WHERE NOT(u.name IN ['A TripAdvisor Member', 'lass=', 'Posted by a La Quinta traveler', 'Posted by an Easytobook.com traveler', 'Posted by an Accorhotels.com traveler', 'Posted by a cheaprooms.com traveler', 'Posted by a Worldhotels.com traveler', 'Posted by a Virgin Holidays traveler', 'Posted by an OctopusTravel traveler', 'Posted by a Hotell.no traveler', 'Posted by a Husa Hoteles traveler', 'Posted by a Best Western traveler', 'Posted by a Langham Hotels traveler', 'Posted by a trip.ru traveler', 'Posted by a BanyanTree.com traveler', 'Posted by a Deutsche Bahn traveler', 'Posted by a Partner traveler', 'Posted by a Cleartrip traveler', 'Posted by a Wyndham Hotel Group traveler']) WITH r,h \
            RETURN DISTINCT h.id, SUM(r.ratingOverall) as sumRating ORDER BY sumRating DESC"

        #print(q)
        return self.checkCache(q)
