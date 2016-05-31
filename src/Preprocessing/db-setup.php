<?php

include 'inc.php';

$constraints = [
    'unique' => [
        'Place' => 'hash',
        'Hotel' => 'id',
        'User' => 'name',
        'Review' => 'id',
        'Country' => 'name'
    ]
];

$queries = [];

foreach ($constraints['unique'] as $node => $property) {
    $queries[] = sprintf('CREATE CONSTRAINT ON (obj:%s) ASSERT obj.%s IS UNIQUE', $node, $property);
    
    //ONLY AVAILABLE IN ENTERPRISE EDITION!
    //$queries[] = sprintf('CREATE CONSTRAINT ON (obj:%s) ASSERT exists(obj.%s)', $node, $property);
}

foreach ($queries as $query) {
    $graph->sendCypherQuery($query);
}
