#!/bin/bash

read -p "Enter the value for D: " D

  for LAMBD in 0.5 0.9 0.95 0.99; do
    echo $LAMBD 
    ./srpt_sim.py --no-weibull --lambd $LAMBD --d $D --n 10
  done
./plot_queue_q.py --no-weibull --srpt --csv ./data-srpt/${D}_choice.csv --d $D

