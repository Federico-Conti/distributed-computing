#!/usr/bin/env python3

import matplotlib.pyplot as plt
import argparse

def plot_queue_lengths(csv_file,d,weibull,shape,srpt):
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
    plt.ylabel('Fraction of queues with at least that size')
    if not srpt:
        plt.title(f"{d} choice/s{' (weibull, shape=' + str(shape) + ')' if weibull else ''}")
        plt.legend()
        plt.grid(True)
        plt.savefig(f"./plots/{d}_choice{'-weibull-shape' + str(shape) + '' if weibull else ''}.png")
    else: 
        plt.title(f"SRPT: {d} choice/s{' (weibull, shape=' + str(shape) + ')' if weibull else ''}")
        plt.legend()
        plt.grid(True)
        plt.savefig(f"./plots-srpt/{d}_choice{'-weibull-shape' + str(shape) + '' if weibull else ''}.png")
        
      
    


def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--weibull', action=argparse.BooleanOptionalAction, help="raname as weibull plot")
    parser.add_argument('--srpt',action=argparse.BooleanOptionalAction, help="use srpt alghoritm")
    parser.add_argument('--csv', help="CSV file in which to store results")
    parser.add_argument('--d', type=int, help="number of queues to sample")
    parser.add_argument('--shape', type=float, default=1, help="weibull shape")
    args = parser.parse_args()
    plot_queue_lengths(args.csv ,args.d,args.weibull,args.shape,args.srpt)
    

if __name__ == '__main__':
    main()
