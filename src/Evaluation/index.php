<?php

require_once "inc.php";

echo "Starting Evaluation..." . PHP_EOL;

function getRecommendations($user, $location) {
    global $graph;

    $q = "MATCH (hotel:Hotel)-[z:LOCATED_IN]->(loc:Place) WHERE loc.name = '" . $location . "' RETURN hotel,rand() as r ORDER BY r LIMIT 100";
    $result = $graph->sendCypherQuery($q)->getBody();

    $retArr = [];

    foreach ($result["results"][0]["data"] as $hotel) {
        $retArr[] = $hotel["row"][0];
    }

    return $retArr;
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

$distance = [
    "total" => 0,
    "amount" => 0,
    "avg" => 0
];

$time = [
    "total" => 0,
    "amount" => 0,
    "avg" => 0
];

$statistics = [
    "locationAmount" => 0,
    "locations" => []
];

foreach ($testLocations as $location) {
    $q = "MATCH (u:User)-[y:HAS_BOOKED]->(hotel:Hotel)-[z:LOCATED_IN]->(loc:Place) MATCH (u)-[p:WROTE]->(r:Review)-[o:RATES]->(hotel) WHERE loc.name = '" . $location . "' RETURN u,loc,hotel,r LIMIT 5";
    $result = $graph->sendCypherQuery($q)->getBody();

    $statistics["locations"][] = [
        "name" => $location,
        "userAmountTotal" => 0,
        "userAmountEvaluated" => 0,
        "time" => [
            "total" => 0,
            "amount" => 0,
            "avg" => 0
        ],
        "distance" => [
            "total" => 0,
            "amount" => 0,
            "avg" => 0
        ]
    ];

    foreach ( $result["results"][0]["data"] as $user ){
        $user = $user["row"];
        $statistics["locations"][count($statistics["locations"])-1]["userAmountTotal"] += 1;

        // TODO: Get User Average Rating and decide if we should evaluate hotel
        if( is_numeric($user[3]["ratingOverall"]) && $user[3]["ratingOverall"] > 3 ){
            $statistics["locations"][count($statistics["locations"])-1]["userAmountEvaluated"] += 1;

            $start = microtime(true);

            $recommendations = getRecommendations($user[0]["name"], $location);

            $time["total"] += microtime(true) - $start;
            $time["amount"] += 1;

            $statistics["locations"][count($statistics["locations"])-1]["time"]["total"] += microtime(true) - $start;
            $statistics["locations"][count($statistics["locations"])-1]["time"]["amount"] += 1;

            $indicies = array_map(function($el){
                return $el["id"];
            }, $recommendations);

            $maxAmount = count($recommendations);
            $index = array_search($user[2]["id"], $indicies);

            if( $index === FALSE ){
                $index = $maxAmount;
            }

            $index = $index/floatval($maxAmount);

            $distance["total"] += $index;
            $distance["amount"] += 1;

            $statistics["locations"][count($statistics["locations"])-1]["distance"]["total"] += $index;
            $statistics["locations"][count($statistics["locations"])-1]["distance"]["amount"] += 1;
        }
    }

    $statistics["locationAmount"] += 1;
    $statistics["locations"][count($statistics["locations"])-1]["distance"]["avg"] = floatval($statistics["locations"][count($statistics["locations"])-1]["distance"]["total"]) / floatval($statistics["locations"][count($statistics["locations"])-1]["distance"]["amount"]);
    $statistics["locations"][count($statistics["locations"])-1]["time"]["avg"] = floatval($statistics["locations"][count($statistics["locations"])-1]["time"]["total"]) / floatval($statistics["locations"][count($statistics["locations"])-1]["time"]["amount"]);
}

$distance["avg"] = $distance["total"] / $distance["amount"];
$time["avg"] = $time["total"] / $time["amount"];

foreach ($statistics["locations"] as $location) {
    echo PHP_EOL . "Location Name:" . $location["name"] . PHP_EOL;
    echo "\tUsers (Evaluated): " . $location["userAmountTotal"] . "(" . $location["userAmountEvaluated"] . ")" . PHP_EOL;
    echo "\tTotal Time: " . $location["time"]["total"] . "s" . PHP_EOL;
    echo "\tAvg Execution Time for Recommendation Algorithm: " . $location["time"]["avg"] . "s" . PHP_EOL;
    echo "\tAvg Distance: " . $location["distance"]["avg"] . PHP_EOL . PHP_EOL;
}

echo PHP_EOL . "Total Time: " . $time["total"] . "s" .PHP_EOL;
echo "Avg Execution Time for Recommendation Algorithm: " . $time["avg"] . "s" . PHP_EOL;
echo "Avg Distance: " . $distance["avg"] . PHP_EOL;