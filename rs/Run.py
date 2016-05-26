__author__ = 'Christian'

from RecommenderSystem import RecommenderSystem

import pprint


class Execution:

    def __init__(self):
        self.rs = RecommenderSystem()

    def run(self, user_id, location):
        #self.rs.sim_measure1(location=location)
        #self.rs.sim_measure2(user_id=user_id, location=location)
        #self.rs.sim_measure3(user_id=user_id, location=location)
        #self.rs.sim_measure4(user_id=user_id, location=location)
        self.rs.sim_measure5(user_id=user_id, location=location)