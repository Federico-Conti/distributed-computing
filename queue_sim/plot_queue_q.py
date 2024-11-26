#import pandas as pd
import matplotlib.pyplot as plt
import argparse

def plot_queue_lengths(csv_file):
    # Legge i dati dal CSV
    with open(csv_file, 'r') as file:
        lines = file.readlines()

    # Parsing del CSV
    data = {}

    while lines:
        current_lambda = float(lines.pop(0).strip())
        data[current_lambda] = []

        while lines and lines[0].strip() != '':
            parts = lines.pop(0).split(',')
            queue_length = int(parts[0])
            fraction = float(parts[1])
            data[current_lambda].append((queue_length, fraction))
        
        if lines:
            lines.pop(0)

    for lambda_value, values in data.items():
        queue_lengths, fractions = zip(*sorted(values))
        plt.plot(queue_lengths, fractions, label=f'λ={lambda_value}')
    

    plt.xlabel('Queue Length')
    plt.ylabel('Fraction')
    #plt.title(f'Queue Length Distribution (d={d})')
    plt.legend()
    plt.show()

    


def main():
   plot_queue_lengths("/home/lolablank/Desktop/dc/distributed-computing/queue_sim/queue_length_distribution.csv")

if __name__ == '__main__':
    main()
