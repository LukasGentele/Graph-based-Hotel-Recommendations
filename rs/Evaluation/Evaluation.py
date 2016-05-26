class Evaluation:
    def sgn(self, val):
            if( val > 0 ):
                return 1.0
            elif( val < 0 ):
                return -1.0
            else:
                return 0.0

    def ndpm(self, recommendations, hotelId):
        countRecommendations = len(recommendations)
        index = recommendations.index(hotelId)

        c_plus = 0.0
        c_minus = 0.0
        c_u = 0.0

        stop = 0.5 * countRecommendations * (countRecommendations-1)
        iter = 0
        i = 0

        while iter < stop:
            j = i + 1

            while j < countRecommendations:
                r_ui = i
                r_uj = j

                if i>index:
                    if index == 0:
                        rt_ui = i
                    else:
                        rt_ui = i+1.0
                elif i<index:
                    rt_ui = i+1.0
                else:
                    rt_ui = 0.0

                if j>index:
                    if index == 0:
                        rt_uj = j
                    else:
                        rt_uj = j+1.0
                elif j<index:
                    rt_uj = j+1
                else:
                    rt_uj = 0.0

                c_plus += self.sgn(r_ui -r_uj) * self.sgn(rt_ui-rt_uj)
                c_minus += self.sgn(r_ui - r_uj) * self.sgn(rt_uj - rt_ui)
                c_u += abs(self.sgn(r_ui -r_uj) * self.sgn(rt_ui-rt_uj))

                iter += 1
                j += 1
            i += 1

        c_plus = max(0.0, c_plus)
        c_minus = max(0.0, c_minus)
        c_u0 = c_u - (c_plus + c_minus)

        return abs((c_minus+0.5*c_u0)/float(c_u)) * ((index+1.0)/2.0)

    def rScore(self, val):
        return 1.0/pow(2, (val/5))

    def isInK(self, recommendations, val):
        index = recommendations.index(val) + 1

        if index <= 10:
            return True
        else:
            return False

e = Evaluation()
print(e.ndpm([1,2,3,6,9], 22))