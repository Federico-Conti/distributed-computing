#/bin/sh

# PLS change the  plt.ylim(60, 100) in plot_p2p.py 
./diverse_blocks_storage.py ./diverse-config/p2p_v1.cfg # N10 K5 AL1y
./diverse_blocks_storage.py ./diverse-config/p2p_v2.cfg # N10 K6 AL1y
./diverse_blocks_storage.py ./diverse-config/p2p_v3.cfg # N10 K7 AL1y
./diverse_blocks_storage.py ./diverse-config/p2p_v4.cfg # N10 K8 AL1y

# PLS change the  plt.ylim(0, 100) in plot_p2p.py 
./diverse_blocks_storage.py ./diverse-config/p2p_v4.1.cfg # N10 K8 AL8d
./diverse_blocks_storage.py ./diverse-config/p2p_v4.2.cfg # N10 K8 AL16d
./diverse_blocks_storage.py ./diverse-config/p2p_v4.3.cfg # N10 K8 AL32d
./diverse_blocks_storage.py ./diverse-config/p2p_v4.4.cfg # N10 K8 AL64d
./diverse_blocks_storage.py ./diverse-config/p2p_v4.5.cfg # N10 K8 AL128d
./diverse_blocks_storage.py ./diverse-config/p2p_v4.6.cfg # N10 K8 AL256d
./diverse_blocks_storage.py ./diverse-config/p2p_v4.7.cfg # N10 K8 AL512d