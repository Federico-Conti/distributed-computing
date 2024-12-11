#!/usr/bin/env python3

import argparse
import csv
import matplotlib.pyplot as plt
import pandas as pd

def plot_data_availability(csv_file,n,k,al,b):
    # Liste per memorizzare i dati
    times = []
    availabilities = []

    # Conversione da secondi a anni (approssimando 1 anno = 365 giorni = 365 * 24 * 3600 secondi)
    SECONDS_IN_WEEK = 7 * 24 * 3600

    # Legge i dati dal file CSV
    with open(csv_file, mode="r") as csvfile:
        csvreader = csv.reader(csvfile)
        for row in csvreader:
            if row:  # Ignora righe vuote
                times.append(float(row[0]) / SECONDS_IN_WEEK)  # Converti in anni
                availabilities.append(float(row[1]))  # Percentuale di disponibilità

    # Creazione del DataFrame per pulire e organizzare i dati
    data = pd.DataFrame({"time": times, "availability": availabilities})
    
    # Calcola la media mobile per tracciare una linea di tendenza più chiara
    data["trend"] = data["availability"].rolling(window=32, center=True).mean()


    # Creazione del grafico con linee continue
    plt.figure(figsize=(10, 6))
    plt.plot(data["time"], data["availability"], linestyle='-', alpha=0.5, label="Data Availability (%)")
    plt.plot(data["time"], data["trend"], color='red', linewidth=2, label="Trend (Moving Average)")
    
    if b == 1:
     plt.title(f"Data Availability Over Time with N={n}, K={k}, AL={al}d")
    else:
     plt.title(f"Data Availability Over Time with N={n}, K={k}, AL={al}d, B={b}")
    
    plt.xlabel("Time (week)")
    plt.ylabel("Availability (%)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.ylim(60, 100)
    # plt.ylim(0, 100) # for AL=8
    plt.xlim(0, 2600)
    
    # Salva o mostra il grafico
    if b == 1:
        output_plot = f"./plots/{csv_file.rsplit('/', 1)[-1].rsplit('.', 1)[0]}.png"
    else:
        output_plot = f"./plots-mb/{csv_file.rsplit('/', 1)[-1].rsplit('.', 1)[0]}.png"
        
    plt.savefig(output_plot)
    
    
def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--csv', help="CSV file in which to store results")
    parser.add_argument('--n', type=int, help="number of blocks")
    parser.add_argument('--k',type=int, help="number of blocks required to reconstruct the original data ")
    parser.add_argument('--al',type=int, help="arrival_time")
    parser.add_argument('--b', type=int, default=1, help="b (default: 1)")
    args = parser.parse_args()
    plot_data_availability(args.csv,args.n,args.k,args.al,args.b)
    

if __name__ == '__main__':
    main()
