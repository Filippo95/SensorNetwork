#!/bin/sh
seed=0
seedfinale=50
num_iter=20
rid=3
while [ $seed -lt $seedfinale ]
do
  sensors=100
  while [ $sensors -lt 1000 ] # Scritto così arriva fino a 1200 sensori
  do
    python3 main.py $sensors $seed "rapp_cap_costo" "distanza_capacita" $num_iter $rid -q --no-display &
    python3 main.py $sensors $seed "rapp_cap_costo" "capacita" $num_iter $rid -q --no-display &
    python3 main.py $sensors $seed "rapp_numsensori_costo" "distanza_capacita" $num_iter $rid -q --no-display &
    python3 main.py $sensors $seed "rapp_numsensori_costo" "capacita" $num_iter $rid -q --no-display &
    echo "----------------------------------------------------------------------------------FINITO CON $sensors SENSORI"
    sensors=$((sensors + 100))
    python3 main.py $sensors $seed "rapp_cap_costo" "distanza_capacita" $num_iter $rid -q --no-display &
    python3 main.py $sensors $seed "rapp_cap_costo" "capacita" $num_iter $rid -q --no-display &
    python3 main.py $sensors $seed "rapp_numsensori_costo" "distanza_capacita" $num_iter $rid -q --no-display &
    python3 main.py $sensors $seed "rapp_numsensori_costo" "capacita" $num_iter $rid -q --no-display &
    echo "----------------------------------------------------------------------------------FINITO CON $sensors SENSORI"
    sensors=$((sensors + 100))
    python3 main.py $sensors $seed "rapp_cap_costo" "distanza_capacita" $num_iter $rid -q --no-display &
    python3 main.py $sensors $seed "rapp_cap_costo" "capacita" $num_iter $rid -q --no-display &
    python3 main.py $sensors $seed "rapp_numsensori_costo" "distanza_capacita" $num_iter $rid -q --no-display &
    python3 main.py $sensors $seed "rapp_numsensori_costo" "capacita" $num_iter $rid -q --no-display
    echo "----------------------------------------------------------------------------------FINITO CON $sensors SENSORI"
    sensors=$((sensors + 100))
    python3 main.py $sensors $seed "rapp_cap_costo" "distanza_capacita" $num_iter $rid -q --no-display &
    python3 main.py $sensors $seed "rapp_cap_costo" "capacita" $num_iter $rid -q --no-display &
    python3 main.py $sensors $seed "rapp_numsensori_costo" "distanza_capacita" $num_iter $rid -q --no-display &
    python3 main.py $sensors $seed "rapp_numsensori_costo" "capacita" $num_iter $rid -q --no-display
    echo "----------------------------------------------------------------------------------FINITO CON $sensors SENSORI"
    sensors=$((sensors + 100))
  done
  echo "-------------------------------------------------------------------------------------------FINITO IL SEED $seed"
  seed=$((seed + 1))
done
