#!/bin/bash

# read -p "Enter the value for D: " D
for D in 1 2 5 10; do
  for LAMBD in 0.5 0.9 0.95 0.99; do
    echo $LAMBD 
    ./queue_sim.py --lambd $LAMBD --d $D --n 10
  done
./plot_queue_q.py --csv ./${D}_choice.csv --d $D
done
