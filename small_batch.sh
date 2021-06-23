#!/bin/sh
# Per esecuzione di piccoli test
seed=0
seedmax=2
sensors=1000
num_iter=10
rid=3
while [ $seed -lt $seedmax ]; do
  python3 main.py $sensors $seed "rapp_cap_costo" "distanza_capacita" $num_iter $rid -q --no-display &
  python3 main.py $sensors $seed "rapp_cap_costo" "capacita" $num_iter $rid -q --no-display &
  python3 main.py $sensors $seed "rapp_numsensori_costo" "distanza_capacita" $num_iter $rid -q --no-display &
  python3 main.py $sensors $seed "rapp_numsensori_costo" "capacita" $num_iter $rid -q --no-display
  echo "-------------------------------------------------------------------------------------------FINITO IL SEED $seed"
  seed=$((seed + 1))
done
echo "----------------------------------------------------------------------------------------------FINITI TUTTI I SEED"
