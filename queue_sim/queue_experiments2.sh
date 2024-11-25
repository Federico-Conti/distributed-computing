#/bin/sh

D=2
for LAMBD in 0.5 0.9 0.95 0.99; do
  echo $LAMBD $D
  ./queue_sim.py --lambd $LAMBD --d $D --n 10 --max-t 100_000
 done
done
