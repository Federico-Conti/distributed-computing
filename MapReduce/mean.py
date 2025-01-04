#!/usr/bin/env python3

import csv
import heapq

import simplemr


class FifaMean(simplemr.MapReduce):    
    def map(self, row):
        yield row['Club'], int(row['Overall'])
        
    def reduce(self, club, values):
        s = count = 0
        for v in values:
            s += v
            count +=1
        yield club, s/count

    
class FifaMeanCombine(simplemr.MapReduceCombine):    
    def map(self, row):
        yield row['Club'], (int(row['Overall']), 1)

    def combine(self, club, pairs):
        s = count = 0
        for v,c in pairs:
            s += v
            count += c
        yield club, (s,count)
        
    def reduce(self, club, pairs):
        s = count = 0
        for v,c in pairs:
            s += v
            count +=c
            
        yield club, s/count


if __name__ == '__main__':

    print("Without combiner")
    with open('fifa21.csv') as f:
        output = FifaMean().run(csv.DictReader(f))
        print(heapq.nlargest(10, output, key=simplemr.second))

    print("With combiner")
    with open('fifa21.csv') as f:
        output = FifaMeanCombine().run(csv.DictReader(f))
        print(heapq.nlargest(10, output, key=simplemr.second))

