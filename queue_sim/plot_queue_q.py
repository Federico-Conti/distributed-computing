#TODO

import pandas as pd
import matplotlib.pyplot as plt

def plot_queue_lengths(csv_file):
    # Legge i dati dal CSV
    with open(csv_file, 'r') as file:
        lines = file.readlines()

    # Parsing del CSV
    data = {}
    current_lambda = None
    for line in lines:
        line = line.strip()
        if not line:
            continue

        parts = line.split(',')
        if len(parts) == 2:  # Indicatore di una nuova sezione lambda
            current_lambda = float(parts[0])
        
            data[current_lambda] = []
        else:  # Riga di dati
            queue_length = int(parts[0])
            fraction = float(parts[1])
            data[current_lambda].append((queue_length, fraction))

    # Crea il grafico
    plt.figure(figsize=(10, 6))
    for lambda_val, values in data.items():
        x = [v[0] for v in values]
        y = [v[1] for v in values]
        plt.plot(x, y, label=f'$\u03BB$ = {lambda_val}')

    # Personalizza il grafico
    plt.title('2 Choices')
    plt.xlabel('Queue length')
    plt.ylabel('Fraction of queues with at least that size')
    plt.legend()
    plt.grid(True)
    plt.savefig("queue_length_distribution.png")

def main():
   plot_queue_lengths("queue_length_distribution.csv")

if __name__ == '__main__':
    main()
