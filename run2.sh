#!/bin/sh
# Per 10 seed:
#   Partendo da 100 sensori fino a 500 sensori, di 100 in 100:
#     Prova tutte le combinazioni di order_by e pack_by sul programma
seed=0
while [ $seed -lt 10 ]
do
  sensors=100
  while [ $sensors -lt 501 ]
  do
    python3 main.py $sensors $seed "rapp_cap_costo" "distanza_capacita" 10 -q --no-display
    python3 main.py $sensors $seed "rapp_cap_costo" "capacita" 10 -q --no-display
    python3 main.py $sensors $seed "rapp_numsensori_costo" "distanza_capacita" 10 -q --no-display
    python3 main.py $sensors $seed "rapp_numsensori_costo" "capacita" 10 -q --no-display
    sensors=${$sensors + 100}
  done
  seed=${$seed + 1}
done
