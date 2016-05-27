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

    def users_and_hotel_in_location(self, location):
        q = "MATCH (p:Place {hash: " + location + "})-[:OFFERS]-(h:Hotel)-[:RATED_BY]-(r:Review)-[:WRITTEN_BY]->(u:User) RETURN u.name,h.id,r.ratingOverall"
        return self.checkCache(q)

    def hotels_in_same_class_in_location(self, hotel, clas):
        q = "MATCH (h1:Hotel {id: \"" + hotel + "\"})-[:LOCATED_IN]-(p:Place)-[:OFFERS]->(h2: Hotel {class: " + str(clas) + "}) RETURN h2"
        #print(q)
        return self.run(q)

    def users_same_hotel_for_target_location(self, hotel, location, user):
        q = "MATCH (h:Hotel {id: \"" + hotel + "\"})-[:BOOKED_BY]->(u:User)-[:HAS_VISITED]->(p:Place {hash: " + location + "}) WHERE NOT u.name = \"" + user + "\" RETURN u"
        #print(q)
        return self.run(q)

    def reviews_for_user_set(self, hotel, users):
        q = "MATCH (h: Hotel {id: \"" + hotel + "\"})-[RATED_BY]-(r:Review)-[WRITTEN_BY]->(u:User) WHERE u.name IN ['" + "','".join(users) + "'] RETURN u,r"
        #print(q)
        return self.run(q)

    def all_users_for_location(self, user=None, location=None):
        if user == None:
            q = "MATCH (p:Place {hash: " + location + "})-[:VISITED_BY]->(u:User) RETURN u"
            return self.checkCache(q)
        else:
            q = "MATCH (p:Place {hash: " + location + "})-[:VISITED_BY]->(u:User) WHERE NOT u.name = \"" + user + "\" RETURN u"
            return self.run(q)

    def all_users_for_hotel(self, user, hotel):
        q = "MATCH (h:Hotel {id: \"" + hotel + "\"})-[:BOOKED_BY]->(u:User) WHERE NOT u.name = \"" + user + "\" RETURN u"

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
