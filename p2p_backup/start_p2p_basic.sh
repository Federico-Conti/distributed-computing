#/bin/sh
./storage.py ./basic-config/p2p_v1.cfg # N10 K5 AL1y
./storage.py ./basic-config/p2p_v2.cfg # N10 K6 AL1y
./storage.py ./basic-config/p2p_v3.cfg # N10 K7 AL1y
./storage.py ./basic-config/p2p_v4.cfg # N10 K8 AL1y
./storage.py ./basic-config/p2p_v4.2.cfg # N10 K8 AL 16d
./storage.py ./basic-config/p2p_v4.3.cfg # N10 K8 AL 32d
./storage.py ./basic-config/p2p_v4.4.cfg # N10 K8 AL 64d
./storage.py ./basic-config/p2p_v4.5.cfg # N10 K8 AL 128d
./storage.py ./basic-config/p2p_v4.6.cfg # N10 K8 AL 256d
./storage.py ./basic-config/p2p_v4.7.cfg # N10 K8 AL 512d
./storage.py ./basic-config/client_server.cfg 

# PLS change the  plt.ylim(0, 100) in plot_p2p.py 
./storage.py ./basic-config/p2p_v4.1.cfg # N10 K8 AL 8d