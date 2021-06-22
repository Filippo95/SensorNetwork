#!/bin/sh
# Per 10 seed:
#   Partendo da 100 sensori fino a 800 sensori, di 100 in 100:
#     Prova tutte le combinazioni di order_by e pack_by sul programma
seed=0
seedfinale=50
num_iter=50
while [ $seed -lt $seedfinale ]
do
  sensors=100
  while [ $sensors -lt 1000 ] # Scritto così arriva fino a 120 sensori
  do
    python3 main.py $sensors $seed "rapp_cap_costo" "distanza_capacita" $num_iter -q --no-display &
    python3 main.py $sensors $seed "rapp_cap_costo" "capacita" $num_iter -q --no-display &
    python3 main.py $sensors $seed "rapp_numsensori_costo" "distanza_capacita" $num_iter -q --no-display &
    python3 main.py $sensors $seed "rapp_numsensori_costo" "capacita" $num_iter -q --no-display &
    echo "----------------------------------------------------------------------------------FINITO CON $sensors SENSORI"
    sensors=$((sensors + 100))
    python3 main.py $sensors $seed "rapp_cap_costo" "distanza_capacita" $num_iter -q --no-display &
    python3 main.py $sensors $seed "rapp_cap_costo" "capacita" $num_iter -q --no-display &
    python3 main.py $sensors $seed "rapp_numsensori_costo" "distanza_capacita" $num_iter -q --no-display &
    python3 main.py $sensors $seed "rapp_numsensori_costo" "capacita" $num_iter -q --no-display &
    echo "----------------------------------------------------------------------------------FINITO CON $sensors SENSORI"
    sensors=$((sensors + 100))
    python3 main.py $sensors $seed "rapp_cap_costo" "distanza_capacita" $num_iter -q --no-display &
    python3 main.py $sensors $seed "rapp_cap_costo" "capacita" $num_iter -q --no-display &
    python3 main.py $sensors $seed "rapp_numsensori_costo" "distanza_capacita" $num_iter -q --no-display &
    python3 main.py $sensors $seed "rapp_numsensori_costo" "capacita" $num_iter -q --no-display
    echo "----------------------------------------------------------------------------------FINITO CON $sensors SENSORI"
    sensors=$((sensors + 100))
    python3 main.py $sensors $seed "rapp_cap_costo" "distanza_capacita" $num_iter -q --no-display &
    python3 main.py $sensors $seed "rapp_cap_costo" "capacita" $num_iter -q --no-display &
    python3 main.py $sensors $seed "rapp_numsensori_costo" "distanza_capacita" $num_iter -q --no-display &
    python3 main.py $sensors $seed "rapp_numsensori_costo" "capacita" $num_iter -q --no-display
    echo "----------------------------------------------------------------------------------FINITO CON $sensors SENSORI"
    sensors=$((sensors + 100))
  done
  echo "-------------------------------------------------------------------------------------------FINITO IL SEED $seed"
  seed=$((seed + 1))
done
