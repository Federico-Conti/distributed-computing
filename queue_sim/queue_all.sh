#!/bin/bash


for D in 1 2 5 10; do
  for LAMBD in 0.5 0.9 0.95 0.99; do
    echo $LAMBD 
    ./queue_sim.py --no-weibull --lambd $LAMBD --d $D --n 10
  done
./plot_queue_q.py --no-weibull --csv ./data/${D}_choice.csv --d $D
done

for S in 0.5 1.0 2.0; do
    for D in 1 2 5 10; do
        for LAMBD in 0.5 0.9 0.95 0.99; do
            echo $LAMBD 
            ./queue_sim.py --shape $S  --weibull --lambd $LAMBD --d $D --n 10
        done
    ./plot_queue_q.py --shape $S --weibull --csv ./data/${D}_choice-weibull-shape${S}.csv --d $D
    done
done


for S in 1.0 2.0; do
    for D in 1 2 5 10; do
        for LAMBD in 0.5 0.9 0.95 0.99; do
            echo $LAMBD 
            ./srpt_sim.py --shape $S --weibull --lambd $LAMBD --d $D --n 10
        done
    ./plot_queue_q.py --shape $S --weibull --csv ./data-srpt/${D}_choice.csv --d $D
    done
done
