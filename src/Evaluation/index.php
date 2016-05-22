<?php

require_once "inc.php";

echo "Lets start...!";


function getRecommendations($user, $location) {

}


//$q = "MATCH (n:Hotel) RETURN n LIMIT 25";
//$result = $graph->sendCypherQuery($q)->getBody();


// "MATCH (hotel:Hotel)-[r:LOCATED_IN]->(location:Place) WHERE location.name='Berlin' RETURN COUNT(location), location.name"
$testLocations = [
    'Baltimore',        // 60
    'Los Angeles',      // 365
    'Paris'             // 913
];

// Get Users
// MATCH p=()-[r:HAS_VISITED]->(loc:Place) WHERE loc.name = 'Paris' RETURN p LIMIT 25
// MATCH (u:User)-[r:HAS_VISITED]->(loc:Place) WHERE loc.name = 'Paris' RETURN COUNT(DISTINCT u)

foreach ($testLocations as $location) {
    $q = "MATCH p=()-[r:HAS_VISITED]->(loc:Place) WHERE loc.name = '" . $location . "' RETURN p LIMIT 10";

    $result = $graph->sendCypherQuery($q)->getBody();
    $recommendations = getRecommendations($result["results"][0]["data"][0]["row"][0][0]["name"], $location);
}