#!/bin/sh
seed=0
mkdir ./"solutions"/$seed
while [ $seed -lt 9 ]
do
  sensors=0
  mkdir ./"solutions"/$seed/$sensors
  while [ $sensors -lt 9 ]
  do
    python3 main.py $sensors $seed >>./"solutions"/$seed/$sensors/log-$seed-$sensors.txt
    sensors=`expr $sensors + 1`
    mkdir ./"solutions"/$seed/$sensors
  done
  seed=`expr $seed + 1`
  mkdir ./"solutions"/$seed
done