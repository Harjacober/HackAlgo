<?php
$n = fgets(STDIN)+0;

while($n>0){
    $line1 = fgets(STDIN);
    $line2 = fgets(STDIN);
    echo ($line1+0)+$line2+0;
    echo "\n";
    $n = $n -1;
}
?>