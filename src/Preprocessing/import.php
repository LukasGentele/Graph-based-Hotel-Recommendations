<?php

include 'inc.php';

$dbQueries = [
    'create' => 'CREATE (obj:%s %s) RETURN obj',
    'connect' => 'MATCH (a:%s %s), (b:%s %s)
                    CREATE UNIQUE (a)-[r:%s]->(b)
                    SET r.count = coalesce(r.count, 0) + 1'
];

$aspects = ['Service', 'Cleanliness', 'Overall', 'Value', 'Sleep Quality', 'Rooms', 'Location'];

$iterator = new DirectoryIterator($dataDirectory);

$startTime = time();

$startIndex = $argv[1];
$endIndex = $startIndex + $argv[2];

$hotelCount = 0;

foreach (new IteratorIterator($iterator) as $index => $fileInfo) {
    if ($index < $startIndex) {
        continue;
    }
    else if ($index >= $endIndex) {
        break;
    }
    $file = $fileInfo->getRealPath();
    
    if (is_file($file)) {
        $data = json_decode(file_get_contents($file));
    
        $hotelCount++;
        
        $hotelData = $data->HotelInfo;
    
    
        if (isset($hotelData->Address) === false) {
            $city = '';
            $region = '';
            $country = '';
            $street = '';
            $postalCode = '';
        }
        else {
            $city = preg_replace('#.*?<span property="v:locality">([^<]*)</span>.*#s', '$1', $hotelData->Address);
            $region = preg_replace('#.*?<span property="v:region">([^<]*)</span>.*#s', '$1', $hotelData->Address);
            $country = preg_replace('#.*? property="v:country-name">([^<]*)</span>.*#s', '$1', $hotelData->Address);
            $street = preg_replace('#.*?<span property="v:street-address">([^<]*)</span>.*#s', '$1', $hotelData->Address);
            $postalCode = preg_replace('#.*?<span property="v:postal-code">([^<]*)</span>.*#s', '$1', $hotelData->Address);
    
            if ($region == $hotelData->Address) {
                $region = '';
            }
    
            if ($country == $hotelData->Address) {
                $country = '';
            }
    
            if ($street == $hotelData->Address) {
                $street = '';
            }
    
            if ($postalCode == $hotelData->Address) {
                $postalCode = '';
            }
        }
        
        if (isset($hotelData->Price) === false) {
            $priceRange = [-1, -1];
        }
        else {
            $priceRange = explode('|', preg_replace('#.*?\$([0-9]+)[^$]*(?:\$([0-9]+))?.*#s', '$1|$2', $hotelData->Price));
    
            if (isset($priceRange[1]) === false) {
                $priceRange = [-1, -1];
            }
            elseif ($priceRange[1] == false) {
                $priceRange[1] = -1;
            }
        }
    
        if (isset($hotelData->ImgURL) === false) {
            $hotelData->ImgURL = '';
        }
        $hotelClass = -1;
    
        if (isset($hotelData->HotelUrl) === false) {
            $hotelData->HotelUrl = '';
        }
        else {
            $hotelSiteContent = file_get_contents('https://www.tripadvisor.de' . $hotelData->HotelURL);
    
            $hotelClass = preg_replace('#.*?<span class="hClass">Hotelklassifizierung:<\/span>([0-9](?:\.[0-9])?).*#s', '$1', $hotelSiteContent);
    
            if ((float)$hotelClass == $hotelClass) {
                $hotelClass = (float)$hotelClass;
            }
        }
        
        if (isset($hotelData->Name) === false) {
            $hotelData->Name = '';
        }
        
        $place = [
            'name' => $city,
            'region' => $region,
            'country' => $country,
            'hash' => crc32($region . '#' . $city),
        ];
        
        $query = sprintf($dbQueries['create'], 'Place', cypherEncode($place));
        $executeQuery($query);
        
        $placeKey = cypherEncode(['hash' => $place['hash']]);
        
        $hotel = [
            'id' => $hotelData->HotelID,
            'name' => cleanText($hotelData->Name),
            'class' => $hotelClass,
            'street' => cleanText($street),
            'postalCode' => $postalCode,
            'priceLowerLimit' => $priceRange[0],
            'priceUpperLimit' => $priceRange[1],
            'url' => $hotelData->HotelURL,
            'imgUrl' => $hotelData->ImgURL
        ];
    
        $hotelKey = cypherEncode(['id' => $hotel['id']]);
        
        $query = sprintf($dbQueries['create'], 'Hotel', cypherEncode($hotel));
        
        if ($executeQuery($query)) {
            $query = sprintf($dbQueries['connect'], 'Hotel', $hotelKey, 'Place', $placeKey, 'LOCATED_IN');
            $executeQuery($query);
    
            $query = sprintf($dbQueries['connect'], 'Place', $placeKey, 'Hotel', $hotelKey, 'OFFERS');
            $executeQuery($query);
        }
        $reviewCount = 0;
        $userCount = 0;
        
        foreach ($data->Reviews as $reviewData) {
            $ratingData = $reviewData->Ratings;
            
            foreach ($aspects as $aspect) {
                if (isset($ratingData->$aspect) === false) {
                    $ratingData->$aspect = -1;
                }
            }
            
            if (isset($reviewData->Title) === false) {
                $reviewData->Title = '';
            }
            $review = [
                'id' => $reviewData->ReviewID,
                'title' => cleanText($reviewData->Title),
                'text' => cleanText($reviewData->Content),
                'date' => (new DateTime($reviewData->Date))->getTimestamp(),
                'ratingOverall' => (float)$ratingData->Overall,
                'ratingValue' => (int)$ratingData->Value,
                'ratingService' => (int)$ratingData->Service,
                'ratingRooms' => (int)$ratingData->Rooms,
                'ratingCleanliness' => (int)$ratingData->Cleanliness,
                'ratingSleepQuality' => (int)$ratingData->{'Sleep Quality'},
                'ratingLocation' => (int)$ratingData->Location,
                'summaryValue' => '',
                'summaryService' => '',
                'summaryRooms' => '',
                'summaryCleanliness' => '',
                'summarySleepQuality' => '',
                'summaryLocation' => ''
            ];
            
            $reviewKey = cypherEncode(['id' => $review['id']]);
            
            $query = sprintf($dbQueries['create'], 'Review', cypherEncode($review));
    
            if ($executeQuery($query)) {
                $reviewCount++;
                
                $query = sprintf($dbQueries['connect'], 'Review', $reviewKey, 'Hotel', $hotelKey, 'RATES');
                $executeQuery($query);
    
                $query = sprintf($dbQueries['connect'], 'Hotel', $hotelKey, 'Review', $reviewKey, 'RATED_BY');
                $executeQuery($query);
                
                if (isset($reviewData->AuthorLocation) === false) {
                    $reviewData->AuthorLocation = '';
                }
                $user = [
                    'name' => $reviewData->Author,
                    'homeTown' => $reviewData->AuthorLocation
                ];
    
                $userKey = cypherEncode(['name' => $user['name']]);
    
                $query = sprintf($dbQueries['create'], 'User', cypherEncode($user));
    
                if ($executeQuery($query)) {
                    $userCount++;
                }
                $query = sprintf($dbQueries['connect'], 'User', $userKey, 'Review', $reviewKey, 'WROTE');
                $executeQuery($query);
    
                $query = sprintf($dbQueries['connect'], 'Review', $reviewKey, 'User', $userKey, 'WRITTEN_BY');
                $executeQuery($query);
    
                $query = sprintf($dbQueries['connect'], 'User', $userKey, 'Hotel', $hotelKey, 'HAS_BOOKED');
                $executeQuery($query);
    
                $query = sprintf($dbQueries['connect'], 'Hotel', $hotelKey, 'User', $userKey, 'BOOKED_BY');
                $executeQuery($query);
                
                $query = sprintf($dbQueries['connect'], 'User', $userKey, 'Place', $placeKey, 'HAS_VISITED');
                $executeQuery($query);
    
                $query = sprintf($dbQueries['connect'], 'Place', $placeKey, 'User', $userKey, 'VISITED_BY');
                $executeQuery($query);
            }
        }
        $infoLog('Hotel number ' . $hotelCount . ' with id ' . $hotel['id'] . ' imported! (+' . $reviewCount . ' reviews, +' . $userCount . ' users, total duration: ' . (time() - $startTime) . 's)');
    }
}