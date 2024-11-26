#!/usr/bin/env python3
from matplotlib import pyplot as plt
import numpy as np
import argparse
import csv
import collections
import logging
from random import expovariate, sample, seed

from discrete_event_sim import Simulation, Event

# One possible modification is to use a different distribution for job sizes or and/or interarrival times.
# Weibull distributions (https://en.wikipedia.org/wiki/Weibull_distribution) are a generalization of the
# exponential distribution, and can be used to see what happens when values are more uniform (shape > 1,
# approaching a "bell curve") or less (shape < 1, "heavy tailed" case when most of the work is concentrated
# on few jobs).

# To use Weibull variates, for a given set of parameter do something like
# from workloads import weibull_generator
# gen = weibull_generator(shape, mean)
#
# and then call gen() every time you need a random variable


# columns saved in the CSV file
CSV_COLUMNS = ['lambd', 'mu', 'max_t', 'n', 'd', 'w']


class Queues(Simulation):
    """Simulation of a system with n servers and n queues.

    The system has n servers with one queue each. Jobs arrive at rate lambd and are served at rate mu.
    When a job arrives, according to the supermarket model, it chooses d queues at random and joins
    the shortest one.
    """

    def __init__(self, lambd, mu, n, d,monitoring_interval):
        super().__init__()
        self.running = [None] * n  # if not None, the id of the running job (per queue)
        self.queues = [collections.deque() for _ in range(n)]  # FIFO queues of the system
        # NOTE: we don't keep the running jobs in self.queues
        self.arrivals = {}  # dictionary mapping job id to arrival time
        self.completions = {}  # dictionary mapping job id to completion time
        self.lambd = lambd
        self.n = n
        self.d = d
        self.mu = mu
        self.arrival_rate = lambd * n  # frequency of new jobs is proportional to the number of queuesù
        
        self.monitoring_interval = monitoring_interval
        self.monitored_data = []  # to store the queue length stats
        self.schedule(0, Monitoring())  # schedule the first monitoring event
        
        self.schedule(expovariate(lambd), Arrival(0))  # schedule the first arrival
        
        
    def schedule_arrival(self, job_id):
        """Schedule the arrival of a new job."""

        # schedule the arrival following an exponential distribution, to compensate the number of queues the arrival
        # time should depend also on "n"

        # memoryless behavior results in exponentially distributed times between arrivals (we use `expovariate`)
        # the rate of arrivals is proportional to the number of queues

        self.schedule(expovariate(self.arrival_rate), Arrival(job_id))

    def schedule_completion(self, job_id, queue_index):  # TODO: complete this method
        """Schedule the completion of a job."""
        
        # schedule the time of the completion event
        # check `schedule_arrival` for inspiration
        
        self.schedule(expovariate(self.mu), Completion(job_id, queue_index))

    def queue_len(self, i):
        """Return the length of the i-th queue.
        
        Notice that the currently running job is counted even if it is not in self.queues[i]."""

        return (self.running[i] is not None) + len(self.queues[i])


class Arrival(Event):
    """Event representing the arrival of a new job."""

    def __init__(self, job_id):
        self.id = job_id

    def process(self, sim: Queues):  # TODO: complete this method
        sim.arrivals[self.id] = sim.t  # set the arrival time of the job
        sample_queues = sample(range(sim.n), sim.d)  # sample the id of d queues at random
        queue_index = min(sample_queues, key=sim.queue_len)  # shortest queue among the sampled ones
        # check the key argument of the min built-in function:
        # https://docs.python.org/3/library/functions.html#min

        # implement the following logic:

        # if there is no running job in the queue:
            # set the incoming one
            # schedule its completion
        # otherwise, put the job into the queue
        # schedule the arrival of the next job
        if sim.running[queue_index] is None:
            sim.running[queue_index] = self.id
            sim.schedule_completion(self.id,queue_index)
        else:
            sim.queues[queue_index].append(self.id)
       
        sim.schedule_arrival(self.id + 1)
        # if you are looking for inspiration, check the `Completion` class below


class Completion(Event):
    """Job completion."""

    def __init__(self, job_id, queue_index):
        self.job_id = job_id  # currently unused, might be useful when extending
        self.queue_index = queue_index

    def process(self, sim: Queues):
        queue_index = self.queue_index
        assert sim.running[queue_index] == self.job_id  # the job must be the one running
        sim.completions[self.job_id] = sim.t
        queue = sim.queues[queue_index]
        if queue:  # queue is not empty
            sim.running[queue_index] = new_job_id = queue.popleft()  # assign the first job in the queue
            sim.schedule_completion(new_job_id, queue_index)  # schedule its completion
        else:
            sim.running[queue_index] = None  # no job is running on the queue
            
            
class Monitoring(Event):
    """Event for periodic monitoring of queue lengths."""
    def process(self, sim: Queues):
        # Record the current queue lengths
        queue_lengths = [sim.queue_len(i) for i in range(sim.n)]
        sim.monitored_data.append(queue_lengths) #snapshot

        # Schedule the next monitoring event
        sim.schedule(sim.t + sim.monitoring_interval, Monitoring())
        
        
def compute_queue_length_distribution(monitored_data, n):
    max_length = max(max(data) for data in monitored_data)
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
    parser.add_argument('--monitor', type=float, default=200, help="monitor interval")
    parser.add_argument('--csv', help="CSV file in which to store results")
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

    sim = Queues(args.lambd, args.mu, args.n, args.d, args.monitor)
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
    output_csv = "queue_length_distribution.csv"
    with open(output_csv, mode="a", newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        
        # Write the header
        csvwriter.writerow([args.lambd])
        
        # Write the data
        for x, fraction in enumerate(queue_length_distribution):
            csvwriter.writerow([x, fraction])
            
        csvwriter.writerow([])  # This adds a blank row       
            
  

if __name__ == '__main__':
    main()
