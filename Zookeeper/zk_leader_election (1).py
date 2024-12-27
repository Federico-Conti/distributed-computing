#!/usr/bin/env python3

import os
import random
import time

from kazoo.client import KazooClient
from kazoo.exceptions import NoNodeError, NodeExistsError

my_pid = os.getpid()

print(f"My pid is {my_pid}")

APP_NODE = "/distributed_computing"
WORKERS_NODE = f"{APP_NODE}/workers"
LEADER_NODE = f"{APP_NODE}/leader"

zk = KazooClient(hosts="localhost:2181")
zk.start()
zk.ensure_path(APP_NODE)  # if not existing, creates it
zk.ensure_path(WORKERS_NODE)
zk.create(f"/distributed_computing/workers/{my_pid}", ephemeral=True)


def print_workers(worker_list):
    print("Known workers:", ' '.join(worker_list))


def workers_changed(event):
    assert event.path == WORKERS_NODE
    worker_list = zk.get_children(event.path)
    print_workers(worker_list)


workers = zk.get_children("/distributed_computing/workers", watch=workers_changed)
print_workers(workers)

time.sleep(random.random() * 30)  # wait 0 to 30 seconds

my_ascii_pid = str(my_pid).encode('ascii')


def choose_leader():
    while True:
        try:
            leader, stat = zk.get(LEADER_NODE)
        except NoNodeError:
            try:
                zk.create(LEADER_NODE, my_ascii_pid, ephemeral=True)
            except NodeExistsError:
                continue
            else:
                leader = my_ascii_pid
        print(f"New leader is {leader.decode('ascii')}")
        return

def handler(event):
    choose_leader()

try:
    leader, stat = zk.get(LEADER_NODE, watch=handler)
except NoNodeError:
    choose_leader()
else:
    print(f"Leader is {leader.decode('ascii')}")

time.sleep(1800)
