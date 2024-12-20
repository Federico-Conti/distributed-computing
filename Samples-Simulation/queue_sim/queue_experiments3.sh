#!/bin/bash

read -p "Enter the value for D: " D #queue choice
read -p "Enter the value for S: " S #shape of weiball distribution

  for LAMBD in 0.5 0.9 0.95 0.99; do
    echo $LAMBD 
    ./queue_sim.py --shape $S  --weibull --lambd $LAMBD --d $D --n 10
  done
./plot_queue_q.py --shape $S --weibull --csv ./data/${D}_choice-weibull-shape${S}.csv --d $D

