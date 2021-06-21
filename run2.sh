#!/bin/sh
# Per 10 seed:
#   Partendo da 100 sensori fino a 500 sensori, di 100 in 100:
#     Prova tutte le combinazioni di order_by e pack_by sul programma
seed=0
while [ $seed -lt 100 ]
do
  sensors=100
  while [ $sensors -lt 501 ] # Scritto così arriva fino a 600 sensori
  do
    python3 main.py $sensors $seed "rapp_cap_costo" "distanza_capacita" 50 -q --no-display &
    python3 main.py $sensors $seed "rapp_cap_costo" "capacita" 50 -q --no-display &
    python3 main.py $sensors $seed "rapp_numsensori_costo" "distanza_capacita" 50 -q --no-display &
    python3 main.py $sensors $seed "rapp_numsensori_costo" "capacita" 50 -q --no-display &
    echo "----------------------------------------------------------------------------------FINITO CON $sensors SENSORI"
    sensors=$((sensors + 100))
    python3 main.py $sensors $seed "rapp_cap_costo" "distanza_capacita" 50 -q --no-display &
    python3 main.py $sensors $seed "rapp_cap_costo" "capacita" 50 -q --no-display &
    python3 main.py $sensors $seed "rapp_numsensori_costo" "distanza_capacita" 50 -q --no-display &
    python3 main.py $sensors $seed "rapp_numsensori_costo" "capacita" 50 -q --no-display &
    echo "----------------------------------------------------------------------------------FINITO CON $sensors SENSORI"
    sensors=$((sensors + 100))
    python3 main.py $sensors $seed "rapp_cap_costo" "distanza_capacita" 50 -q --no-display &
    python3 main.py $sensors $seed "rapp_cap_costo" "capacita" 50 -q --no-display &
    python3 main.py $sensors $seed "rapp_numsensori_costo" "distanza_capacita" 50 -q --no-display &
    python3 main.py $sensors $seed "rapp_numsensori_costo" "capacita" 50 -q --no-display
    echo "----------------------------------------------------------------------------------FINITO CON $sensors SENSORI"
    sensors=$((sensors + 100))
  done
  echo "-------------------------------------------------------------------------------------------FINITO IL SEED $seed"
  seed=$((seed + 1))
done
