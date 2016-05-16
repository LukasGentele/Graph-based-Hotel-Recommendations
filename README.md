# Graph-based-Hotel-Recommendations

## Recommender System Architecture
### Graph
Layer 1: Places (city, district?), no inter-connection but edges to Layer 1 and Layer 2
Layer 2: 1 node for every user with inter-connections (user-user edge with annotation for Similarity Measure 1) and connections to layer 2 (visited places) as well as to layer 3 (hotels stayed at, with annotation for reviews containing aspect ratings)
Layer 3: Hotels, no inter-connections but edges to Layer 2 and Layer 1

### Similarity Measure 1 for User-User (hotel-specific):
Collaborative filtering for every hotel: Matrix containing all users with at least 5 reviews x aspects of the reviews
=> Cosine Similarity

### Similarity Measure 2 for User-User (basic attitude):
For all hotels a user has visited calculate:
1) For every aspect: deviation of a user's rating to the average rating of all users
2) Average hotel class (+variance) + price range

### Pre-processing:
- Crawl city names / location data
- Crawl hotel class