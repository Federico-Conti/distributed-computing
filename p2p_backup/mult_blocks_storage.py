#!/usr/bin/env python3

import argparse
import configparser
import csv
import logging
import random
from dataclasses import dataclass
from random import expovariate
from typing import Optional, List
from humanfriendly import format_timespan, parse_size, parse_timespan
from discrete_event_sim import Simulation, Event
import subprocess


def exp_rv(mean):
    """Return an exponential random variable with the given mean."""
    return expovariate(1 / mean)


class DataLost(Exception):
    """Not enough redundancy in the system, data is lost. We raise this exception to stop the simulation."""
    pass


class Backup(Simulation):
    """Backup simulation."""

    def __init__(self, nodes: List['Node']):
        super().__init__()  # call the __init__ method of parent class
        self.nodes = nodes
        self.data = {}
        self.schedule(0, Monitoring())

        # Initialize online and fail events for all nodes
        for node in nodes:
            self.schedule(node.arrival_time, Online(node))
            self.schedule(node.arrival_time + exp_rv(node.average_lifetime), Fail(node))

    def schedule_transfer(self, uploader: 'Node', downloader: 'Node', block_id: int, restore: bool):
        """Helper function called by `Node.schedule_next_upload` and `Node.schedule_next_download`."""
        block_size = downloader.block_size if restore else uploader.block_size

        assert uploader.current_upload is None
        assert downloader.current_download is None

        speed = min(uploader.upload_speed, downloader.download_speed)
        delay = block_size / speed
        event = BlockRestoreComplete(uploader, downloader, block_id) if restore else BlockBackupComplete(uploader, downloader, block_id)
        self.schedule(delay, event)
        uploader.current_upload = downloader.current_download = event

    def log_info(self, msg):
        """Override method to get human-friendly logging for time."""
        logging.info(f'{format_timespan(self.t)}: {msg}')


class Monitoring(Event):
    def process(self, sim: Backup):
        available_nodes = sum(
            sum(node.local_blocks) >= node.k for node in sim.nodes
        )
        percentage_available = (available_nodes / len(sim.nodes)) * 100
        sim.data[sim.t] = percentage_available
        sim.schedule(parse_timespan("12w"), Monitoring())


@dataclass(eq=False)
class Node:
    """Class representing the configuration of a given node."""
    name: str
    n: int
    k: int
    data_size: int
    storage_size: int
    upload_speed: float
    download_speed: float
    average_uptime: float
    average_downtime: float
    average_lifetime: float
    average_recover_time: float
    arrival_time: float
    b: int  # Maximum blocks per peer

    def __post_init__(self):
        self.online: bool = False
        self.failed: bool = False
        self.block_size: int = self.data_size // self.k if self.k > 0 else 0
        self.free_space: int = self.storage_size - self.block_size * self.n
        assert self.free_space >= 0, "Node without enough space to hold its own data"
        self.local_blocks: list[bool] = [True] * self.n
        self.backed_up_blocks: list[Optional[Node]] = [None] * self.n
        self.remote_blocks_held: dict[Node, int] = {}
        self.blocks_per_peer: dict[Node, int] = {}
        self.current_upload: Optional[TransferComplete] = None
        self.current_download: Optional[TransferComplete] = None

    def find_block_to_back_up(self):
        for block_id, (held_locally, peer) in enumerate(zip(self.local_blocks, self.backed_up_blocks)):
            if held_locally and peer is None:
                return block_id
        return None

    def schedule_next_upload(self, sim: Backup):
        if self.current_upload is not None:
            return

        # Restore blocks for peers if needed
        for peer, block_id in self.remote_blocks_held.items():
            if not peer.local_blocks[block_id] and peer.online and peer.current_download is None:
                sim.schedule_transfer(self, peer, block_id, restore=True)
                return

        # Attempt backups for own blocks
        for block_id in range(self.n):
            if self.backed_up_blocks[block_id] is None:
                for peer in sim.nodes:
                    if (
                        peer is not self
                        and peer.online
                        and peer.current_download is None
                        and self.blocks_per_peer.get(peer, 0) < self.b
                        and peer.free_space >= self.block_size
                    ):
                        sim.schedule_transfer(self, peer, block_id, restore=False)
                        self.blocks_per_peer[peer] = self.blocks_per_peer.get(peer, 0) + 1
                        return

    def schedule_next_download(self, sim: Backup):
        if self.current_download is not None:
            return

        for block_id, (held_locally, peer) in enumerate(zip(self.local_blocks, self.backed_up_blocks)):
            if not held_locally and peer is not None and peer.online and peer.current_upload is None:
                sim.schedule_transfer(peer, self, block_id, restore=True)
                return

    def __hash__(self):
        return id(self)

    def __str__(self):
        return self.name


@dataclass
class NodeEvent(Event):
    node: Node

    def process(self, sim: Simulation):
        raise NotImplementedError


