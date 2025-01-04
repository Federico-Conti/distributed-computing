#!/usr/bin/env python3

import pandas as pd
from tabulate import tabulate

file_path = 'data-srpt/avg_time.csv'

columns = ['Lambda', 'Mu', 'Max T', 'N', 'D', 'Average Time Spent(SRPT)', 'Theoretical Time']

df = pd.read_csv(file_path, header=None, names=columns)
df = df.drop(columns=['Max T'])

df['Average Time Spent(SRPT)'] = df['Average Time Spent(SRPT)'].round(2)
df['Theoretical Time'] = df['Theoretical Time'].round(2)

output_path = 'data-srpt/processed_avg_time.csv'
df.to_csv(output_path, index=False)

processed_df = pd.read_csv(output_path)

def tabulate_with_separators(df, headers, tablefmt, separator_interval):
    table = tabulate(df, headers=headers, tablefmt=tablefmt).split('\n')
    result = []
    for i, line in enumerate(table):
        if i < 2:
            result.append(line)
            continue
        result.append(line)
        if (i - 2) % separator_interval == 0 and i != 2:
            result.append('-' * len(line))
    return '\n'.join(result)

print(tabulate_with_separators(processed_df, headers='keys', tablefmt='psql', separator_interval=4))
