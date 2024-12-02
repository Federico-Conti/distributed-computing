#!/usr/bin/env python3
from matplotlib import pyplot as plt
import numpy as np
import argparse
import csv
import collections
import logging
import heapq
from random import expovariate, sample, seed

from discrete_event_sim_srpt import Simulation, Event

from workloads import weibull_generator

CSV_COLUMNS = ['lambd', 'mu', 'max_t', 'n', 'd', 'w']

class Job:
    """Class to store details of each job in the system."""

    def __init__(self, job_id,remaining_time):
        self.job_id = job_id
        self.remaining_time = remaining_time

class Queues(Simulation):
    """Simulation of a system with n servers and n queues.

    The system has n servers with one queue each. Jobs arrive at rate lambd and are served at rate mu.
    When a job arrives, according to the supermarket model, it chooses d queues at random and joins
    the shortest one.
    """

    def __init__(self, lambd, mu, n, d,monitoring_interval,weibull,shape):
        super().__init__()
        self.running = [None] * n  # if not None, the id of the running job (per queue)
        self.queues = [[] for _ in range(n)]  # FIFO queues of the system
        # NOTE: we don't keep the running jobs in self.queues
        self.arrivals = {}  # dictionary mapping job id to arrival time
        self.completions = {}  # dictionary mapping job id to completion time
     
        self.lambd = lambd
        self.n = n
        self.d = d
        self.mu = mu
        self.arrival_rate = lambd * n  # frequency of new jobs is proportional to the number of queues

        self.monitoring_interval = monitoring_interval
        self.monitored_data = []  # to store the queue length stats
        self.schedule(0, Monitoring())  # schedule the first monitoring event

        self.shape = shape 
        self.useWeibull = weibull

        self.arrival_gen = weibull_generator(shape, 1/self.arrival_rate)
        self.service_gen = weibull_generator(shape, 1/self.mu)
        
        initial_remaining_time = self.service_gen() if weibull else expovariate(mu)
        # initial_job = Job(0, initial_remaining_time)
        # self.jobs[0] = initial_job
        self.schedule(initial_remaining_time, Arrival(0,self))

    def schedule_arrival(self, job_id):
        """Schedule the arrival of a new job."""
        remaining_time = self.arrival_gen() if self.useWeibull else expovariate(self.arrival_rate)
        self.schedule(remaining_time, Arrival(job_id,self))

    def schedule_completion(self, job, queue_index):  
        """Schedule the completion of a job."""

        self.schedule(job.remaining_time,Completion(job, queue_index))


    def queue_len(self, i):
        """Return the length of the i-th queue.

        Notice that the currently running job is counted even if it is not in self.queues[i]."""

        return (self.running[i] is not None) + len(self.queues[i])


class Arrival(Event):
    """Event representing the arrival of a new job."""

    def __init__(self, job_id,sim: Queues):
        remaining_time = sim.service_gen() if sim.useWeibull else expovariate(sim.mu)
        self.job = Job(job_id,remaining_time)

    def process(self, sim: Queues):  
        sim.arrivals[self.job.job_id] = sim.t  # set the arrival time of the job
        sample_queues = sample(range(sim.n), sim.d)  # sample the id of d queues at random
        queue_index = min(sample_queues, key=sim.queue_len)  # shortest queue among the sampled ones

        if sim.running[queue_index] is None:
            sim.running[queue_index] = self.job
            sim.schedule_completion(self.job,queue_index)
        else:
            heapq.heappush(sim.queues[queue_index], (self.job.remaining_time, self.job))
            
          
        sim.schedule_arrival(self.job.job_id + 1)

class Completion(Event):
    """Job completion."""

    def __init__(self, job, queue_index):
        self.job = job  
        self.queue_index = queue_index

    def process(self, sim: Queues):
        queue_index = self.queue_index
        assert sim.running[queue_index].job_id == self.job.job_id  # the job must be the one running
        sim.completions[self.job.job_id] = sim.t
        
        queue = sim.queues[queue_index]

        if queue:
            # Assign the job with the shortest remaining time to start running
            _,shortest_job = heapq.heappop(queue)
            sim.running[queue_index] = shortest_job      
            sim.schedule_completion(shortest_job, queue_index)
        else:
            sim.running[queue_index] = None  # No job is running on the queue

class Monitoring(Event):
    """Event for periodic monitoring of queue lengths."""
    def process(self, sim: Queues):
        # Record the current queue lengths
        queue_lengths = [sim.queue_len(i) for i in range(sim.n)]
        sim.monitored_data.append(queue_lengths) #snapshot

        # Schedule the next monitoring event
        sim.schedule(sim.monitoring_interval, Monitoring())


def compute_queue_length_distribution(monitored_data, n):
    max_length = 30
    fractions = []
    for x in range(max_length + 1):
        fraction = [
            sum(1 for length in data if length >= x) / n
            for data in monitored_data
        ]
        fractions.append(np.mean(fraction))
    return fractions

def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--lambd', type=float, default=0.5, help="arrival rate")
    parser.add_argument('--mu', type=float, default=1, help="service rate")
    parser.add_argument('--max-t', type=float, default=1_000_000, help="maximum time to run the simulation")
    parser.add_argument('--n', type=int, default=10, help="number of servers")
    parser.add_argument('--d', type=int, default=2, help="number of queues to sample")
    parser.add_argument('--shape', type=float, default=1, help="weibull shape")
    parser.add_argument('--csv', help="CSV file in which to store results")
    parser.add_argument('--weibull', action=argparse.BooleanOptionalAction, default=False, help="use weibull distribution")
    parser.add_argument("--seed", help="random seed")
    parser.add_argument("--verbose", action='store_true')

    args = parser.parse_args()
    
  
    params = [getattr(args, column) for column in CSV_COLUMNS[:-1]]
    # corresponds to params = [args.lambd, args.mu, args.max_t, args.n, args.d]

    if any(x <= 0 for x in params):
        logging.error("lambd, mu, max-t, n and d must all be positive")
        exit(1)

    if args.seed:
        seed(args.seed)  # set a seed to make experiments repeatable
    if args.verbose:
        # output info on stderr
        logging.basicConfig(format='{levelname}:{message}', level=logging.INFO, style='{')

    if args.lambd >= args.mu:
        logging.warning("The system is unstable: lambda >= mu")

    monitor_delay = (args.max_t*0.001)/(args.n*args.lambd)
    sim = Queues(args.lambd, args.mu, args.n, args.d, monitor_delay, args.weibull,args.shape)
    sim.run(args.max_t)

    completions = sim.completions
    W = ((sum(completions.values()) - sum(sim.arrivals[job_id] for job_id in completions))
         / len(completions))
    print(f"Average time spent in the system: {W}")
    if args.mu == 1 and args.lambd != 1:
        print(f"Theoretical expectation for random server choice (d=1): {1 / (1 - args.lambd)}")

    if args.csv is not None:
        with open(args.csv, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(params + [W])

    # After the simulation ends
    queue_length_distribution = compute_queue_length_distribution(sim.monitored_data, args.n)

    # Save the results in a CSV file
    output_csv = f"./data-srpt/{args.d}_choice-weibull-shape{args.shape}.csv" if args.weibull else f"./data-srpt/{args.d}_choice.csv"
    with open(output_csv, mode="a", newline='') as csvfile:
        csvwriter = csv.writer(csvfile)

        # Write the header
        csvwriter.writerow([args.lambd])

        # Write the data
        for x, fraction in enumerate(queue_length_distribution):
            csvwriter.writerow([x, fraction])

        csvwriter.writerow([]) 



if __name__ == '__main__':
    main()
