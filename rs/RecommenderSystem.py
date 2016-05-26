__author__ = 'Christian'

from DbRequests import DbRequests
from scipy.stats import pearsonr
from sklearn.preprocessing import MinMaxScaler
import numpy as np
import json
import pprint
import random


class RecommenderSystem:
    def __init__(self):
        self.db = DbRequests()
        self.blacklist = ["Posted by an Accorhotels.com traveler", "A TripAdvisor Member"]

    def sim_measure1(self, location):
        res = self.db.reviews_per_hotel_per_place(location)
        hotel_scores = dict()
        for result in res:
            #print(result[0]["data"])
            node_id = result[0]["data"]["id"]
            score = result[1]["data"]["ratingOverall"]
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

        for key in hotel_scores.keys():
            print(key, hotel_scores[key])

        return hotel_scores

    def sim_measure2(self, user_id, location):
        res = self.db.user_reviews_per_hotel_sim2(user_id, location)
        count = 0
        avg_class = 0
        for result in res:
            hotel_class = result[0]["data"]["class"]
            if 0 < hotel_class < 6:
                avg_class = avg_class + hotel_class
                count += 1

        avg_class = float(avg_class) / count

        res = self.db.hotels_per_place(location)

        hotel_scores = dict()
        maxi = 0
        for result in res:
            node_id = result[0]["data"]["id"]
            hotel_class = result[0]["data"]["class"]
            class_distance = abs(avg_class - hotel_class)
            maxi = max(maxi, class_distance)
            hotel_scores[node_id] = class_distance

        for key in hotel_scores.keys():
            hotel_scores[key] = 1 - hotel_scores[key] / maxi

        return hotel_scores

    def sim_measure3(self, user_id, location):
        res = self.db.user_reviews_per_hotel_sim2(user_id, location)

        lower_limit = list()
        upper_limit = list()
        for result in res:
            lower_limit_temp = int(result[0]["data"]["priceLowerLimit"])
            upper_limit_temp = int(result[0]["data"]["priceUpperLimit"])

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
            node_id = result[0]["data"]["id"]
            lower_limit_temp = int(result[0]["data"]["priceLowerLimit"])
            upper_limit_temp = int(result[0]["data"]["priceUpperLimit"])
            if lower_limit < 1 or upper_limit < 1:
                hotel_scores[node_id] = 0
            else:
                score_lower = 1
                if lower_limit > lower_limit_temp:
                    score_lower = 1 - ((lower_limit - lower_limit_temp) / float(lower_limit))
                elif upper_limit < lower_limit_temp:
                    score_lower = 0

                score_upper = 1
                if upper_limit < upper_limit_temp:
                    score_upper = 1 - ((upper_limit_temp - upper_limit) / float(upper_limit))
                elif lower_limit > upper_limit_temp:
                    score_upper = 0

                hotel_scores[node_id] = score_upper * 0.75 + score_lower * 0.25

        return hotel_scores

    def sim_measure4(self, user_id, location):
        res = self.db.user_reviews_per_hotel(user_id, location)

        user = res[0][0]["data"]
        user_reviews = list()
        hotels = list()

        for i in range(len(res)):
            user_reviews.append(res[i][1]["data"])
            hotels.append(res[i][2]["data"])

        service_list = list()
        location_list = list()
        sleep_quality_list = list()
        value_list = list()
        cleanliness_list = list()
        rooms_list = list()

        for review in user_reviews:
            service = review["ratingService"]
            if service > 0:
                service_list.append(service)

            location_rating = review["ratingLocation"]
            if location_rating > 0:
                location_list.append(location_rating)

            sleep_quality = review["ratingSleepQuality"]
            if sleep_quality > 0:
                sleep_quality_list.append(sleep_quality)

            value = review["ratingValue"]
            if value > 0:
                value_list.append(value)

            cleanliness = review["ratingCleanliness"]
            if cleanliness > 0:
                cleanliness_list.append(cleanliness)

            rooms = review["ratingRooms"]
            if rooms > 0:
                rooms_list.append(rooms)

        service_var = np.var(service_list)
        location_var = np.var(location_list)
        sleep_quality_var = np.var(sleep_quality_list)
        value_var = np.var(value_list)
        cleanliness_var = np.var(cleanliness_list)
        rooms_var = np.var(rooms_list)

        service_mean = np.mean(service_list)
        location_mean = np.mean(location_list)
        sleep_quality_mean = np.mean(sleep_quality_list)
        value_mean = np.mean(value_list)
        cleanliness_mean = np.mean(cleanliness_list)
        rooms_mean = np.mean(rooms_list)

        weights = [service_var, location_var, sleep_quality_var, value_var, cleanliness_var, rooms_var]

        res = self.db.reviews_per_hotel_per_place(location)

        hotel_avg_asp_rating = dict()
        for result in res:
            node_id = result[0]["data"]["id"]
            score_service = result[1]["data"]["ratingService"]
            score_location = result[1]["data"]["ratingLocation"]
            score_sleep_quality = result[1]["data"]["ratingSleepQuality"]
            score_value = result[1]["data"]["ratingValue"]
            score_cleanliness = result[1]["data"]["ratingCleanliness"]
            score_rooms = result[1]["data"]["ratingRooms"]
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
            temp_list.append(np.mean(self.remove_mv(temp_dic["ratingService"])))
            temp_list.append(np.mean(self.remove_mv(temp_dic["ratingLocation"])))
            temp_list.append(np.mean(self.remove_mv(temp_dic["ratingSleepQuality"])))
            temp_list.append(np.mean(self.remove_mv(temp_dic["ratingValue"])))
            temp_list.append(np.mean(self.remove_mv(temp_dic["ratingCleanliness"])))
            temp_list.append(np.mean(self.remove_mv(temp_dic["ratingRooms"])))

            hotel_avgs_list.append(temp_list)

        user = [user_id, service_mean, location_mean, sleep_quality_mean, value_mean, cleanliness_mean, rooms_mean]

        hotel_scores = dict()
        maxi = 0
        for hotel in hotel_avgs_list:
            distance = self.weighted_euclidean_distance(user[1:7], hotel[1:7], weights)
            maxi = max(maxi, distance)
            hotel_scores[hotel[0]] = distance

        #for hotel in hotel_scores.keys():
        #    print(hotel, (1 - (hotel_scores[hotel] / maxi)))

        return hotel_scores

    def sim_measure5(self, user_id, location):
        res = self.db.user_reviews_per_hotel(user_id, location)
        hotels = list()
        reviews = list()

        for row in res:
            hotels.append(row[2]["data"]["id"])
            reviews.append(row[1]["data"])

        hotel_list_with_other_user = list()
        for i in range(len(hotels)):
            hotel_matrix = list()

            res = self.db.users_same_hotel_for_target_location(hotels[i], location, user_id)
            users = list()
            for row in res:
                users.append(row[0]["data"]["name"])

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
            temp = self.get_rating_values_from_review(reviews[i])
            user_hotel_rating = list()
            user_hotel_rating.append(user_id)
            for rating in temp:
                user_hotel_rating.append(rating)
            hotel_matrix = hotel_list_with_other_user[i]
            for other_user_rating in hotel_matrix:
                confidence = pearsonr(user_hotel_rating[1:7], other_user_rating[1:7])[0]
                if np.isnan(confidence) or confidence <= 0:
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
                rating = row[0]["data"]["ratingOverall"]
                if rating > 3:
                    hotel_id = row[1]["data"]["id"]
                    rating = (rating * filtered_scores[key])/float(5)
                    hotel_scores[hotel_id] = rating

        #for key in hotel_scores.keys():
        #    print(key, hotel_scores[key])

        return hotel_scores

    def get_rating_values_from_review(self, review):
        return_list = list()
        return_list.append(review["ratingService"])
        return_list.append(review["ratingLocation"])
        return_list.append(review["ratingSleepQuality"])
        return_list.append(review["ratingValue"])
        return_list.append(review["ratingCleanliness"])
        return_list.append(review["ratingRooms"])
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
        print(x,y,w)
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