class Online(NodeEvent):
    def process(self, sim: Backup):
        node = self.node
        if node.online or node.failed:
            return
        node.online = True
        node.schedule_next_upload(sim)
        node.schedule_next_download(sim)
        downtime = exp_rv(node.average_uptime)
        sim.schedule(downtime, Offline(node))


class Recover(Online):
    def process(self, sim: Backup):
        node = self.node
        sim.log_info(f"{node} recovers")
        node.failed = False
        super().process(sim)
        sim.schedule(exp_rv(node.average_lifetime), Fail(node))


class Disconnection(NodeEvent):
    def process(self, sim: Simulation):
        raise NotImplementedError

    def disconnect(self):
        node = self.node
        node.online = False
        if node.current_upload:
            node.current_upload.canceled = True
        if node.current_download:
            node.current_download.canceled = True


class Offline(Disconnection):
    def process(self, sim: Backup):
        if not self.node.failed:
            self.disconnect()
            sim.schedule(exp_rv(self.node.average_downtime), Online(self.node))


class Fail(Disconnection):
    def process(self, sim: Backup):
        sim.log_info(f"{self.node} fails")
        self.disconnect()
        self.node.local_blocks = [False] * self.node.n
        for peer, block_id in self.node.remote_blocks_held.items():
            peer.backed_up_blocks[block_id] = None
        self.node.remote_blocks_held.clear()
        recover_time = exp_rv(self.node.average_recover_time)
        sim.schedule(recover_time, Recover(self.node))


@dataclass
class TransferComplete(Event):
    uploader: Node
    downloader: Node
    block_id: int
    canceled: bool = False

    def process(self, sim: Backup):
        if not self.canceled:
            self.update_block_state()
        self.uploader.current_upload = None
        self.downloader.current_download = None
        self.uploader.schedule_next_upload(sim)
        self.downloader.schedule_next_download(sim)

    def update_block_state(self):
        raise NotImplementedError


class BlockBackupComplete(TransferComplete):
    def update_block_state(self):
        self.downloader.free_space -= self.uploader.block_size
        self.uploader.backed_up_blocks[self.block_id] = self.downloader
        self.downloader.remote_blocks_held[self.uploader] = self.block_id


class BlockRestoreComplete(TransferComplete):
    def update_block_state(self):
        self.downloader.local_blocks[self.block_id] = True
        if sum(self.downloader.local_blocks) >= self.downloader.k:
            self.downloader.local_blocks = [True] * self.downloader.n


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("config", help="configuration file")
    parser.add_argument("--max-t", default="100 years")
    parser.add_argument("--seed", help="random seed")
    parser.add_argument("--verbose", action='store_true')
    args = parser.parse_args()

    if args.seed:
        random.seed(args.seed)  # set a seed to make experiments repeatable
    if args.verbose:
        logging.basicConfig(format='{levelname}:{message}', level=logging.INFO, style='{')  # output info on stdout

    # functions to parse every parameter of peer configuration
    parsing_functions = [
        ('n', int), ('k', int),
        ('data_size', parse_size),
        ('storage_size', parse_size),
        ('upload_speed', parse_size),
        ('download_speed', parse_size),
        ('average_uptime', parse_timespan),
        ('average_downtime', parse_timespan),
        ('average_lifetime', parse_timespan),
        ('average_recover_time', parse_timespan),
        ('arrival_time', parse_timespan),
        ('b',parse_size)
    ]

    config = configparser.ConfigParser()
    if not config.read(args.config):
     raise FileNotFoundError(f"Configuration file '{args.config}' could not be read.")
    
    nodes = []  # we build the list of nodes to pass to the Backup class
    for node_class in config.sections():
        class_config = config[node_class]
        # list comprehension: https://docs.python.org/3/tutorial/datastructures.html#list-comprehensions
        cfg = [parse(class_config[name]) for name, parse in parsing_functions]
        # the `callable(p1, p2, *args)` idiom is equivalent to `callable(p1, p2, args[0], args[1], ...)
        nodes.extend(Node(f"{node_class}-{i}", *cfg) for i in range(class_config.getint('number')))
    sim = Backup(nodes)
    sim.run(parse_timespan(args.max_t))
    sim.log_info(f"Simulation over")
    
    
    
    output_csv = f"./data-mb/availability_N{cfg[0]}_K{cfg[1]}_AL{int(cfg[8] / (24 * 3600))}d_B{cfg[11]}.csv"
    with open(output_csv, mode="a", newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        for time, availability in sim.data.items():
            csvwriter.writerow([time, availability])
    subprocess.run(["python3", "plot_p2p.py", "--csv", output_csv, "--n", f"{cfg[0]}", "--k", f"{cfg[1]}","--al",f"{int(cfg[8] / (24 * 3600))}","--b",f"{cfg[11]}"])

if __name__ == '__main__':
    main()
