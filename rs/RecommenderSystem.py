__author__ = 'Christian'

from DbRequests import DbRequests
from scipy.stats import pearsonr
import numpy as np
import itertools


class RecommenderSystem:
    def __init__(self):
        self.db = DbRequests()
        self.blacklist = ['A TripAdvisor Member', 'lass=', 'Posted by a La Quinta traveler', 'Posted by an Easytobook.com traveler', 'Posted by an Accorhotels.com traveler', 'Posted by a cheaprooms.com traveler', 'Posted by a Worldhotels.com traveler', 'Posted by a Virgin Holidays traveler', 'Posted by an OctopusTravel traveler', 'Posted by a Hotell.no traveler', 'Posted by a Husa Hoteles traveler', 'Posted by a Best Western traveler', 'Posted by a Langham Hotels traveler', 'Posted by a trip.ru traveler', 'Posted by a BanyanTree.com traveler', 'Posted by a Deutsche Bahn traveler', 'Posted by a Partner traveler', 'Posted by a Cleartrip traveler', 'Posted by a Wyndham Hotel Group traveler']
        np.seterr(all="ignore")

    def setSkipAtUserAmount(self, userAmount):
        self.db.skipAtUserAmount = userAmount

    def sim_measure1(self, location):
        #print("Measure 1")
        res = self.db.reviews_per_hotel_per_place(location)

        hotel_scores = dict()
        for result in res:
            #print(result[0]["data"])
            node_id = result[0]
            score = result[1]
            if node_id in hotel_scores.keys():
                tmp_list = hotel_scores[node_id]
                tmp_list.append(score)
                hotel_scores[node_id] = tmp_list
            else:
                hotel_scores[node_id] = [score]

        maxi = 0
        for key in hotel_scores.keys():
            avg_score = np.mean(hotel_scores[key])
            maxi = max(avg_score, maxi)
            hotel_scores[key] = avg_score

        for key in hotel_scores.keys():
            hotel_scores[key] = hotel_scores[key] / maxi

        return hotel_scores

    def sim_measure2(self, user_id, location):
        #print("Measure 2")
        res = self.db.user_reviews_per_hotel_sim2(user_id, location)
        count = 0
        avg_class = 0
        for result in res:
            hotel_class = result[0]
            if 0 < hotel_class < 6:
                avg_class = avg_class + hotel_class
                count += 1

        if count == 0:
            return False

        avg_class = float(avg_class) / count

        res = self.db.hotels_per_place(location)

        hotel_scores = dict()
        maxi = 0
        for result in res:
            node_id = result[0]
            hotel_class = result[1]
            class_distance = abs(avg_class - hotel_class)
            maxi = max(maxi, class_distance)
            hotel_scores[node_id] = class_distance

        for key in hotel_scores.keys():
            hotel_scores[key] = 1 - hotel_scores[key] / maxi

        return hotel_scores

    def sim_measure3(self, user_id, location):
        #print("Measure 3")
        res = self.db.user_reviews_per_hotel_sim2(user_id, location)

        lower_limit = list()
        upper_limit = list()
        for result in res:
            lower_limit_temp = int(result[1])
            upper_limit_temp = int(result[2])

            if lower_limit_temp < 1:
                continue
            if upper_limit_temp < 1:
                continue
            lower_limit.append(lower_limit_temp)
            upper_limit.append(upper_limit_temp)

        lower_limit = np.mean(lower_limit) - np.sqrt((np.std(lower_limit)))
        upper_limit = np.mean(upper_limit) + np.sqrt(np.std(upper_limit))

        res = self.db.hotels_per_place(location)

        hotel_scores = dict()
        for result in res:
            node_id = result[0]
            lower_limit_temp = int(result[2])
            upper_limit_temp = int(result[3])
            if lower_limit_temp < 1 or upper_limit_temp < 1 or lower_limit < 1 or upper_limit < 1 or str(lower_limit) == "nan" or str(upper_limit) == "nan":
                hotel_scores[node_id] = 0
            else:
                score_lower = 1
                if lower_limit > lower_limit_temp:
                    score_lower = 1 - ((lower_limit - lower_limit_temp) / float(lower_limit))
                elif upper_limit < lower_limit_temp:
                    score_lower = 0

                score_upper = 1
                if upper_limit < upper_limit_temp:
                    score_upper = 1 - ((upper_limit_temp - upper_limit) / float(upper_limit_temp))
                elif lower_limit > upper_limit_temp:
                    score_upper = 0

                hotel_scores[node_id] = score_upper * 0.75 + score_lower * 0.25

        return hotel_scores

    def sim_measure4(self, user_id, location):
        #print("Measure 4")
        res = self.db.user_reviews_per_hotel(user_id, location)

        if len(res) == 0:
            return False

        service_list = list()
        location_list = list()
        sleep_quality_list = list()
        value_list = list()
        cleanliness_list = list()
        rooms_list = list()

        for result in res:
            service = result[1]
            if service > 0:
                service_list.append(service)

            location_rating = result[2]
            if location_rating > 0:
                location_list.append(location_rating)

            sleep_quality = result[3]
            if sleep_quality > 0:
                sleep_quality_list.append(sleep_quality)

            value = result[4]
            if value > 0:
                value_list.append(value)

            cleanliness = result[5]
            if cleanliness > 0:
                cleanliness_list.append(cleanliness)

            rooms = result[6]
            if rooms > 0:
                rooms_list.append(rooms)

        small_number = 0.00000001

        service_var = np.var(service_list)
        if service_var == 0 or str(service_var) == "nan":
            service_var = small_number

        location_var = np.var(location_list)
        if location_var == 0 or str(location_var) == "nan":
            location_var = small_number

        sleep_quality_var = np.var(sleep_quality_list)
        if sleep_quality_var == 0 or str(sleep_quality_var) == "nan":
            sleep_quality_var = small_number

        value_var = np.var(value_list)
        if value_var == 0 or str(value_var) == "nan":
            value_var = small_number

        cleanliness_var = np.var(cleanliness_list)
        if cleanliness_var == 0 or str(cleanliness_var) == "nan":
            cleanliness_var = small_number

        rooms_var = np.var(rooms_list)
        if rooms_var == 0 or str(rooms_var) == "nan":
            rooms_var = small_number


        if len(service_list) == 0:
            service_mean = 3
        else:
            service_mean = np.mean(service_list)

        if len(location_list) == 0:
            location_mean = 3
        else:
            location_mean = np.mean(location_list)

        if len(sleep_quality_list) == 0:
            sleep_quality_mean = 3
        else:
            sleep_quality_mean = np.mean(sleep_quality_list)

        if len(value_list) == 0:
            value_mean = 3
        else:
            value_mean = np.mean(value_list)

        if len(cleanliness_list) == 0:
            cleanliness_mean = 3
        else:
            cleanliness_mean = np.mean(cleanliness_list)

        if len(rooms_list) == 0:
            rooms_mean = 3
        else:
            rooms_mean = np.mean(rooms_list)

        weights = [service_var, location_var, sleep_quality_var, value_var, cleanliness_var, rooms_var]

        res = self.db.reviews_per_hotel_per_place(location)

        hotel_avg_asp_rating = dict()
        for result in res:
            node_id = result[0]
            score_service = result[2]
            score_location = result[3]
            score_sleep_quality = result[4]
            score_value = result[5]
            score_cleanliness = result[6]
            score_rooms = result[7]
            if node_id in hotel_avg_asp_rating.keys():
                tmp_dic = hotel_avg_asp_rating[node_id]

                tmp = tmp_dic["ratingService"]
                tmp.append(score_service)
                tmp_dic["ratingService"] = tmp

                tmp = tmp_dic["ratingLocation"]
                tmp.append(score_location)
                tmp_dic["ratingLocation"] = tmp

                tmp = tmp_dic["ratingSleepQuality"]
                tmp.append(score_sleep_quality)
                tmp_dic["ratingSleepQuality"] = tmp

                tmp = tmp_dic["ratingValue"]
                tmp.append(score_value)
                tmp_dic["ratingValue"] = tmp

                tmp = tmp_dic["ratingCleanliness"]
                tmp.append(score_cleanliness)
                tmp_dic["ratingCleanliness"] = tmp

                tmp = tmp_dic["ratingRooms"]
                tmp.append(score_rooms)
                tmp_dic["ratingRooms"] = tmp

                hotel_avg_asp_rating[node_id] = tmp_dic
            else:
                tmp_dic = dict()
                tmp_dic["ratingService"] = [score_service]
                tmp_dic["ratingLocation"] = [score_location]
                tmp_dic["ratingSleepQuality"] = [score_sleep_quality]
                tmp_dic["ratingValue"] = [score_value]
                tmp_dic["ratingCleanliness"] = [score_cleanliness]
                tmp_dic["ratingRooms"] = [score_rooms]
                hotel_avg_asp_rating[node_id] = tmp_dic

        hotel_avgs_list = list()
        for key in hotel_avg_asp_rating.keys():
            temp_dic = hotel_avg_asp_rating[key]
            temp_list = list()

            temp_list.append(key)

            if len(self.remove_mv(temp_dic["ratingService"])) == 0:
                temp_list.append(3)
            else:
                temp_list.append(np.mean(self.remove_mv(temp_dic["ratingService"])))

            if len(self.remove_mv(temp_dic["ratingLocation"])) == 0:
                temp_list.append(3)
            else:
                temp_list.append(np.mean(self.remove_mv(temp_dic["ratingLocation"])))

            if len(self.remove_mv(temp_dic["ratingSleepQuality"])) == 0:
                temp_list.append(3)
            else:
                temp_list.append(np.mean(self.remove_mv(temp_dic["ratingSleepQuality"])))

            if len(self.remove_mv(temp_dic["ratingValue"])) == 0:
                temp_list.append(3)
            else:
                temp_list.append(np.mean(self.remove_mv(temp_dic["ratingValue"])))

            if len(self.remove_mv(temp_dic["ratingCleanliness"])) == 0:
                temp_list.append(3)
            else:
                temp_list.append(np.mean(self.remove_mv(temp_dic["ratingCleanliness"])))

            if len(self.remove_mv(temp_dic["ratingRooms"])) == 0:
                temp_list.append(3)
            else:
                temp_list.append(np.mean(self.remove_mv(temp_dic["ratingRooms"])))

            hotel_avgs_list.append(temp_list)

        #user = [user_id, service_mean, location_mean, sleep_quality_mean, value_mean, cleanliness_mean, rooms_mean]
        user = [user_id, 5, 5, 5, 5, 5, 5]

        hotel_scores = dict()
        maxi = 0
        for hotel in hotel_avgs_list:
            distance = self.weighted_euclidean_distance(user[1:7], hotel[1:7], weights)
            maxi = max(maxi, distance)
            hotel_scores[hotel[0]] = distance

        for hotel in hotel_scores.keys():
            hotel_scores[hotel] = (1 - (hotel_scores[hotel] / maxi))

        for hotel in hotel_scores.keys():
            if str(hotel_scores[hotel]) == "nan":
                print(hotel, hotel_scores[hotel])

        return hotel_scores

    def sim_measure5(self, user_id, location):
        #print("Measure 5")
        res = self.db.user_reviews_per_hotel(user_id, location)
        hotels = list()
        reviews = list()

        maxReviews = 100
        #print(len(res))

        for row in res:
            hotels.append(row[0])
            reviews.append([row[1],row[2],row[3],row[4],row[5],row[6]])

            maxReviews -= 1

            if maxReviews <= 0:
                return {}


        hotel_list_with_other_user = list()
        for i in range(len(hotels)):
            hotel_matrix = list()

            res = self.db.users_same_hotel_for_target_location(hotels[i], location, user_id)
            users = list()
            for row in res:
                users.append(row[0]["data"]["name"].replace("'", "\\'"))

            for blacklisted in self.blacklist:
                if blacklisted in users:
                    users.remove(blacklisted)

            res = self.db.reviews_for_user_set(hotels[i], users)
            for j in range(0, len(res), 2):
                line_in_matrix = list()
                line_in_matrix.append(res[j][0]["data"]["name"])
                rev = self.get_rating_values_from_review(res[j][1]["data"])
                for asp in rev:
                    line_in_matrix.append(asp)

                hotel_matrix.append(line_in_matrix)
            hotel_list_with_other_user.append(hotel_matrix)

        similarity_score = list()
        for i in range(len(hotels)):
            temp = reviews[i]
            user_hotel_rating = list()
            user_hotel_rating.append(user_id)
            for rating in temp:
                user_hotel_rating.append(rating)
            hotel_matrix = hotel_list_with_other_user[i]

            for other_user_rating in hotel_matrix:
                temp_other_user = other_user_rating[1:7]
                temp_user = user_hotel_rating[1:7]

                bitmask = list()
                for j in range(len(temp_user)):
                    if temp_user[j] < 1 or temp_other_user[j] < 1:
                        bitmask.append(0)
                    else:
                        bitmask.append(1)

                temp_user = list(itertools.compress(temp_user, bitmask))
                temp_other_user = list(itertools.compress(temp_other_user, bitmask))

                if len(temp_user) == 0:
                    confidence = 0
                else:
                    confidence = pearsonr(temp_user, temp_other_user)[0]

                if np.isnan(confidence) or float(confidence) <= float(0):
                    confidence = 0

                similarity_score.append((other_user_rating[0], confidence))
        filtered_scores = dict()
        for sims in similarity_score:
            if not sims[1] == 0:
                if sims[0] in filtered_scores.keys():
                    filtered_scores[sims[0]] = max(sims[1], filtered_scores[sims[0]])
                else:
                    filtered_scores[sims[0]] = sims[1]

        hotel_scores = dict()
        for key in filtered_scores.keys():
            res = self.db.hotel_review_for_user_and_location(key,location)
            for row in res:
                rating = row[0]
                if rating > 3:
                    hotel_id = row[1]
                    rating = (rating * filtered_scores[key])/float(5)
                    if hotel_id in hotel_scores.keys():
                        hotel_scores[hotel_id] = max(rating, hotel_scores[hotel_id])
                    else:
                        hotel_scores[hotel_id] = rating

        for key in hotel_scores.keys():
            if np.isnan(hotel_scores[key]):
                hotel_scores.pop(key, None)

        return hotel_scores

    def sim_measure6(self, user_id, location):
        res = self.db.nationality_majoriy_voting(user_id, location)

        if res == False or len(res) == 0 or len(res[0]) != 2:
            return {}

        hotel_scores = dict()

        maxi = res[0][1]
        for row in res:
            hotel_scores[row[0]] = float(row[1]) / float(maxi)

        return hotel_scores

    def get_rating_values_from_review(self, review):
        return_list = list()
        return_list.append(int(review["ratingService"]))
        return_list.append(int(review["ratingLocation"]))
        return_list.append(int(review["ratingSleepQuality"]))
        return_list.append(int(review["ratingValue"]))
        return_list.append(int(review["ratingCleanliness"]))
        return_list.append(int(review["ratingRooms"]))
        return return_list

    def weighted_mean(self, x, w):
        sum = 0
        for i in range(len(x)):
            sum = sum + x[i]*w[i]
        return float(sum / float(np.sum(w)))

    def weighted_covariance(self, x, y, w):
        weighted_mean_x = self.weighted_mean(x,w)
        weighted_mean_y = self.weighted_mean(y,w)

        sum = 0
        for i in range(len(x)):
           sum = sum + (w[i] * (x[i] - weighted_mean_x) * (y[i] - weighted_mean_y))

        return float(sum / float(np.sum(w)))

    def weighted_correlation(self, x, y, w):
        #print(x,y,w)
        return float(self.weighted_covariance(x, y, w) / float((np.sqrt((self.weighted_covariance(x, x, w)) * self.weighted_covariance(y, y, w)))))

    def weighted_euclidean_distance(self, x, y, w):
        sum = 0
        for i in range(len(x)):
            sum += np.sqrt(w[i] * (x[i] - y[i])**2)

        return sum


    def remove_mv(self, x):
        temp = list()
        for i in range(len(x)):
            if x[i] > 0:
                temp.append(x[i])

        return temp


