<?php


function sgn($in) {
    if( $in > 0 ) {
        return 1;
    }
    else if( $in == 0 ) {
        return 0;
    }
    else{
        return -1;
    }
}

/*
 * Normalized Distance-based Performance Measure
 */
function NDPM ($recommendations, $hotelId) {
    $countRecommendations = count($recommendations);
    $index = array_search($hotelId, $recommendations);

    if( $index === FALSE ){
        $index = $countRecommendations - 1;
    }

    $c_plus = 0;
    $c_minus = 0;
    $c_u = 0;

    $stop = 0.5 * $countRecommendations * ($countRecommendations-1);

    $iter = 0;
    for($i=0;$iter<$stop;$i++){
        for($j=$i+1;$j<$countRecommendations;$j++,$iter++) {
            $r_ui = $i;
            $r_uj = $j;

            if( $i > $index ) {
                $rt_ui = ($index == 0) ? $i : $i+1;
            }
            else if ( $i < $index ) {
                $rt_ui = $i + 1;
            }
            else {
                $rt_ui = 0.0;
            }

            if( $j > $index ) {
                $rt_uj = ($index == 0) ? $j : $j+1;
            }
            else if ( $j < $index ) {
                $rt_uj = $j + 1;
            }
            else {
                $rt_uj = 0.0;
            }

            $c_plus += sgn($r_ui - $r_uj) * sgn($rt_ui - $rt_uj);
            $c_minus += sgn($r_ui - $r_uj) * sgn($rt_uj - $rt_ui);
            $c_u += abs(sgn($r_ui - $r_uj) * sgn($r_ui - $r_uj));
        }
    }

    $c_plus = max(0, $c_plus);
    $c_minus = max(0, $c_minus);
    $c_u0 = $c_u - ($c_plus + $c_minus);

    echo $c_plus . PHP_EOL;
    echo $c_minus . PHP_EOL;
    echo $c_u0 . PHP_EOL;
    echo $c_u . PHP_EOL;

    return abs(($c_minus+0.5*$c_u0)/$c_u) * (($index+1)/2);
}

/**
 * Exponential Decay Score
 */
function R_Score($index) {
    return 1/pow(2, (($index)/5));
}

/**
 * Recommendation Score
 */
function contains($arr, $index, $m) {

}

echo NDPM([11,2,33,4], 4);
//echo R_Score(10);