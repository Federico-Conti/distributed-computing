#!/usr/bin/env python3

import argparse
import csv
import matplotlib.pyplot as plt
import pandas as pd

def plot_data_availability(csv_file,n,k,al,diverse):

    times = []
    availabilities = []

    SECONDS_IN_WEEK = 7 * 24 * 3600
   
    with open(csv_file, mode="r") as csvfile:
        csvreader = csv.reader(csvfile)
        for row in csvreader:
            if row:  
                times.append(float(row[0]) / SECONDS_IN_WEEK)  
                availabilities.append(float(row[1])) 

    # Create DataFrame to clean and organize data
    data = pd.DataFrame({"time": times, "availability": availabilities})
    
    # Calculate the moving average to plot a clearer trend line
    data["trend"] = data["availability"].rolling(window=32, center=True).mean()

    plt.figure(figsize=(10, 6))
    plt.plot(data["time"], data["availability"], linestyle='-', alpha=0.5, label="Data Availability (%)")
    plt.plot(data["time"], data["trend"], color='red', linewidth=2, label="Trend (Moving Average)")
    plt.title(f"Data Availability Over Time with N={n}, K={k}, AL={al}d")

    
    plt.xlabel("Time (week)")
    plt.ylabel("Availability (%)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    # plt.ylim(60, 100) # for cfg with AL >= 1 year
    plt.ylim(0, 100) # for others
    plt.xlim(0, 2600)
    
    if diverse:
        output_plot = f"./diverse-plots/{csv_file.rsplit('/', 1)[-1].rsplit('.', 1)[0]}.png"
    else:
        output_plot = f"./basic-plots/{csv_file.rsplit('/', 1)[-1].rsplit('.', 1)[0]}.png"
        
    plt.savefig(output_plot)
    
    
def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--csv', help="CSV file in which to store results")
    parser.add_argument('--n', type=int, help="number of blocks")
    parser.add_argument('--k',type=int, help="number of blocks required to reconstruct the original data ")
    parser.add_argument('--al',type=int, help="arrival_time")
    parser.add_argument('--diverse',action=argparse.BooleanOptionalAction, default=0, help="random diverse block")
    
    args = parser.parse_args()
    plot_data_availability(args.csv,args.n,args.k,args.al,args.diverse)
    

if __name__ == '__main__':
    main()
