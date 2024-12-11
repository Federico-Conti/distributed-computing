import csv
import matplotlib.pyplot as plt
import pandas as pd

# Percorso del file CSV
input_csv = "./data/availability.csv"

# Liste per memorizzare i dati
times = []
availabilities = []

# Conversione da secondi a anni (approssimando 1 anno = 365 giorni = 365 * 24 * 3600 secondi)
SECONDS_IN_YEAR = 365 * 24 * 3600

# Legge i dati dal file CSV
with open(input_csv, mode="r") as csvfile:
    csvreader = csv.reader(csvfile)
    for row in csvreader:
        if row:  # Ignora righe vuote
            times.append(float(row[0]) / SECONDS_IN_YEAR)  # Converti in anni
            availabilities.append(float(row[1]))  # Percentuale di disponibilità

# Creazione del DataFrame per pulire e organizzare i dati
data = pd.DataFrame({"time": times, "availability": availabilities})

# Calcola la media mobile per tracciare una linea di tendenza più chiara
data["trend"] = data["availability"].rolling(window=12, center=True).mean()

# Creazione del grafico con linee continue
plt.figure(figsize=(10, 6))
plt.plot(data["time"], data["availability"], linestyle='-', alpha=0.5, label="Data Availability (%)")
plt.plot(data["time"], data["trend"], color='red', linewidth=2, label="Trend (Moving Average)")
plt.title("Data Availability Over Time with Continuous Lines")
plt.xlabel("Time (years)")
plt.ylabel("Availability (%)")
plt.grid(True)
plt.legend()
plt.tight_layout()

# Salva o mostra il grafico
output_plot = "./data/availability_continuous_plot.png"
plt.savefig(output_plot)
plt.show()
