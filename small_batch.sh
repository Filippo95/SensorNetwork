#!/bin/sh
# Per esecuzione di piccoli test
seed=0
sensors=400
while [ $seed -lt 10 ]; do
  python3 main.py $sensors $seed "rapp_cap_costo" "distanza_capacita" 20 -q --no-display &
  python3 main.py $sensors $seed "rapp_cap_costo" "capacita" 20 -q --no-display &
  python3 main.py $sensors $seed "rapp_numsensori_costo" "distanza_capacita" 20 -q --no-display &
  python3 main.py $sensors $seed "rapp_numsensori_costo" "capacita" 20 -q --no-display
  echo "-------------------------------------------------------------------------------------------FINITO IL SEED $seed"
  seed=$((seed + 1))
done
echo "----------------------------------------------------------------------------------------------FINITI TUTTI I SEED"
