<?php

include 'inc.php';

$geoCodingAPI = 'http://www.datasciencetoolkit.org/maps/api/geocode/json?address=';

$dbQueries = [
    'homeTowns' => 'MATCH (u:User) WHERE u.homeTown <> "" AND NOT (u)-[:IS_CITIZEN_OF]->() WITH DISTINCT u.homeTown as distinctHomeTown, COUNT(u) as numUsers WHERE numUsers = 1 RETURN distinctHomeTown', //optional: WHERE NOT (u)-[:IS_CITIZEN_OF]->() 
    'create' => 'CREATE (obj:%s %s) RETURN obj',
    'connect' => 'MATCH (a:%s %s), (b:%s %s)
                    CREATE UNIQUE (a)-[r:%s]->(b)
                    SET r.count = coalesce(r.count, 0) + 1'
];

$offset = $argv[1];
$limit = $argv[2];

$query = sprintf($dbQueries['homeTowns'], $offset, $limit);
$executeQuery($query);

$response = $graph->getResponse()->getBody();

$results = $response['results'][0]['data'];

$startTime = time();

if (count($results) > 0) {
    foreach ($results as $result) {
        $homeTown = $result['row'][0];
        
        if ($homeTown != false) {
            $homeTownKey = cypherEncode(['homeTown' => $homeTown]);
            $apiResponse = json_decode(file_get_contents($geoCodingAPI . urlencode($homeTown)));
            
            if ($apiResponse != false) {
                $apiResults = $apiResponse->results;
                
                if (count($apiResults) === 1) {
                    $countryInfo = end($apiResults[0]->address_components);
                    $countryName = $countryInfo->long_name;
                    $countryCode = $countryInfo->short_name;
                    
                    if ($countryName != false) {
                        $country = [
                            'name' => $countryName,
                            'code' => $countryCode
                        ];
                        $countryKey = cypherEncode(['code' => $countryCode]);
                        
                        $query = sprintf($dbQueries['create'], 'Country', cypherEncode($country));
                        $executeQuery($query);
                        
                        $query = sprintf($dbQueries['connect'], 'User', $homeTownKey, 'Country', $countryKey, 'IS_CITIZEN_OF');
                        $executeQuery($query);

                        $query = sprintf($dbQueries['connect'], 'Country', $countryKey, 'User', $homeTownKey, 'HAS_CITIZEN');
                        $executeQuery($query);

                        $infoLog('Successfully encoded home town ' . $homeTown . ' as ' . $countryCode . '! (total duration: ' . (time() - $startTime) . 's)');
                        
                        continue;
                    }
                }
            }
        }
        $infoLog('Could not encode home town ' . $homeTown . '! (total duration: ' . (time() - $startTime) . 's)');
    }
}