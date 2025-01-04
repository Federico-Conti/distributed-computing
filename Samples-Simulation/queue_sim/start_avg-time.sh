#!/bin/bash


for D in 1 2 5 10; do
  for LAMBD in 0.5 0.9 0.95 0.99; do
    echo $LAMBD 
    ./queue_sim.py --no-weibull --lambd $LAMBD --d $D --n 10
  done
done

for S in 1.0; do # with shape = 1, we have the same exponential distribution of before, hence memoryless behavior;
    for D in 1 2 5 10; do
        for LAMBD in 0.5 0.9 0.95 0.99; do
            echo $LAMBD 
            ./srpt_sim.py --shape $S --weibull --lambd $LAMBD --d $D --n 10
        done
    done
done
