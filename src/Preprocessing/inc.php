<?php

fclose(STDIN);
fclose(STDOUT);
fclose(STDERR);
$STDIN = fopen('/dev/null', 'r');
$STDOUT = fopen('php_output_' . $argv[1] . '.log', 'wb');
$STDERR = fopen('php_error_' . $argv[1] . '.log', 'wb');

use Neoxygen\NeoClient\ClientBuilder;

$dataDirectory = '../../data';
$dbAccessDataFile = '../.db-access.json';

include 'vendor/autoload.php';

$accessData = json_decode(file_get_contents($dbAccessDataFile));

$connUrl = parse_url($accessData->url);

$graph = ClientBuilder::create()->addConnection('default', $connUrl['scheme'], $connUrl['host'], $connUrl['port'], true, $accessData->user, $accessData->password)->build();

function cleanText($str) {
    return $str;
    /*
    return preg_replace_callback('#\\\\u([0-9a-fA-F]{4})#s', function ($match) {
        return mb_convert_encoding(pack('H*', $match[1]), 'UTF-8', 'UTF-16BE');
    }, $str);*/
}

function cypherEncode($obj) {
    $re = json_encode($obj, JSON_UNESCAPED_SLASHES);
    
    $re = preg_replace('#"([^"]*)":#', '$1:', $re);
    
    return $re;
}

$executeQuery = function($query) use ($graph, $argv) {
    try {
        $graph->sendCypherQuery($query);
        
        return true;
    }
    catch (Exception $e) {
        if (strpos($e->getMessage(), 'Neo.ClientError.Schema.ConstraintValidationFailed') === false) {
            file_put_contents('error_' . $argv[1] . '.log', 'Query Error: ' . $query . PHP_EOL . $e->getMessage() . PHP_EOL . PHP_EOL, FILE_APPEND);
        }
    }
    return false;
};

$infoLog = function($message) use($argv) {
    file_put_contents('info_' . $argv[1] . '.log', $message . PHP_EOL, FILE_APPEND);
};