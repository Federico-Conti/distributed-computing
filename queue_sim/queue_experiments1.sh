#/bin/sh

for D in 1 2 5 10; do
  for LAMBD in 0.5 0.9 0.95 0.99; do
    echo $LAMBD 
    ./queue_sim.py --no-weibull --lambd $LAMBD --d $D --n 10 --csv ./data/${D}_choice_avg_time.csv
  done
done
